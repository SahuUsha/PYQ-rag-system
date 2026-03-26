import os
import shutil
import json
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.pdf_services import extract_questions
from app.services.db_service import save_question
from app.services.qdrant_service import insert_vector
from app.services.embedding import generate_embedding


router = APIRouter()


@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):

    file_path = f"temp_{file.filename}"

    try:

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract questions using Gemini
        questions = extract_questions(file_path)

        print("\nExtracted Questions:\n")
        print(json.dumps(questions, indent=4))

        saved_count = 0

        for q in questions:

            main_text = q.get("question_text")
            subquestions = q.get("subquestions", [])

            if not main_text and not subquestions:
                print("Skipping empty question")
                continue

            # For embedding, use main_text if available, else concat subquestions
            embedding_text = main_text or " ".join([sq.get("text", "") for sq in subquestions])

            marks = str(q.get("marks") or "")

            saved_question = save_question(
                question_text=q,  # store full JSON
                subject=q.get("subject"),
                year=q.get("year"),
                semester=q.get("semester"),
                exam_type=q.get("exam_type"),
                marks=marks,
            )

            print("Saving question:", q)

            # embedding using only main statement
            vector = generate_embedding(embedding_text)

            if hasattr(vector, "tolist"):
                vector = vector.tolist()

            insert_vector(
                question_id=saved_question.id,
                vector=vector,
                payload={
                    "question": q.get("question_text"),
                    "subject": q.get("subject"),
                    "year": q.get("year"),
                    "semester": q.get("semester"),
                    "exam_type": q.get("exam_type"),
                    "marks": marks,
                },
            )

            saved_count += 1
            
        print("Questions returned from Gemini:", len(questions))
        
        return {
            "message": "PDF processed successfully",
            "total_questions": saved_count
        }

    except Exception as e:

        print("ERROR OCCURRED:", str(e))

        raise HTTPException(status_code=500, detail=str(e))

    finally:

        if os.path.exists(file_path):
            os.remove(file_path)