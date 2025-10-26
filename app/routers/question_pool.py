from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..models import get_db, QuestionPageAssignment
from ..services.question_pool_service import QuestionPoolService
from ..services.csv_import_service import CSVImportExportService
from ..schemas.question_pool import (
    CategoryCreate, CategoryUpdate, QuestionPoolCreate, QuestionPoolUpdate, 
    QuestionPageAssignmentCreate, QuestionPoolFilter
)
from .admin import require_admin
from typing import Optional, List
import io

router = APIRouter(prefix="/admin", tags=["question_pool"])
templates = Jinja2Templates(directory="app/templates")

# Question Pool Management Routes

@router.get("/question-pool", response_class=HTMLResponse)
async def question_pool_dashboard(
    request: Request,
    category_id: Optional[int] = None,
    question_type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Question pool management dashboard."""
    # Get filters
    filters = QuestionPoolFilter(
        category_id=category_id,
        question_type=question_type,
        search_text=search,
        skip=(page - 1) * 20,
        limit=20
    )
    
    # Get data
    questions = QuestionPoolService.get_questions_pool(db, filters)
    categories = QuestionPoolService.get_categories(db)
    stats = QuestionPoolService.get_pool_statistics(db)
    
    # Serialize questions for template
    serialized_questions = []
    for question in questions:
        question_dict = QuestionPoolService.serialize_question_for_response(question)
        question_dict['category'] = question.category
        serialized_questions.append(question_dict)
    
    return templates.TemplateResponse(
        "admin/question_pool.html",
        {
            "request": request,
            "admin": admin,
            "questions": serialized_questions,
            "categories": categories,
            "stats": stats,
            "current_filters": {
                "category_id": category_id,
                "question_type": question_type,
                "search": search,
                "page": page
            },
            "question_types": ["essay", "slider", "mcq", "ordering"]
        }
    )

# Category Management

@router.get("/categories", response_class=HTMLResponse)
async def manage_categories(
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Category management interface."""
    categories = QuestionPoolService.get_categories(db, active_only=False)
    return templates.TemplateResponse(
        "admin/categories.html",
        {"request": request, "admin": admin, "categories": categories}
    )

@router.post("/categories")
async def create_category(
    name: str = Form(...),
    description: str = Form(""),
    color: str = Form("#3498db"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Create a new category."""
    try:
        category_data = CategoryCreate(
            name=name,
            description=description if description else None,
            color=color
        )
        QuestionPoolService.create_category(db, category_data)
        return RedirectResponse(url="/admin/categories", status_code=302)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/categories/{category_id}/edit")
async def update_category(
    category_id: int,
    name: str = Form(...),
    description: str = Form(""),
    color: str = Form(...),
    is_active: Optional[str] = Form(None),  # HTML checkbox sends string or None
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Update a category."""
    category_update = CategoryUpdate(
        name=name,
        description=description if description else None,
        color=color,
        is_active=is_active == "on"  # Convert HTML checkbox to boolean
    )
    updated_category = QuestionPoolService.update_category(db, category_id, category_update)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return RedirectResponse(url="/admin/categories", status_code=302)

@router.post("/categories/{category_id}/delete")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Delete a category."""
    success = QuestionPoolService.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return RedirectResponse(url="/admin/categories", status_code=302)

# Question Pool CRUD

@router.post("/question-pool/create")
async def create_question_pool(
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Create a new question in the pool."""
    form = await request.form()
    
    # Parse form data based on question type
    question_type = form.get("question_type")
    
    # Basic fields
    question_data = {
        "title": form.get("title"),
        "question_text": form.get("question_text"),
        "question_type": question_type,
        "category_id": int(form.get("category_id")) if form.get("category_id") else None,
        "is_required": form.get("is_required") == "on",
        "created_by": admin.username
    }
    
    # Type-specific fields
    if question_type == "essay":
        char_limit = form.get("essay_char_limit")
        question_data["essay_char_limit"] = int(char_limit) if char_limit else None
    
    elif question_type == "slider":
        question_data["slider_min_label"] = form.get("slider_min_label") or None
        question_data["slider_max_label"] = form.get("slider_max_label") or None
    
    elif question_type == "mcq":
        options = form.getlist("mcq_option")
        correct_flags = form.getlist("mcq_correct")
        
        if len(options) < 2:
            raise HTTPException(status_code=400, detail="MCQ questions must have at least 2 options")
        
        mcq_options = [opt for opt in options if opt.strip()]
        mcq_correct = []
        
        for i, option in enumerate(mcq_options):
            if str(i) in correct_flags:
                mcq_correct.append(i)
        
        if not mcq_correct:
            raise HTTPException(status_code=400, detail="At least one correct answer must be selected")
        
        question_data["mcq_options"] = mcq_options
        question_data["mcq_correct_answer"] = mcq_correct
        question_data["allow_multiple_selection"] = form.get("allow_multiple_selection") == "on"
    
    elif question_type == "ordering":
        items = form.getlist("ordering_option")
        
        if len(items) < 2:
            raise HTTPException(status_code=400, detail="Ordering questions must have at least 2 items")
        
        ordering_options = [item for item in items if item.strip()]
        question_data["ordering_options"] = ordering_options
        question_data["randomize_order"] = form.get("randomize_order") == "on"
    
    # Create question
    question_create = QuestionPoolCreate(**question_data)
    QuestionPoolService.create_question_pool(db, question_create)
    
    return RedirectResponse(url="/admin/question-pool", status_code=302)

@router.post("/question-pool/{question_id}/delete")
async def delete_question_pool(
    question_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Delete a question from the pool."""
    success = QuestionPoolService.delete_question_pool(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return RedirectResponse(url="/admin/question-pool", status_code=302)

# CSV Import/Export Routes

@router.get("/csv-templates/{question_type}")
async def download_csv_template(question_type: str, admin=Depends(require_admin)):
    """Download CSV template for a specific question type."""
    if question_type not in ["essay", "slider", "mcq", "ordering"]:
        raise HTTPException(status_code=400, detail="Invalid question type")
    
    template_path = f"app/templates/csv_templates/{question_type}_template.csv"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create streaming response
        def generate():
            yield content
        
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={question_type}_template.csv"}
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Template not found")

@router.post("/csv-import/{question_type}")
async def import_csv_questions(
    question_type: str,
    csv_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Import questions from CSV file."""
    if question_type not in ["essay", "slider", "mcq", "ordering"]:
        raise HTTPException(status_code=400, detail="Invalid question type")
    
    if not csv_file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read CSV content
        content = await csv_file.read()
        csv_content = content.decode('utf-8')
        
        # Import questions
        result = CSVImportExportService.validate_and_import_csv(
            db=db,
            csv_content=csv_content,
            question_type=question_type,
            filename=csv_file.filename,
            imported_by=admin.username
        )
        
        # Return result as JSON for AJAX handling
        return JSONResponse(content={
            "success": True,
            "total_rows": result.total_rows,
            "successful_imports": result.successful_imports,
            "failed_imports": result.failed_imports,
            "errors": result.errors
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )

@router.post("/csv-export")
async def export_questions_csv(
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Export selected questions to CSV."""
    form = await request.form()
    
    question_ids = form.getlist("question_ids")
    question_type = form.get("question_type")
    
    if not question_ids:
        raise HTTPException(status_code=400, detail="No questions selected")
    
    if not question_type:
        raise HTTPException(status_code=400, detail="Question type is required")
    
    try:
        question_ids = [int(qid) for qid in question_ids]
        csv_content = CSVImportExportService.export_questions_to_csv(
            db=db,
            question_ids=question_ids,
            question_type=question_type
        )
        
        return StreamingResponse(
            io.BytesIO(csv_content.encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=questions_{question_type}.csv"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Page Assignment Routes

@router.get("/pages/{page_id}/assign-questions", response_class=HTMLResponse)
async def page_question_assignment(
    page_id: int,
    request: Request,
    category_id: Optional[str] = None,
    question_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Interface for assigning questions to a page."""
    from ..services.question_service import get_page_by_id
    
    page = get_page_by_id(db, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Convert and validate parameters
    parsed_category_id = None
    if category_id and category_id.strip():
        try:
            parsed_category_id = int(category_id)
        except ValueError:
            pass  # Invalid category_id, ignore it
    
    parsed_question_type = None
    if question_type and question_type.strip() and question_type != "all":
        parsed_question_type = question_type
    
    parsed_search = None
    if search and search.strip():
        parsed_search = search
    
    # Get available questions
    filters = QuestionPoolFilter(
        category_id=parsed_category_id,
        question_type=parsed_question_type,
        search_text=parsed_search,
        limit=100
    )
    
    # Debug print to see what filters are being applied
    print(f"DEBUG: Filters - category_id: {parsed_category_id}, question_type: {parsed_question_type}, search: {parsed_search}")
    
    available_questions = QuestionPoolService.get_questions_pool(db, filters)
    assigned_questions = QuestionPoolService.get_page_assigned_questions(db, page_id)
    categories = QuestionPoolService.get_categories(db)
    
    # Serialize questions
    serialized_available = []
    for question in available_questions:
        question_dict = QuestionPoolService.serialize_question_for_response(question)
        question_dict['category'] = question.category
        # Check if already assigned
        question_dict['is_assigned'] = any(
            assign.question_pool_id == question.id for assign in assigned_questions
        )
        serialized_available.append(question_dict)
    
    # Serialize assigned questions
    serialized_assigned = []
    for assignment in assigned_questions:
        question_dict = QuestionPoolService.serialize_question_for_response(assignment.question)
        question_dict['category'] = assignment.question.category
        question_dict['assignment_id'] = assignment.id
        question_dict['order_index'] = assignment.order_index
        serialized_assigned.append(question_dict)
    
    return templates.TemplateResponse(
        "admin/page_question_assignment.html",
        {
            "request": request,
            "admin": admin,
            "page": page,
            "available_questions": serialized_available,
            "assigned_questions": sorted(serialized_assigned, key=lambda x: x['order_index']),
            "categories": categories,
            "current_filters": {
                "category_id": parsed_category_id,
                "question_type": parsed_question_type, 
                "search": parsed_search
            },
            "question_types": ["essay", "slider", "mcq", "ordering"]
        }
    )

@router.post("/pages/{page_id}/assign-question")
async def assign_question_to_page(
    page_id: int,
    question_pool_id: int = Form(...),
    order_index: int = Form(0),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Assign a question from pool to a page."""
    assignment = QuestionPageAssignmentCreate(
        question_pool_id=question_pool_id,
        page_id=page_id,
        order_index=order_index,
        assigned_by=admin.username
    )
    
    QuestionPoolService.assign_question_to_page(db, assignment)
    return RedirectResponse(url=f"/admin/pages/{page_id}/assign-questions", status_code=302)

@router.post("/pages/{page_id}/unassign-question")
async def unassign_question_from_page(
    page_id: int,
    question_pool_id: int = Form(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Remove a question assignment from a page."""
    success = QuestionPoolService.unassign_question_from_page(db, question_pool_id, page_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    return RedirectResponse(url=f"/admin/pages/{page_id}/assign-questions", status_code=302)

@router.post("/update-question-order")
async def update_question_order(
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Update the order of assigned questions."""
    data = await request.json()
    updates = data.get("updates", [])
    
    for update in updates:
        assignment = db.query(QuestionPageAssignment).filter(
            QuestionPageAssignment.question_pool_id == update["question_id"]
        ).first()
        
        if assignment:
            assignment.order_index = update["order_index"]
    
    db.commit()
    return JSONResponse({"success": True})