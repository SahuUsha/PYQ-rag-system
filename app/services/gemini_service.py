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
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash-lite")


PROMPT = """
Extract all university exam questions from this PDF.

Your task is to read the provided PDF exam paper and extract ALL questions.

Return ONLY valid JSON. Do NOT include explanations or markdown.



Schema:

[
 {
  "question_text": "",
  "subquestions":[
      {"label":"i","text":""}
  ],
  "marks": null,
  "semester": "",
  "subject": "",
  "year": null,
  "exam_type": "",
  "visual_content_latex": null
 }
]

Rules:
- Remove numbering like Q1.A
- Extract subquestions i ii iii
- Extract marks if present
- If the question paper contains graphs, tables, generate the equivalent LaTeX code and put it in the "visual_content_latex" field. Otherwise, set it to null.
- Return only JSON
"""


def parse_pdf_with_gemini(file_path):

    with open(file_path, "rb") as f:
        pdf_bytes = f.read()

    response = model.generate_content(
        [
            {"mime_type": "application/pdf", "data": pdf_bytes},
            PROMPT
        ]
    )

    content = response.text

    content = content.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(content)
    except:
        print("JSON parse failed")
        return []