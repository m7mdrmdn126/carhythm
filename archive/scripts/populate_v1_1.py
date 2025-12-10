"""
CaRhythm v1.1 Database Population Script
Complete implementation of the new assessment structure with:
- 5-point Likert scale (1-5)
- Behavioral tags on every item
- Strength label scoring
- Ikigai zones
- 3 consolidated pages: RIASEC, Big Five, Behavioral
"""

import os
import sys
import json

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.database import SessionLocal, create_tables
from app.models import Page, Question, QuestionType, QuestionAnswer, StudentResponse

def clear_database():
    """Delete all existing pages and questions - FRESH START"""
    print("🗑️  Clearing all existing questions and pages...")
    db = SessionLocal()
    try:
        # Delete in correct order to avoid foreign key constraints
        db.query(QuestionAnswer).delete()
        db.query(StudentResponse).delete()
        db.query(Question).delete()
        db.query(Page).delete()
        db.commit()
        print("✅ Database cleared successfully - Ready for v1.1!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error clearing database: {e}")
        raise
    finally:
        db.close()


def create_riasec_page():
    """Page 1: ALL RIASEC Questions (18 Likert + 6 Forced Choice + 3 Ranking = 27 items)"""
    print("📊 Creating RIASEC Page (ALL questions)...")
    db = SessionLocal()
    
    try:
        page = Page(
            title="What Energizes You?",
            description="Rate statements, choose preferences, and rank activities",
            order_index=1,
            module_name="RIASEC",
            is_active=True,
            completion_message="Great! RIASEC complete! 🎉"
        )
        db.add(page)
        db.flush()
        
        question_counter = 0
        
        # Likert scale labels (5-point)
        scale_labels = json.dumps(["Not at all", "A little", "Kinda", "Mostly", "Totally!"])
        
        # All 18 Likert questions (3 sets × 6 domains)
        likert_questions = [
            # Set 1
            ("R1", "R", "When my phone stops working properly, I try troubleshooting it before seeking help", ["problem_solving", "self_reliance"]),
            ("I1", "I", "I enjoy spending time on apps that challenge my problem-solving skills", ["curiosity", "analytical_thinking"]),
            ("A1", "A", "I often customize my digital spaces to reflect my personal style", ["self_expression", "creativity"]),
            ("S1", "S", "I naturally explain tech concepts to friends who are less familiar with them", ["teaching", "helping"]),
            ("E1", "E", "In group projects, I tend to coordinate deadlines and delegate tasks", ["leadership", "organization"]),
            ("C1", "C", "I maintain organized systems for tracking my appointments and commitments", ["planning", "detail_orientation"]),
            
            # Set 2
            ("R2", "R", "I prefer learning new software by exploring its features hands-on rather than reading instructions", ["experiential_learning", "hands_on"]),
            ("I2", "I", "When I hear about new scientific discoveries, I look up more information to understand them better", ["research_driven", "knowledge_seeking"]),
            ("A2", "A", "I enjoy creating digital content like social media posts or videos that express my perspective", ["content_creation", "storytelling"]),
            ("S2", "S", "I often help neighbors or community members with tasks they find challenging", ["community_support", "altruism"]),
            ("E2", "E", "I'm comfortable presenting my ideas in virtual meetings or online forums", ["public_speaking", "influence"]),
            ("C2", "C", "I feel satisfied when I complete all items on my daily task list in order", ["task_completion", "orderliness"]),
            
            # Set 3
            ("R3", "R", "I enjoy assembling furniture or electronics following visual guides", ["assembly", "visual_learning"]),
            ("I3", "I", "When planning trips, I research multiple options to find the most efficient routes", ["efficiency", "planning"]),
            ("A3", "A", "I rearrange my living or workspace periodically to create a fresh environment", ["environment_design", "aesthetic_sense"]),
            ("S3", "S", "I organize casual get-togethers that help people connect with each other", ["social_bonding", "community_building"]),
            ("E3", "E", "I naturally take charge of coordinating group decisions when no one else does", ["initiative", "decision_making"]),
            ("C3", "C", "I create detailed plans for complex tasks broken into manageable steps", ["structured_approach", "step_by_step"]),
        ]
        
        for item_id, domain, text, tags in likert_questions:
            question = Question(
                page_id=page.id,
                item_id=item_id,
                question_text=text,
                question_type=QuestionType.slider,
                order_index=question_counter,
                is_required=True,
                domain=domain,
                tags=json.dumps(tags),
                reverse_scored=False,
                scale_type="likert_5",
                scale_labels=scale_labels,
                slider_min_label="Not at all",
                slider_max_label="Totally!"
            )
            db.add(question)
            question_counter += 1
        
        # ========== FORCED CHOICE QUESTIONS ==========
        # 6 forced choice questions
        forced_choices = [
            ("FC_RI_1", "Choose one:", [
                {"label": "Fix a malfunctioning kitchen appliance using online tutorials", "value": "A", "domain": "R", "score_value": 3, "tags": ["task_initiation", "hands_on_learning"]},
                {"label": "Research how renewable energy technologies work for a school project", "value": "B", "domain": "I", "score_value": 3, "tags": ["curiosity_driven", "research_oriented"]}
            ]),
            ("FC_IA_1", "Choose one:", [
                {"label": "Analyze data patterns to improve your community's recycling program", "value": "A", "domain": "I", "score_value": 3, "tags": ["data_analysis", "systematic_thinking"]},
                {"label": "Design an original logo for a local community initiative", "value": "B", "domain": "A", "score_value": 3, "tags": ["visual_design", "creative_expression"]}
            ]),
            ("FC_AS_1", "Choose one:", [
                {"label": "Create a mural that represents your neighborhood's diversity", "value": "A", "domain": "A", "score_value": 3, "tags": ["public_art", "cultural_expression"]},
                {"label": "Tutor someone struggling with a subject you understand well", "value": "B", "domain": "S", "score_value": 3, "tags": ["mentoring", "knowledge_sharing"]}
            ]),
            ("FC_SE_1", "Choose one:", [
                {"label": "Organize a neighborhood watch program to enhance safety", "value": "A", "domain": "S", "score_value": 3, "tags": ["community_service", "safety_oriented"]},
                {"label": "Lead a fundraising campaign for a cause you care about", "value": "B", "domain": "E", "score_value": 3, "tags": ["persuasion", "campaign_management"]}
            ]),
            ("FC_EC_1", "Choose one:", [
                {"label": "Negotiate with local businesses to sponsor a community event", "value": "A", "domain": "E", "score_value": 3, "tags": ["negotiation", "resource_acquisition"]},
                {"label": "Create a streamlined system for managing event registrations", "value": "B", "domain": "C", "score_value": 3, "tags": ["process_optimization", "efficiency"]}
            ]),
            ("FC_CR_1", "Choose one:", [
                {"label": "Follow detailed instructions to set up a complex smart home system OR repair basic household items", "value": "A", "domain": "C", "score_value": 3, "tags": ["instruction_following", "precision"]},
                {"label": "Build raised garden beds for a community vegetable patch", "value": "B", "domain": "R", "score_value": 3, "tags": ["construction", "community_project"]}
            ]),
        ]
        
        for item_id, text, options in forced_choices:
            question = Question(
                page_id=page.id,
                item_id=item_id,
                question_text=text,
                question_type=QuestionType.mcq,
                order_index=question_counter,
                is_required=True,
                domain=None,  # Multiple domains in options
                tags=json.dumps([]),
                reverse_scored=False,
                scale_type="forced_choice",
                scale_labels=None,
                mcq_options=json.dumps(options),
                allow_multiple_selection=False
            )
            db.add(question)
            question_counter += 1
        
        # ========== RANKING QUESTIONS ==========
        # 3 ranking sets
        ranking_sets = [
            {
                "item_id": "RANK1",
                "text": "Drag these into order — what would you do FIRST if you had a free day? (1 = Most appealing, 6 = Least appealing)",
                "activities": [
                    {"text": "Repair a bicycle for a family member who needs transportation", "domain": "R", "tags": ["practical_help", "mechanical"]},
                    {"text": "Research the health benefits of different cooking methods", "domain": "I", "tags": ["health_research", "curiosity"]},
                    {"text": "Design personalized greeting cards for upcoming birthdays", "domain": "A", "tags": ["personalized_creativity", "craft"]},
                    {"text": "Help a recent transplant learn their way around the neighborhood", "domain": "S", "tags": ["orientation_help", "welcoming"]},
                    {"text": "Coordinate a potluck dinner where everyone contributes", "domain": "E", "tags": ["event_coordination", "social_leadership"]},
                    {"text": "Create a shared calendar system for household responsibilities", "domain": "C", "tags": ["shared_planning", "organization"]},
                ]
            },
            {
                "item_id": "RANK2",
                "text": "Drag these into order — what would you do FIRST in a work/study setting? (1 = Most appealing, 6 = Least appealing)",
                "activities": [
                    {"text": "Test and troubleshoot new software before team implementation", "domain": "R", "tags": ["quality_assurance", "technical"]},
                    {"text": "Compare different approaches to reduce energy consumption", "domain": "I", "tags": ["sustainability_analysis", "comparative"]},
                    {"text": "Develop engaging presentation visuals for an important meeting", "domain": "A", "tags": ["visual_communication", "design"]},
                    {"text": "Facilitate a discussion where diverse viewpoints are shared", "domain": "S", "tags": ["dialogue_facilitation", "inclusion"]},
                    {"text": "Persuade colleagues to adopt a more efficient workflow", "domain": "E", "tags": ["change_management", "influence"]},
                    {"text": "Document standard procedures for recurring team tasks", "domain": "C", "tags": ["documentation", "standardization"]},
                ]
            },
            {
                "item_id": "RANK3",
                "text": "Drag these into order — what would you do FIRST on a weekend? (1 = Most appealing, 6 = Least appealing)",
                "activities": [
                    {"text": "Install smart home devices OR repair basic household items to improve daily life", "domain": "R", "tags": ["home_improvement", "practical"]},
                    {"text": "Complete challenging puzzles or strategy games with friends", "domain": "I", "tags": ["mental_challenge", "collaborative_play"]},
                    {"text": "Visit local art exhibits or craft markets for inspiration", "domain": "A", "tags": ["artistic_exploration", "inspiration"]},
                    {"text": "Participate in a community clean-up or neighborhood improvement", "domain": "S", "tags": ["civic_engagement", "teamwork"]},
                    {"text": "Organize a skill-sharing workshop among friends", "domain": "E", "tags": ["knowledge_exchange", "leadership"]},
                    {"text": "Plan the upcoming week's meals and shopping list", "domain": "C", "tags": ["meal_planning", "preparation"]},
                ]
            },
        ]
        
        for ranking_set in ranking_sets:
            question = Question(
                page_id=page.id,
                item_id=ranking_set["item_id"],
                question_text=ranking_set["text"],
                question_type=QuestionType.ordering,
                order_index=question_counter,
                is_required=True,
                domain=None,  # Multiple domains
                tags=json.dumps([]),
                reverse_scored=False,
                scale_type="ranking",
                scale_labels=None,
                ordering_options=json.dumps(ranking_set["activities"]),
                randomize_order=True
            )
            db.add(question)
            question_counter += 1
        
        db.commit()
        print(f"✅ Created Page 1: RIASEC with 27 questions (18 Likert + 6 Forced Choice + 3 Ranking)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating RIASEC page: {e}")
        raise
    finally:
        db.close()


