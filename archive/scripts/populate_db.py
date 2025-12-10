"""
Database Population Script for Career DNA Assessment
This script fills the database with realistic fake data for testing and demonstration.
"""

import os
import sys
import random
from datetime import datetime, timedelta
from faker import Faker

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.database import SessionLocal, create_tables
from app.models import Admin, Page, Question, QuestionType, StudentResponse, QuestionAnswer
from app.utils.security import get_password_hash

# Initialize Faker
fake = Faker()

def clear_database():
    """Clear all existing data (except admin users)"""
    print("🗑️  Clearing existing data...")
    db = SessionLocal()
    try:
        # Delete in correct order to avoid foreign key constraints
        db.query(QuestionAnswer).delete()
        db.query(StudentResponse).delete()
        db.query(Question).delete()
        db.query(Page).delete()
        db.commit()
        print("✅ Database cleared successfully")
    except Exception as e:
        db.rollback()
        print(f"❌ Error clearing database: {e}")
    finally:
        db.close()

def create_sample_pages_and_questions():
    """Create realistic pages and questions for career assessment"""
    print("📄 Creating sample pages and questions...")
    
    db = SessionLocal()
    try:
        # Sample pages with career-focused content
        pages_data = [
            {
                "title": "Personal Background",
                "description": "Tell us about your educational and professional background",
                "order_index": 0
            },
            {
                "title": "Work Preferences", 
                "description": "Help us understand your ideal work environment and preferences",
                "order_index": 1
            },
            {
                "title": "Skills & Interests",
                "description": "Share your skills, interests, and areas of expertise",
                "order_index": 2
            },
            {
                "title": "Career Goals",
                "description": "Describe your career aspirations and future plans",
                "order_index": 3
            },
            {
                "title": "Values & Motivation",
                "description": "What drives you and what do you value most in your career?",
                "order_index": 4
            }
        ]
        
        pages = []
        for page_data in pages_data:
            page = Page(**page_data)
            db.add(page)
            pages.append(page)
        
        db.commit()
        
        # Create questions for each page
        questions_data = [
            # Personal Background Page
            {
                "page_id": pages[0].id,
                "question_text": "Please describe your educational background, including your highest degree, field of study, and any relevant certifications or training.",
                "question_type": QuestionType.essay,
                "order_index": 0,
                "is_required": True,
                "essay_char_limit": 500
            },
            {
                "page_id": pages[0].id,
                "question_text": "How many years of professional work experience do you have?",
                "question_type": QuestionType.slider,
                "order_index": 1,
                "is_required": True,
                "slider_min_label": "0 years",
                "slider_max_label": "20+ years"
            },
            {
                "page_id": pages[0].id,
                "question_text": "Describe your current or most recent job role and key responsibilities.",
                "question_type": QuestionType.essay,
                "order_index": 2,
                "is_required": True,
                "essay_char_limit": 400
            },
            
            # Work Preferences Page
            {
                "page_id": pages[1].id,
                "question_text": "Rate how important work-life balance is to you in your career.",
                "question_type": QuestionType.slider,
                "order_index": 0,
                "is_required": True,
                "slider_min_label": "Not Important",
                "slider_max_label": "Extremely Important"
            },
            {
                "page_id": pages[1].id,
                "question_text": "Do you prefer working independently or as part of a team? Explain your preference.",
                "question_type": QuestionType.essay,
                "order_index": 1,
                "is_required": True,
                "essay_char_limit": 300
            },
            {
                "page_id": pages[1].id,
                "question_text": "How comfortable are you with remote/hybrid work arrangements?",
                "question_type": QuestionType.slider,
                "order_index": 2,
                "is_required": False,
                "slider_min_label": "Prefer Office",
                "slider_max_label": "Love Remote Work"
            },
            
            # Skills & Interests Page
            {
                "page_id": pages[2].id,
                "question_text": "List your top 5 technical or professional skills and rate your proficiency in each.",
                "question_type": QuestionType.essay,
                "order_index": 0,
                "is_required": True,
                "essay_char_limit": 400
            },
            {
                "page_id": pages[2].id,
                "question_text": "How interested are you in learning new technologies and staying up-to-date with industry trends?",
                "question_type": QuestionType.slider,
                "order_index": 1,
                "is_required": True,
                "slider_min_label": "Not Interested",
                "slider_max_label": "Very Eager"
            },
            {
                "page_id": pages[2].id,
                "question_text": "Describe a project or achievement you're particularly proud of and what made it successful.",
                "question_type": QuestionType.essay,
                "order_index": 2,
                "is_required": False,
                "essay_char_limit": 450
            },
            
            # Career Goals Page
            {
                "page_id": pages[3].id,
                "question_text": "Where do you see yourself professionally in the next 3-5 years?",
                "question_type": QuestionType.essay,
                "order_index": 0,
                "is_required": True,
                "essay_char_limit": 400
            },
            {
                "page_id": pages[3].id,
                "question_text": "How important is career advancement and leadership opportunities to you?",
                "question_type": QuestionType.slider,
                "order_index": 1,
                "is_required": True,
                "slider_min_label": "Not Important",
                "slider_max_label": "Very Important"
            },
            {
                "page_id": pages[3].id,
                "question_text": "Are you open to changing industries or exploring new career paths?",
                "question_type": QuestionType.slider,
                "order_index": 2,
                "is_required": False,
                "slider_min_label": "Not Open",
                "slider_max_label": "Very Open"
            },
            
            # Values & Motivation Page
            {
                "page_id": pages[4].id,
                "question_text": "What motivates you most in your work? (e.g., impact, creativity, financial rewards, recognition)",
                "question_type": QuestionType.essay,
                "order_index": 0,
                "is_required": True,
                "essay_char_limit": 350
            },
            {
                "page_id": pages[4].id,
                "question_text": "How important is having a positive impact on society through your work?",
                "question_type": QuestionType.slider,
                "order_index": 1,
                "is_required": True,
                "slider_min_label": "Not Important",
                "slider_max_label": "Very Important"
            },
            {
                "page_id": pages[4].id,
                "question_text": "Describe what an ideal work culture looks like to you.",
                "question_type": QuestionType.essay,
                "order_index": 2,
                "is_required": False,
                "essay_char_limit": 300
            }
        ]
        
        questions = []
        for question_data in questions_data:
            question = Question(**question_data)
            db.add(question)
            questions.append(question)
        
        db.commit()
        print(f"✅ Created {len(pages)} pages and {len(questions)} questions")
        
        return pages, questions
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating pages and questions: {e}")
        return [], []
    finally:
        db.close()

