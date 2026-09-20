from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()


groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise ValueError("Missing GROQ_API_KEY. Add it to .env (or export GROQ_API_KEY).")

Client = Groq(api_key=groq_key)

def analyser(jd_text):
    response = Client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {
                "role" : "system",
                "content" : """ You are a senior tech recuriter in india analysing job description
                You must respond only with a JSON object . No explainations before or after . No markdown .Jsut raw JSON.
                Use excatly this structure :
                {
                "role_summary" : "one line description",
                "must_have_skill":["skill 1","skill 2"],
                "good_to_have_skill" : ["skill1","skill2"],
                "company_type":"Early startup / Growth startup / Mid-size product / Enterprise",
                "experience_years": "X-Y years",
                "honest_take": "one paragraph"
                }

"""
             },
             {
                 "role":"user",
                 "content":f"Analyse the Job description\n\n{jd_text}"
             }

        ]
    )

    raw=response.choices[0].message.content
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        print("the model didnot return json")
        print(raw)
        parsed = None  

    
    return parsed




sample_jd = """
About the Role
We are hiring Backend Engineers for our API team, responsible for exposing and managing a family of ML models — ASR, TTS, LLM, Vision, and more — over high-performance APIs. You will build low-latency, fault-tolerant, and cloud-agnostic systems that serve millions of requests reliably across Azure, AWS, GCP, and on-prem infrastructures.

What You'll Do
Design, develop, and optimise Python-based APIs (FastAPI, Django, Flask, or similar) for serving ML models at scale.
Build robust communication layers using HTTP, WebSockets, and gRPC.
Architect low-latency, fault-tolerant, and secure backend systems for real-time inference workloads.
Implement authentication, rate limiting, prioritisation, and secure coding practices.
Develop and manage integrations with voice agent SDKs, LLM SDKs, and related AI interfaces.
Work with PostgreSQL, Redis, and ClickHouse for data management and performance optimisation.
Build event-driven and streaming architectures using Kafka and Redis Streams.
Collaborate on canary deployments, feature rollouts, and CI/CD pipelines for smooth production releases.
Ensure systems are observable, reliable, and vendor-agnostic across multiple cloud environments.
What We're Looking For
Strong proficiency in Python and hands-on experience with FastAPI, Django, Flask, or similar frameworks.
Deep understanding of HTTP, WebSockets, and gRPC protocols.
Proven experience building low-latency, distributed backend systems.
Hands-on experience with PostgreSQL, Redis, ClickHouse, or related data systems.
Familiarity with Kafka or Redis Streams for message handling.
Solid understanding of API authentication, authorisation, and security best practices.
Experience with Docker, Kubernetes, and CI/CD pipelines.
Hands-on experience with at least one major cloud platform (Azure preferred).

"""
result = analyser(sample_jd)
# Now you can USE the data, not just print it
print("Role:", result["role_summary"])
print("Must-have skills:", result["must_have_skill"])
print("Experience needed:", result["experience_years"])
print("Skill count:", len(result["must_have_skill"]))

# Simulate a skill gap check
my_skills = ["SQL", "Python", "Power BI", "Tableau"]
missing = [s for s in result["must_have_skill"] if s not in my_skills]
print("\nSkills I'm missing:", missing)

