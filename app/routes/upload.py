import os
from fastapi import APIRouter, UploadFile, File
import shutil
from app.services.pdf_services import extract_questions
from app.services.db_service import save_question
from app.services.qdrant_service import insert_vector
from app.services.embedding import generate_embedding


router = APIRouter()

@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"

    # Save file temporarily
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract structured questions
    questions = extract_questions(file_path)

    for q in questions:

        saved_question = save_question(
            question_text=q["question_text"],
            subject=q["subject"],
            year=q["year"],
            semester=q["semester"],
            exam_type=q["exam_type"],
            marks=q["marks"],
        )

        # Generate embedding
        vector = generate_embedding(q["question_text"])

        # Insert into Qdrant
        insert_vector(
            question_id=saved_question.id,
            vector=vector,
            payload={
                "subject": q["subject"],
                "year": q["year"],
                "semester": q["semester"],
                "exam_type": q["exam_type"],
                "marks": q["marks"],
            },
        )

    # Optional: delete temp file
    os.remove(file_path)

    return {
        "message": "PDF processed successfully",
        "total_questions": len(questions)
    }
 