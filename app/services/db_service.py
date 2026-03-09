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

        print("Question saved:", question.id)

        return question

    except Exception as e:

        db.rollback()
        print("DB ERROR:", str(e))
        raise

    finally:
        db.close()


def get_questions_by_ids(ids):

    db = SessionLocal()

    try:

        questions = db.query(Question).filter(Question.id.in_(ids)).all()

        return [
            {
                "id": q.id,
                "question": q.question_text,
                "subject": q.subject,
                "year": q.year,
                "semester": q.semester,
                "exam_type": q.exam_type,
                "marks": q.marks
            }
            for q in questions
        ]

    finally:
        db.close()