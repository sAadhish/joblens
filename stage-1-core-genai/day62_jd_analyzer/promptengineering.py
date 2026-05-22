from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise ValueError("Missing GROQ_API_KEY. Add it to .env (or export GROQ_API_KEY).")

Client = Groq(api_key=groq_key)

def analyze_jd(jd_text):
    response = Client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        messages=[
           {
            "role":"system",
            "content": """ You are a senior tech recruiter in India with 10 years of experience 
at product-based startups. You analyze job descriptions with precision.
When given a JD , respond in the exact same format:

ROLE SUMMARY:
[One line — what this role actually is]

MUST-HAVE SKILLS:
- [skill 1]
- [skill 2]

GOOD-TO-HAVE SKILLS:
- [skill 1]
- [skill 2]

COMPANY TYPE:
[Early startup / Growth startup / Mid-size product / Enterprise — pick one and explain in one line]

HONEST TAKE :
[One paragraph — what kind of person actually gets this role. Be direct.]

            """
           },
          {
            "role":"user",
            "content":f"Analyse this job description :\n\n{jd_text}"
          }
     ]
)
    return response.choices[0].message.content




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

print(analyze_jd(sample_jd))