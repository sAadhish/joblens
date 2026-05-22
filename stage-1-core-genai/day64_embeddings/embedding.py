from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as num

model=SentenceTransformer("all-MiniLM-L6-v2")

"""
text = "I have experience in machine learning"
embedding = model.encode(text)

print("Text :" ,text)
print("Embedding shape:" , embedding.shape)
print("First 5 numbers :",embedding[:5])
"""

"""
sentences = [
    "machine learning engineer with Python experience",   # query
    "I built predictive models using Python",  # similar meaning
    "I worked with neural networks and NLP",   # similar meaning  
    "I am a yoga instructor",                  # unrelated
    "I managed social media accounts",         # unrelated
]

embeddings = model.encode(sentences) # this will be 2D list
query_embeding=embeddings[0].reshape(1,-1) # we are taking first values from the list , so its 1D and we are again converting to 2D
score= cosine_similarity(query_embeding,embeddings[1:]) # the scores for the encodes values which compared against the first value in a single row

print("\n--- Similarity Scores ---")
for i , score in enumerate(score[0]):
    print(f"{sentences[i+1][:45]:<45} → {score:.3f}")
"""

job_requirement = "Looking for someone with data analysis and SQL experience"

resumes = [
    "5 years of data analysis, SQL, and Python experience",
    "Worked as a BI developer building dashboards in Qlik Sense",
    "Experience in digital marketing and SEO campaigns",
    "Machine learning engineer with TensorFlow and PyTorch",
]

job_embedding = model.encode([job_requirement])
resume_embeddings = model.encode(resumes)

scores = cosine_similarity(job_embedding, resume_embeddings)[0] # cosine_similarity returns a 2d row , using[0] we are making it to 1D

print("\n--- Resume Match Scores ---")
ranked = sorted(zip(scores,resumes),reverse=True)

for i,(score,resume) in enumerate(ranked):
    print(f"[{i+1}]{resume[:60]}→ {score:3f}")