"""
Sample data for testing Career DNA Assessment application
"""
import json

# Sample admin data
SAMPLE_ADMINS = [
    {
        "username": "testadmin1",
        "password": "testpass123"
    },
    {
        "username": "testadmin2", 
        "password": "testpass456"
    }
]

# Sample category data
SAMPLE_CATEGORIES = [
    {
        "name": "Career Exploration",
        "description": "Questions about career paths and interests",
        "color": "#3498db"
    },
    {
        "name": "Work Style",
        "description": "Questions about work preferences and style",
        "color": "#2ecc71"
    },
    {
        "name": "Skills Assessment",
        "description": "Questions to assess various skills",
        "color": "#e74c3c"
    },
    {
        "name": "Personal Development",
        "description": "Questions about growth and development goals",
        "color": "#f39c12"
    }
]

# Sample page data
SAMPLE_PAGES = [
    {
        "title": "Introduction",
        "description": "Welcome to the Career DNA Assessment. This first section will help us understand your background.",
        "order_index": 0,
        "is_active": True
    },
    {
        "title": "Work Preferences", 
        "description": "Tell us about your work style and preferences.",
        "order_index": 1,
        "is_active": True
    },
    {
        "title": "Skills and Interests",
        "description": "Assess your skills and areas of interest.",
        "order_index": 2,
        "is_active": True
    },
    {
        "title": "Career Goals",
        "description": "Share your career aspirations and future plans.",
        "order_index": 3,
        "is_active": True
    }
]

# Sample question data
SAMPLE_QUESTIONS = [
    # Introduction page questions
    {
        "page_title": "Introduction",
        "question_text": "Please describe your educational background and any relevant experience.",
        "question_type": "essay",
        "order_index": 0,
        "is_required": True,
        "essay_char_limit": 500
    },
    {
        "page_title": "Introduction", 
        "question_text": "How would you rate your overall satisfaction with your current career path?",
        "question_type": "slider",
        "order_index": 1,
        "is_required": True,
        "slider_min_label": "Very dissatisfied",
        "slider_max_label": "Very satisfied"
    },
    
    # Work Preferences questions
    {
        "page_title": "Work Preferences",
        "question_text": "Describe your ideal work environment.",
        "question_type": "essay",
        "order_index": 0,
        "is_required": True,
        "essay_char_limit": 300
    },
    {
        "page_title": "Work Preferences",
        "question_text": "How important is work-life balance to you?",
        "question_type": "slider",
        "order_index": 1,
        "is_required": True,
        "slider_min_label": "Not important",
        "slider_max_label": "Extremely important"
    },
    {
        "page_title": "Work Preferences",
        "question_text": "Do you prefer working independently or as part of a team?",
        "question_type": "slider",
        "order_index": 2,
        "is_required": True,
        "slider_min_label": "Independently",
        "slider_max_label": "Team-oriented"
    },
    
    # Skills and Interests questions
    {
        "page_title": "Skills and Interests",
        "question_text": "What are your strongest technical skills? Please provide specific examples.",
        "question_type": "essay",
        "order_index": 0,
        "is_required": True,
        "essay_char_limit": 400
    },
    {
        "page_title": "Skills and Interests",
        "question_text": "Which of the following work environments do you prefer?",
        "question_type": "mcq",
        "order_index": 1,
        "is_required": True,
        "mcq_options": json.dumps(["Office-based", "Remote work", "Hybrid", "Field work"]),
        "mcq_correct_answer": json.dumps([0]),
        "allow_multiple_selection": False
    },
    {
        "page_title": "Skills and Interests",
        "question_text": "Which skills would you like to develop further? (Select all that apply)",
        "question_type": "mcq",
        "order_index": 2,
        "is_required": True,
        "mcq_options": json.dumps(["Leadership", "Communication", "Technical", "Project Management", "Creative"]),
        "mcq_correct_answer": json.dumps([0, 1]),
        "allow_multiple_selection": True
    },
    {
        "page_title": "Skills and Interests",
        "question_text": "How confident are you in your problem-solving abilities?",
        "question_type": "slider",
        "order_index": 3,
        "is_required": True,
        "slider_min_label": "Not confident",
        "slider_max_label": "Very confident"
    },
    {
        "page_title": "Skills and Interests",
        "question_text": "Rate your interest in continuous learning and professional development.",
        "question_type": "slider",
        "order_index": 4,
        "is_required": True,
        "slider_min_label": "Low interest",
        "slider_max_label": "High interest"
    },
    {
        "page_title": "Skills and Interests",
        "question_text": "Rank these career factors by importance to you",
        "question_type": "ordering",
        "order_index": 5,
        "is_required": True,
        "ordering_options": json.dumps(["Salary and Benefits", "Work-Life Balance", "Career Growth", "Job Security", "Company Culture"]),
        "randomize_order": True
    },
    
    # Career Goals questions
    {
        "page_title": "Career Goals",
        "question_text": "Where do you see yourself professionally in 5 years? Please be specific about your goals and aspirations.",
        "question_type": "essay",
        "order_index": 0,
        "is_required": True,
        "essay_char_limit": 600
    },
    {
        "page_title": "Career Goals",
        "question_text": "How important is career advancement and promotion to you?",
        "question_type": "slider",
        "order_index": 1,
        "is_required": True,
        "slider_min_label": "Not important",
        "slider_max_label": "Very important"
    }
]

