from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from ..models import Category, QuestionPool, QuestionPageAssignment, ImportLog, Page
from ..schemas.question_pool import (
    CategoryCreate, CategoryUpdate, QuestionPoolCreate, QuestionPoolUpdate,
    QuestionPageAssignmentCreate, QuestionPoolFilter, CSVImportResult
)
from typing import List, Optional, Dict, Any
import json
import csv
import io
from datetime import datetime

class QuestionPoolService:
    
    # Category Management
    @staticmethod
    def create_category(db: Session, category: CategoryCreate) -> Category:
        """Create a new category."""
        db_category = Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    def get_categories(db: Session, active_only: bool = True) -> List[Category]:
        """Get all categories."""
        query = db.query(Category).order_by(Category.name)
        if active_only:
            query = query.filter(Category.is_active == True)
        return query.all()
    
    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        return db.query(Category).filter(Category.id == category_id).first()
    
    @staticmethod
    def update_category(db: Session, category_id: int, category_update: CategoryUpdate) -> Optional[Category]:
        """Update a category."""
        db_category = db.query(Category).filter(Category.id == category_id).first()
        if not db_category:
            return None
        
        update_data = category_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        """Delete a category (sets questions to no category)."""
        db_category = db.query(Category).filter(Category.id == category_id).first()
        if not db_category:
            return False
        
        # Set questions in this category to no category
        db.query(QuestionPool).filter(QuestionPool.category_id == category_id).update({
            QuestionPool.category_id: None
        })
        
        db.delete(db_category)
        db.commit()
        return True
    
    # Question Pool Management
    @staticmethod
    def create_question_pool(db: Session, question: QuestionPoolCreate) -> QuestionPool:
        """Create a new question in the pool."""
        question_data = question.dict()
        
        # Convert list fields to JSON strings for database storage
        if question_data.get('mcq_options'):
            question_data['mcq_options'] = json.dumps(question_data['mcq_options'])
        if question_data.get('mcq_correct_answer'):
            question_data['mcq_correct_answer'] = json.dumps(question_data['mcq_correct_answer'])
        if question_data.get('ordering_options'):
            question_data['ordering_options'] = json.dumps(question_data['ordering_options'])
        if question_data.get('mcq_options_ar'):
            question_data['mcq_options_ar'] = json.dumps(question_data['mcq_options_ar'])
        if question_data.get('ordering_options_ar'):
            question_data['ordering_options_ar'] = json.dumps(question_data['ordering_options_ar'])
        
        db_question = QuestionPool(**question_data)
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question
    
    @staticmethod
    def get_questions_pool(db: Session, filters: QuestionPoolFilter) -> List[QuestionPool]:
        """Get questions from pool with filtering."""
        query = db.query(QuestionPool).join(Category, isouter=True)
        
        # Apply filters
        if filters.category_id:
            query = query.filter(QuestionPool.category_id == filters.category_id)
        
        if filters.question_type:
            query = query.filter(QuestionPool.question_type == filters.question_type)
        
        if filters.search_text:
            search = f"%{filters.search_text}%"
            query = query.filter(or_(
                QuestionPool.title.ilike(search),
                QuestionPool.question_text.ilike(search)
            ))
        
        if filters.created_by:
            query = query.filter(QuestionPool.created_by == filters.created_by)
        
        if filters.usage_min is not None:
            query = query.filter(QuestionPool.usage_count >= filters.usage_min)
        
        if filters.usage_max is not None:
            query = query.filter(QuestionPool.usage_count <= filters.usage_max)
        
        # Order by updated_at desc
        query = query.order_by(QuestionPool.updated_at.desc())
        
        return query.offset(filters.skip).limit(filters.limit).all()
    
    @staticmethod
    def get_question_pool_by_id(db: Session, question_id: int) -> Optional[QuestionPool]:
        """Get question from pool by ID."""
        return db.query(QuestionPool).filter(QuestionPool.id == question_id).first()
    
    @staticmethod
    def update_question_pool(db: Session, question_id: int, question_update: QuestionPoolUpdate) -> Optional[QuestionPool]:
        """Update a question in the pool."""
        db_question = db.query(QuestionPool).filter(QuestionPool.id == question_id).first()
        if not db_question:
            return None
        
        update_data = question_update.dict(exclude_unset=True)
        
        # Convert list fields to JSON strings for database storage
        if 'mcq_options' in update_data and update_data['mcq_options'] is not None:
            update_data['mcq_options'] = json.dumps(update_data['mcq_options'])
        if 'mcq_correct_answer' in update_data and update_data['mcq_correct_answer'] is not None:
            update_data['mcq_correct_answer'] = json.dumps(update_data['mcq_correct_answer'])
        if 'ordering_options' in update_data and update_data['ordering_options'] is not None:
            update_data['ordering_options'] = json.dumps(update_data['ordering_options'])
        
        for field, value in update_data.items():
            setattr(db_question, field, value)
        
        # Update timestamp
        db_question.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_question)
        return db_question
    
    @staticmethod
    def delete_question_pool(db: Session, question_id: int) -> bool:
        """Delete a question from the pool."""
        db_question = db.query(QuestionPool).filter(QuestionPool.id == question_id).first()
        if not db_question:
            return False
        
        # Delete all assignments first
        db.query(QuestionPageAssignment).filter(
            QuestionPageAssignment.question_pool_id == question_id
        ).delete()
        
        db.delete(db_question)
        db.commit()
        return True
    
    # Assignment Management
    @staticmethod
    def assign_question_to_page(db: Session, assignment: QuestionPageAssignmentCreate) -> QuestionPageAssignment:
        """Assign a question from pool to a page."""
        # Check if already assigned
        existing = db.query(QuestionPageAssignment).filter(
            and_(
                QuestionPageAssignment.question_pool_id == assignment.question_pool_id,
                QuestionPageAssignment.page_id == assignment.page_id
            )
        ).first()
        
        if existing:
            # Update order if different
            if existing.order_index != assignment.order_index:
                existing.order_index = assignment.order_index
                db.commit()
                db.refresh(existing)
            return existing
        
        # Create new assignment
        db_assignment = QuestionPageAssignment(**assignment.dict())
        db.add(db_assignment)
        
        # Update usage count
        db_question = db.query(QuestionPool).filter(
            QuestionPool.id == assignment.question_pool_id
        ).first()
        if db_question:
            if db_question.usage_count is None:
                db_question.usage_count = 1
            else:
                db_question.usage_count += 1
        
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    
    @staticmethod
    def unassign_question_from_page(db: Session, question_pool_id: int, page_id: int) -> bool:
        """Remove a question assignment from a page."""
        assignment = db.query(QuestionPageAssignment).filter(
            and_(
                QuestionPageAssignment.question_pool_id == question_pool_id,
                QuestionPageAssignment.page_id == page_id
            )
        ).first()
        
        if not assignment:
            return False
        
        # Decrease usage count
        db_question = db.query(QuestionPool).filter(
            QuestionPool.id == question_pool_id
        ).first()
        if db_question:
            if db_question.usage_count is None:
                db_question.usage_count = 0
            elif db_question.usage_count > 0:
                db_question.usage_count -= 1
        
        db.delete(assignment)
        db.commit()
        return True
    
    @staticmethod
    def get_page_assigned_questions(db: Session, page_id: int) -> List[QuestionPageAssignment]:
        """Get all questions assigned to a page."""
        return db.query(QuestionPageAssignment).filter(
            QuestionPageAssignment.page_id == page_id
        ).order_by(QuestionPageAssignment.order_index).all()
    
    @staticmethod
    def get_question_assignments(db: Session, question_pool_id: int) -> List[QuestionPageAssignment]:
        """Get all page assignments for a question."""
        return db.query(QuestionPageAssignment).filter(
            QuestionPageAssignment.question_pool_id == question_pool_id
        ).all()
    
    # Statistics and Analytics
    @staticmethod
    def get_pool_statistics(db: Session) -> Dict[str, Any]:
        """Get question pool statistics."""
        total_questions = db.query(func.count(QuestionPool.id)).scalar()
        
        # Questions by type
        type_stats = db.query(
            QuestionPool.question_type,
            func.count(QuestionPool.id)
        ).group_by(QuestionPool.question_type).all()
        
        # Questions by category
        category_stats = db.query(
            Category.name,
            func.count(QuestionPool.id)
        ).outerjoin(QuestionPool).group_by(Category.id, Category.name).all()
        
        # Most used questions
        most_used = db.query(QuestionPool).filter(
            QuestionPool.usage_count > 0
        ).order_by(QuestionPool.usage_count.desc()).limit(10).all()
        
        return {
            "total_questions": total_questions,
            "by_type": dict(type_stats),
            "by_category": dict(category_stats),
            "most_used": [{"id": q.id, "title": q.title, "usage_count": q.usage_count} for q in most_used]
        }
    
    @staticmethod
    def serialize_question_for_response(question: QuestionPool) -> dict:
        """Convert database question to response format with JSON field parsing."""
        question_dict = {
            "id": question.id,
            "title": question.title,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "category_id": question.category_id,
            "is_required": question.is_required,
            "image_path": question.image_path,
            "created_at": question.created_at,
            "updated_at": question.updated_at,
            "created_by": question.created_by,
            "usage_count": question.usage_count,
            "essay_char_limit": question.essay_char_limit,
            "slider_min_label": question.slider_min_label,
            "slider_max_label": question.slider_max_label,
            "allow_multiple_selection": question.allow_multiple_selection,
            "randomize_order": question.randomize_order,
            "question_text_ar": question.question_text_ar,
            "slider_min_label_ar": question.slider_min_label_ar,
            "slider_max_label_ar": question.slider_max_label_ar,
        }
        
        # Parse JSON fields
        try:
            question_dict["mcq_options"] = json.loads(question.mcq_options) if question.mcq_options else None
        except (json.JSONDecodeError, TypeError):
            question_dict["mcq_options"] = None
            
        try:
            question_dict["mcq_correct_answer"] = json.loads(question.mcq_correct_answer) if question.mcq_correct_answer else None
        except (json.JSONDecodeError, TypeError):
            question_dict["mcq_correct_answer"] = None
            
        try:
            question_dict["ordering_options"] = json.loads(question.ordering_options) if question.ordering_options else None
        except (json.JSONDecodeError, TypeError):
            question_dict["ordering_options"] = None
        
        try:
            question_dict["mcq_options_ar"] = json.loads(question.mcq_options_ar) if question.mcq_options_ar else None
        except (json.JSONDecodeError, TypeError):
            question_dict["mcq_options_ar"] = None
            
        try:
            question_dict["ordering_options_ar"] = json.loads(question.ordering_options_ar) if question.ordering_options_ar else None
        except (json.JSONDecodeError, TypeError):
            question_dict["ordering_options_ar"] = None
        
        return question_dict