from pipeline import run_joblens

if __name__ == "__main__":
    
    candidate_profile = """
    1 year experience as BI Developer and Data Analyst.
    Skills: Qlik Sense, Power BI, Tableau, SQL, Python,
    Snowflake, AWS, Apache Airflow, Databricks, FastAPI.
    Currently learning: GenAI, RAG systems, LangChain,
    vector databases, prompt engineering, embeddings.
    Built production dashboards for global clients US and EMEA.
    """
    
    job_data = [
        {
            "company": "Sarvam AI",
            "jd_text": """Backend Engineer to build low-latency APIs 
            for serving ML models at scale. Strong Python, FastAPI, 
            gRPC, PostgreSQL, Redis, Docker, Kubernetes. 
            Distributed systems, AWS or GCP. 3-6 years."""
        },
        {
            "company": "Freshworks",
            "jd_text": """Data Analyst for product analytics team. 
            SQL, Python, Tableau or Power BI, Excel, statistical 
            analysis, A/B testing. 2-4 years experience."""
        },
        {
            "company": "Haptik",
            "jd_text": """AI Engineer to build conversational AI. 
            Python, NLP, LLMs, LangChain, vector databases, RAG, 
            FastAPI, prompt engineering. 2-5 years."""
        },
        {
            "company": "Zoho",
            "jd_text": """GenAI Developer to integrate AI features 
            across product suite. Python, LLMs, prompt engineering, 
            REST APIs, SQL, ML concepts. 1-3 years."""
        },
        {
            "company": "Razorpay",
            "jd_text": """Data Engineer for data pipelines. Python, 
            SQL, Apache Airflow, Snowflake, AWS, dbt. ETL pipelines 
            and data warehouse design. 2-5 years."""
        },
    ]


    run_joblens(candidate_profile, job_data)