def create_sample_student_responses(questions, num_responses=25):
    """Create realistic student responses with fake data"""
    print(f"👥 Creating {num_responses} sample student responses...")
    
    db = SessionLocal()
    try:
        # Refresh questions from database to avoid session issues
        questions = db.query(Question).order_by(Question.id).all()
        # Sample career-related data for realistic responses
        education_levels = [
            "High School Diploma", "Associate Degree", "Bachelor's Degree", 
            "Master's Degree", "PhD", "Professional Certificate", "Bootcamp Graduate"
        ]
        
        experience_levels = [
            "0-1 years", "1-3 years", "3-5 years", "5-10 years", "10+ years"
        ]
        
        job_titles = [
            "Software Developer", "Data Analyst", "Marketing Specialist", "Project Manager",
            "UX Designer", "Sales Representative", "Business Analyst", "Product Manager",
            "Customer Success Manager", "Operations Coordinator", "HR Specialist",
            "Financial Analyst", "Content Writer", "Digital Marketer", "DevOps Engineer"
        ]
        
        # Career-focused essay response templates
        essay_templates = {
            0: [  # Educational background
                "I hold a {education} in {field} from {university}. During my studies, I focused on {specialization} and completed several projects in {area}. I also earned certifications in {certification} to enhance my practical skills.",
                "My educational journey includes a {education} with a concentration in {field}. I supplemented my formal education with online courses in {skill} and participated in {activity} to gain hands-on experience.",
                "I have a {education} and have continued my learning through professional development courses. My academic background gave me a strong foundation in {subject}, which I've applied in various {context} projects."
            ],
            2: [  # Current job role
                "I currently work as a {title} at {company}, where I'm responsible for {responsibility}. My daily tasks include {tasks} and I regularly collaborate with {teams} to achieve our goals.",
                "In my role as {title}, I focus on {area} and have successfully {achievement}. I work closely with {stakeholders} and use tools like {tools} to deliver results.",
                "As a {title}, I manage {scope} and have been instrumental in {impact}. My role involves {activities} and requires strong skills in {skills}."
            ],
            4: [  # Team vs independent work
                "I thrive in collaborative environments where I can {collaboration_style}. While I enjoy working independently on {tasks}, I find that team collaboration leads to {benefits} and better outcomes.",
                "I prefer a balanced approach - I'm highly productive when working independently on {work_type}, but I also value team collaboration for {scenarios}. The ideal setup allows me to {preference}.",
                "Team work energizes me, especially when {team_context}. I contribute best by {contribution} while learning from my colleagues' expertise in {areas}."
            ],
            6: [  # Technical skills
                "My core technical skills include {skill1}, {skill2}, and {skill3}. I'm proficient in {tools} and have experience with {technologies}. I'm particularly strong in {strength} and continuously improving in {learning_area}.",
                "I specialize in {domain} with expertise in {specific_skills}. My technical toolkit includes {technologies} and I have {experience_level} experience in {field}. I'm currently expanding my knowledge in {new_area}.",
                "My skill set spans {area1} and {area2}, with deep knowledge in {expertise}. I've worked extensively with {platforms} and have successfully {achievement} using these technologies."
            ],
            9: [  # Career goals
                "In the next 3-5 years, I aim to {goal} and transition into a {role} position. I want to {objective} and contribute to {area}. My long-term vision includes {vision} and making an impact in {field}.",
                "I see myself growing into a {position} role where I can {responsibility}. My goal is to {achievement} and potentially {aspiration}. I'm particularly interested in {interest} and want to {contribution}.",
                "My career trajectory points toward {direction} with a focus on {focus_area}. I plan to {plan} and eventually {long_term_goal}. This path aligns with my passion for {passion}."
            ],
            12: [  # What motivates you
                "I'm most motivated by {motivation1} and the opportunity to {opportunity}. {driving_factor} gives me energy, and I find fulfillment in {fulfillment}. Recognition for {achievement_type} also drives me to excel.",
                "My primary motivation comes from {source} and seeing {impact}. I'm energized by {energy_source} and find purpose in {purpose}. Financial stability is {importance}, but {priority} matters more to me.",
                "What drives me is {driver} and the chance to {chance}. I'm passionate about {passion} and motivated by {motivator}. The combination of {factor1} and {factor2} keeps me engaged and productive."
            ]
        }
        
        responses = []
        
        for i in range(num_responses):
            # Create student response
            student = StudentResponse(
                session_id=f"demo-session-{i+1}",
                full_name=fake.name(),
                email=fake.email(),
                age_group=random.choice(["18-25", "26-35", "36-45", "46-55", "55+"]),
                country=fake.country(),
                origin_country=fake.country(),
                created_at=fake.date_time_between(start_date="-30d", end_date="now")
            )
            db.add(student)
            responses.append(student)
        
        db.commit()
        
        # Create answers for each student
        for student in responses:
            essay_question_indices = [0, 2, 4, 6, 8, 9, 12, 14]  # Essay question positions
            slider_question_indices = [1, 3, 5, 7, 10, 11, 13]   # Slider question positions
            
            for i, question in enumerate(questions):
                # Skip some optional questions randomly
                if not question.is_required and random.random() < 0.3:
                    continue
                
                answer = QuestionAnswer(
                    response_id=student.id,
                    question_id=question.id
                )
                
                if question.question_type == QuestionType.essay:
                    # Generate realistic essay responses
                    if i in essay_templates:
                        template = random.choice(essay_templates[i])
                        
                        # Fill in template variables with realistic data
                        replacements = {
                            'education': random.choice(education_levels),
                            'field': random.choice(['Computer Science', 'Business', 'Engineering', 'Marketing', 'Psychology', 'Communications']),
                            'university': fake.company() + ' University',
                            'specialization': random.choice(['data analysis', 'software development', 'project management', 'digital marketing']),
                            'area': random.choice(['web development', 'data science', 'mobile apps', 'user research']),
                            'certification': random.choice(['AWS', 'Google Analytics', 'PMP', 'Salesforce', 'Adobe Creative Suite']),
                            'skill': random.choice(['Python', 'JavaScript', 'SQL', 'Excel', 'Tableau']),
                            'activity': random.choice(['internships', 'hackathons', 'volunteer projects', 'research']),
                            'subject': random.choice(['analytics', 'programming', 'design', 'communication']),
                            'context': random.choice(['academic', 'professional', 'personal']),
                            'title': random.choice(job_titles),
                            'company': fake.company(),
                            'responsibility': random.choice(['managing client relationships', 'developing software solutions', 'analyzing market trends']),
                            'tasks': random.choice(['coding and testing', 'data analysis', 'client meetings', 'project planning']),
                            'teams': random.choice(['engineering', 'marketing', 'sales', 'design']),
                            'collaboration_style': random.choice(['share ideas and learn from others', 'contribute my expertise', 'solve complex problems together']),
                            'motivation1': random.choice(['solving challenging problems', 'helping others succeed', 'creating innovative solutions']),
                            'goal': random.choice(['advance to a senior position', 'start my own company', 'specialize in my field']),
                            'role': random.choice(['leadership', 'senior', 'management', 'specialist'])
                        }
                        
                        answer_text = template
                        for key, value in replacements.items():
                            answer_text = answer_text.replace(f'{{{key}}}', str(value))
                        
                        answer.answer_text = answer_text[:question.essay_char_limit] if question.essay_char_limit else answer_text
                    else:
                        # Fallback to generic responses
                        answer.answer_text = fake.text(max_nb_chars=question.essay_char_limit or 300)
                
                elif question.question_type == QuestionType.slider:
                    # Generate realistic slider values (1-100)
                    if i == 1:  # Years of experience
                        answer.answer_value = random.randint(0, 100)  # 0-20+ years mapped to 0-100
                    elif i in [3, 5, 7, 10, 11, 13]:  # Preference/importance questions
                        # Most people rate things in the middle-high range
                        answer.answer_value = random.randint(40, 95)
                    else:
                        answer.answer_value = random.randint(30, 90)
                
                db.add(answer)
        
        db.commit()
        print(f"✅ Created {len(responses)} student responses with realistic answers")
        
        return responses
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating student responses: {e}")
        return []
    finally:
        db.close()

