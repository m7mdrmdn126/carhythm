from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..models import get_db
from ..services import question_service, response_service
from ..schemas import StudentResponseCreate, QuestionAnswerCreate, SubmitAnswer
from ..utils.helpers import generate_session_id
from typing import Optional, List
import json

router = APIRouter(tags=["examination"])
templates = Jinja2Templates(directory="app/templates")

def get_session_id(request: Request) -> str:
    """Get or create session ID."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = generate_session_id()
    return session_id

@router.get("/", response_class=HTMLResponse)
async def redirect_to_welcome():
    """Redirect root to welcome page."""
    return RedirectResponse(url="/student/welcome")

@router.get("/student/welcome", response_class=HTMLResponse)
async def welcome_page(request: Request):
    """Student welcome page."""
    return templates.TemplateResponse("student/welcome.html", {"request": request})

@router.get("/paid", response_class=HTMLResponse)
async def premium_landing_page(
    request: Request,
    discount: Optional[str] = None,
    utm_source: Optional[str] = None,
    utm_medium: Optional[str] = None,
    utm_content: Optional[str] = None
):
    """
    Premium report landing page with discount handling.
    
    Query params:
        - discount: Discount code (e.g., LAUNCH50 for 50% off)
        - utm_source: UTM source tracking
        - utm_medium: UTM medium tracking
        - utm_content: UTM content tracking (section name)
    """
    # Discount validation
    valid_discounts = {
        "LAUNCH50": {"amount": 50, "label": "50% LAUNCH DISCOUNT"},
        "EARLY30": {"amount": 30, "label": "30% EARLY BIRD"},
        "STUDENT20": {"amount": 20, "label": "20% STUDENT DISCOUNT"}
    }
    
    discount_info = None
    if discount and discount.upper() in valid_discounts:
        discount_info = valid_discounts[discount.upper()]
    
    # Default pricing
    original_price = 49.99
    discounted_price = original_price
    
    if discount_info:
        discount_percent = discount_info["amount"]
        discounted_price = original_price * (1 - discount_percent / 100)
    
    return templates.TemplateResponse(
        "student/premium_landing.html",
        {
            "request": request,
            "discount_code": discount,
            "discount_info": discount_info,
            "original_price": f"${original_price:.2f}",
            "discounted_price": f"${discounted_price:.2f}",
            "savings": f"${original_price - discounted_price:.2f}",
            "utm_source": utm_source,
            "utm_medium": utm_medium,
            "utm_content": utm_content
        }
    )

@router.get("/student/exam", response_class=HTMLResponse)
async def start_examination(
    request: Request,
    db: Session = Depends(get_db)
):
    """Start the examination."""
    # Get all active pages
    pages = question_service.get_pages(db, active_only=True)
    if not pages:
        return templates.TemplateResponse(
            "student/welcome.html", 
            {"request": request, "error": "No examination pages available"}
        )
    
    session_id = get_session_id(request)
    
    # Start with first page
    current_page = 0
    page = pages[current_page]
    questions = question_service.get_questions_by_page(db, page.id)
    
    # Get existing answers for this session (if any)
    student_response = response_service.get_student_response_by_session(db, session_id)
    existing_answers = {}
    if student_response:
        answers = response_service.get_answers_by_response(db, student_response.id)
        for answer in answers:
            existing_answers[answer.question_id] = {
                'text': answer.answer_text,
                'value': answer.answer_value,
                'json': answer.answer_json
            }
    
    response = templates.TemplateResponse(
        "student/examination.html",
        {
            "request": request,
            "page": page,
            "questions": questions,
            "current_page": current_page,
            "total_pages": len(pages),
            "session_id": session_id,
            "is_first_page": current_page == 0,
            "is_last_page": current_page == len(pages) - 1,
            "existing_answers": existing_answers
        }
    )
    
    # Set session cookie
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response

@router.get("/student/exam/page/{page_number}", response_class=HTMLResponse)
async def get_exam_page(
    page_number: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a specific examination page."""
    pages = question_service.get_pages(db, active_only=True)
    
    if page_number < 0 or page_number >= len(pages):
        raise HTTPException(status_code=404, detail="Page not found")
    
    session_id = get_session_id(request)
    
    page = pages[page_number]
    questions = question_service.get_questions_by_page(db, page.id)
    
    # Get existing answers for this session
    student_response = response_service.get_student_response_by_session(db, session_id)
    existing_answers = {}
    if student_response:
        answers = response_service.get_answers_by_response(db, student_response.id)
        for answer in answers:
            existing_answers[answer.question_id] = {
                'text': answer.answer_text,
                'value': answer.answer_value,
                'json': answer.answer_json
            }
    
    return templates.TemplateResponse(
        "student/examination.html",
        {
            "request": request,
            "page": page,
            "questions": questions,
            "current_page": page_number,
            "total_pages": len(pages),
            "session_id": session_id,
            "is_first_page": page_number == 0,
            "is_last_page": page_number == len(pages) - 1,
            "existing_answers": existing_answers
        }
    )

