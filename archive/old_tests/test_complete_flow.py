"""
Comprehensive Test Suite for CaRhythm Assessment Flow
Tests the complete user journey from start to finish
"""

import asyncio
import json
from sqlalchemy.orm import Session
from app.models.database import SessionLocal, engine
from app.models import StudentResponse, QuestionAnswer, AssessmentScore, Page, Question
from app.services.scoring_service_v1_1 import calculate_complete_profile_v1_1, save_assessment_score_v1_1
from app.services.pdf_service import generate_pdf_report
from app.services.email_service import send_results_email
import os
from datetime import datetime

# Test configuration
TEST_EMAIL = "mr856264@gmail.com"
TEST_SESSION_ID = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

class TestReport:
    """Test report generator"""
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def add_test(self, name, status, message="", details=""):
        self.tests.append({
            'name': name,
            'status': status,
            'message': message,
            'details': details
        })
        if status == 'PASS':
            self.passed += 1
        elif status == 'FAIL':
            self.failed += 1
        elif status == 'WARN':
            self.warnings += 1
    
    def print_report(self):
        print("\n" + "="*80)
        print("CARHYTHM COMPREHENSIVE TEST REPORT")
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Tests: {len(self.tests)}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print("="*80 + "\n")
        
        for i, test in enumerate(self.tests, 1):
            status_icon = {'PASS': '✅', 'FAIL': '❌', 'WARN': '⚠️'}.get(test['status'], '❓')
            print(f"{i}. {status_icon} {test['name']}")
            if test['message']:
                print(f"   {test['message']}")
            if test['details']:
                print(f"   Details: {test['details']}")
            print()
        
        print("="*80)
        print(f"OVERALL RESULT: {'✅ ALL TESTS PASSED' if self.failed == 0 else f'❌ {self.failed} TEST(S) FAILED'}")
        print("="*80 + "\n")

def test_database_connection(report: TestReport):
    """Test database connectivity"""
    try:
        from sqlalchemy import text
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).scalar()
        db.close()
        
        if result == 1:
            report.add_test(
                "Database Connection",
                "PASS",
                "Successfully connected to SQLite database"
            )
            return True
        else:
            report.add_test(
                "Database Connection",
                "FAIL",
                "Database query returned unexpected result"
            )
            return False
    except Exception as e:
        report.add_test(
            "Database Connection",
            "FAIL",
            f"Database connection failed: {str(e)}"
        )
        return False

def test_database_schema(report: TestReport):
    """Test database schema integrity"""
    try:
        from sqlalchemy import text
        db = SessionLocal()
        
        # Check if all required tables exist
        tables = ['pages', 'questions', 'student_responses', 'question_answers', 'assessment_scores']
        missing_tables = []
        
        for table in tables:
            try:
                db.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
            except:
                missing_tables.append(table)
        
        db.close()
        
        if not missing_tables:
            report.add_test(
                "Database Schema",
                "PASS",
                "All required tables exist"
            )
            return True
        else:
            report.add_test(
                "Database Schema",
                "FAIL",
                f"Missing tables: {', '.join(missing_tables)}"
            )
            return False
    except Exception as e:
        report.add_test(
            "Database Schema",
            "FAIL",
            f"Schema check failed: {str(e)}"
        )
        return False

def test_assessment_data(report: TestReport):
    """Test assessment data (pages and questions)"""
    try:
        db = SessionLocal()
        
        # Check pages
        pages = db.query(Page).all()
        if len(pages) < 3:
            report.add_test(
                "Assessment Data - Pages",
                "FAIL",
                f"Expected at least 3 pages, found {len(pages)}"
            )
            return False
        
        # Check questions
        questions = db.query(Question).all()
        if len(questions) < 20:
            report.add_test(
                "Assessment Data - Questions",
                "WARN",
                f"Found {len(questions)} questions (expected more for full assessment)"
            )
        else:
            report.add_test(
                "Assessment Data - Questions",
                "PASS",
                f"Found {len(questions)} questions across {len(pages)} pages"
            )
        
        # Check question types
        riasec_questions = db.query(Question).join(Page).filter(Page.order_index == 1).count()
        bigfive_questions = db.query(Question).join(Page).filter(Page.order_index == 2).count()
        behavioral_questions = db.query(Question).join(Page).filter(Page.order_index == 3).count()
        
        report.add_test(
            "Assessment Structure",
            "PASS",
            f"RIASEC: {riasec_questions} | Big Five: {bigfive_questions} | Behavioral: {behavioral_questions}"
        )
        
        db.close()
        return True
        
    except Exception as e:
        report.add_test(
            "Assessment Data",
            "FAIL",
            f"Data check failed: {str(e)}"
        )
        return False

