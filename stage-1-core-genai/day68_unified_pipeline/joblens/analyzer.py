from config import groq_client
import json
import re

def analyze_jd(jd_text: str) -> dict:
    """Takes raw JD text, returns structured JSON."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": """You are a senior tech recruiter in India.
Analyze the job description and return ONLY this JSON structure.
No markdown. No explanation. Raw JSON only. 
{
  "role": "job title",
  "company_type": "startup/product/enterprise",
  "role_type": "engineering/data/ai/product/marketing",
  "must_have_skills": ["skill1", "skill2"],
  "good_to_have_skills": ["skill1", "skill2"],
  "experience_min": 2,
  "experience_max": 5,
  "location": "city name",
  "remote_ok": true,
  "one_line_summary": "what this role actually is"
}"""
            },
            {
                "role": "user",
                "content": f"Analyze this JD:\n\n{jd_text}"
            }
        ]
    )

    raw = response.choices[0].message.content
    cleaned = re.sub(r"```json|```", "", raw).strip()  # strip markdown first

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("Model did not return valid JSON. Raw output:")
        print(raw)
        return {}
    