@router.post("/student/exam/submit-answers")
async def submit_answers(
    request: Request,
    db: Session = Depends(get_db)
):
    """Submit answers for the current page."""
    form = await request.form()
    session_id = form.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    # Get or create student response record
    student_response = response_service.get_student_response_by_session(db, session_id)
    if not student_response:
        # Create temporary response (will be completed when student info is submitted)
        temp_response = StudentResponseCreate(
            session_id=session_id,
            email="temp@temp.com",
            full_name="Temporary",
            age_group="temp",
            country="temp",
            origin_country="temp"
        )
        student_response = response_service.create_student_response(db, temp_response)
    
    # Process answers
    processed_questions = set()
    
    for key, value in form.items():
        if key.startswith("question_"):
            parts = key.split("_")
            question_id = int(parts[1])
            
            # Skip if already processed this question
            if question_id in processed_questions:
                continue
            
            # Get question to determine type
            question = question_service.get_question_by_id(db, question_id)
            if not question:
                continue
                
            answer_data = None
            
            if question.question_type == "essay":
                # Essay question
                text_key = f"question_{question_id}_text"
                if text_key in form:
                    answer_data = QuestionAnswerCreate(
                        response_id=student_response.id,
                        question_id=question_id,
                        answer_text=form[text_key],
                        answer_value=None,
                        answer_json=None
                    )
            
            elif question.question_type == "slider":
                # Slider question
                slider_key = f"question_{question_id}_slider"
                if slider_key in form:
                    answer_data = QuestionAnswerCreate(
                        response_id=student_response.id,
                        question_id=question_id,
                        answer_text=None,
                        answer_value=float(form[slider_key]),
                        answer_json=None
                    )
            
            elif question.question_type == "mcq":
                # MCQ question - collect selected options
                selected_options = form.getlist(f"question_{question_id}_mcq")
                if selected_options:
                    mcq_answer = {
                        "selected_options": [int(opt) for opt in selected_options],
                        "question_type": "mcq"
                    }
                    answer_data = QuestionAnswerCreate(
                        response_id=student_response.id,
                        question_id=question_id,
                        answer_text=None,
                        answer_value=None,
                        answer_json=json.dumps(mcq_answer)
                    )
            
            elif question.question_type == "ordering":
                # Ordering question - get the ordered list
                ordering_key = f"question_{question_id}_ordering"
                if ordering_key in form:
                    try:
                        ordered_items = json.loads(form[ordering_key])
                        ordering_answer = {
                            "ordered_items": ordered_items,
                            "question_type": "ordering"
                        }
                        answer_data = QuestionAnswerCreate(
                            response_id=student_response.id,
                            question_id=question_id,
                            answer_text=None,
                            answer_value=None,
                            answer_json=json.dumps(ordering_answer)
                        )
                    except json.JSONDecodeError:
                        continue
            
            # Create or update the answer
            if answer_data:
                response_service.create_question_answer(db, answer_data)
                processed_questions.add(question_id)
    
    return JSONResponse({"status": "success"})

@router.get("/student/info", response_class=HTMLResponse)
async def student_info_page(request: Request):
    """Student information collection page."""
    session_id = get_session_id(request)
    return templates.TemplateResponse(
        "student/student_info.html", 
        {"request": request, "session_id": session_id}
    )

@router.post("/student/info")
async def submit_student_info(
    request: Request,
    session_id: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    age_group: str = Form(...),
    country: str = Form(...),
    origin_country: str = Form(...),
    db: Session = Depends(get_db)
):
    """Submit student information and complete the examination."""
    # Update student response with real information
    student_response = response_service.get_student_response_by_session(db, session_id)
    
    if not student_response:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update with actual student information
    student_response.email = email
    student_response.full_name = full_name
    student_response.age_group = age_group
    student_response.country = country
    student_response.origin_country = origin_country
    
    db.commit()
    
    # Mark as completed
    response_service.complete_student_response(db, session_id)
    
    response = RedirectResponse(url="/student/completion", status_code=302)
    response.delete_cookie("session_id")
    return response

@router.get("/student/completion", response_class=HTMLResponse)
async def completion_page(request: Request):
    """Examination completion page."""
    return templates.TemplateResponse("student/completion.html", {"request": request})

# API endpoint for AJAX requests
@router.post("/api/submit-answer")
async def submit_single_answer(
    answer: SubmitAnswer,
    session_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Submit a single answer via API."""
    # Get or create student response
    student_response = response_service.get_student_response_by_session(db, session_id)
    if not student_response:
        temp_response = StudentResponseCreate(
            session_id=session_id,
            email="temp@temp.com",
            full_name="Temporary",
            age_group="temp",
            country="temp",
            origin_country="temp"
        )
        student_response = response_service.create_student_response(db, temp_response)
    
    # Create answer
    answer_data = QuestionAnswerCreate(
        response_id=student_response.id,
        question_id=answer.question_id,
        answer_text=answer.answer_text,
        answer_value=answer.answer_value
    )
    
    response_service.create_question_answer(db, answer_data)
    return {"status": "success"}