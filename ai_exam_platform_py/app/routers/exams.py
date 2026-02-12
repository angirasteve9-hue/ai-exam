from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from .. import models, database
from ..database import get_db
from fastapi.templating import Jinja2Templates
from ..services.pdf_service import extract_text_from_pdf
from ..services.ai_service import structure_exam_content
import json

router = APIRouter(tags=["Exams"])
templates = Jinja2Templates(directory="app/templates")

def get_current_user(request: Request, db: Session = Depends(get_db)):
    email = request.cookies.get("user_email")
    if not email:
        return None
    return db.query(models.User).filter(models.User.email == email).first()

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    exams = db.query(models.Exam).filter(models.Exam.owner_id == user.id).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "exams": exams, "title": "Dashboard"})

@router.post("/upload")
async def upload_exam(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")

    # 1. Read PDF
    content = await file.read()
    text = extract_text_from_pdf(content)
    
    # 2. AI Processing (Ideally this should be a background task)
    structured_data = structure_exam_content(text)
    
    if not structured_data:
        # Handle error
        return RedirectResponse(url="/dashboard?error=ProcessingFailed", status_code=303)
        
    # 3. Save to DB
    new_exam = models.Exam(
        title=structured_data.get("exam_title", "Untitled Exam"),
        subject=structured_data.get("subject", "General"),
        owner_id=user.id
    )
    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)
    
    # Save questions
    for q_data in structured_data.get("questions", []):
        question = models.Question(
            exam_id=new_exam.id,
            question_number=q_data.get("question_number"),
            text=q_data.get("text"),
            marks=q_data.get("marks"),
            question_type=q_data.get("type", "short"),
            mark_scheme_answer="" # Mark scheme would be uploaded separately in full version
        )
        db.add(question)
    db.commit()
    
    return RedirectResponse(url=f"/exam/{new_exam.id}", status_code=303)

@router.get("/exam/{exam_id}", response_class=HTMLResponse)
def take_exam(exam_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")
        
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    return templates.TemplateResponse("exam_mode.html", {"request": request, "exam": exam, "title": exam.title})

@router.post("/exam/{exam_id}/submit")
async def submit_exam(
    exam_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")
        
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # Parse form data
    form_data = await request.form()
    
    # Create Attempt
    attempt = models.ExamAttempt(
        user_id=user.id,
        exam_id=exam.id,
        score_out_of=0,
        total_score=0
    )
    db.add(attempt)
    db.commit()
    
    total_score = 0
    max_score = 0
    
    # Process answers
    # Note: In a real app, this should be async/backgrounded so user doesn't wait for 10 AI calls
    from ..services.ai_service import grade_answer
    
    for question in exam.questions:
        user_answer = form_data.get(f"answers[{question.id}]")
        if user_answer:
            # AI Grading
            grade_result = grade_answer(
                question_text=question.text,
                mark_scheme=question.mark_scheme_answer or "Use best judgement based on question",
                user_answer=user_answer,
                max_marks=question.marks
            )
            
            score = grade_result.get("score_awarded", 0)
            feedback = grade_result.get("feedback", "")
            
            # Record Answer
            answer_record = models.UserAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                user_response=user_answer,
                ai_score=score,
                ai_feedback=feedback
            )
            db.add(answer_record)
            
            total_score += score
        
        max_score += question.marks
        
    attempt.total_score = total_score
    attempt.score_out_of = max_score
    attempt.completed_at = models.datetime.utcnow()
    db.commit()
    
    return RedirectResponse(url=f"/exam/{exam_id}/results/{attempt.id}", status_code=303)

@router.get("/exam/{exam_id}/results/{attempt_id}", response_class=HTMLResponse)
def view_results(exam_id: int, attempt_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    attempt = db.query(models.ExamAttempt).filter(models.ExamAttempt.id == attempt_id).first()
    return templates.TemplateResponse("results.html", {"request": request, "attempt": attempt, "title": "Results"})
