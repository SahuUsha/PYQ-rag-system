import streamlit as st
import requests

DEFAULT_BACKEND_URL = "http://localhost:8001"

st.set_page_config(page_title="PYQ RAG System", layout="wide")
st.title("PYQ RAG System")

backend_url =  DEFAULT_BACKEND_URL

if not backend_url:
    st.sidebar.error("Please set the backend URL.")

st.subheader("Upload PDF")
with st.form("upload_form"):
    uploaded_file = st.file_uploader("Choose a PDF file to upload", type=["pdf"])
    upload_button = st.form_submit_button("Upload PDF")

if upload_button:
    if not backend_url:
        st.error("Backend URL is required for upload.")
    elif not uploaded_file:
        st.warning("Please choose a PDF file before uploading.")
    else:
        with st.spinner("Uploading PDF to backend..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = requests.post(f"{backend_url}/upload", files=files)

                if response.status_code == 200:
                    result = response.json()
                    st.success("PDF uploaded successfully.")
                    st.write("**Result:**")
                    st.write(f"- Message: {result.get('message', 'Uploaded')}")
                    st.write(f"- Total questions processed: {result.get('total_questions', 0)}")
                else:
                    st.error(f"Upload failed: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as exc:
                st.error(f"Upload request failed: {exc}")

st.markdown("---")

st.header("Search Questions")
with st.form("search_form"):
    query = st.text_input("Enter your search query")
    search_button = st.form_submit_button("Search")

if search_button:
    if not backend_url:
        st.error("Backend URL is required for search.")
    elif not query:
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Searching..."):
            try:
                params = {"query": query}
                response = requests.get(f"{backend_url}/search", params=params)

                if response.status_code == 200:
                    result = response.json()
                    st.subheader("Retrieved Questions")
                    questions = result.get("retrieved_questions", [])

                    if questions:
                        for i, q in enumerate(questions, 1):
                            with st.expander(f"Question {i}"):
                                data = q.get("question", {})

                                if data.get("question_text"):
                                    st.write(f"**Question:** {data['question_text']}")

                                if data.get("subquestions"):
                                    st.write("**Subquestions:**")
                                    for sq in data["subquestions"]:
                                        st.write(f"- {sq.get('text', '')}")

                                st.write(f"**Subject:** {q.get('subject', 'N/A')}")
                                st.write(f"**Year:** {q.get('year', 'N/A')}")
                                st.write(f"**Semester:** {q.get('semester', 'N/A')}")
                                st.write(f"**Exam Type:** {q.get('exam_type', 'N/A')}")
                                st.write(f"**Marks:** {q.get('marks', 'N/A')}")
                    else:
                        st.write("No questions found.")
                else:
                    st.error(f"Search failed: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as exc:
                st.error(f"Search request failed: {exc}")
