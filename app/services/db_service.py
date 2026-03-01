from app.database import SessionLocal
from app.models import Question


def save_question(
    question_text,
    subject=None,
    year=None,
    semester=None,
    exam_type=None,
    marks=None,
):
    db = SessionLocal()
    try:
        question = Question(
            question_text=question_text,
            subject=subject,
            year=year,
            semester=semester,
            exam_type=exam_type,
            marks=marks,
        )

        db.add(question)
        db.commit()
        db.refresh(question)

        return question

    finally:
        db.close()


def get_questions_by_ids(ids):
    db = SessionLocal()
    try:
        return db.query(Question).filter(Question.id.in_(ids)).all()
    finally:
        db.close()