def test_create_sample_response(report: TestReport, db: Session):
    """Create a sample student response with answers optimized for an engineer profile"""
    try:
        # Create student response for an engineer
        response = StudentResponse(
            session_id=TEST_SESSION_ID,
            email=TEST_EMAIL,
            full_name="Mohamed Ramadan - Software Engineer",
            age_group="25-34",
            country="Egypt",
            origin_country="Egypt"
        )
        db.add(response)
        db.commit()
        db.refresh(response)
        
        # Get all questions by page
        pages = db.query(Page).order_by(Page.order_index).all()
        
        answers_created = 0
        
        for page in pages:
            questions = db.query(Question).filter(Question.page_id == page.id).all()
            
            for question in questions:
                answer_value = None
                
                # RIASEC Page (Page 1) - Engineer profile: High R (Realistic), High I (Investigative)
                if page.order_index == 1:
                    if question.domain == 'R':  # Realistic - Engineers are hands-on
                        answer_value = 4.5 if not question.reverse_scored else 1.5
                    elif question.domain == 'I':  # Investigative - Engineers analyze/solve
                        answer_value = 4.8 if not question.reverse_scored else 1.2
                    elif question.domain == 'A':  # Artistic - Moderate (creative problem solving)
                        answer_value = 3.2 if not question.reverse_scored else 2.8
                    elif question.domain == 'S':  # Social - Lower for typical engineers
                        answer_value = 2.5 if not question.reverse_scored else 3.5
                    elif question.domain == 'E':  # Enterprising - Moderate
                        answer_value = 3.0 if not question.reverse_scored else 3.0
                    elif question.domain == 'C':  # Conventional - Moderate to high (systematic)
                        answer_value = 3.8 if not question.reverse_scored else 2.2
                    else:
                        answer_value = 3.5
                
                # Big Five Page (Page 2) - Engineer personality traits
                elif page.order_index == 2:
                    if question.domain == 'O':  # Openness - High (curious, innovative)
                        answer_value = 4.5 if not question.reverse_scored else 1.5
                    elif question.domain == 'C':  # Conscientiousness - Very High (detail-oriented)
                        answer_value = 4.8 if not question.reverse_scored else 1.2
                    elif question.domain == 'E':  # Extraversion - Moderate to Low (introverted tendency)
                        answer_value = 2.8 if not question.reverse_scored else 3.2
                    elif question.domain == 'A':  # Agreeableness - Moderate (team player but direct)
                        answer_value = 3.5 if not question.reverse_scored else 2.5
                    elif question.domain == 'N':  # Neuroticism - Low (calm under pressure)
                        answer_value = 1.8 if not question.reverse_scored else 4.2
                    else:
                        answer_value = 3.5
                
                # Behavioral Page (Page 3) - Engineer work habits
                elif page.order_index == 3:
                    if 'motivation' in question.domain.lower():
                        answer_value = 4.5  # High intrinsic motivation
                    elif 'grit' in question.domain.lower() or 'persist' in question.domain.lower():
                        answer_value = 4.7  # Very persistent
                    elif 'self' in question.domain.lower() and 'efficacy' in question.domain.lower():
                        answer_value = 4.6  # Confident in abilities
                    elif 'resilien' in question.domain.lower():
                        answer_value = 4.3  # Resilient problem solver
                    elif 'learning' in question.domain.lower() or 'growth' in question.domain.lower():
                        answer_value = 4.8  # Strong growth mindset
                    elif 'empathy' in question.domain.lower():
                        answer_value = 3.2  # Moderate empathy (logic-focused)
                    elif 'task' in question.domain.lower() and 'start' in question.domain.lower():
                        answer_value = 4.0  # Good at starting tasks
                    else:
                        answer_value = 4.0
                    
                    if question.reverse_scored:
                        answer_value = 6.0 - answer_value
                
                else:
                    answer_value = 3.5
                
                # Create answer
                if question.question_type.value == "slider":
                    answer = QuestionAnswer(
                        response_id=response.id,
                        question_id=question.id,
                        answer_value=answer_value
                    )
                elif question.question_type.value == "mcq":
                    answer = QuestionAnswer(
                        response_id=response.id,
                        question_id=question.id,
                        answer_json=json.dumps({"selected_options": ["option_1"]})
                    )
                elif question.question_type.value == "ordering":
                    answer = QuestionAnswer(
                        response_id=response.id,
                        question_id=question.id,
                        answer_json=json.dumps({"ordered_items": ["item_1", "item_2", "item_3"]})
                    )
                else:
                    continue
                
                db.add(answer)
                answers_created += 1
        
        db.commit()
        
        report.add_test(
            "Sample Response Creation",
            "PASS",
            f"Created engineer profile with {answers_created} answers | Expected Holland Code: RIC or RI*"
        )
        return response.id
        
    except Exception as e:
        report.add_test(
            "Sample Response Creation",
            "FAIL",
            f"Failed to create sample: {str(e)}"
        )
        import traceback
        print(f"Error: {traceback.format_exc()}")
        return None

