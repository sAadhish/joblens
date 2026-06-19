from config import groq_client
import json
import re

def analyze_gap(profile: str, jd_text: str, company: str) -> dict:
    """Returns structured skill gap analysis."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": """You are an expert career advisor for tech roles in India.
Given a candidate profile and job description, return ONLY this JSON.
No markdown. No explanation. Raw JSON only.

{
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "experience_gap": "candidate has X years, role needs Y-Z years",
  "gap_severity": "low/medium/high",
  "ready_in_weeks": 4,
  "top_advice": "one specific actionable sentence"
}"""
            },
            {
                "role": "user",
                "content": f"Candidate:\n{profile}\n\nJob at {company}:\n{jd_text}"
            }
        ]
    )

    raw = response.choices[0].message.content
    cleaned = re.sub(r"```json|```", "", raw).strip()
    return json.loads(cleaned)

