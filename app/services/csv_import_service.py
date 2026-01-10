import csv
import io
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import Category, ImportLog
from ..services.question_pool_service import QuestionPoolService
from ..schemas.question_pool import QuestionPoolCreate, CSVImportResult

class CSVImportExportService:
    
    @staticmethod
    def validate_and_import_csv(
        db: Session, 
        csv_content: str, 
        question_type: str, 
        filename: str, 
        imported_by: str
    ) -> CSVImportResult:
        """Validate and import questions from CSV content."""
        
        errors = []
        successful_imports = 0
        failed_imports = 0
        
        try:
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            rows = list(csv_reader)
            total_rows = len(rows)
            
            # Create import log
            import_log = ImportLog(
                filename=filename,
                import_type=question_type,
                total_rows=total_rows,
                imported_by=imported_by
            )
            db.add(import_log)
            db.flush()  # Get the ID
            
            # Get categories for name lookup
            categories = {cat.name: cat.id for cat in QuestionPoolService.get_categories(db, active_only=False)}
            
            for row_num, row in enumerate(rows, start=2):  # Start at 2 since row 1 is header
                try:
                    # Validate and process based on question type
                    if question_type == "essay":
                        question_data = CSVImportExportService._process_essay_row(row, categories)
                    elif question_type == "slider":
                        question_data = CSVImportExportService._process_slider_row(row, categories)
                    elif question_type == "mcq":
                        question_data = CSVImportExportService._process_mcq_row(row, categories)
                    elif question_type == "ordering":
                        question_data = CSVImportExportService._process_ordering_row(row, categories)
                    else:
                        raise ValueError(f"Unsupported question type: {question_type}")
                    
                    # Add metadata
                    question_data['created_by'] = imported_by
                    
                    # Create question
                    question_create = QuestionPoolCreate(**question_data)
                    QuestionPoolService.create_question_pool(db, question_create)
                    successful_imports += 1
                    
                except Exception as e:
                    failed_imports += 1
                    errors.append({
                        "row": row_num,
                        "error": str(e),
                        "data": dict(row)
                    })
            
            # Update import log
            import_log.successful_imports = successful_imports
            import_log.failed_imports = failed_imports
            import_log.errors = json.dumps(errors) if errors else None
            
            db.commit()
            
            return CSVImportResult(
                total_rows=total_rows,
                successful_imports=successful_imports,
                failed_imports=failed_imports,
                errors=errors,
                import_log_id=import_log.id
            )
            
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to process CSV: {str(e)}")
    
    @staticmethod
    def _process_essay_row(row: Dict[str, str], categories: Dict[str, int]) -> Dict[str, Any]:
        """Process a row for essay question type."""
        # Required fields
        if not row.get('title') or not row.get('question_text'):
            raise ValueError("Title and question_text are required")
        
        # Get category ID
        category_id = None
        if row.get('category_name'):
            if row['category_name'] not in categories:
                raise ValueError(f"Category '{row['category_name']}' does not exist")
            category_id = categories[row['category_name']]
        
        # Parse boolean
        is_required = str(row.get('is_required', 'TRUE')).upper() in ['TRUE', '1', 'YES']
        
        # Parse character limit
        char_limit = None
        if row.get('essay_char_limit'):
            try:
                char_limit = int(row['essay_char_limit'])
                if char_limit < 1:
                    raise ValueError("Character limit must be positive")
            except ValueError:
                raise ValueError("Invalid character limit")
        
        return {
            'title': row['title'].strip(),
            'question_text': row['question_text'].strip(),
            'question_type': 'essay',
            'category_id': category_id,
            'is_required': is_required,
            'essay_char_limit': char_limit,
            'question_text_ar': row.get('question_text_ar', '').strip() or None
        }
    
    @staticmethod
    
    def _process_slider_row(row: Dict[str, str], categories: Dict[str, int]) -> Dict[str, Any]:
        """Process a row for slider question type."""
        # Required fields
        if not row.get('title') or not row.get('question_text'):
            raise ValueError("Title and question_text are required")
        
        # Get category ID
        category_id = None
        if row.get('category_name'):
            if row['category_name'] not in categories:
                raise ValueError(f"Category '{row['category_name']}' does not exist")
            category_id = categories[row['category_name']]
        
        # Parse boolean
        is_required = str(row.get('is_required', 'TRUE')).upper() in ['TRUE', '1', 'YES']
        
        return {
            'title': row['title'].strip(),
            'question_text': row['question_text'].strip(),
            'question_type': 'slider',
            'category_id': category_id,
            'is_required': is_required,
            'slider_min_label': row.get('slider_min_label', '').strip() or None,
            'slider_max_label': row.get('slider_max_label', '').strip() or None,
            'question_text_ar': row.get('question_text_ar', '').strip() or None,
            'slider_min_label_ar': row.get('slider_min_label_ar', '').strip() or None,
            'slider_max_label_ar': row.get('slider_max_label_ar', '').strip() or None
        }
    
    @staticmethod
    def _process_mcq_row(row: Dict[str, str], categories: Dict[str, int]) -> Dict[str, Any]:
        """Process a row for MCQ question type."""
        # Required fields
        if not row.get('title') or not row.get('question_text'):
            raise ValueError("Title and question_text are required")
        
        # Get category ID
        category_id = None
        if row.get('category_name'):
            if row['category_name'] not in categories:
                raise ValueError(f"Category '{row['category_name']}' does not exist")
            category_id = categories[row['category_name']]
        
        # Parse boolean fields
        is_required = str(row.get('is_required', 'TRUE')).upper() in ['TRUE', '1', 'YES']
        allow_multiple = str(row.get('allow_multiple_selection', 'FALSE')).upper() in ['TRUE', '1', 'YES']
        
        # Collect options
        options = []
        for i in range(1, 7):  # Support up to 6 options
            option_key = f'option_{i}'
            if row.get(option_key) and row[option_key].strip():
                options.append(row[option_key].strip())
        
        if len(options) < 2:
            raise ValueError("At least 2 options are required for MCQ questions")
        
        # Parse correct answers
        correct_answers = []
        if row.get('correct_answers'):
            try:
                # Support formats: "1,2,3" or "1" or "[1,2,3]"
                correct_str = row['correct_answers'].strip()
                if correct_str.startswith('[') and correct_str.endswith(']'):
                    correct_str = correct_str[1:-1]
                
                for answer_str in correct_str.split(','):
                    answer_idx = int(answer_str.strip()) - 1  # Convert to 0-based index
                    if answer_idx < 0 or answer_idx >= len(options):
                        raise ValueError(f"Correct answer index {answer_idx + 1} is out of range")
                    correct_answers.append(answer_idx)
            except ValueError as e:
                raise ValueError(f"Invalid correct answers format: {e}")
        
        if not correct_answers:
            raise ValueError("At least one correct answer must be specified")
        
        # Collect Arabic options if provided
        options_ar = []
        for i in range(1, 7):
            option_key = f'option_{i}_ar'
            if row.get(option_key) and row[option_key].strip():
                options_ar.append(row[option_key].strip())
        
        return {
            'title': row['title'].strip(),
            'question_text': row['question_text'].strip(),
            'question_type': 'mcq',
            'category_id': category_id,
            'is_required': is_required,
            'allow_multiple_selection': allow_multiple,
            'mcq_options': options,
            'mcq_correct_answer': correct_answers,
            'question_text_ar': row.get('question_text_ar', '').strip() or None,
            'mcq_options_ar': options_ar if options_ar else None
        }
    
    @staticmethod
    def _process_ordering_row(row: Dict[str, str], categories: Dict[str, int]) -> Dict[str, Any]:
        """Process a row for ordering question type."""
        # Required fields
        if not row.get('title') or not row.get('question_text'):
            raise ValueError("Title and question_text are required")
        
        # Get category ID
        category_id = None
        if row.get('category_name'):
            if row['category_name'] not in categories:
                raise ValueError(f"Category '{row['category_name']}' does not exist")
            category_id = categories[row['category_name']]
        
        # Parse boolean fields
        is_required = str(row.get('is_required', 'TRUE')).upper() in ['TRUE', '1', 'YES']
        randomize_order = str(row.get('randomize_order', 'TRUE')).upper() in ['TRUE', '1', 'YES']
        
        # Collect items
        items = []
        for i in range(1, 7):  # Support up to 6 items
            item_key = f'item_{i}'
            if row.get(item_key) and row[item_key].strip():
                items.append(row[item_key].strip())
        
        if len(items) < 2:
            raise ValueError("At least 2 items are required for ordering questions")
        
        # Collect Arabic items if provided
        items_ar = []
        for i in range(1, 7):
            item_key = f'item_{i}_ar'
            if row.get(item_key) and row[item_key].strip():
                items_ar.append(row[item_key].strip())
        
        return {
            'title': row['title'].strip(),
            'question_text': row['question_text'].strip(),
            'question_type': 'ordering',
            'category_id': category_id,
            'is_required': is_required,
            'randomize_order': randomize_order,
            'ordering_options': items,
            'question_text_ar': row.get('question_text_ar', '').strip() or None,
            'ordering_options_ar': items_ar if items_ar else None
        }
    
    @staticmethod
    def export_questions_to_csv(db: Session, question_ids: List[int], question_type: str) -> str:
        """Export questions to CSV format."""
        from ..services.question_pool_service import QuestionPoolService
        
        questions = []
        for qid in question_ids:
            question = QuestionPoolService.get_question_pool_by_id(db, qid)
            if question and question.question_type == question_type:
                questions.append(question)
        
        if not questions:
            raise ValueError(f"No {question_type} questions found with the given IDs")
        
        # Generate CSV based on question type
        output = io.StringIO()
        
        if question_type == "essay":
            writer = csv.DictWriter(output, fieldnames=['title', 'question_text', 'category_name', 'is_required', 'essay_char_limit'])
            writer.writeheader()
            
            for q in questions:
                writer.writerow({
                    'title': q.title,
                    'question_text': q.question_text,
                    'category_name': q.category.name if q.category else '',
                    'is_required': 'TRUE' if q.is_required else 'FALSE',
                    'essay_char_limit': q.essay_char_limit or ''
                })
        
        elif question_type == "slider":
            writer = csv.DictWriter(output, fieldnames=['title', 'question_text', 'category_name', 'is_required', 'slider_min_label', 'slider_max_label'])
            writer.writeheader()
            
            for q in questions:
                writer.writerow({
                    'title': q.title,
                    'question_text': q.question_text,
                    'category_name': q.category.name if q.category else '',
                    'is_required': 'TRUE' if q.is_required else 'FALSE',
                    'slider_min_label': q.slider_min_label or '',
                    'slider_max_label': q.slider_max_label or ''
                })
        
        elif question_type == "mcq":
            fieldnames = ['title', 'question_text', 'category_name', 'is_required', 'allow_multiple_selection']
            fieldnames.extend([f'option_{i}' for i in range(1, 7)])
            fieldnames.append('correct_answers')
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for q in questions:
                serialized = QuestionPoolService.serialize_question_for_response(q)
                options = serialized.get('mcq_options', [])
                correct = serialized.get('mcq_correct_answer', [])
                
                row_data = {
                    'title': q.title,
                    'question_text': q.question_text,
                    'category_name': q.category.name if q.category else '',
                    'is_required': 'TRUE' if q.is_required else 'FALSE',
                    'allow_multiple_selection': 'TRUE' if q.allow_multiple_selection else 'FALSE',
                    'correct_answers': ','.join([str(i + 1) for i in correct]) if correct else ''
                }
                
                # Add options
                for i, option in enumerate(options):
                    if i < 6:
                        row_data[f'option_{i + 1}'] = option
                
                writer.writerow(row_data)
        
        elif question_type == "ordering":
            fieldnames = ['title', 'question_text', 'category_name', 'is_required', 'randomize_order']
            fieldnames.extend([f'item_{i}' for i in range(1, 7)])
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for q in questions:
                serialized = QuestionPoolService.serialize_question_for_response(q)
                items = serialized.get('ordering_options', [])
                
                row_data = {
                    'title': q.title,
                    'question_text': q.question_text,
                    'category_name': q.category.name if q.category else '',
                    'is_required': 'TRUE' if q.is_required else 'FALSE',
                    'randomize_order': 'TRUE' if q.randomize_order else 'FALSE'
                }
                
                # Add items
                for i, item in enumerate(items):
                    if i < 6:
                        row_data[f'item_{i + 1}'] = item
                
                writer.writerow(row_data)
        
        return output.getvalue()