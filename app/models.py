from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text)
    subject =Column(String(255))
    year = Column(Integer)
    type = Column(String(50))
    semester = Column(String(50))
    marks = Column(Integer)