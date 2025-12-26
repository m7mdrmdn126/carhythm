#!/bin/bash

# Server Database Update Script
# This script updates the production database with all recent changes
# Run this on the server after git pull

echo "=========================================="
echo "🔄 CaRhythm Database Update Script"
echo "=========================================="
echo ""

# Set variables
DB_PATH="career_dna.db"
BACKUP_PATH="career_dna.db.backup_$(date +%Y%m%d_%H%M%S)"

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "❌ Error: Database not found at $DB_PATH"
    exit 1
fi

# 1. Backup database
echo "📦 Step 1/4: Creating backup..."
cp "$DB_PATH" "$BACKUP_PATH"
if [ $? -eq 0 ]; then
    echo "✅ Backup created: $BACKUP_PATH"
else
    echo "❌ Backup failed!"
    exit 1
fi

# 2. Add translation columns (if not already present)
echo ""
echo "🔧 Step 2/4: Adding Arabic translation columns..."
python3 scripts/add_translation_columns.py
if [ $? -eq 0 ]; then
    echo "✅ Translation columns added"
else
    echo "⚠️  Warning: Translation columns may already exist (this is OK)"
fi

# 3. Populate Arabic translations
echo ""
echo "🌍 Step 3/4: Populating Arabic translations..."
python3 scripts/add_arabic_translations.py
if [ $? -eq 0 ]; then
    echo "✅ Arabic translations added (73 questions)"
else
    echo "❌ Translation population failed!"
    exit 1
fi

# 4. Update module names and descriptions
echo ""
echo "📝 Step 4/4: Updating module metadata..."
sqlite3 "$DB_PATH" << 'EOF'
UPDATE pages SET 
  title = 'The Signal',
  title_ar = 'الإشارة',
  module_name = 'The Signal',
  module_name_ar = 'الإشارة',
  module_emoji = '🧠',
  description = 'Decoding Your Mental Engine',
  module_description = 'Your grades measure what you remember. This measures what lights you up. We are tracing the sparks in your brain to see which problems you naturally love to solve. Do you build, analyze, create, or lead?'
WHERE id = 1;

UPDATE pages SET 
  title = 'The Fingerprint',
  title_ar = 'البصمة',
  module_name = 'The Fingerprint',
  module_name_ar = 'البصمة',
  module_emoji = '👆',
  description = 'Mapping Your Unique Design',
  module_description = 'Skills can be learned, but your nature is fixed ink. Are you a rock or a river? Detailed or big-picture? We map the deep, unchangeable traits that make you you—so you can stop fighting your nature and start leveraging it.'
WHERE id = 2;

UPDATE pages SET 
  title = 'The Compass',
  title_ar = 'البوصلة',
  module_name = 'The Compass',
  module_name_ar = 'البوصلة',
  module_emoji = '🎵',
  description = 'Calibrating Your Work Rhythm',
  module_description = 'You have the map. Now let us check the engine. This section measures the physics of how you work. What fuels you? How fast do you rebound from failure? Do you sprint or marathon? Let us find your operational rhythm.'
WHERE id = 3;
EOF

if [ $? -eq 0 ]; then
    echo "✅ Module metadata updated"
else
    echo "❌ Module update failed!"
    exit 1
fi

# Verify updates
echo ""
echo "=========================================="
echo "🔍 Verification"
echo "=========================================="
echo ""
echo "Module Configuration:"
sqlite3 "$DB_PATH" "SELECT id, module_name, module_name_ar, module_emoji FROM pages;"

echo ""
echo "Question Translation Status:"
sqlite3 "$DB_PATH" "SELECT COUNT(*) || ' questions have Arabic translations' FROM questions WHERE question_text_ar IS NOT NULL;"

echo ""
echo "=========================================="
echo "✅ Database Update Complete!"
echo "=========================================="
echo ""
echo "Backup saved at: $BACKUP_PATH"
echo ""
echo "Next steps:"
echo "  1. Restart backend: sudo systemctl restart carhythm-backend"
echo "  2. Test the application"
echo ""