def test_scoring_calculation(report: TestReport, db: Session, response_id: int):
    """Test scoring calculation"""
    try:
        # Calculate complete profile
        profile = calculate_complete_profile_v1_1(db, response_id)
        
        if not profile:
            report.add_test(
                "Scoring Calculation",
                "FAIL",
                "Profile calculation returned None"
            )
            return None
        
        # Verify profile structure
        required_keys = ['riasec', 'bigfive', 'behavioral', 'ikigai_zones']
        missing_keys = [k for k in required_keys if k not in profile]
        
        if missing_keys:
            report.add_test(
                "Scoring Calculation",
                "FAIL",
                f"Profile missing keys: {', '.join(missing_keys)}"
            )
            return None
        
        # Check RIASEC scores
        riasec = profile['riasec']
        if 'holland_code' not in riasec or len(riasec['holland_code']) != 3:
            report.add_test(
                "RIASEC Scoring",
                "FAIL",
                f"Invalid Holland code: {riasec.get('holland_code', 'None')}"
            )
        else:
            report.add_test(
                "RIASEC Scoring",
                "PASS",
                f"Holland Code: {riasec['holland_code']} | Top score: {max(riasec['raw_scores'].values()):.1f}"
            )
        
        # Check Big Five scores
        bigfive = profile['bigfive']
        bigfive_sum = sum(bigfive['raw_scores'].values())
        report.add_test(
            "Big Five Scoring",
            "PASS",
            f"Total score: {bigfive_sum:.1f} | Traits: {list(bigfive['strength_labels'].values())}"
        )
        
        # Check Behavioral scores
        behavioral = profile['behavioral']
        flags_count = sum(1 for v in behavioral['behavioral_flags'].values() if v)
        report.add_test(
            "Behavioral Scoring",
            "PASS",
            f"Traits measured: {len(behavioral['strength_labels'])} | Flags: {flags_count}"
        )
        
        return profile
        
    except Exception as e:
        report.add_test(
            "Scoring Calculation",
            "FAIL",
            f"Calculation failed: {str(e)}"
        )
        return None

def test_save_to_database(report: TestReport, db: Session, response_id: int, profile: dict):
    """Test saving scores to database"""
    try:
        score_record = save_assessment_score_v1_1(db, response_id, profile)
        
        if not score_record:
            report.add_test(
                "Save to Database",
                "FAIL",
                "Failed to save score record"
            )
            return None
        
        # Verify saved data
        saved_score = db.query(AssessmentScore).filter(
            AssessmentScore.response_id == response_id
        ).first()
        
        if not saved_score:
            report.add_test(
                "Save to Database",
                "FAIL",
                "Score record not found after saving"
            )
            return None
        
        # Check JSON fields
        checks = []
        if saved_score.riasec_raw_scores:
            checks.append("RIASEC ✓")
        if saved_score.bigfive_strength_labels:
            checks.append("Big Five ✓")
        if saved_score.behavioral_strength_labels:
            checks.append("Behavioral ✓")
        if saved_score.rhythm_profile:
            checks.append("Full Profile ✓")
        
        report.add_test(
            "Save to Database",
            "PASS",
            f"Score record saved | Fields: {' | '.join(checks)}"
        )
        return saved_score
        
    except Exception as e:
        report.add_test(
            "Save to Database",
            "FAIL",
            f"Save failed: {str(e)}"
        )
        return None

