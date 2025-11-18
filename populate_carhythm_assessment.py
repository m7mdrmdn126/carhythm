"""
CaRhythm Assessment Database Population Script
This script populates the database with all questions from the CaRhythm Q Inventory.
Includes: RIASEC, Big Five Personality, and Work Rhythm Traits assessments.
"""

import os
import sys
import json

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.database import SessionLocal, create_tables
from app.models import Page, Question, QuestionType, QuestionAnswer, StudentResponse

def clear_database():
    """Delete all existing pages and questions"""
    print("🗑️  Clearing all existing questions and pages...")
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
        raise
    finally:
        db.close()

def create_riasec_pages():
    """Create RIASEC Career Interest Assessment pages and questions"""
    print("📊 Creating RIASEC Assessment...")
    db = SessionLocal()
    
    try:
        # Page 1: RIASEC Quick Assessment
        page1 = Page(
            title="RIASEC Quick Assessment",
            description="Measure your interest alignment across six Holland career domains using Likert ratings, forced-choice comparisons, and ranking sets. Completion time: ≈5 minutes.",
            order_index=1,
            is_active=True
        )
        db.add(page1)
        db.flush()
        
        # Likert Set 1 (6 questions)
        likert_1_questions = [
            ("Use power tools to build or repair something.", "R"),
            ("Solve logic or math puzzles in your free time.", "I"),
            ("Draw or paint to express ideas.", "A"),
            ("Help friends understand a new concept or skill.", "S"),
            ("Start a group project and take the lead.", "E"),
            ("Keep records and organize information neatly.", "C"),
        ]
        
        order_idx = 0
        for q_text, domain in likert_1_questions:
            question = Question(
                page_id=page1.id,
                question_text=f"[{domain}] {q_text}",
                question_type=QuestionType.slider,
                order_index=order_idx,
                is_required=True,
                slider_min_label="Not like me",
                slider_max_label="Totally like me"
            )
            db.add(question)
            order_idx += 1
        
        # Likert Set 2 (6 questions)
        likert_2_questions = [
            ("Fix a gadget to see why it was not working.", "R"),
            ("Do a small science experiment just to see what happens.", "I"),
            ("Write a short story or blog post.", "A"),
            ("Volunteer to help at an event.", "S"),
            ("Sell or promote something you believe in.", "E"),
            ("Follow a recipe or written instructions carefully.", "C"),
        ]
        
        for q_text, domain in likert_2_questions:
            question = Question(
                page_id=page1.id,
                question_text=f"[{domain}] {q_text}",
                question_type=QuestionType.slider,
                order_index=order_idx,
                is_required=True,
                slider_min_label="Not like me",
                slider_max_label="Totally like me"
            )
            db.add(question)
            order_idx += 1
        
        # Likert Set 3 (6 questions)
        likert_3_questions = [
            ("Work on an engine or mechanical tool.", "R"),
            ("Research facts and analyze results to understand why.", "I"),
            ("Design a living space or poster to look inviting.", "A"),
            ("Organize and host a get-together for others.", "S"),
            ("Give a short speech or presentation to a group.", "E"),
            ("Plan a trip and prepare the schedule.", "C"),
        ]
        
        for q_text, domain in likert_3_questions:
            question = Question(
                page_id=page1.id,
                question_text=f"[{domain}] {q_text}",
                question_type=QuestionType.slider,
                order_index=order_idx,
                is_required=True,
                slider_min_label="Not like me",
                slider_max_label="Totally like me"
            )
            db.add(question)
            order_idx += 1
        
        # Forced Choice Items (6 pairs)
        forced_choices = [
            ("Repair or assemble equipment. (R)", "Create art or take photographs. (A)"),
            ("Analyze a problem using data. (I)", "Explain steps to help someone learn. (S)"),
            ("Lead a team to finish a project. (E)", "Keep records and budgets organized. (C)"),
            ("Work out how a machine functions. (R)", "Design a logo or flyer. (A)"),
            ("Investigate why something went wrong. (I)", "Convince others to support your idea. (E)"),
            ("Support and coach teammates. (S)", "Record figures and sort information. (C)"),
        ]
        
        for option_a, option_b in forced_choices:
            question = Question(
                page_id=page1.id,
                question_text="Which activity is more like you?",
                question_type=QuestionType.mcq,
                order_index=order_idx,
                is_required=True,
                mcq_options=json.dumps([option_a, option_b]),
                allow_multiple_selection=False
            )
            db.add(question)
            order_idx += 1
        
        # Ranking Set 1 - Daily Life Activities
        ranking_1_items = [
            "Repair a broken object at home. (R)",
            "Do a science experiment or research online. (I)",
            "Draw something creative just for fun. (A)",
            "Teach a friend how to do something new. (S)",
            "Organize and lead a group project. (E)",
            "Sort and arrange files neatly. (C)"
        ]
        
        question = Question(
            page_id=page1.id,
            question_text="Rank these daily activities from 1 (Most Enjoyed) to 6 (Least Enjoyed):",
            question_type=QuestionType.ordering,
            order_index=order_idx,
            is_required=True,
            ordering_options=json.dumps(ranking_1_items),
            randomize_order=True
        )
        db.add(question)
        order_idx += 1
        
        # Ranking Set 2 - Work or Study Tasks
        ranking_2_items = [
            "Operate tools or equipment. (R)",
            "Analyze data and draw conclusions. (I)",
            "Write a short story or presentation script. (A)",
            "Collaborate with a team to help others. (S)",
            "Plan a budget or fund-raising event. (E)",
            "Follow set rules and procedures carefully. (C)"
        ]
        
        question = Question(
            page_id=page1.id,
            question_text="Rank these work/study tasks from 1 (Most Enjoyed) to 6 (Least Enjoyed):",
            question_type=QuestionType.ordering,
            order_index=order_idx,
            is_required=True,
            ordering_options=json.dumps(ranking_2_items),
            randomize_order=True
        )
        db.add(question)
        order_idx += 1
        
        # Ranking Set 3 - Weekend Preferences
        ranking_3_items = [
            "Build or fix something. (R)",
            "Solve puzzles or read science articles. (I)",
            "Play music or attend an art show. (A)",
            "Volunteer in the community. (S)",
            "Run an event or promote an idea online. (E)",
            "Plan household tasks or finances. (C)"
        ]
        
        question = Question(
            page_id=page1.id,
            question_text="Rank these weekend activities from 1 (Most Enjoyed) to 6 (Least Enjoyed):",
            question_type=QuestionType.ordering,
            order_index=order_idx,
            is_required=True,
            ordering_options=json.dumps(ranking_3_items),
            randomize_order=True
        )
        db.add(question)
        
        # Page 2: RIASEC - Realistic (R)
        page2 = Page(
            title="RIASEC - Realistic (R)",
            description="Working with Objects & Hands-On Tasks. Rate how much you enjoy each activity.",
            order_index=2,
            is_active=True
        )
        db.add(page2)
        db.flush()
        
        realistic_questions = [
            "Use power tools to build or repair something.",
            "Care for animals or pets.",
            "Tinker with gadgets to see how they work.",
            "Play sports or do physical activities.",
            "Set up electronic equipment or home devices.",
            "Cook or grill meals for family and friends.",
            "Fix electrical or mechanical things.",
            "Build or assemble objects or DIY projects.",
            "Work on vehicles or engines.",
            "Paint or decorate a room."
        ]
        
        for idx, q_text in enumerate(realistic_questions):
            question = Question(
                page_id=page2.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="Not me",
                slider_max_label="Totally me"
            )
            db.add(question)
        
        # Page 3: RIASEC - Investigative (I)
        page3 = Page(
            title="RIASEC - Investigative (I)",
            description="Thinking, Research, Problem Solving. Rate how much you enjoy each activity.",
            order_index=3,
            is_active=True
        )
        db.add(page3)
        db.flush()
        
        investigative_questions = [
            "Solve logic or math puzzles.",
            "Repair computer or tech glitches.",
            "Analyze evidence like in a crime scene.",
            "Read science articles or fiction.",
            "Join science fairs or competitions.",
            "Build models (rockets, robots, etc.).",
            "Work in a lab to test ideas.",
            "Study the weather and patterns in nature.",
            "Do complex puzzles or mind games.",
            "Study other cultures and human behavior.",
            "Dissect or examine biological samples."
        ]
        
        for idx, q_text in enumerate(investigative_questions):
            question = Question(
                page_id=page3.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="Not me",
                slider_max_label="Totally me"
            )
            db.add(question)
        
        # Page 4: RIASEC - Artistic (A)
        page4 = Page(
            title="RIASEC - Artistic (A)",
            description="Creative Expression & Design. Rate how much you enjoy each activity.",
            order_index=4,
            is_active=True
        )
        db.add(page4)
        db.flush()
        
        artistic_questions = [
            "Draw or paint pictures.",
            "Learn and use different languages or scripts.",
            "Take photographs and edit images.",
            "Write stories, blog posts, or poems.",
            "Arrange flowers or decor for events.",
            "Design clothes or fashion accessories.",
            "Play a musical instrument or compose music.",
            "Act in a theater play or film.",
            "Lead a book or art discussion group.",
            "Rearrange or decorate a room creatively."
        ]
        
        for idx, q_text in enumerate(artistic_questions):
            question = Question(
                page_id=page4.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="Not me",
                slider_max_label="Totally me"
            )
            db.add(question)
        
        # Page 5: RIASEC - Social (S)
        page5 = Page(
            title="RIASEC - Social (S)",
            description="Helping / Teaching / Supporting People. Rate how much you enjoy each activity.",
            order_index=5,
            is_active=True
        )
        db.add(page5)
        db.flush()
        
        social_questions = [
            "Organize and host a get-together or event.",
            "Help people solve their problems.",
            "Provide first aid or care when someone is hurt.",
            "Take part in clubs or community projects.",
            "Volunteer time to help others.",
            "Meet new people and make friends.",
            "Cheer or support a team at an event.",
            "Talk openly about feelings and emotions.",
            "Teach someone a skill or topic.",
            "Guide people on a tour or visit new places.",
            "Translate languages to help others communicate."
        ]
        
        for idx, q_text in enumerate(social_questions):
            question = Question(
                page_id=page5.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="Not me",
                slider_max_label="Totally me"
            )
            db.add(question)
        
        # Page 6: RIASEC - Enterprising (E)
        page6 = Page(
            title="RIASEC - Enterprising (E)",
            description="Leading, Persuading, Promoting Ideas. Rate how much you enjoy each activity.",
            order_index=6,
            is_active=True
        )
        db.add(page6)
        db.flush()
        
        enterprising_questions = [
            "Start a club or group for a cause.",
            "Sell or promote products you like.",
            "Collaborate with leaders or influencers.",
            "Run for a student office or leadership role.",
            "Manage budget or money for projects.",
            "Debate or argue a case (like a lawyer).",
            "Negotiate and close a deal or agreement.",
            "Make presentations or give speeches to groups.",
            "Plan and run campaigns or projects.",
            "Manage or supervise a team or event."
        ]
        
        for idx, q_text in enumerate(enterprising_questions):
            question = Question(
                page_id=page6.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="Not me",
                slider_max_label="Totally me"
            )
            db.add(question)
        
        # Page 7: RIASEC - Conventional (C)
        page7 = Page(
            title="RIASEC - Conventional (C)",
            description="Organizing, Details, Procedures. Rate how much you enjoy each activity.",
            order_index=7,
            is_active=True
        )
        db.add(page7)
        db.flush()
        
        conventional_questions = [
            "Follow a recipe to make something.",
            "Plan a trip and book everything on time.",
            "Follow written instructions carefully.",
            "Keep your workspace or room organized and tidy.",
            "Create and manage a personal budget.",
            "Stick to the same daily schedule.",
            "Use office software and business machines.",
            "Sort or group items by type or order.",
            "Track expenses and balance budgets.",
            "Maintain detailed records or reports.",
            "Type and format text accurately on a computer."
        ]
        
        for idx, q_text in enumerate(conventional_questions):
            question = Question(
                page_id=page7.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="Not me",
                slider_max_label="Totally me"
            )
            db.add(question)
        
        db.commit()
        print("✅ Created 7 RIASEC pages with 79 questions")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating RIASEC pages: {e}")
        raise
    finally:
        db.close()

