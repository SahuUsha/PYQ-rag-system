import re
from unstructured.partition.pdf import partition_pdf


def extract_questions(file_path):
    elements = partition_pdf(filename=file_path)

    # 🔹 Extract clean text
    full_text = "\n".join(
        [el.text for el in elements if hasattr(el, "text") and el.text]
    )

    # -----------------------------
    # 🔹 Metadata Extraction
    # -----------------------------

    subject = extract_subject(full_text)
    semester = extract_semester(full_text)
    exam_type, year = extract_exam_info(full_text)

    # -----------------------------
    # 🔹 Question Extraction
    # -----------------------------

    # Match blocks starting with 1., 2., 3.
    question_pattern = r"\d+\.\s*(.*?)(?=\n\d+\.|\Z)"
    question_blocks = re.findall(question_pattern, full_text, re.DOTALL)

    structured_questions = []

    for block in question_blocks:

        # Split sub-questions (a), (b)
        sub_questions = re.split(r"\(\w\)", block)

        for sq in sub_questions:
            sq = sq.strip()

            if len(sq) < 40:
                continue

            marks, co = extract_marks_and_co(sq)
            q_type = detect_type(marks)

            structured_questions.append({
                "question_text": clean_question(sq),
                "marks": marks,
                "semester": semester,
                "subject": subject,
                "year": year,
                "exam_type": exam_type
            })

    return structured_questions


# ----------------------------------
# 🔹 Metadata Extraction
# ----------------------------------

def extract_subject(text):
    # Example: DEEP LEARNING – I
    match = re.search(r"\n([A-Z\s]+[-–]\s*\w+)\n", text)
    return match.group(1).strip() if match else None


def extract_semester(text):
    match = re.search(
        r"(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth)\s+Semester",
        text,
        re.IGNORECASE
    )
    return match.group(0) if match else None


def extract_exam_info(text):
    match = re.search(r"\b(RS|MS)\s*[-–]?\s*(\d{2})\b", text, re.IGNORECASE)

    if match:
        code = match.group(1).upper()
        short_year = int(match.group(2))
        year = 2000 + short_year

        exam_map = {
            "RS": "Regular",
            "MS": "Makeup"
        }

        return exam_map.get(code), year

    # Direct 4-digit year fallback
    match = re.search(r"\b(20\d{2})\b", text)
    if match:
        return None, int(match.group(1))

    return None, None

# ----------------------------------
# 🔹 Marks + CO Extraction
# ----------------------------------

def extract_marks_and_co(text):
    match = re.search(r"(\d+)\s*\(CO(\d+)\)", text)

    if match:
        marks = int(match.group(1))
        co = f"CO{match.group(2)}"
        return marks, co

    return None, None


def detect_type(marks):
    if marks is None:
        return "Unknown"
    elif marks <= 5:
        return "Short"
    else:
        return "Long"


def clean_question(text):
    # Remove marks and CO like 6(CO1)
    text = re.sub(r"\d+\s*\(CO\d+\)", "", text)
    return text.strip()