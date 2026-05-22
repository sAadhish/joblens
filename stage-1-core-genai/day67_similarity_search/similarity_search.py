import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
import hashlib
import json
import os
from dotenv import load_dotenv

load_dotenv()


groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise ValueError("Missing GROQ_API_KEY. Add it to .env (or export GROQ_API_KEY).")

model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.Client()

groq_client = Groq(api_key=groq_key)


#create collection
collection =chroma_client.create_collection(
    name="resumes_with_metadata",
    metadata={"hnsw:space": "cosine"}
)


job_descriptions = [
    {
        "text": """Sarvam AI is looking for a Backend Engineer to build 
        low-latency APIs for serving ML models at scale. Requirements: 
        Strong Python, FastAPI or Django, gRPC, PostgreSQL, Redis, 
        Docker, Kubernetes. Experience with distributed systems and 
        cloud platforms AWS or GCP. 3-6 years experience.""",
        "metadata": {
            "company": "Sarvam AI",
            "role": "Backend Engineer",
            "role_type": "engineering",
            "experience_min": 3,
            "experience_max": 6,
            "location": "Bangalore",
            "remote_ok": False,
            "company_type": "startup"
        }
    },
    {
        "text": """Freshworks hiring Data Analyst to work with product 
        analytics team. Requirements: SQL, Python, Tableau or Power BI, 
        Excel, statistical analysis. Work with large datasets to drive 
        product decisions. Experience with A/B testing preferred. 
        2-4 years experience.""",
        "metadata": {
            "company": "Freshworks",
            "role": "Data Analyst",
            "role_type": "data",
            "experience_min": 2,
            "experience_max": 4,
            "location": "Chennai",
            "remote_ok": True,
            "company_type": "product"
        }
    },
    {
        "text": """Haptik looking for AI Engineer to build conversational 
        AI products. Requirements: Python, NLP, LLMs, LangChain, 
        vector databases, RAG systems, FastAPI. Experience building 
        chatbots or voice assistants. Familiarity with prompt engineering. 
        2-5 years experience.""",
        "metadata": {
            "company": "Haptik",
            "role": "AI Engineer",
            "role_type": "ai",
            "experience_min": 2,
            "experience_max": 5,
            "location": "Mumbai",
            "remote_ok": True,
            "company_type": "product"
        }
    },
    {
        "text": """Zoho hiring GenAI Developer to integrate AI features 
        across Zoho product suite. Requirements: Python, LLMs, prompt 
        engineering, REST APIs, SQL. Understanding of ML concepts. 
        Build AI-powered features for CRM, analytics products. 
        1-3 years experience.""",
        "metadata": {
            "company": "Zoho",
            "role": "GenAI Developer",
            "role_type": "ai",
            "experience_min": 1,
            "experience_max": 3,
            "location": "Chennai",
            "remote_ok": False,
            "company_type": "product"
        }
    },
    {
        "text": """Razorpay looking for Data Engineer to build and maintain 
        data pipelines. Requirements: Python, SQL, Apache Airflow, 
        Snowflake, AWS, dbt. Experience with ETL pipelines and 
        data warehouse design. Strong analytical thinking. 
        2-5 years experience.""",
        "metadata": {
            "company": "Razorpay",
            "role": "Data Engineer",
            "role_type": "data",
            "experience_min": 2,
            "experience_max": 5,
            "location": "Bangalore",
            "remote_ok": True,
            "company_type": "product"
        }
    },
]

def get_id(text):
    return hashlib.md5(text.encode()).hexdigest()

#insert into collection
collection.add(
    documents=[j["text"] for j in job_descriptions],
    embeddings=model.encode([j["text"] for j in job_descriptions]).tolist(),
    metadatas=[j["metadata"] for j in job_descriptions],
    ids=[get_id(j["text"])for j in job_descriptions]
)

print(f"Stored {collection.count()} JDs\n")


# --- My actual sample profile ---
candidate_profile = """
1 year experience as BI Developer and Data Analyst.
Skills: Qlik Sense, Power BI, Tableau, SQL, Python, 
Snowflake, AWS, Apache Airflow, Databricks, FastAPI.
Currently learning: GenAI, RAG systems, LangChain, 
vector databases, prompt engineering, embeddings.
Background in building production dashboards for 
global clients across US and EMEA regions.
"""