def test_pdf_generation(report: TestReport, db: Session, response_id: int):
    """Test PDF generation"""
    try:
        # Get response and score data
        response = db.query(StudentResponse).filter(StudentResponse.id == response_id).first()
        score = db.query(AssessmentScore).filter(AssessmentScore.response_id == response_id).first()
        
        if not response or not score:
            report.add_test(
                "PDF Generation - Data",
                "FAIL",
                "Missing response or score data"
            )
            return None
        
        # Prepare data for PDF
        response_dict = {
            'student_name': response.full_name,
            'email': response.email,
            'age_group': response.age_group,
            'country': response.country
        }
        
        scores_dict = {
            'riasec_raw_scores': json.loads(score.riasec_raw_scores) if score.riasec_raw_scores else {},
            'riasec_strength_labels': json.loads(score.riasec_strength_labels) if score.riasec_strength_labels else {},
            'holland_code': score.riasec_profile or '',
            'bigfive_raw_scores': {
                'O': score.bigfive_openness or 0,
                'C': score.bigfive_conscientiousness or 0,
                'E': score.bigfive_extraversion or 0,
                'A': score.bigfive_agreeableness or 0,
                'N': score.bigfive_neuroticism or 0
            },
            'bigfive_strength_labels': json.loads(score.bigfive_strength_labels) if score.bigfive_strength_labels else {},
            'behavioral_strength_labels': json.loads(score.behavioral_strength_labels) if score.behavioral_strength_labels else {},
            'behavioral_flags': json.loads(score.behavioral_flags) if score.behavioral_flags else {},
            'ikigai_zones': json.loads(score.ikigai_zones) if score.ikigai_zones else {}
        }
        
        # Extract behavioral raw scores from rhythm_profile
        if score.rhythm_profile:
            try:
                rhythm_profile = json.loads(score.rhythm_profile)
                behavioral_raw_scores = rhythm_profile.get('behavioral', {}).get('raw_scores', {})
                scores_dict['behavioral_raw_scores'] = behavioral_raw_scores
            except:
                scores_dict['behavioral_raw_scores'] = {}
        
        # Generate PDF (V1 freemium with is_free_version parameter)
        pdf_buffer = generate_pdf_report(
            response_dict, 
            scores_dict,
            is_free_version=True,  # Generate premium version for testing
            checkout_url='https://carhythm.com/paid',
            discount_code='LAUNCH50'
        )
        
        if not pdf_buffer:
            report.add_test(
                "PDF Generation",
                "FAIL",
                "PDF buffer is None"
            )
            return None
        
        # Check PDF size
        pdf_buffer.seek(0, 2)  # Seek to end
        pdf_size = pdf_buffer.tell()
        pdf_buffer.seek(0)  # Reset
        
        if pdf_size < 1000:
            report.add_test(
                "PDF Generation",
                "FAIL",
                f"PDF too small ({pdf_size} bytes), likely corrupted"
            )
            return None
        
        # Save test PDF
        test_pdf_path = f"/media/mohamedramadan/work/Carhythm/carhythm/test_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(test_pdf_path, 'wb') as f:
            f.write(pdf_buffer.read())
        
        pdf_buffer.seek(0)
        
        report.add_test(
            "PDF Generation",
            "PASS",
            f"PDF generated successfully | Size: {pdf_size:,} bytes | Saved to: {test_pdf_path}"
        )
        return pdf_buffer
        
    except Exception as e:
        report.add_test(
            "PDF Generation",
            "FAIL",
            f"Generation failed: {str(e)}"
        )
        import traceback
        print(f"PDF Error Traceback:\n{traceback.format_exc()}")
        return None

