"""
Sample data for testing Career DNA Assessment application
"""

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
        "question_text": "How confident are you in your problem-solving abilities?",
        "question_type": "slider",
        "order_index": 1,
        "is_required": True,
        "slider_min_label": "Not confident",
        "slider_max_label": "Very confident"
    },
    {
        "page_title": "Skills and Interests",
        "question_text": "Rate your interest in continuous learning and professional development.",
        "question_type": "slider",
        "order_index": 2,
        "is_required": True,
        "slider_min_label": "Low interest",
        "slider_max_label": "High interest"
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