def find_matching_jobs(profile,company=None,role=None,role_type=None,experience_min=None,
                       experience_max=None,location=None,remote_ok=False,company_type=None,top_k=3):
    
    query_embedding=model.encode([profile]).tolist()

    #Build where filter
    conditions=[]
    if role:
        conditions.append({"role":role})
    if company:
        conditions.append({"company":company})
    if role_type:
        conditions.append({"role_type":role_type})
    if experience_min:
        conditions.append({"experience_min":{"$gte": experience_min}})
    if experience_max:
        conditions.append({"experience_max":{"$lte":experience_max}})
    if location:
        conditions.append({"location":location})
    if remote_ok:
        conditions.append({"remote_ok":True})
    if company_type:
        conditions.append({"company_type":company_type})

    where_filter = None

    if len(conditions)==1:
        where_filter=conditions[0]
    elif len(conditions)>1:
        where_filter={"$and",conditions}
    
    # Query the output
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where=where_filter
    )
    
    print(f"Profile match results:")
    if where_filter:
        print(f"Filters applied: {where_filter}")
    print()


    MINIMUM_SIMILARITY = 0.35
    matches=[]

    for i, (docs, distance,meta) in  enumerate(zip(results["documents"][0],results["distances"][0],results["metadatas"][0])):
        similarity =1-distance
        if similarity >= MINIMUM_SIMILARITY:
            print(f"Rank {i+1}: {meta['company']} — {meta['role']}")
            print(f"         Score: {similarity:.3f} | "
                  f"Location: {meta['location']} | "
                  f"Remote: {meta['remote_ok']} | "
                  f"Experience: {meta['experience_min']}-{meta['experience_max']}yrs")
            print()

            matches.append({"company": meta["company"],
                          "role": meta["role"],
                          "score": similarity,
                          "jd_text": docs})
        else:
            print(f"Rank {i+1}: Weak match — {meta['company']} "
                  f"(score: {similarity:.3f})")
    return matches


# --- Experiment 1: All roles ---
print("=" * 55)
print("EXPERIMENT 1 — Best matching roles overall")
print("=" * 55)
all_matches = find_matching_jobs(candidate_profile, top_k=5)

# --- Experiment 2: AI roles only ---
print("=" * 55)
print("EXPERIMENT 2 — AI roles only")
print("=" * 55)
ai_matches = find_matching_jobs(candidate_profile, role_type="ai")

# --- Experiment 3: Remote + any role ---
print("=" * 55)
print("EXPERIMENT 3 — Remote friendly roles only")
print("=" * 55)
remote_matches = find_matching_jobs(candidate_profile, remote_ok=True)

if all_matches:
    best_match = all_matches[0]
    print("=" * 55)
    print(f"SKILL GAP ANALYSIS — {best_match['company']}")
    print("=" * 55)

    response=groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {
                "role":"system",
                "content":""" Your an expert career advisor . Given is a candidate profile and a job description ,  No explainations before or after . No markdown .Jsut raw JSON.
                Use excatly this structure :
                {
                "matching_skills": ["skill1", "skill2"],
                "missing_skills": ["skill1", "skill2"],
                "gap_severity": "low/medium/high",
                "ready_in_weeks": 4,
                "top_advice": "one specific actionable sentence"
                
                }


                Return only JSON. No markdown. No explanation."""
            },
            {
                "role":"user",
                "content":f"Candidate : {candidate_profile}\n\nJD: {best_match["jd_text"]}"
            }
        ]
    )

    raw=response.choices[0].message.content
    try:
        gap = json.loads(raw)
    except json.JSONDecodeError:
        print("the model didnot return json")
        print(raw)
        gap = None  

    print(f"Matching skills:  {gap['matching_skills']}")
    print(f"Missing skills:   {gap['missing_skills']}")
    print(f"Gap severity:     {gap['gap_severity']}")
    print(f"Ready in:         {gap['ready_in_weeks']} weeks")
    print(f"Top advice:       {gap['top_advice']}")