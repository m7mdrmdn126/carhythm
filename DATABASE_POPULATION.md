# Database Population Guide

## Overview
The `populate_db.py` script creates realistic fake data for the Career DNA Assessment application, perfect for testing and demonstration purposes.

## What Gets Created

### 📄 Assessment Pages (5 pages)
1. **Personal Background** - Education and professional history
2. **Work Preferences** - Ideal work environment and preferences  
3. **Skills & Interests** - Technical skills and areas of expertise
4. **Career Goals** - Future aspirations and career plans
5. **Values & Motivation** - What drives you in your career

### ❓ Questions (15 questions total)
- **Essay Questions (9)**: Open-ended questions about background, preferences, skills, and goals
- **Slider Questions (6)**: Rating scales for experience level, importance ratings, preferences

### 👥 Student Responses
- Realistic student profiles with names, emails, age groups, and countries
- Completed examination responses with contextual answers
- Variety of career backgrounds and experience levels

### 👤 Admin Users
- Additional demo admin accounts for testing

## Usage

### Quick Start (Automatic Mode)
```bash
# Windows
.\populate_db.bat

# Or run directly with Python
python populate_db.py --auto --responses=25
```

### Interactive Mode
```bash
python populate_db.py
```
You'll be prompted to:
- Choose whether to clear existing data
- Specify number of student responses to create

### Command Line Options
```bash
# Auto mode with custom response count
python populate_db.py --auto --responses=50

# Auto mode with data clearing
python populate_db.py --auto --clear --responses=30

# Help
python populate_db.py --help
```

## Sample Data Quality

### Realistic Essay Responses
The script generates contextually appropriate answers using templates:

- **Educational Background**: Degrees, universities, certifications, specializations
- **Job Roles**: Current positions, responsibilities, achievements
- **Career Goals**: 3-5 year plans, advancement objectives, industry interests
- **Skills**: Technical proficiencies, tools, platforms, experience levels
- **Motivations**: What drives career decisions and work satisfaction

### Career-Focused Content
All generated content is relevant to career assessment:
- Job titles from various industries
- Realistic skill combinations
- Appropriate experience levels
- Industry-standard tools and technologies
- Professional development activities

### Diverse Demographics
- Various age groups (18-25, 26-35, 36-45, 46-55, 55+)
- Global representation with different countries
- Mixed education levels (High School to PhD)
- Range of experience levels (0-20+ years)

## Database Structure After Population

```
📊 Typical Result:
├── 5 Assessment Pages
├── 15 Questions (9 essay + 6 slider)  
├── 25 Student Responses (customizable)
├── 375 Individual Answers (15 questions × 25 students)
└── Additional Admin Accounts
```

## Additional Admin Accounts Created

| Username   | Password | Purpose        |
|------------|----------|----------------|
| demo_admin | demo123  | Demo/Testing   |
| test_user  | test123  | Testing        |

## Benefits for Testing

### 1. **Realistic Demo Data**
- Professional-looking content for demonstrations
- Varied response types and lengths
- Contextually appropriate career information

### 2. **Development Testing**
- Test pagination with multiple pages
- Verify question rendering (essay vs slider)
- Test answer submission and storage
- Validate admin dashboard functionality

### 3. **Performance Testing**
- Generate large datasets for load testing
- Test database query performance
- Verify UI responsiveness with real data

### 4. **User Acceptance Testing**
- Realistic content for stakeholder reviews
- Complete user flow demonstration
- Professional appearance for client presentations

## Customization

### Modify Number of Responses
```bash
# Create 100 student responses
python populate_db.py --auto --responses=100
```

### Preserve Existing Data
```bash
# Don't clear existing data, just add more
python populate_db.py --auto
# (and choose 'N' when prompted, or omit --clear flag)
```

### Custom Content
Edit the `populate_db.py` script to:
- Add new question types or topics
- Modify essay response templates
- Change demographic distributions
- Add industry-specific content

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure `faker` is installed
   ```bash
   pip install faker
   ```

2. **Database Lock**: Close any database connections/admin panels before running

3. **Permission Error**: Ensure write permissions to the database file location

### Verification Steps

After running the script:
1. Visit http://localhost:8000/admin (login: admin/admin123)
2. Check "Manage Pages" - should see 5 pages
3. Check "Manage Questions" - should see 15 questions
4. Check "View Results" - should see student responses
5. Test student interface at http://localhost:8000

## Production Notes

⚠️ **Important**: This script is for development and testing only. Do not run on production databases without understanding the implications:

- Uses `--clear` flag to delete existing data
- Generates fake personal information
- Creates test admin accounts with simple passwords
- Bypasses normal application validation flows

For production use:
- Remove or secure additional admin accounts
- Use real content instead of generated text
- Implement proper data validation
- Follow your organization's data policies