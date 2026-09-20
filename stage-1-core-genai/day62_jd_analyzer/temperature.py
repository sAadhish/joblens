from groq import Groq
import time
import os
from dotenv import load_dotenv

load_dotenv()


groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise ValueError("Missing GROQ_API_KEY. Add it to .env (or export GROQ_API_KEY).")

client = Groq(api_key=groq_key)


# Test 1 — Temperature 0 (should be same every run)
print("===== Temperature 0 =====")
for i in range(5):
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Write a creative one-line tagline for a coffee shop."}],
        temperature=0
    )
    print(f"Run {i+1}:", r.choices[0].message.content.strip())
    time.sleep(2)

print("---")

# Test 2 — Temperature 1 (should vary each run)
print("===== Temperature 1 =====")
for i in range(5):
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Write a creative one-line tagline for a coffee shop."}],
        temperature=1
    )
    print(f"Run {i+1}:", r.choices[0].message.content.strip())
    time.sleep(2)

print("---")

# Test 3 — Token usage
print("===== Token Usage =====")
r = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "What is a token in LLMs? Explain in 2 sentences."}],
    temperature=0
)
print("Answer:", r.choices[0].message.content)
print("Prompt tokens:", r.usage.prompt_tokens)
print("Reply tokens:", r.usage.completion_tokens)