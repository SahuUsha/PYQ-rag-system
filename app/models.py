from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    question_text = Column(JSONB)

    subject = Column(Text)

    year = Column(Integer)

    exam_type = Column(Text)

    semester = Column(Text)

    marks = Column(String)