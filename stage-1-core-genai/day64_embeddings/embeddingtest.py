from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as num

model=SentenceTransformer("all-MiniLM-L6-v2")

job_requirement = "Looking for someone with data analysis and SQL experience"

resumes = [
    "5 years of data analysis, SQL, and Python experience",
    "Worked as a BI developer building dashboards in Qlik Sense",
    "Experience in digital marketing and SEO campaigns",
    "Machine learning engineer with TensorFlow and PyTorch",
]

job_embedding= model.encode([job_requirement]) #it should be in [] , because we need a list to encode
resume_embedding=model.encode(resumes)

scores=cosine_similarity(job_embedding,resume_embedding)[0]

ranked = sorted(zip(scores,resumes),reverse=True)
for i , (score, resume)in enumerate(ranked):
    print(f"Rank {i+1}: {resume[:60]} → {score:.4f}")
    