def create_bigfive_pages():
    """Create Big Five Personality Assessment pages and questions"""
    print("🧠 Creating Big Five Personality Assessment...")
    db = SessionLocal()
    
    try:
        # Page 8: Big Five - Openness
        page8 = Page(
            title="Big Five - Openness to Experience",
            description="Curiosity – Imagination – Creativity. Rate how accurately each statement describes you.",
            order_index=8,
            is_active=True
        )
        db.add(page8)
        db.flush()
        
        openness_questions = [
            "I have a vivid imagination and see possibilities others miss.",
            "I enjoy hearing and sharing new ideas.",
            "I believe art and creative expressions add meaning to life.",
            "I like learning about how things work and why they happen.",
            "I find beauty and patterns in everyday things.",
            "I can picture what the future might look like and plan for it.",
            "I often come up with unusual or original solutions to problems.",
            "Creative projects help me relax and feel motivated."
        ]
        
        for idx, q_text in enumerate(openness_questions):
            question = Question(
                page_id=page8.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="Not like me",
                slider_max_label="A lot like me"
            )
            db.add(question)
        
        # Page 9: Big Five - Conscientiousness
        page9 = Page(
            title="Big Five - Conscientiousness",
            description="Organization – Discipline – Dependability. Rate how accurately each statement describes you.",
            order_index=9,
            is_active=True
        )
        db.add(page9)
        db.flush()
        
        conscientiousness_questions = [
            "I like to plan ahead and stick to my plans.",
            "I get tasks done promptly and thoroughly.",
            "I take care of details and double-check my work.",
            "People can count on me to keep my promises.",
            "I feel satisfied when everything is in order.",
            "I prepare for challenges before they arrive.",
            "I use my time wisely to finish what matters most.",
            "I like having structure and clear routines in my day."
        ]
        
        for idx, q_text in enumerate(conscientiousness_questions):
            question = Question(
                page_id=page9.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="Not like me",
                slider_max_label="A lot like me"
            )
            db.add(question)
        
        # Page 10: Big Five - Extraversion
        page10 = Page(
            title="Big Five - Extraversion",
            description="Energy – Sociability – Enthusiasm. Rate how accurately each statement describes you.",
            order_index=10,
            is_active=True
        )
        db.add(page10)
        db.flush()
        
        extraversion_questions = [
            "I feel comfortable starting conversations with new people.",
            "I am talkative and enjoy sharing ideas out loud.",
            "I get energy from being around others.",
            "I like to make people laugh and lighten the mood.",
            "I can lead or host a group activity with confidence.",
            "I make friends easily and stay in touch.",
            "I like being at the center of fun or discussion.",
            "I bring positive energy to social situations."
        ]
        
        for idx, q_text in enumerate(extraversion_questions):
            question = Question(
                page_id=page10.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="Not like me",
                slider_max_label="A lot like me"
            )
            db.add(question)
        
        # Page 11: Big Five - Agreeableness
        page11 = Page(
            title="Big Five - Agreeableness",
            description="Kindness – Empathy – Cooperation. Rate how accurately each statement describes you.",
            order_index=11,
            is_active=True
        )
        db.add(page11)
        db.flush()
        
        agreeableness_questions = [
            "I see the good in people and accept them as they are.",
            "I go out of my way to make someone's day a bit brighter.",
            "I treat others with kindness and respect even when it's hard.",
            "I stop what I'm doing to help someone who needs it.",
            "I forgive people easily after conflict.",
            "I prefer cooperation to competition.",
            "I listen with interest when others share their feelings.",
            "I believe everyone deserves understanding and support."
        ]
        
        for idx, q_text in enumerate(agreeableness_questions):
            question = Question(
                page_id=page11.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="Not like me",
                slider_max_label="A lot like me"
            )
            db.add(question)
        
        # Page 12: Big Five - Neuroticism
        page12 = Page(
            title="Big Five - Neuroticism",
            description="Emotional Stability vs Sensitivity. Rate how accurately each statement describes you.",
            order_index=12,
            is_active=True
        )
        db.add(page12)
        db.flush()
        
        neuroticism_questions = [
            "I often worry about what might go wrong.",
            "My moods can change quickly.",
            "I get stressed easily when plans don't work out.",
            "I sometimes doubt my own abilities.",
            "I find it hard to relax after a busy day.",
            "Small problems can bother me more than they should.",
            "I feel down or discouraged more often than I'd like.",
            "I use humor or creative outlets to recover from stress. (reverse-moderator)"
        ]
        
        for idx, q_text in enumerate(neuroticism_questions):
            question = Question(
                page_id=page12.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="Not like me",
                slider_max_label="A lot like me"
            )
            db.add(question)
        
        db.commit()
        print("✅ Created 5 Big Five pages with 40 questions")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating Big Five pages: {e}")
        raise
    finally:
        db.close()

