import streamlit as st
import requests

# Backend URL - adjust if needed
BACKEND_URL = "http://localhost:8001"

st.title("PYQ RAG System")

st.header("Search Questions")
query = st.text_input("Enter your search query")

if st.button("Search"):
    if query:
        with st.spinner("Searching..."):
            params = {"query": query}
            response = requests.get(f"{BACKEND_URL}/search", params=params)

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
                st.error(f"Error: {response.text}")
    else:
        st.warning("Please enter a search query.")