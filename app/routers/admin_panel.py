from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..models import get_db, QuestionType
from ..services import question_service, response_service
from ..services import scoring_service, pdf_service
from ..schemas import PageCreate, PageUpdate, QuestionCreate, QuestionUpdate
from ..utils.helpers import save_upload_file, validate_image_file, delete_file, format_datetime
from .admin import require_admin
from typing import Optional
import csv
import io

router = APIRouter(prefix="/admin", tags=["admin_panel"])
templates = Jinja2Templates(directory="app/templates")

# Page Management Routes

@router.get("/pages", response_class=HTMLResponse)
async def manage_pages(request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Page management interface."""
    pages = question_service.get_pages(db)
    return templates.TemplateResponse(
        "admin/pages.html", 
        {"request": request, "pages": pages, "admin": admin}
    )

@router.post("/pages")
async def create_page(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    order_index: int = Form(0),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Create a new page."""
    page_data = PageCreate(
        title=title,
        description=description if description else None,
        order_index=order_index
    )
    question_service.create_page(db, page_data)
    return RedirectResponse(url="/admin/pages", status_code=302)

@router.post("/pages/{page_id}/edit")
async def update_page(
    page_id: int,
    title: str = Form(...),
    description: str = Form(""),
    order_index: int = Form(...),
    is_active: bool = Form(False),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Update an existing page."""
    page_update = PageUpdate(
        title=title,
        description=description if description else None,
        order_index=order_index,
        is_active=is_active
    )
    question_service.update_page(db, page_id, page_update)
    return RedirectResponse(url="/admin/pages", status_code=302)

@router.post("/pages/{page_id}/delete")
async def delete_page(
    page_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Delete a page."""
    question_service.delete_page(db, page_id)
    return RedirectResponse(url="/admin/pages", status_code=302)

# Question Management Routes

@router.get("/questions", response_class=HTMLResponse)
async def manage_questions(
    request: Request,
    page_id: Optional[int] = None,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Question management interface."""
    pages = question_service.get_pages(db)
    questions = []
    selected_page = None
    
    if page_id:
        questions = question_service.get_questions_by_page(db, page_id)
        selected_page = question_service.get_page_by_id(db, page_id)
    
    return templates.TemplateResponse(
        "admin/questions.html", 
        {
            "request": request, 
            "pages": pages, 
            "questions": questions,
            "selected_page": selected_page,
            "admin": admin,
            "question_types": [qt.value for qt in QuestionType]
        }
    )

@router.post("/questions")
async def create_question(
    request: Request,
    page_id: int = Form(...),
    question_text: str = Form(...),
    question_type: str = Form(...),
    order_index: int = Form(0),
    is_required: bool = Form(False),
    slider_min_label: str = Form(""),
    slider_max_label: str = Form(""),
    essay_char_limit: Optional[int] = Form(None),
    # MCQ fields
    allow_multiple_selection: bool = Form(False),
    # Ordering fields  
    randomize_order: bool = Form(True),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Create a new question."""
    # Handle image upload
    image_path = None
    if image and image.filename:
        if validate_image_file(image):
            image_path = save_upload_file(image)
        else:
            raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Handle MCQ and ordering options from form data
    form_data = await request.form()
    mcq_options = None
    mcq_correct_answers = None
    ordering_options = None
    
    if question_type == "mcq":
        # Collect MCQ options
        options = form_data.getlist("mcq_option")
        correct_flags = form_data.getlist("mcq_correct")
        
        if len(options) < 2:
            raise HTTPException(status_code=400, detail="MCQ questions must have at least 2 options")
        
        mcq_options = [opt for opt in options if opt.strip()]
        mcq_correct_answers = []
        
        # Determine correct answers based on checkboxes
        for i, option in enumerate(mcq_options):
            if str(i) in correct_flags:
                mcq_correct_answers.append(i)
        
        if not mcq_correct_answers:
            raise HTTPException(status_code=400, detail="At least one correct answer must be selected for MCQ")
    
    elif question_type == "ordering":
        # Collect ordering options
        options = form_data.getlist("ordering_option")
        
        if len(options) < 2:
            raise HTTPException(status_code=400, detail="Ordering questions must have at least 2 items")
        
        ordering_options = [opt for opt in options if opt.strip()]
    
    # Create question
    question_data = QuestionCreate(
        page_id=page_id,
        question_text=question_text,
        question_type=QuestionType(question_type),
        order_index=order_index,
        is_required=is_required,
        slider_min_label=slider_min_label if slider_min_label else None,
        slider_max_label=slider_max_label if slider_max_label else None,
        essay_char_limit=essay_char_limit,
        mcq_options=mcq_options,
        mcq_correct_answer=mcq_correct_answers,
        allow_multiple_selection=allow_multiple_selection,
        ordering_options=ordering_options,
        randomize_order=randomize_order
    )
    
    question = question_service.create_question(db, question_data)
    
    # Update image path if uploaded
    if image_path:
        question_service.update_question_image(db, question.id, image_path)
    
    return RedirectResponse(url=f"/admin/questions?page_id={page_id}", status_code=302)

@router.post("/questions/{question_id}/edit")
async def update_question(
    question_id: int,
    question_text: str = Form(...),
    question_type: str = Form(...),
    order_index: int = Form(...),
    is_required: bool = Form(False),
    slider_min_label: str = Form(""),
    slider_max_label: str = Form(""),
    essay_char_limit: Optional[int] = Form(None),
    image: UploadFile = File(None),
    remove_image: bool = Form(False),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Update an existing question."""
    # Get current question
    current_question = question_service.get_question_by_id(db, question_id)
    if not current_question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Handle image updates
    new_image_path = current_question.image_path
    
    if remove_image:
        if current_question.image_path:
            delete_file(current_question.image_path)
        new_image_path = None
    elif image and image.filename:
        if validate_image_file(image):
            if current_question.image_path:
                delete_file(current_question.image_path)
            new_image_path = save_upload_file(image)
        else:
            raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Update question
    question_update = QuestionUpdate(
        question_text=question_text,
        question_type=QuestionType(question_type),
        order_index=order_index,
        is_required=is_required,
        slider_min_label=slider_min_label if slider_min_label else None,
        slider_max_label=slider_max_label if slider_max_label else None,
        essay_char_limit=essay_char_limit
    )
    
    question_service.update_question(db, question_id, question_update)
    
    # Update image path
    question_service.update_question_image(db, question_id, new_image_path)
    
    return RedirectResponse(url=f"/admin/questions?page_id={current_question.page_id}", status_code=302)

@router.post("/questions/{question_id}/delete")
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Delete a question."""
    # Get question to find page_id for redirect
    question = question_service.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    page_id = question.page_id
    
    # Delete image file if exists
    if question.image_path:
        delete_file(question.image_path)
    
    # Delete question
    question_service.delete_question(db, question_id)
    
    return RedirectResponse(url=f"/admin/questions?page_id={page_id}", status_code=302)

# Results Management Routes

@router.get("/results", response_class=HTMLResponse)
async def view_results(
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """View all student responses and results."""
    responses = response_service.get_all_responses(db)
    statistics = response_service.get_response_statistics(db)
    
    return templates.TemplateResponse(
        "admin/results.html",
        {
            "request": request,
            "responses": responses,
            "statistics": statistics,
            "admin": admin,
            "format_datetime": format_datetime
        }
    )

@router.get("/results/{response_id}", response_class=HTMLResponse)
async def view_response_detail(
    response_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """View detailed response with all answers and calculated scores."""
    response = response_service.get_response_with_answers(db, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    # Get questions with answers
    answers_by_question = {}
    for answer in response.answers:
        question = question_service.get_question_by_id(db, answer.question_id)
        answers_by_question[question.id] = {
            'question': question,
            'answer': answer
        }
    
    # Get or calculate scores
    scores = scoring_service.get_scores_for_response(db, response_id)
    
    return templates.TemplateResponse(
        "admin/response_detail.html",
        {
            "request": request,
            "response": response,
            "answers_by_question": answers_by_question,
            "scores": scores,
            "admin": admin,
            "format_datetime": format_datetime
        }
    )

@router.post("/results/{response_id}/delete")
async def delete_response(
    response_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Delete a student response."""
    response_service.delete_student_response(db, response_id)
    return RedirectResponse(url="/admin/results", status_code=302)


@router.post("/results/{response_id}/calculate-scores")
async def calculate_response_scores(
    response_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Calculate and save scores for a specific response."""
    try:
        scores = scoring_service.calculate_and_save_scores(db, response_id)
        return JSONResponse(content={
            "success": True,
            "message": "Scores calculated successfully",
            "scores_id": scores.id
        })
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@router.get("/results/export/csv")
async def export_results_csv(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Export all results with scores to CSV."""
    responses = response_service.get_all_responses(db)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Response ID', 'Session ID', 'Name', 'Email', 'Age Group', 'Country', 'Origin Country',
        'Started At', 'Completed At', 'Status',
        # RIASEC scores
        'RIASEC R', 'RIASEC I', 'RIASEC A', 'RIASEC S', 'RIASEC E', 'RIASEC C', 'RIASEC Profile',
        # Big Five scores
        'Big5 Openness', 'Big5 Conscientiousness', 'Big5 Extraversion', 'Big5 Agreeableness', 'Big5 Neuroticism',
        # Work Rhythm scores
        'WR Motivation', 'WR Grit', 'WR Self-Efficacy', 'WR Resilience', 'WR Learning', 'WR Empathy', 'WR Procrastination',
        'Scores Calculated At'
    ])
    
    # Write data rows
    for response in responses:
        scores = scoring_service.get_scores_for_response(db, response.id)
        
        status = "Complete" if response.completed_at else "In Progress"
        
        row = [
            response.id,
            response.session_id,
            response.full_name,
            response.email,
            response.age_group,
            response.country,
            response.origin_country,
            response.created_at.strftime('%Y-%m-%d %H:%M:%S') if response.created_at else '',
            response.completed_at.strftime('%Y-%m-%d %H:%M:%S') if response.completed_at else '',
            status
        ]
        
        # Add scores if available
        if scores:
            row.extend([
                scores.riasec_r_score or '',
                scores.riasec_i_score or '',
                scores.riasec_a_score or '',
                scores.riasec_s_score or '',
                scores.riasec_e_score or '',
                scores.riasec_c_score or '',
                scores.riasec_profile or '',
                scores.bigfive_openness or '',
                scores.bigfive_conscientiousness or '',
                scores.bigfive_extraversion or '',
                scores.bigfive_agreeableness or '',
                scores.bigfive_neuroticism or '',
                scores.workrhythm_motivation or '',
                scores.workrhythm_grit or '',
                scores.workrhythm_self_efficacy or '',
                scores.workrhythm_resilience or '',
                scores.workrhythm_learning or '',
                scores.workrhythm_empathy or '',
                scores.workrhythm_procrastination or '',
                scores.calculated_at.strftime('%Y-%m-%d %H:%M:%S') if scores.calculated_at else ''
            ])
        else:
            row.extend([''] * 21)  # Empty columns for scores
        
        writer.writerow(row)
    
    # Prepare response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=carhythm_results_export.csv"}
    )


@router.get("/results/{response_id}/export/pdf")
async def export_response_pdf(
    response_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Export individual response as PDF report with scores and visualizations."""
    response = response_service.get_response_with_answers(db, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    # Get scores (calculate if not exists)
    scores = scoring_service.get_scores_for_response(db, response_id)
    if not scores:
        # Calculate scores if they don't exist
        scores = scoring_service.calculate_and_save_scores(db, response_id)
    
    if not scores:
        raise HTTPException(status_code=400, detail="Unable to calculate scores for this response")
    
    # Generate PDF
    try:
        pdf_buffer = pdf_service.generate_pdf_report(response, scores)
        
        # Create safe filename
        safe_name = "".join(c for c in response.full_name if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"CaRhythm_Report_{safe_name}_{response.id}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")