def create_additional_admin_users():
    """Create some additional admin users for testing"""
    print("👤 Creating additional admin users...")
    
    db = SessionLocal()
    try:
        additional_admins = [
            {"username": "demo_admin", "password": "demo123"},
            {"username": "test_user", "password": "test123"},
        ]
        
        created_count = 0
        for admin_data in additional_admins:
            existing = db.query(Admin).filter(Admin.username == admin_data["username"]).first()
            if not existing:
                admin = Admin(
                    username=admin_data["username"],
                    password_hash=get_password_hash(admin_data["password"])
                )
                db.add(admin)
                created_count += 1
        
        db.commit()
        
        if created_count > 0:
            print(f"✅ Created {created_count} additional admin users")
            print("📝 Additional admin credentials:")
            for admin_data in additional_admins:
                print(f"   - Username: {admin_data['username']}, Password: {admin_data['password']}")
        else:
            print("ℹ️  Additional admin users already exist")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin users: {e}")
    finally:
        db.close()

def main(auto_mode=False, clear_data=True, num_responses=25):
    """Main function to populate the database with fake data"""
    print("🧬 Career DNA Assessment - Database Population Script")
    print("=" * 60)
    
    # Ensure tables exist
    print("🏗️  Ensuring database tables exist...")
    create_tables()
    
    # Ask user if they want to clear existing data (unless in auto mode)
    if auto_mode:
        if clear_data:
            clear_database()
    else:
        response = input("\n🤔 Do you want to clear existing data first? (y/N): ").lower().strip()
        if response in ['y', 'yes']:
            clear_database()
    
    # Create sample data
    pages, questions = create_sample_pages_and_questions()
    
    if questions:
        if not auto_mode:
            user_input = input(f"\n📊 How many student responses to create? (default: 25): ").strip()
            try:
                num_responses = int(user_input) if user_input else 25
            except ValueError:
                num_responses = 25
        
        responses = create_sample_student_responses(questions, num_responses)
        
        # Create additional admin users
        create_additional_admin_users()
        
        print("\n" + "=" * 60)
        print("🎉 Database population completed successfully!")
        print(f"📈 Summary:")
        print(f"   - {len(pages)} assessment pages")
        print(f"   - {len(questions)} questions")
        print(f"   - {len(responses)} student responses")
        print(f"\n🌐 You can now access:")
        print(f"   - Student interface: http://localhost:8000")
        print(f"   - Admin panel: http://localhost:8000/admin")
        print(f"   - Default admin: admin / admin123")
        
    else:
        print("❌ Failed to create questions, skipping student responses")

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    auto_mode = "--auto" in sys.argv or "-a" in sys.argv
    clear_data = "--clear" in sys.argv or "-c" in sys.argv or auto_mode
    
    # Get number of responses from command line
    num_responses = 25
    for arg in sys.argv:
        if arg.startswith("--responses="):
            try:
                num_responses = int(arg.split("=")[1])
            except ValueError:
                print(f"Invalid number of responses: {arg}")
                num_responses = 25
    
    if auto_mode:
        print("🤖 Running in automatic mode...")
        main(auto_mode=True, clear_data=clear_data, num_responses=num_responses)
    else:
        main()