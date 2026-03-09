# from unstructured.partition.pdf import partition_pdf
# from app.services.gemini_service import parse_questions_with_gemini


# def extract_questions(file_path):

#     elements = partition_pdf(
#         filename=file_path,
#         strategy="fast"
#     )

#     text = "\n".join(
#         el.text for el in elements
#         if hasattr(el, "text") and el.text
#     )

#     print("\n====== EXTRACTED TEXT FROM PDF ======\n")
#     print(text[:1000])  # print first 1000 characters
#     print("\n=====================================\n")

#     if not text.strip():
#         print("⚠️ No text extracted from PDF")
#         return []

#     questions = parse_questions_with_gemini(text)

#     print(f"Extracted {len(questions)} questions from Gemini")

#     return questions


from app.services.gemini_service import parse_pdf_with_gemini


def extract_questions(file_path):

    questions = parse_pdf_with_gemini(file_path)

    print(f"Extracted {len(questions)} questions")

    return questions