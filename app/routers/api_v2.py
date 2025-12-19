"""
REST API v2 for Story Mode React Frontend
Provides endpoints for modern assessment interface with enhanced UX
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid
import json

from ..models import get_db, Page, Question, StudentResponse, QuestionAnswer, QuestionType, AssessmentScore
from ..services import question_service, response_service
from ..services.scoring_service_v1_1 import calculate_complete_profile_v1_1, save_assessment_score_v1_1
from ..services.email_service import send_results_email, send_admin_notification
from ..services.pdf_service import generate_pdf_report
from ..schemas import StudentResponseCreate, QuestionAnswerCreate
from ..config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["api_v2"])

# ============================================================================
# Pydantic Models for API
# ============================================================================

class ModuleInfo(BaseModel):
    """Information about an assessment module/chapter"""
    id: int
    name: str
    emoji: str
    title: str
    description: Optional[str]
    total_pages: int
    total_questions: int
    estimated_minutes: Optional[int]
    theme: Optional[str]
    chapter_number: Optional[int]
    order_index: int

class QuestionResponse(BaseModel):
    """Question data for frontend"""
    id: int
    type: str
    text: str
    scene_title: Optional[str]
    scene_narrative: Optional[str]
    scene_image: Optional[str]
    scene_theme: Optional[str]
    required: bool
    options: Dict[str, Any]

class NavigationInfo(BaseModel):
    """Navigation information"""
    current_page: int
    total_pages: int
    is_first: bool
    is_last: bool
    previous_page_id: Optional[int]
    next_page_id: Optional[int]

class AnswerSubmission(BaseModel):
    """Answer submission from frontend"""
    session_id: str
    question_id: int
    answer: Dict[str, Any]

class StudentInfoSubmission(BaseModel):
    """Student information submission"""
    session_id: str
    email: EmailStr
    full_name: str
    age_group: str
    country: str
    origin_country: str

class ProgressResponse(BaseModel):
    """Progress tracking information"""
    session_id: str
    modules: List[Dict[str, Any]]
    total_xp: int
    badges: List[str]
    current_page_id: Optional[int]
    percentage_complete: float

# ============================================================================
# Endpoints
# ============================================================================

@router.get("/modules", response_model=List[ModuleInfo])
async def get_modules(db: Session = Depends(get_db)):
    """
    Get all assessment modules/chapters with metadata.
    Groups pages by module for Story Mode presentation.
    """
    pages = question_service.get_pages(db, active_only=True)
    
    # Group pages by module
    modules_dict = {}
    
    for page in pages:
        module_name = page.module_name or "Assessment"
        
        if module_name not in modules_dict:
            modules_dict[module_name] = {
                "pages": [],
                "emoji": page.module_emoji or "📝",
                "chapter_number": page.chapter_number or 0,
                "theme": "default"
            }
        
        modules_dict[module_name]["pages"].append(page)
    
    # Convert to response format
    modules = []
    for module_name, module_data in modules_dict.items():
        module_pages = module_data["pages"]
        
        # Count total questions
        total_questions = sum(len(p.questions) for p in module_pages)
        
        # Calculate estimated time
        estimated_minutes = sum(p.estimated_minutes or 0 for p in module_pages)
        if estimated_minutes == 0:
            # Fallback: estimate based on question count
            estimated_minutes = max(5, total_questions // 10)
        
        # Get first page for reference
        first_page = module_pages[0]
        
        modules.append(ModuleInfo(
            id=first_page.id,  # Use first page ID as module ID
            name=module_name,
            emoji=module_data["emoji"],
            title=f"Chapter: {module_name}",
            description=first_page.description,
            total_pages=len(module_pages),
            total_questions=total_questions,
            estimated_minutes=estimated_minutes,
            theme=module_data["theme"],
            chapter_number=module_data["chapter_number"],
            order_index=first_page.order_index
        ))
    
    # Sort by order_index
    modules.sort(key=lambda x: x.order_index)
    
    return modules


@router.get("/questions")
async def get_questions(
    page_id: int,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get questions for a specific page with navigation info.
    """
    # Get page
    page = question_service.get_page_by_id(db, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Get questions
    questions = question_service.get_questions_by_page(db, page_id)
    
    # Get all pages for navigation
    all_pages = question_service.get_pages(db, active_only=True)
    page_ids = [p.id for p in all_pages]
    
    try:
        current_index = page_ids.index(page_id)
    except ValueError:
        current_index = 0
    
    # Build navigation info
    navigation = NavigationInfo(
        current_page=current_index + 1,
        total_pages=len(all_pages),
        is_first=current_index == 0,
        is_last=current_index == len(all_pages) - 1,
        previous_page_id=page_ids[current_index - 1] if current_index > 0 else None,
        next_page_id=page_ids[current_index + 1] if current_index < len(all_pages) - 1 else None
    )
    
    # Format questions for frontend
    formatted_questions = []
    for q in questions:
        # Build options dict based on question type
        options = {}
        
        if q.question_type == QuestionType.slider:
            options = {
                "min": 1,  # v1.1: 5-point Likert scale
                "max": 5,
                "step": 1,
                "min_label": q.slider_min_label or "Not at all",
                "max_label": q.slider_max_label or "Totally!",
                "scale_labels": json.loads(q.scale_labels) if q.scale_labels else ["Not at all", "A little", "Kinda", "Mostly", "Totally!"],
                "item_id": q.item_id,  # v1.1: Include item ID for scoring
                "domain": q.domain,  # v1.1: Include domain
                "reverse_scored": q.reverse_scored  # v1.1: Include reverse scoring flag
            }
        elif q.question_type == QuestionType.mcq:
            mcq_options = json.loads(q.mcq_options) if q.mcq_options else []
            options = {
                "choices": mcq_options,
                "multiple": q.allow_multiple_selection,
                "item_id": q.item_id  # v1.1: Include item ID
            }
        elif q.question_type == QuestionType.ordering:
            ordering_options = json.loads(q.ordering_options) if q.ordering_options else []
            options = {
                "items": ordering_options,
                "randomize": q.randomize_order,
                "item_id": q.item_id  # v1.1: Include item ID
            }
        elif q.question_type == QuestionType.essay:
            options = {
                "char_limit": q.essay_char_limit
            }
        
        formatted_questions.append(QuestionResponse(
            id=q.id,
            type=q.question_type.value,
            text=q.question_text,
            scene_title=q.scene_title,
            scene_narrative=q.scene_narrative,
            scene_image=q.scene_image_url or q.image_path,
            scene_theme=q.scene_theme,
            required=q.is_required,
            options=options
        ))
    
    return {
        "page": {
            "id": page.id,
            "title": page.title,
            "description": page.description,
            "module": page.module_name,
            "module_emoji": page.module_emoji,
            "module_description": page.module_description,
            "chapter_number": page.chapter_number,
            "estimated_minutes": page.estimated_minutes,
            "module_color_primary": page.module_color_primary,
            "module_color_secondary": page.module_color_secondary,
            "completion_message": page.completion_message
        },
        "questions": formatted_questions,
        "navigation": navigation
    }


@router.post("/session/start")
async def start_session(db: Session = Depends(get_db)):
    """
    Create a new assessment session.
    Returns a unique session ID for tracking progress.
    """
    session_id = str(uuid.uuid4())
    
    # Create temporary response entry
    temp_response = StudentResponseCreate(
        session_id=session_id,
        email="temp@temp.com",
        full_name="In Progress",
        age_group="temp",
        country="temp",
        origin_country="temp"
    )
    
    response_service.create_student_response(db, temp_response)
    
    return {
        "session_id": session_id,
        "created_at": datetime.now().isoformat()
    }


@router.get("/session/{session_id}/validate")
async def validate_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Check if session exists and return progress info for resume.
    Returns valid=False if session not found or expired (30 days).
    """
    session_info = response_service.validate_session(db, session_id)
    
    if not session_info:
        return {
            "valid": False,
            "reason": "Session not found or expired"
        }
    
    return {
        "valid": True,
        "session": {
            "session_id": session_info["session_id"],
            "status": session_info["status"],
            "current_page_id": session_info["current_page_id"],
            "last_activity": session_info["last_activity"]
        },
        "progress": session_info["progress"]
    }


@router.post("/session/{session_id}/abandon")
async def abandon_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Mark session as abandoned when user chooses Start Fresh.
    This allows user to start a new session without affecting old progress.
    """
    success = response_service.mark_session_abandoned(db, session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "success": True,
        "message": "Session marked as abandoned. You can now start fresh!"
    }


@router.post("/answers/submit")
async def submit_answer(
    submission: AnswerSubmission,
    db: Session = Depends(get_db)
):
    """
    Submit an answer for a question.
    Returns XP gained and progress information.
    """
    # Get or validate session
    student_response = response_service.get_student_response_by_session(db, submission.session_id)
    if not student_response:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get question
    question = question_service.get_question_by_id(db, submission.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Format answer based on type
    answer_data = None
    answer_dict = submission.answer
    
    if answer_dict.get("type") == "slider":
        answer_data = QuestionAnswerCreate(
            response_id=student_response.id,
            question_id=submission.question_id,
            answer_value=float(answer_dict.get("value", 0))
        )
    elif answer_dict.get("type") == "mcq":
        answer_data = QuestionAnswerCreate(
            response_id=student_response.id,
            question_id=submission.question_id,
            answer_json=json.dumps({
                "selected_options": answer_dict.get("selected_options", []),
                "question_type": "mcq"
            })
        )
    elif answer_dict.get("type") == "ordering":
        answer_data = QuestionAnswerCreate(
            response_id=student_response.id,
            question_id=submission.question_id,
            answer_json=json.dumps({
                "ordered_items": answer_dict.get("ordered_items", []),
                "question_type": "ordering"
            })
        )
    elif answer_dict.get("type") == "essay":
        answer_data = QuestionAnswerCreate(
            response_id=student_response.id,
            question_id=submission.question_id,
            answer_text=answer_dict.get("text", "")
        )
    
    if answer_data:
        # Delete existing answer for this question if any
        existing = db.query(QuestionAnswer).filter(
            QuestionAnswer.response_id == student_response.id,
            QuestionAnswer.question_id == submission.question_id
        ).first()
        if existing:
            db.delete(existing)
        
        # Create new answer
        response_service.create_question_answer(db, answer_data)
    
    # Calculate progress
    total_questions = db.query(Question).join(Page).filter(Page.is_active == True).count()
    answered_questions = db.query(QuestionAnswer).filter(
        QuestionAnswer.response_id == student_response.id
    ).count()
    
    # Simple XP calculation
    xp_gained = 10
    total_xp = answered_questions * 10
    
    # Check for badges (simplified)
    badges = []
    if answered_questions == 1:
        badges.append("first_answer")
    if answered_questions % 10 == 0:
        badges.append("milestone_" + str(answered_questions))
    
    return {
        "success": True,
        "xp_gained": xp_gained,
        "total_xp": total_xp,
        "badges_unlocked": badges,
        "progress": {
            "questions_answered": answered_questions,
            "total_questions": total_questions,
            "percentage": round((answered_questions / total_questions * 100), 1) if total_questions > 0 else 0
        }
    }


@router.get("/session/{session_id}/progress")
async def get_progress(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get current progress for a session.
    """
    student_response = response_service.get_student_response_by_session(db, session_id)
    if not student_response:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get answered questions count
    answered_count = db.query(QuestionAnswer).filter(
        QuestionAnswer.response_id == student_response.id
    ).count()
    
    # Get total questions
    total_questions = db.query(Question).join(Page).filter(Page.is_active == True).count()
    
    # Get modules progress
    pages = question_service.get_pages(db, active_only=True)
    modules_progress = []
    
    modules_dict = {}
    for page in pages:
        module_name = page.module_name or "Assessment"
        if module_name not in modules_dict:
            modules_dict[module_name] = {
                "total": 0,
                "completed": 0
            }
        
        page_questions = len(page.questions)
        modules_dict[module_name]["total"] += page_questions
        
        # Count answered questions for this page
        answered_in_page = db.query(QuestionAnswer).filter(
            QuestionAnswer.response_id == student_response.id,
            QuestionAnswer.question_id.in_([q.id for q in page.questions])
        ).count()
        
        modules_dict[module_name]["completed"] += answered_in_page
    
    for module_name, data in modules_dict.items():
        modules_progress.append({
            "name": module_name,
            "completed": data["completed"],
            "total": data["total"],
            "status": "completed" if data["completed"] == data["total"] else "in_progress"
        })
    
    # Calculate XP and badges
    total_xp = answered_count * 10
    badges = []
    if answered_count >= 1:
        badges.append("first_answer")
    if answered_count >= 10:
        badges.append("streak_10")
    
    percentage = round((answered_count / total_questions * 100), 1) if total_questions > 0 else 0
    
    return {
        "session_id": session_id,
        "modules": modules_progress,
        "total_xp": total_xp,
        "badges": badges,
        "current_page_id": None,  # Could track this with additional logic
        "percentage_complete": percentage
    }


@router.get("/session/{session_id}/answered-questions")
async def get_answered_questions(
    session_id: str,
    page_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of answered question IDs for a session, optionally filtered by page.
    """
    student_response = response_service.get_student_response_by_session(db, session_id)
    if not student_response:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Base query for answered questions
    query = db.query(QuestionAnswer.question_id).filter(
        QuestionAnswer.response_id == student_response.id
    )
    
    # Filter by page if specified
    if page_id is not None:
        query = query.join(Question).filter(Question.page_id == page_id)
    
    answered_ids = [row[0] for row in query.all()]
    
    return {
        "session_id": session_id,
        "page_id": page_id,
        "answered_question_ids": answered_ids
    }


@router.post("/student/info")
async def submit_student_info(
    submission: StudentInfoSubmission,
    db: Session = Depends(get_db)
):
    """
    Submit student information, calculate scores, generate PDF, and send via email.
    Returns success/failure and appropriate message for frontend.
    """
    try:
        # 1. Get student response
        student_response = response_service.get_student_response_by_session(db, submission.session_id)
        if not student_response:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # 2. Update with student information
        student_response.email = submission.email
        student_response.full_name = submission.full_name
        student_response.age_group = submission.age_group
        student_response.country = submission.country
        student_response.origin_country = submission.origin_country
        db.commit()
        
        # 3. Mark as completed
        response_service.complete_student_response(db, submission.session_id)
        
        # 4. Calculate v1.1 profile
        profile = calculate_complete_profile_v1_1(db, student_response.id)
        if not profile:
            raise HTTPException(
                status_code=400,
                detail="Unable to calculate results. Please ensure all questions are answered."
            )
        
        # 5. Save assessment scores
        assessment_score = save_assessment_score_v1_1(db, student_response.id, profile)
        
        # 6. Check if email is enabled
        if not settings.ENABLE_EMAIL:
            logger.warning("Email delivery is disabled in settings")
            return {
                "success": True,
                "message": "Assessment completed successfully! (Email delivery disabled)",
                "email_sent": False
            }
        
        # 7. Generate PDF report
        logger.info(f"Generating PDF report for {submission.full_name}")
        response_dict = {
            'student_name': submission.full_name,
            'email': submission.email,
            'age_group': submission.age_group,
            'country': submission.country,
            'origin_country': submission.origin_country
        }
        
        # Parse JSON fields from assessment_score
        import json as json_lib
        
        scores_dict = {
            'riasec_raw_scores': json_lib.loads(assessment_score.riasec_raw_scores) if assessment_score.riasec_raw_scores else {},
            'riasec_strength_labels': json_lib.loads(assessment_score.riasec_strength_labels) if assessment_score.riasec_strength_labels else {},
            'holland_code': assessment_score.riasec_profile or '',
            'bigfive_raw_scores': {
                'O': assessment_score.bigfive_openness or 0,
                'C': assessment_score.bigfive_conscientiousness or 0,
                'E': assessment_score.bigfive_extraversion or 0,
                'A': assessment_score.bigfive_agreeableness or 0,
                'N': assessment_score.bigfive_neuroticism or 0
            },
            'bigfive_strength_labels': json_lib.loads(assessment_score.bigfive_strength_labels) if assessment_score.bigfive_strength_labels else {},
            'behavioral_strength_labels': json_lib.loads(assessment_score.behavioral_strength_labels) if assessment_score.behavioral_strength_labels else {},
            'behavioral_flags': json_lib.loads(assessment_score.behavioral_flags) if assessment_score.behavioral_flags else {},
            'ikigai_zones': json_lib.loads(assessment_score.ikigai_zones) if assessment_score.ikigai_zones else {}
        }
        
        # Extract behavioral raw scores from rhythm_profile
        if assessment_score.rhythm_profile:
            try:
                rhythm_profile = json_lib.loads(assessment_score.rhythm_profile)
                behavioral_raw_scores = rhythm_profile.get('behavioral', {}).get('raw_scores', {})
                scores_dict['behavioral_raw_scores'] = behavioral_raw_scores
            except:
                scores_dict['behavioral_raw_scores'] = {}
        
        pdf_buffer = generate_pdf_report(
            response_dict, 
            scores_dict,
            is_free_version=True,  # Generate free version with blurred premium sections
            checkout_url='https://carhythm.com/paid',
            discount_code='LAUNCH50'
        )
        
        # 8. Send email with PDF attachment
        logger.info(f"Sending results email to {submission.email}")
        
        # Get holland_code and top_strength from scores
        holland_code = scores_dict.get('holland_code', 'N/A')
        
        # Get top strength from Big Five
        bigfive_strength_labels = scores_dict.get('bigfive_strength_labels', {})
        if bigfive_strength_labels:
            # Find trait with highest score
            bigfive_raw = scores_dict.get('bigfive_raw_scores', {})
            top_trait = max(bigfive_raw.items(), key=lambda x: x[1])[0] if bigfive_raw else 'O'
            trait_names = {'O': 'Openness', 'C': 'Conscientiousness', 'E': 'Extraversion', 'A': 'Agreeableness', 'N': 'Neuroticism'}
            top_strength = f"{trait_names.get(top_trait, 'Openness')} ({bigfive_strength_labels.get(top_trait, 'High')})"
        else:
            top_strength = 'Openness'
        
        email_result = await send_results_email(
            to_email=submission.email,
            student_name=submission.full_name,
            holland_code=holland_code,
            top_strength=top_strength,
            pdf_buffer=pdf_buffer
        )
        
        if email_result['success']:
            logger.info(f"Email sent successfully to {submission.email}")
            return {
                "success": True,
                "message": f"Your results have been sent to {submission.email}. Please check your inbox!",
                "email_sent": True,
                "session_id": submission.session_id
            }
        else:
            # Email failed - notify admin and return error
            logger.error(f"Failed to send email to {submission.email}: {email_result.get('error', 'Unknown error')}")
            
            # Send admin notification
            try:
                await send_admin_notification(
                    student_name=submission.full_name,
                    student_email=submission.email,
                    session_id=submission.session_id,
                    error_message="Email delivery failed after retries"
                )
            except Exception as admin_error:
                logger.error(f"Failed to send admin notification: {admin_error}")
            
            return {
                "success": False,
                "message": "Assessment completed, but we couldn't send the email. Please contact support.",
                "email_sent": False,
                "session_id": submission.session_id
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in submit_student_info: {str(e)}", exc_info=True)
        
        # Try to notify admin
        try:
            if 'submission' in locals():
                await send_admin_notification(
                    student_name=submission.full_name if hasattr(submission, 'full_name') else 'Unknown',
                    student_email=submission.email if hasattr(submission, 'email') else 'Unknown',
                    session_id=submission.session_id if hasattr(submission, 'session_id') else 'Unknown',
                    error_message=str(e)
                )
        except:
            pass
        
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Our team has been notified."
        )


class ResendRequest(BaseModel):
    """Request to resend results email"""
    session_id: str
    new_email: Optional[EmailStr] = None


@router.post("/resend-results")
async def resend_results(
    request: ResendRequest,
    db: Session = Depends(get_db)
):
    """
    Resend assessment results to student email.
    Optionally update email address before resending.
    """
    try:
        # 1. Get student response
        student_response = response_service.get_student_response_by_session(db, request.session_id)
        if not student_response:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # 2. Check if assessment is completed
        if not student_response.completed:
            raise HTTPException(status_code=400, detail="Assessment not completed yet")
        
        # 3. Update email if provided
        target_email = request.new_email if request.new_email else student_response.email
        if request.new_email and request.new_email != student_response.email:
            logger.info(f"Updating email from {student_response.email} to {request.new_email}")
            student_response.email = request.new_email
            db.commit()
        
        # 4. Get assessment scores
        assessment_score = db.query(AssessmentScore).filter(
            AssessmentScore.response_id == student_response.id
        ).first()
        
        if not assessment_score:
            raise HTTPException(status_code=404, detail="Assessment scores not found")
        
        # 5. Check if email is enabled
        if not settings.ENABLE_EMAIL:
            return {
                "success": False,
                "message": "Email delivery is currently disabled"
            }
        
        # 6. Regenerate PDF
        logger.info(f"Regenerating PDF for session {request.session_id}")
        response_dict = {
            'student_name': student_response.full_name,
            'email': target_email,
            'age_group': student_response.age_group,
            'country': student_response.country,
            'origin_country': student_response.origin_country
        }
        
        scores_dict = {
            'riasec_scores_v1_1': assessment_score.riasec_scores_v1_1,
            'bigfive_scores_v1_1': assessment_score.bigfive_scores_v1_1,
            'behavioral_scores_v1_1': assessment_score.behavioral_scores_v1_1,
            'behavioral_flags_v1_1': assessment_score.behavioral_flags_v1_1,
            'holland_code_v1_1': assessment_score.holland_code_v1_1
        }
        
        pdf_buffer = generate_pdf_report(
            response_dict, 
            scores_dict,
            is_free_version=True,  # Generate free version with blurred premium sections
            checkout_url='https://carhythm.com/paid',
            discount_code='LAUNCH50'
        )
        
        # 7. Resend email
        logger.info(f"Resending results to {target_email}")
        email_success = await send_results_email(
            to_email=target_email,
            student_name=student_response.full_name,
            pdf_buffer=pdf_buffer,
            session_id=request.session_id
        )
        
        if email_success:
            return {
                "success": True,
                "message": f"Results resent successfully to {target_email}",
                "email": target_email
            }
        else:
            # Notify admin
            try:
                await send_admin_notification(
                    student_name=student_response.full_name,
                    student_email=target_email,
                    session_id=request.session_id,
                    error_message="Resend failed after retries"
                )
            except:
                pass
            
            return {
                "success": False,
                "message": "Failed to send email. Please try again or contact support."
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in resend_results: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while resending results"
        )


@router.get("/settings/theme")
async def get_theme_settings():
    """
    Get theme settings for frontend customization.
    For now, returns default CaRhythm branding.
    """
    return {
        "primary_color": "#6D3B8E",
        "secondary_color": "#FF6B6B",
        "accent_color": "#F9C74F",
        "welcome_message": "Your Career Story Begins Here",
        "welcome_subtitle": "Discover the rhythm of your professional journey",
        "thank_you_message": "You Found Your Rhythm!",
        "logo_url": "/static/img/logo.png",
        "brand_name": "CaRhythm"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for API v2"""
    return {"status": "healthy", "version": "2.0"}


@router.get("/scores/{session_id}")
async def get_rhythm_profile(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete CaRhythm v1.1 profile for a completed assessment.
    Returns RIASEC, Big Five, Behavioral scores with strength labels,
    behavioral flags, and Ikigai zones.
    """
    # Get student response
    student_response = response_service.get_student_response_by_session(db, session_id)
    if not student_response:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if already scored
    existing_score = db.query(AssessmentScore).filter(
        AssessmentScore.response_id == student_response.id
    ).first()
    
    if existing_score and existing_score.rhythm_profile:
        # Return existing profile
        profile = json.loads(existing_score.rhythm_profile)
        return {
            "session_id": session_id,
            "profile": profile,
            "cached": True
        }
    
    # Calculate new profile
    profile = calculate_complete_profile_v1_1(db, student_response.id)
    
    if not profile:
        raise HTTPException(
            status_code=400, 
            detail="Assessment incomplete. Please answer all questions."
        )
    
    # Save to database
    save_assessment_score_v1_1(db, student_response.id, profile)
    
    return {
        "session_id": session_id,
        "profile": profile,
        "cached": False
    }


@router.get("/scores/{session_id}/summary")
async def get_score_summary(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get simplified summary of scores for quick display.
    Returns top Holland Code, top Big Five traits, and key behavioral flags.
    """
    student_response = response_service.get_student_response_by_session(db, session_id)
    if not student_response:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get or calculate profile
    existing_score = db.query(AssessmentScore).filter(
        AssessmentScore.response_id == student_response.id
    ).first()
    
    if not existing_score or not existing_score.rhythm_profile:
        # Calculate if not exists
        profile = calculate_complete_profile_v1_1(db, student_response.id)
        if profile:
            save_assessment_score_v1_1(db, student_response.id, profile)
    else:
        profile = json.loads(existing_score.rhythm_profile)
    
    if not profile:
        raise HTTPException(status_code=400, detail="Assessment incomplete")
    
    # Extract summary
    summary = {
        "holland_code": profile['riasec']['holland_code'],
        "top_riasec_domains": [
            {"domain": k, "label": v} 
            for k, v in sorted(
                profile['riasec']['strength_labels'].items(), 
                key=lambda x: profile['riasec']['raw_scores'][x[0]], 
                reverse=True
            )[:3]
        ],
        "top_bigfive_traits": [
            {"trait": k, "label": v}
            for k, v in sorted(
                profile['bigfive']['strength_labels'].items(),
                key=lambda x: profile['bigfive']['raw_scores'][x[0]],
                reverse=True
            )[:3]
        ],
        "behavioral_flags": profile['behavioral']['behavioral_flags'],
        "ikigai_zones": {
            k: v['level'] 
            for k, v in profile['ikigai_zones'].items()
        }
    }
    
    return summary