def create_bigfive_page():
    """Page 2: ALL Big Five Questions (25 questions, 5 traits × 5 items)"""
    print("🎨 Creating Big Five Page (ALL questions)...")
    db = SessionLocal()
    
    try:
        page = Page(
            title="How You're Wired",
            description="Rate how much each statement describes you",
            order_index=2,
            module_name="Big Five",
            is_active=True,
            completion_message="Big Five complete! 🧠"
        )
        db.add(page)
        db.flush()
        
        question_counter = 0
        scale_labels = json.dumps(["Not at all", "A little", "Kinda", "Mostly", "Totally!"])
        
        traits = [
            {
                "trait_id": "O",
                "trait_name": "Openness to Experience",
                "items": [
                    ("BF_O1", "When friends suggest trying new foods or activities, I'm usually eager to join", ["novelty_seeking", "adventure"]),
                    ("BF_O2", "I enjoy conversations with people who have different life experiences than mine", ["diversity_appreciation", "perspective_taking"]),
                    ("BF_O3", "I often notice and appreciate artistic elements in everyday environments", ["aesthetic_sensitivity", "observation"]),
                    ("BF_O4", "Learning how everyday technologies actually work interests me", ["technical_curiosity", "how_things_work"]),
                    ("BF_O5", "I frequently combine ideas from different sources to solve problems", ["integrative_thinking", "innovation"]),
                ]
            },
            {
                "trait_id": "C",
                "trait_name": "Conscientiousness",
                "items": [
                    ("BF_C1", "I naturally create systems to track my commitments and deadlines", ["systematic", "reliable"]),
                    ("BF_C2", "I complete household responsibilities before relaxing for the evening", ["responsibility", "discipline"]),
                    ("BF_C3", "I double-check important messages before sending them", ["attention_to_detail", "accuracy"]),
                    ("BF_C4", "People know they can rely on me when they need support", ["dependability", "trustworthy"]),
                    ("BF_C5", "I allocate specific times for work, family, and personal interests", ["time_management", "balance"]),
                ]
            },
            {
                "trait_id": "E",
                "trait_name": "Extraversion",
                "items": [
                    ("BF_E1", "I feel comfortable striking up conversations while waiting in lines", ["social_initiation", "outgoing"]),
                    ("BF_E2", "Video calls with friends and family leave me feeling energized", ["digital_socializing", "energy_from_others"]),
                    ("BF_E3", "In group settings, I naturally help include quieter participants", ["inclusion", "social_awareness"]),
                    ("BF_E4", "I maintain connections with people from different phases of my life", ["relationship_maintenance", "networking"]),
                    ("BF_E5", "I often use humor to lighten the mood in stressful situations", ["humor", "stress_relief"]),
                ]
            },
            {
                "trait_id": "A",
                "trait_name": "Agreeableness",
                "items": [
                    ("BF_A1", "I assume people have good intentions until shown otherwise", ["trust", "positive_regard"]),
                    ("BF_A2", "I notice when someone seems down and try to offer encouragement", ["empathy", "supportive"]),
                    ("BF_A3", "I treat service workers with the same respect as close friends", ["equality", "respect"]),
                    ("BF_A4", "Team accomplishments feel more satisfying than individual achievements", ["collaboration", "collective_success"]),
                    ("BF_A5", "I give people my full attention when they share personal stories", ["active_listening", "presence"]),
                ]
            },
            {
                "trait_id": "N",
                "trait_name": "Emotional Stability",
                "items": [
                    ("BF_N1", "Unexpected changes in plans don't typically upset me", ["adaptability", "flexibility"], True),
                    ("BF_N2", "I approach challenging situations with confidence in my coping abilities", ["self_confidence", "resilience"], True),
                    ("BF_N3", "Minor setbacks don't affect my overall mood throughout the day", ["mood_stability", "emotional_regulation"], True),
                    ("BF_N4", "I transition smoothly from work mode to relaxation in the evenings", ["work_life_balance", "recovery"], True),
                    ("BF_N5", "I have several strategies that help me manage stressful periods effectively", ["coping_skills", "stress_management"], True),
                ]
            },
        ]
        
        for trait in traits:
            for item in trait["items"]:
                item_id = item[0]
                text = item[1]
                tags = item[2]
                reverse_scored = item[3] if len(item) > 3 else False
                
                question = Question(
                    page_id=page.id,
                    item_id=item_id,
                    question_text=text,
                    question_type=QuestionType.slider,
                    order_index=question_counter,
                    is_required=True,
                    domain=trait["trait_id"],
                    tags=json.dumps(tags),
                    reverse_scored=reverse_scored,
                    scale_type="likert_5",
                    scale_labels=scale_labels,
                    slider_min_label="Not at all",
                    slider_max_label="Totally!"
                )
                db.add(question)
                question_counter += 1
        
        db.commit()
        print(f"✅ Created Page 2: Big Five with 25 questions (5 traits × 5 items)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating Big Five page: {e}")
        raise
    finally:
        db.close()


