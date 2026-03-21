import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.models import Question, Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def verify():
    db = SessionLocal()
    try:
        test_q = Question(
            question_text={"text": "Test Question", "marks": "4(CO 4)"},
            subject="TEST SUBJECT",
            year=2024,
            exam_type="Regular",
            semester="First Semester",
            marks="4(CO 4)"
        )
        db.add(test_q)
        db.commit()
        db.refresh(test_q)
        print(f"Verification successful: Question inserted with ID {test_q.id}")
        
        # Cleanup
        db.delete(test_q)
        db.commit()
        print("Cleanup successful: Test question deleted")
        return True
    except Exception as e:
        print(f"Verification failed: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    verify()
