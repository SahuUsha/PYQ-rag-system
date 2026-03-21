# import os
# import json
# import google.generativeai as genai
# from dotenv import load_dotenv
# from sympy import content

# load_dotenv()

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# model = genai.GenerativeModel("gemini-2.5-flash")


# PROMPT = """
# You are an AI that extracts university exam questions.

# Convert the exam paper text into structured JSON.

# Return ONLY JSON.

# Schema:

# [
#  {
#   "question_text": "",
#   "subquestions":[
#       {"label":"i","text":""}
#   ],
#   "marks": null,
#   "semester": "",
#   "subject": "",
#   "year": null,
#   "exam_type": ""
#  }
# ]

# Rules:
# - Remove numbering like Q1.A
# - Extract subquestions like i ii iii
# - Extract observations if present
# """


# def parse_questions_with_gemini(text):

#     chunks = chunk_text(text)

#     all_questions = []

#     for chunk in chunks:

#         response = model.generate_content([
#             PROMPT,
#             f"Exam Paper Text:\n{chunk}"
#         ])

#         content = response.text

#         try:
#             content = content.replace("```json", "").replace("```", "").strip()
#             data = json.loads(content)

#             all_questions.extend(data)

#         except:
#             print("Failed to parse chunk")

#     return all_questions


# def chunk_text(text, size=12000):
#     return [text[i:i+size] for i in range(0, len(text), size)]


import os
import json
import google.generativeai as genai
import re
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


PROMPT = """
Extract all university exam questions from the provided PDF exam paper.

Your task is to read the entire document carefully and extract ALL questions, preserving their structure and meaning.

Return ONLY valid JSON. Do NOT include explanations, comments, or markdown.

Schema:
[
{
"question_text": "",
"subquestions": [
{ "label": "i", "text": "" }
],
"marks": null,
"semester": "",
"subject": "",
"year": null,
"exam_type": "",
"visual_content_latex": null
}
]

Instructions:

Question Extraction:
Extract every question from the paper.
Remove numbering prefixes like "Q1", "Q1.A", "1.", etc.
Keep the main question in "question_text".
If subquestions exist (i, ii, iii, a, b, c), extract them into "subquestions".
Subquestions:
Normalize labels to lowercase (i, ii, iii, iv, a, b, c).
Each subquestion should contain only its own text.
Marks:
Extract marks if mentioned (e.g., (5 marks), [10], etc.).
If not available, set to null.
Semester:
Extract semester exactly as written but normalize format like:
Example: "Fourth Semester", "3rd Semester"
Subject:
Extract subject name exactly as mentioned in the paper.
Exam Type:
Identify exam type from codes:
"RS" → Regular
"MS" → MakeUp
"MSVRU" → treat as MakeUp
Store normalized value: "Regular" or "MakeUp"
Year Extraction (IMPORTANT):
Extract year from codes like:
RS-22 → 2022
RS–23 → 2023
MS-18 → 2018
MSVRU/RS–21 → 2021
Rule:
If a 2-digit year is found (e.g., 18, 22, 05):
If between 00–30 → convert to 2000–2030
Otherwise → convert to 1900s (fallback)
Store as integer (e.g., 2022).
Visual Content:
If the question includes diagrams, tables, graphs, circuits, or structured data:
Convert them into equivalent LaTeX code.
Store in "visual_content_latex".
If no visual content exists, set it to null.
Output Rules:
Return strictly valid JSON.
Do NOT include extra text.
Ensure proper formatting and escaping.
Include all questions in order.

"""

def extract_year_from_text(text):
    """
    Handles:
    RS – 25 → 2025
    RS-18 → 2018
    MS/19 → 2019
    2022-23 → 2022
    2024 → 2024
    """

    # RS / MS patterns (robust)
    match = re.search(r'(RS|MS|MSVRU)[^\d]{0,5}(\d{2})', text, re.IGNORECASE)
    if match:
        y = int(match.group(2))
        return 2000 + y if y <= 30 else 1900 + y

    # Academic year (2022-23)
    match = re.search(r'(20\d{2})\s*[-/]\s*\d{2}', text)
    if match:
        return int(match.group(1))

    # Full year
    match = re.search(r'\b(20\d{2})\b', text)
    if match:
        return int(match.group(1))

    return None


# ================= CLEAN HELPERS =================
def clean_marks(m):
    if not m:
        return None
    match = re.search(r"\d+", str(m))
    return int(match.group()) if match else None


def normalize_exam_type(val):
    if not val:
        return None
    val = val.lower()
    if "rs" in val or "regular" in val:
        return "Regular"
    if "ms" in val or "make" in val:
        return "MakeUp"
    return None


# ================= SAFE JSON =================
def safe_json_load(text):
    try:
        return json.loads(text)
    except:
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)
        text = text.replace("\n", " ")
        try:
            return json.loads(text)
        except:
            print("⚠️ JSON parsing failed")
            return []


# ================= METADATA EXTRACTION =================
def extract_metadata_from_pdf(pdf_bytes):

    META_PROMPT = """
    Extract ALL visible text from the FIRST PAGE of the exam paper.
    Do NOT summarize.
    Return plain text only.
    """

    response = model.generate_content(
        [
            {"mime_type": "application/pdf", "data": pdf_bytes},
            META_PROMPT
        ]
    )

    text = response.text

    print("\n📄 FIRST PAGE TEXT:\n", text[:500])

    # 🔥 Apply REGEX (not Gemini)
    year = extract_year_from_text(text)
    exam_type = normalize_exam_type(text)

    return {
        "year": year,
        "exam_type": exam_type,
        "subject": None,
        "semester": None
    }


# ================= MAIN FUNCTION =================
def parse_pdf_with_gemini(file_path):

    try:
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()

        # 🔥 STEP 1: Extract metadata using RAW TEXT
        metadata = extract_metadata_from_pdf(pdf_bytes)

        print("📌 METADATA:", metadata)

        # 🔥 STEP 2: Extract questions
        response = model.generate_content(
            [
                {"mime_type": "application/pdf", "data": pdf_bytes},
                PROMPT
            ]
        )

        content = response.text

        print("\n---- GEMINI RAW OUTPUT ----")
        print(content[:1000])
        print("---------------------------\n")

        content = content.replace("```json", "").replace("```", "").strip()
        data = safe_json_load(content)

        cleaned_data = []

        for q in data:

            if not isinstance(q, dict):
                continue

            cleaned_q = {
                "question_text": q.get("question_text"),
                "subquestions": q.get("subquestions", []),
                "marks": clean_marks(q.get("marks")),
                "semester": q.get("semester") or metadata.get("semester"),
                "subject": q.get("subject") or metadata.get("subject"),
                "year": q.get("year") if isinstance(q.get("year"), int) else metadata.get("year"),
                "exam_type": normalize_exam_type(q.get("exam_type")) or metadata.get("exam_type"),
                "visual_content_latex": q.get("visual_content_latex"),
            }

            if cleaned_q["question_text"]:
                cleaned_data.append(cleaned_q)

        print(f"✅ Total Questions Extracted: {len(cleaned_data)}")

        return cleaned_data

    except Exception as e:
        print("❌ ERROR:", str(e))
        return []