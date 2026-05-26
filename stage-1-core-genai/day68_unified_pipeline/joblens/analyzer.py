import re
import json
from config import groq_client
from logger import logger

def analyze_jd(jd_text: str) -> dict | None:
    """Takes raw JD text, returns structured JSON. Returns None on failure."""

    if not jd_text or not jd_text.strip():
        logger.warning("analyze_jd received empty JD text")
        return None

    try:
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
        cleaned = re.sub(r"```json|```", "", raw).strip()
        structured = json.loads(cleaned)
        logger.info(f"JD analyzed successfully — role: {structured.get('role')}")
        return structured

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {e} | Raw output: {raw[:100]}")
        return None

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return None