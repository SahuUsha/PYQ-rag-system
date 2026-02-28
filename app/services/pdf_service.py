import re
from unstructured.partition.pdf import partition_pdf


def extract_questions(file_path):
    elements = partition_pdf(file_path)
    full_text = "\n".join([str(el) for el in elements])
    
    # Simple question splitting using numbering pattern
    questions = re.split(r"\n\d+\.", full_text)
    
    cleaned_questions = [q.strip() for q in questions if len(q.strip()) > 30]

    return cleaned_questions
    