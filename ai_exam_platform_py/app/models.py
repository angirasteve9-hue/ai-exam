from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    exams = relationship("Exam", back_populates="owner")
    attempts = relationship("ExamAttempt", back_populates="user")

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    subject = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Store the raw text/file path if needed
    file_path = Column(String, nullable=True)
    
    owner = relationship("User", back_populates="exams")
    questions = relationship("Question", back_populates="exam")
    attempts = relationship("ExamAttempt", back_populates="exam")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    question_number = Column(String) # "1", "1a", "2"
    text = Column(Text)
    marks = Column(Integer)
    question_type = Column(String) # "short", "long", "mcq"
    mark_scheme_answer = Column(Text) # The ideal answer or criteria
    
    exam = relationship("Exam", back_populates="questions")

class ExamAttempt(Base):
    __tablename__ = "exam_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))
    score_out_of = Column(Integer)
    total_score = Column(Integer) # Sum of marks awarded
    feedback_summary = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="attempts")
    exam = relationship("Exam", back_populates="attempts")
    answers = relationship("UserAnswer", back_populates="attempt")

class UserAnswer(Base):
    __tablename__ = "user_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("exam_attempts.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    user_response = Column(Text)
    ai_score = Column(Integer, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    
    attempt = relationship("ExamAttempt", back_populates="answers")
