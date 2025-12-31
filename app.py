# from langchain_groq import ChatGroq
# from langchain_community.document_loaders import WebBaseLoader
# from langchain_core.prompts import PromptTemplate
# from db import init_db
# # from langchain_core.output_parsers import JsonOutputParser
# from dotenv import load_dotenv

# load_dotenv()

# # json_parser = JsonOutputParser()

# collection = init_db()

# llm = ChatGroq(
#   model="llama-3.3-70b-versatile",
#   temperature=0,
# )

# loader = WebBaseLoader("https://www.accenture.com/us-en/careers/jobdetails?id=13852370_en&title=Senior+Python+Developer+6033119")
# page_data = loader.load().pop().page_content

# # response = llm.invoke("The first person to land on moon was ...")
# # print(response.content)



# prompt_extract = PromptTemplate.from_template(
# """
# ### SCRAPED TEXT FROM WEBSITE:
# {page_data}

# ### INSTRUCTION:
# The above text is scraped from a company's careers page.

# Your task is to extract ALL job postings and return them as a JSON array.
# Each job posting MUST follow the exact schema below.

# ### JSON SCHEMA:
# [
#   {{
#     "role": "string",
#     "experience": "string | null",
#     "skills": ["string"],
#     "description": "string"
#   }}
# ]

# ### RULES:
# - Return ONLY valid JSON (no explanation, no markdown, no extra text)
# - If multiple jobs exist, return multiple objects in the array
# - If a field is missing, use null (for experience) or empty array (for skills)
# - Extract only job-related information
# - Ignore company overview, benefits, culture, legal text, or unrelated content
# - Do NOT hallucinate or invent information

# ### VALID JSON ONLY (NO PREAMBLE):
# """
# )

# chain_extract = prompt_extract | llm
# res = chain_extract.invoke(input={'page_data':page_data})
# # print(res.content)
# # print(type(res.content))

# # json_res = json_parser.parse(res.content)
# # print(json_res)

# results = collection.query(
#     query_texts=["Python Django PostgreSQL"],
#     n_results=2
# )

# print(results)



import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text


def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")
    url_input = st.text_input("Enter a URL:", value="https://www.accenture.com/us-en/careers/jobdetails?id=13852370_en&title=Senior+Python+Developer+6033119")
    submit_button = st.button("Submit")

    if submit_button:
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)
            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)
                st.code(email, language='markdown')
        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)