# Sample student response data
SAMPLE_STUDENTS = [
    {
        "email": "john.doe@email.com",
        "full_name": "John Doe",
        "age_group": "23-25",
        "country": "United States",
        "origin_country": "United States"
    },
    {
        "email": "maria.garcia@email.com",
        "full_name": "Maria Garcia",
        "age_group": "26-30",
        "country": "Spain",
        "origin_country": "Mexico"
    },
    {
        "email": "ahmed.hassan@email.com",
        "full_name": "Ahmed Hassan",
        "age_group": "19-22",
        "country": "Canada",
        "origin_country": "Egypt"
    },
    {
        "email": "priya.sharma@email.com",
        "full_name": "Priya Sharma",
        "age_group": "31-35",
        "country": "Australia",
        "origin_country": "India"
    },
    {
        "email": "alex.chen@email.com",
        "full_name": "Alex Chen",
        "age_group": "26-30", 
        "country": "United Kingdom",
        "origin_country": "South Korea"
    }
]

# Sample answer data
SAMPLE_ANSWERS = {
    "essay_answers": [
        "I have a Bachelor's degree in Computer Science and 2 years of experience as a software developer. I've worked primarily with Python and JavaScript, building web applications and APIs.",
        
        "My ideal work environment is collaborative but also allows for focused individual work. I prefer open office spaces with quiet areas available for concentration. I value companies that prioritize innovation and continuous learning.",
        
        "My strongest technical skills include full-stack web development, database design, and API development. For example, I built a customer management system using React, Node.js, and PostgreSQL that improved client response time by 40%.",
        
        "In 5 years, I see myself as a senior software engineer or team lead, possibly specializing in cloud architecture or AI/ML applications. I want to mentor junior developers and contribute to technical decision-making in my organization."
    ],
    
    "slider_answers": [75, 85, 60, 90, 70, 88, 95, 80]  # Values from 0-100
}

# Countries list for testing
COUNTRIES = [
    "United States", "Canada", "United Kingdom", "Germany", "France", 
    "Australia", "Japan", "South Korea", "India", "Brazil", "Mexico",
    "Spain", "Italy", "Netherlands", "Sweden", "Norway", "Denmark"
]

# Age groups for testing
AGE_GROUPS = [
    "16-18", "19-22", "23-25", "26-30", "31-35", "36+"
]

def get_sample_complete_assessment():
    """
    Get a complete sample assessment with all components
    """
    return {
        "pages": SAMPLE_PAGES,
        "questions": SAMPLE_QUESTIONS,
        "students": SAMPLE_STUDENTS[:2],  # Use first 2 students
        "answers": SAMPLE_ANSWERS
    }

# Sample Question Pool data
SAMPLE_QUESTION_POOL = [
    {
        "title": "Career Aspirations",
        "question_text": "What are your long-term career goals?",
        "question_type": "essay",
        "category_name": "Career Exploration",
        "is_required": True,
        "essay_char_limit": 500,
        "created_by": "admin"
    },
    {
        "title": "Teamwork Rating",
        "question_text": "How much do you enjoy working in teams?",
        "question_type": "slider",
        "category_name": "Work Style",
        "is_required": True,
        "slider_min_label": "Prefer solo work",
        "slider_max_label": "Love teamwork",
        "created_by": "admin"
    },
    {
        "title": "Preferred Industries",
        "question_text": "Which industries interest you most?",
        "question_type": "mcq",
        "category_name": "Career Exploration",
        "is_required": True,
        "mcq_options": json.dumps(["Technology", "Healthcare", "Finance", "Education", "Manufacturing"]),
        "mcq_correct_answer": json.dumps([0]),
        "allow_multiple_selection": True,
        "created_by": "admin"
    },
    {
        "title": "Value Priorities",
        "question_text": "Rank these work values by importance",
        "question_type": "ordering",
        "category_name": "Work Style",
        "is_required": True,
        "ordering_options": json.dumps(["Autonomy", "Recognition", "Stability", "Innovation", "Impact"]),
        "randomize_order": True,
        "created_by": "admin"
    }
]

# Sample CSV data for testing imports
SAMPLE_CSV_ESSAY = """title,question_text,category_name,is_required,essay_char_limit
Career Background,Describe your professional background and experience,Career Exploration,TRUE,500
Future Goals,What are your career goals for the next 5 years?,Career Exploration,TRUE,400
Work Environment,Describe your ideal work environment,Work Style,TRUE,300"""

SAMPLE_CSV_SLIDER = """title,question_text,category_name,is_required,slider_min_label,slider_max_label
Leadership Interest,How interested are you in leadership roles?,Skills Assessment,TRUE,Not interested,Very interested
Technical Skills,Rate your technical proficiency,Skills Assessment,TRUE,Beginner,Expert
Creativity Level,How creative do you consider yourself?,Personal Development,TRUE,Not creative,Highly creative"""

SAMPLE_CSV_MCQ = """title,question_text,category_name,is_required,option_1,option_2,option_3,option_4,correct_answers,allow_multiple_selection
Work Schedule,What is your preferred work schedule?,Work Style,TRUE,9-5 weekdays,Flexible hours,Remote,Shift work,1,FALSE
Skills to Develop,Which skills would you like to improve?,Skills Assessment,TRUE,Communication,Leadership,Technical,Analytical,1 2,TRUE"""

SAMPLE_CSV_ORDERING = """title,question_text,category_name,is_required,item_1,item_2,item_3,item_4,randomize_order
Career Factors,Rank these career factors,Career Exploration,TRUE,Salary,Growth,Balance,Security,TRUE
Job Priorities,Prioritize these job aspects,Work Style,TRUE,Culture,Location,Benefits,Title,TRUE"""

# Invalid CSV data for error testing
INVALID_CSV_ESSAY = """title,question_text,category_name,is_required,essay_char_limit
Missing Title,,Career Exploration,TRUE,500
Invalid Limit,Some question text,Career Exploration,TRUE,invalid
Nonexistent Category,Question text,Fake Category,TRUE,300"""