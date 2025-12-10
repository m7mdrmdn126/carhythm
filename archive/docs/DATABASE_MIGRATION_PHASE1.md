# Database Migration for Phase 1: Session Management

## Overview
Phase 1 adds session status tracking to enable pause/resume functionality and the "Start Fresh" feature.

## Changes Made to Models

### 1. SessionStatus Enum (new)
```python
class SessionStatus(enum.Enum):
    active = "active"                              # Current session in progress
    completed = "completed"                         # Assessment finished
    abandoned = "user_abandoned_not_completed"      # User chose "Start Fresh"
```

### 2. StudentResponse Model (updated)
Added 3 new fields:
- **status**: Tracks session lifecycle (active/completed/abandoned)
- **last_activity**: Auto-updates timestamp for 30-day expiration logic
- **current_page_id**: Tracks where user left off for resume functionality

## Migration SQL

### For SQLite (if using SQLite):
```sql
-- Add status column (default to 'active')
ALTER TABLE student_responses ADD COLUMN status TEXT DEFAULT 'active' NOT NULL;

-- Add last_activity column (default to current timestamp)
ALTER TABLE student_responses ADD COLUMN last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add current_page_id column (nullable, references pages table)
ALTER TABLE student_responses ADD COLUMN current_page_id INTEGER REFERENCES pages(id);

-- Create index on status for query performance
CREATE INDEX idx_student_responses_status ON student_responses(status);
```

### For PostgreSQL (if using PostgreSQL):
```sql
-- Create enum type
CREATE TYPE sessionstatus AS ENUM ('active', 'completed', 'user_abandoned_not_completed');

-- Add status column
ALTER TABLE student_responses ADD COLUMN status sessionstatus DEFAULT 'active' NOT NULL;

-- Add last_activity column
ALTER TABLE student_responses ADD COLUMN last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add current_page_id column
ALTER TABLE student_responses ADD COLUMN current_page_id INTEGER REFERENCES pages(id);

-- Create index
CREATE INDEX idx_student_responses_status ON student_responses(status);
```

## Migration Steps

### Option 1: Manual SQL Execution
1. Stop the application
2. Backup your database:
   ```bash
   # For SQLite
   cp carhythm.db carhythm.db.backup
   
   # For PostgreSQL
   pg_dump -U your_user carhythm > carhythm_backup.sql
   ```
3. Connect to your database and run the appropriate SQL above
4. Restart the application

### Option 2: Using Alembic (if configured)
```bash
# Generate migration
alembic revision -m "add_session_status_tracking"

# Edit the generated migration file in alembic/versions/
# Copy the SQL commands from above into upgrade() and create downgrade()

# Apply migration
alembic upgrade head
```

## Verification

After migration, verify the changes:

```sql
-- Check new columns exist
PRAGMA table_info(student_responses);  -- SQLite
-- or
\d student_responses  -- PostgreSQL

-- Check index exists
.indexes student_responses  -- SQLite
-- or
\di idx_student_responses_status  -- PostgreSQL
```

## New API Endpoints

These endpoints are now available after Phase 1:

### 1. Validate Session
```
GET /api/v2/session/{session_id}/validate
```
Returns:
- `valid`: boolean (false if not found or expired)
- `session`: session info (status, current_page_id, last_activity)
- `progress`: progress info (questions_answered, total_xp, percentage)

### 2. Abandon Session
```
POST /api/v2/session/{session_id}/abandon
```
Marks session as "user_abandoned_not_completed" when user chooses "Start Fresh"

### 3. Updated Answer Submission
```
POST /api/v2/answers/submit
```
Now returns XP information:
- `xp_gained`: 10 (fixed per question)
- `total_xp`: total XP earned in session
- `progress`: detailed progress info

## Testing

After migration, test the new functionality:

```bash
# Test session validation (should return valid=false for non-existent session)
curl http://localhost:8000/api/v2/session/test-123/validate

# Start a new session
curl -X POST http://localhost:8000/api/v2/session/start

# Test abandon endpoint (use real session_id from above)
curl -X POST http://localhost:8000/api/v2/session/YOUR_SESSION_ID/abandon
```

## Rollback

If needed, rollback the migration:

### SQLite:
```sql
-- Cannot directly drop columns in SQLite
-- Restore from backup instead
cp carhythm.db.backup carhythm.db
```

### PostgreSQL:
```sql
-- Drop columns
ALTER TABLE student_responses DROP COLUMN current_page_id;
ALTER TABLE student_responses DROP COLUMN last_activity;
ALTER TABLE student_responses DROP COLUMN status;

-- Drop index
DROP INDEX idx_student_responses_status;

-- Drop enum type
DROP TYPE sessionstatus;
```

## Notes

- **30-Day Expiration**: Sessions older than 30 days (based on `last_activity`) will be considered invalid
- **Backwards Compatibility**: Existing records will have `status='active'` by default
- **Current Page Tracking**: Will be NULL for existing records (they can continue normally)
- **Performance**: Index on `status` field improves query performance for filtering active sessions

## Next Steps

After applying this migration:
1. ✅ Backend is ready for pause/resume
2. ⏳ Continue with Phase 2: Frontend Storage Layer
3. ⏳ Then Phase 3: Resume Modal Component

The frontend will start using these endpoints in Phase 2-3.
