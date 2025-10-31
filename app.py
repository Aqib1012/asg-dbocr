import streamlit as st
import sqlite3
import os
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from config import gemini  # 🔹 API key securely fetched from config.py

st.set_page_config(page_title="🧠 Smart SQL Agent (Gemini 2.5)", page_icon="🧠", layout="wide")

st.title("🧠 Smart SQL Agent (Gemini 2.5)")
st.markdown("""
Upload your **SQLite database (.db)** and ask natural language questions —  
Gemini 2.5 will automatically analyze and query your data! 💬
""")

# ---- File Upload ----
uploaded_file = st.file_uploader("📂 Upload your SQLite database", type=["db"])

if uploaded_file is not None:
    # Save uploaded DB file temporarily
    db_path = os.path.join("temp_db", uploaded_file.name)
    os.makedirs("temp_db", exist_ok=True)

    with open(db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ Database uploaded successfully: `{uploaded_file.name}`")

    # ---- Connect Database ----
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

    # ---- Setup Gemini LLM ----
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=gemini(),
        temperature=0.3,
    )

    # ---- System Prompt ----
    system_prompt = """
    You are a professional SQL data analyst.
    You can read and understand the database schema.
    Always generate correct SQL queries and explain results clearly.
    Never say "I don't know". If uncertain, make your best analysis based on data.
    """

    # ---- Create SQL Agent ----
    agent = create_sql_agent(
        llm=llm,
        db=db,
        verbose=True,
        handle_parsing_errors=True,
        system_message=system_prompt
    )

    # ---- User Query ----
    st.subheader("💬 Ask your question:")
    query = st.text_input("Type your question according to your uploaded db:")

    if query:
        with st.spinner("🔍 Processing your query... please wait"):
            try:
                response = agent.invoke({"input": query}, handle_parsing_errors=True)
                st.success("✅ Query processed successfully!")
                st.markdown("### 🧾 Response:")
                st.write(response["output"])

            except Exception as e:
                st.error(f"⚠️ Something went wrong while processing your query.\n\n**Error:** {str(e)}")

else:
    st.info("📂 Please upload a `.db` file to get started.")