def create_behavioral_page():
    """Page 3: Behavioral Traits (21 questions, 7 traits × 3)"""
    print("🚀 Creating Behavioral Traits Page...")
    db = SessionLocal()
    
    try:
        page = Page(
            title="How You Roll Under Pressure",
            description="Quick questions about your work style and habits",
            order_index=3,
            module_name="Behavioral",
            is_active=True,
            completion_message="Assessment complete! Let's see your rhythm profile... 🎉"
        )
        db.add(page)
        db.flush()
        
        question_counter = 0
        scale_labels = json.dumps(["Not at all", "A little", "Kinda", "Mostly", "Totally!"])
        
        behavioral_items = [
            # Motivation Type
            ("BH_M1", "motivation_type", "Working on projects that align with my personal values feels inherently rewarding", ["intrinsic_motivation", "purpose_driven"], False),
            ("BH_M2", "motivation_type", "Learning new skills through online courses holds my attention without external incentives", ["self_directed_learning", "autonomy"], False),
            ("BH_M3", "motivation_type", "Public recognition significantly influences how much effort I put into tasks", ["extrinsic_motivation", "validation_seeking"], True),
            
            # Grit / Persistence
            ("BH_G1", "grit_persistence", "I continue practicing difficult skills until I achieve noticeable improvement", ["perseverance", "mastery_orientation"], False),
            ("BH_G2", "grit_persistence", "When my initial approach fails, I try alternative methods rather than giving up", ["adaptability", "problem_solving"], False),
            ("BH_G3", "grit_persistence", "I lose motivation when I don't see quick results from my efforts", ["impatience", "outcome_dependent"], True),
            
            # Self-Efficacy
            ("BH_SE1", "self_efficacy", "When facing unfamiliar challenges, I trust my ability to figure things out", ["confidence", "resourcefulness"], False),
            ("BH_SE2", "self_efficacy", "I approach new software or apps with confidence I can learn to use them", ["tech_confidence", "learning_agency"], False),
            ("BH_SE3", "self_efficacy", "Technical problems sometimes feel beyond my capability to solve", ["self_doubt", "helplessness"], True),
            
            # Resilience / Stress Tolerance
            ("BH_R1", "resilience", "I maintain focus during busy periods when multiple demands compete for attention", ["focus_under_pressure", "multitasking"], False),
            ("BH_R2", "resilience", "After disappointing outcomes, I quickly identify constructive next steps", ["bounce_back", "solution_oriented"], False),
            ("BH_R3", "resilience", "Minor technical glitches can frustrate me for hours", ["frustration_tolerance", "emotional_reactivity"], True),
            
            # Learning Orientation
            ("BH_L1", "learning_orientation", "I believe people can develop most abilities through dedicated practice", ["growth_mindset", "effort_belief"], False),
            ("BH_L2", "learning_orientation", "Challenging tasks appeal to me because they expand my capabilities", ["challenge_seeking", "skill_building"], False),
            ("BH_L3", "learning_orientation", "I avoid activities where others might see me make mistakes", ["perfectionism", "fear_of_failure"], True),
            
            # Empathy / Emotional Intelligence
            ("BH_EM1", "empathy", "I notice subtle changes in people's tone of voice during conversations", ["emotional_detection", "sensitivity"], False),
            ("BH_EM2", "empathy", "I consider how my decisions might affect different people in my life", ["perspective_taking", "impact_awareness"], False),
            ("BH_EM3", "empathy", "Friends often seek my perspective when navigating difficult situations", ["trusted_advisor", "supportive"], False),
            
            # Task Start Tempo
            ("BH_T1", "task_start_tempo", "I often delay beginning tasks until deadlines feel urgent", ["procrastination_risk", "deadline_driven"], True),
            ("BH_T2", "task_start_tempo", "Taking the first small action on projects gives me momentum to continue", ["task_initiation", "momentum_builder"], False),
            ("BH_T3", "task_start_tempo", "I spend more time planning tasks than actually executing them", ["over_planning", "perfectionism"], True),
        ]
        
        for item_id, trait, text, tags, reverse_scored in behavioral_items:
            question = Question(
                page_id=page.id,
                item_id=item_id,
                question_text=text,
                question_type=QuestionType.slider,
                order_index=question_counter,
                is_required=True,
                domain=trait,
                tags=json.dumps(tags),
                reverse_scored=reverse_scored,
                scale_type="likert_5",
                scale_labels=scale_labels,
                slider_min_label="Not at all",
                slider_max_label="Totally!"
            )
            db.add(question)
            question_counter += 1
        
        db.commit()
        print(f"✅ Created Page 3: Behavioral Traits with 21 questions (7 traits × 3 items)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating Behavioral page: {e}")
        raise
    finally:
        db.close()


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🎯 CaRhythm v1.1 Database Population (3-Page Version)")
    print("="*70 + "\n")
    
    # Ensure tables exist
    create_tables()
    
    # Clear old data
    clear_database()
    
    # Create all 3 consolidated pages
    create_riasec_page()      # Page 1: ALL 27 RIASEC questions
    create_bigfive_page()     # Page 2: ALL 25 Big Five questions  
    create_behavioral_page()  # Page 3: ALL 21 Behavioral questions
    
    print("\n" + "="*70)
    print("✅ Database population complete!")
    print("="*70)
    print("\n📊 Summary:")
    print("  • 3 pages created (consolidated)")
    print("  • 73 total questions")
    print("  • Page 1 - RIASEC: 18 Likert + 6 Forced Choice + 3 Ranking = 27 items")
    print("  • Page 2 - Big Five: 5 traits × 5 items = 25 items")
    print("  • Page 3 - Behavioral: 7 traits × 3 items = 21 items")
    print("  • Ready for CaRhythm v1.1! 🚀")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
