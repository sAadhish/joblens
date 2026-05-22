import chromadb
from sentence_transformers import SentenceTransformer
import hashlib

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client()

collection = client.create_collection(
    name = "resumes",
    metadata={"hnsw:space":"cosine"}
    )

resumes=[
    "5 years of data analysis, SQL, and Python experience",
    "Worked as a BI developer building dashboards in Qlik Sense",
    "Experience in digital marketing and SEO campaigns",
    "Machine learning engineer with TensorFlow and PyTorch",
    "Data scientist with experience in statistical modeling and R",
    "Full stack developer with React and Node.js experience",
    "Product manager with experience in agile and roadmap planning",
    "Python developer with FastAPI and PostgreSQL experience",
]

emmbedding = model.encode(resumes).tolist()
def get_id(text):
    return hashlib.md5(text.encode()).hexdigest()   #use hashid so that when duplicate comes it wont crash 
#inserting to chromaDB
collection.add(
#    ids=[f"resume_{i}" for i in range(len(resumes))],
    embeddings=emmbedding,
    documents=resumes,
    ids=[get_id(resume) for resume in resumes]
)

print(f"stored {collection.count()} resumes in vector db")

# --- Search ---
def search_resumes(job_requirement,top_k=3):
    query_embedding=model.encode(job_requirement).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    print(f"\nJob: {job_requirement}")
    print("Top matches:")
    MINIMUM_SIMILARITY = 0.35
    for i , (doc,distance) in enumerate(zip(results["documents"][0],results["distances"][0])):
        similarity = 1 - distance
 
        if similarity >= MINIMUM_SIMILARITY:
            print(f"Rank {i+1}: {doc[:60]} → {similarity:.3f}")
        else:
            print(f"Rank {i+1}: No confident match found")


search_resumes("Looking for a data analyst with SQL skills")
search_resumes("Need a Python backend developer")
search_resumes("Hiring a machine learning engineer")