def create_work_rhythm_pages():
    """Create Work Rhythm Traits Module pages and questions"""
    print("⚡ Creating Work Rhythm Traits Assessment...")
    db = SessionLocal()
    
    try:
        # Page 13: Work Rhythm - Motivation Type
        page13 = Page(
            title="Work Rhythm - Motivation Type",
            description="Intrinsic vs Extrinsic Motivation. When you think about your daily work or study, how true are these statements?",
            order_index=13,
            is_active=True
        )
        db.add(page13)
        db.flush()
        
        motivation_questions = [
            "Tasks that feel worthwhile keep my interest even if no one else notices.",
            "I stay engaged because I enjoy the work itself.",
            "I find it hard to get motivated unless there's a reward or recognition. (reverse)"
        ]
        
        for idx, q_text in enumerate(motivation_questions):
            question = Question(
                page_id=page13.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="😐 Not like me",
                slider_max_label="😄 A lot like me"
            )
            db.add(question)
        
        # Page 14: Work Rhythm - Grit/Persistence
        page14 = Page(
            title="Work Rhythm - Grit / Persistence",
            description="Think about how you handle long or difficult projects.",
            order_index=14,
            is_active=True
        )
        db.add(page14)
        db.flush()
        
        grit_questions = [
            "I finish what I start, even if it takes a long time.",
            "I keep working on a skill until I get it right.",
            "It's easy for me to lose interest when progress is slow. (reverse)"
        ]
        
        for idx, q_text in enumerate(grit_questions):
            question = Question(
                page_id=page14.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="😐 Not like me",
                slider_max_label="😄 A lot like me"
            )
            db.add(question)
        
        # Page 15: Work Rhythm - Self-Efficacy
        page15 = Page(
            title="Work Rhythm - Self-Efficacy",
            description="Confidence in Ability. Consider how you respond to new or challenging situations.",
            order_index=15,
            is_active=True
        )
        db.add(page15)
        db.flush()
        
        self_efficacy_questions = [
            "I usually find a way to solve tough problems.",
            "I feel capable of succeeding in most tasks I try.",
            "I sometimes doubt my ability to handle unexpected situations. (reverse)"
        ]
        
        for idx, q_text in enumerate(self_efficacy_questions):
            question = Question(
                page_id=page15.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="😐 Not like me",
                slider_max_label="😄 A lot like me"
            )
            db.add(question)
        
        # Page 16: Work Rhythm - Resilience
        page16 = Page(
            title="Work Rhythm - Resilience / Stress Tolerance",
            description="When plans go off track or pressure rises...",
            order_index=16,
            is_active=True
        )
        db.add(page16)
        db.flush()
        
        resilience_questions = [
            "I stay calm under pressure.",
            "After setbacks, I bounce back quickly.",
            "Small problems can throw off my mood for the whole day. (reverse)"
        ]
        
        for idx, q_text in enumerate(resilience_questions):
            question = Question(
                page_id=page16.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="😐 Not like me",
                slider_max_label="😄 A lot like me"
            )
            db.add(question)
        
        # Page 17: Work Rhythm - Learning Orientation
        page17 = Page(
            title="Work Rhythm - Learning Orientation / Growth Mindset",
            description="When you face something you haven't yet mastered...",
            order_index=17,
            is_active=True
        )
        db.add(page17)
        db.flush()
        
        learning_questions = [
            "I believe skills can improve with practice.",
            "I see challenges as chances to learn and grow.",
            "If I'm not good at something, I prefer to avoid it. (reverse)"
        ]
        
        for idx, q_text in enumerate(learning_questions):
            question = Question(
                page_id=page17.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="😐 Not like me",
                slider_max_label="😄 A lot like me"
            )
            db.add(question)
        
        # Page 18: Work Rhythm - Empathy
        page18 = Page(
            title="Work Rhythm - Empathy / Emotional Intelligence",
            description="When you're around others...",
            order_index=18,
            is_active=True
        )
        db.add(page18)
        db.flush()
        
        empathy_questions = [
            "I quickly notice when someone seems upset or stressed.",
            "I try to understand things from the other person's point of view.",
            "People often come to me for comfort or advice."
        ]
        
        for idx, q_text in enumerate(empathy_questions):
            question = Question(
                page_id=page18.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="😐 Not like me",
                slider_max_label="😄 A lot like me"
            )
            db.add(question)
        
        # Page 19: Work Rhythm - Procrastination
        page19 = Page(
            title="Work Rhythm - Procrastination / Task Start Tempo",
            description="How often do you notice these situations around starting tasks?",
            order_index=19,
            is_active=True
        )
        db.add(page19)
        db.flush()
        
        procrastination_questions = [
            "Deadlines tend to sneak up on me because I don't begin right away. (reverse)",
            "I gain energy and focus once I take the first small step on something.",
            "I often plan tasks in my head for a while before starting them. (reverse)"
        ]
        
        for idx, q_text in enumerate(procrastination_questions):
            question = Question(
                page_id=page19.id,
                question_text=q_text,
                question_type=QuestionType.slider,
                order_index=idx,
                is_required=True,
                slider_min_label="😐 Not like me",
                slider_max_label="😄 A lot like me"
            )
            db.add(question)
        
        db.commit()
        print("✅ Created 7 Work Rhythm pages with 21 questions")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating Work Rhythm pages: {e}")
        raise
    finally:
        db.close()

def main():
    """Main execution function"""
    print("=" * 60)
    print("🎯 CaRhythm Assessment Database Population")
    print("=" * 60)
    
    try:
        # Ensure tables exist
        create_tables()
        print("✅ Database tables ready\n")
        
        # Clear existing data
        clear_database()
        print()
        
        # Create all assessment modules
        create_riasec_pages()
        print()
        
        create_bigfive_pages()
        print()
        
        create_work_rhythm_pages()
        print()
        
        # Summary
        db = SessionLocal()
        page_count = db.query(Page).count()
        question_count = db.query(Question).count()
        db.close()
        
        print("=" * 60)
        print("🎉 SUCCESS! Database populated with:")
        print(f"   📄 {page_count} Pages")
        print(f"   ❓ {question_count} Questions")
        print()
        print("Assessment Modules:")
        print("   ✓ RIASEC Career Interests (7 pages, 79 questions)")
        print("   ✓ Big Five Personality (5 pages, 40 questions)")
        print("   ✓ Work Rhythm Traits (7 pages, 21 questions)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