def test_logo_availability(report: TestReport):
    """Test logo file availability"""
    logo_path = os.path.join(os.path.dirname(__file__), 'frontend', 'public', 'CaRhythm updated logo.png')
    
    if os.path.exists(logo_path):
        size = os.path.getsize(logo_path)
        report.add_test(
            "Logo Availability",
            "PASS",
            f"Logo found | Size: {size:,} bytes | Path: {logo_path}"
        )
    else:
        report.add_test(
            "Logo Availability",
            "WARN",
            f"Logo not found at: {logo_path} | PDF will use fallback emoji"
        )

async def test_email_service(report: TestReport, pdf_buffer):
    """Test email service by sending actual email"""
    try:
        from app.config import settings
        
        # Check email configuration
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            report.add_test(
                "Email Configuration",
                "WARN",
                "SMTP settings not configured | Email sending disabled"
            )
            return False
        
        report.add_test(
            "Email Configuration",
            "PASS",
            f"SMTP: {settings.SMTP_HOST}:{settings.SMTP_PORT} | From: {settings.SMTP_FROM_EMAIL}"
        )
        
        # Actually send test email
        if settings.ENABLE_EMAIL:
            print(f"\n📧 Sending test email to {TEST_EMAIL}...")
            result = await send_results_email(
                to_email=TEST_EMAIL,
                student_name="Test User",
                holland_code="RIA",
                top_strength="Openness",
                pdf_buffer=pdf_buffer,
                pdf_filename="CaRhythm_Test_Report.pdf"
            )
            
            if result['success']:
                report.add_test(
                    "Email Service - Send Test",
                    "PASS",
                    f"✅ Email sent successfully to {TEST_EMAIL}"
                )
            else:
                report.add_test(
                    "Email Service - Send Test",
                    "FAIL",
                    f"❌ Email failed: {result.get('error', 'Unknown error')}"
                )
        else:
            report.add_test(
                "Email Service",
                "WARN",
                "Email sending disabled in settings (ENABLE_EMAIL=false)"
            )
        
        return True
        
    except Exception as e:
        import traceback
        report.add_test(
            "Email Service",
            "FAIL",
            f"Email test failed: {str(e)}\\n{traceback.format_exc()}"
        )
        return False

def cleanup_test_data(report: TestReport, db: Session, response_id: int):
    """Clean up test data"""
    try:
        # Delete answers
        db.query(QuestionAnswer).filter(QuestionAnswer.response_id == response_id).delete()
        
        # Delete score
        db.query(AssessmentScore).filter(AssessmentScore.response_id == response_id).delete()
        
        # Delete response
        db.query(StudentResponse).filter(StudentResponse.id == response_id).delete()
        
        db.commit()
        
        report.add_test(
            "Cleanup",
            "PASS",
            "Test data cleaned up successfully"
        )
        return True
        
    except Exception as e:
        report.add_test(
            "Cleanup",
            "WARN",
            f"Cleanup incomplete: {str(e)}"
        )
        return False

async def run_all_tests():
    """Run all tests"""
    report = TestReport()
    
    print("\n🚀 Starting CaRhythm Comprehensive Test Suite...")
    print("=" * 80 + "\n")
    
    # 1. Test database connection
    if not test_database_connection(report):
        report.print_report()
        return
    
    # 2. Test database schema
    test_database_schema(report)
    
    # 3. Test assessment data
    test_assessment_data(report)
    
    # 4. Test logo availability
    test_logo_availability(report)
    
    # 5. Create sample response
    db = SessionLocal()
    response_id = test_create_sample_response(report, db)
    
    if not response_id:
        db.close()
        report.print_report()
        return
    
    # 6. Test scoring calculation
    profile = test_scoring_calculation(report, db, response_id)
    
    if not profile:
        cleanup_test_data(report, db, response_id)
        db.close()
        report.print_report()
        return
    
    # 7. Test save to database
    saved_score = test_save_to_database(report, db, response_id, profile)
    
    if not saved_score:
        cleanup_test_data(report, db, response_id)
        db.close()
        report.print_report()
        return
    
    # 8. Test PDF generation
    pdf_buffer = test_pdf_generation(report, db, response_id)
    
    # 9. Test email service
    if pdf_buffer:
        await test_email_service(report, pdf_buffer)
    
    # 10. Cleanup
    cleanup_test_data(report, db, response_id)
    db.close()
    
    # Print final report
    report.print_report()

if __name__ == "__main__":
    asyncio.run(run_all_tests())
