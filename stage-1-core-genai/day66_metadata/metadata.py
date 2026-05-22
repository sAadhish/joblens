import chromadb
from sentence_transformers import SentenceTransformer
import hashlib

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client()

collection =client.create_collection(
    name="resumes_with_metadata",
    metadata={"hnsw:space": "cosine"}
)


resumes = [
    {
        "text": "5 years of data analysis, SQL, and Python experience",
        "metadata": {
            "role_type": "data",
            "experience_years": 5,
            "skills": "SQL, Python, data analysis",
            "location": "Chennai"
        }
    },
    {
        "text": "Worked as a BI developer building dashboards in Qlik Sense",
        "metadata": {
            "role_type": "data",
            "experience_years": 1,
            "skills": "Qlik Sense, dashboards, BI",
            "location": "Chennai"
        }
    },
    {
        "text": "Experience in digital marketing and SEO campaigns",
        "metadata": {
            "role_type": "marketing",
            "experience_years": 3,
            "skills": "SEO, digital marketing, campaigns",
            "location": "Mumbai"
        }
    },
    {
        "text": "Machine learning engineer with TensorFlow and PyTorch",
        "metadata": {
            "role_type": "ml",
            "experience_years": 4,
            "skills": "TensorFlow, PyTorch, ML",
            "location": "Bangalore"
        }
    },
    {
        "text": "Data scientist with experience in statistical modeling and R",
        "metadata": {
            "role_type": "data",
            "experience_years": 3,
            "skills": "R, statistics, modeling",
            "location": "Bangalore"
        }
    },
    {
        "text": "Full stack developer with React and Node.js experience",
        "metadata": {
            "role_type": "engineering",
            "experience_years": 2,
            "skills": "React, Node.js, JavaScript",
            "location": "Chennai"
        }
    },
    {
        "text": "Product manager with experience in agile and roadmap planning",
        "metadata": {
            "role_type": "product",
            "experience_years": 5,
            "skills": "agile, roadmap, product strategy",
            "location": "Mumbai"
        }
    },
    {
        "text": "Python developer with FastAPI and PostgreSQL experience",
        "metadata": {
            "role_type": "engineering",
            "experience_years": 2,
            "skills": "Python, FastAPI, PostgreSQL",
            "location": "Chennai"
        }
    },
]

def get_id(text):
    return hashlib.md5(text.encode()).hexdigest()

collection.add(
    documents=[r["text"] for r in resumes],
    embeddings=model.encode([r["text"] for r in resumes]).tolist(),
    metadatas=[r["metadata"] for r in resumes],
    ids=[get_id(r["text"]) for r in resumes]
)

print(f"stored {collection.count()} resumes\n")

def build_filter(role_type=None, min_experience=None, location=None):
    conditions =[]

    if role_type:
        conditions.append({"role_type": role_type})
    
    if min_experience:
        conditions.append({"experience_years": {"$gte": min_experience}})
    
    if location:
        conditions.append({"location": location})

    if len(conditions)==0:
        return None
    if len(conditions)==1:
        return conditions[0]
    # Multiple filters — wrap in $and
    return {"$and": conditions}


def search_resumes(job_requirement,role_type =None,min_experience=None,location=None,top_k=3):

    query_embedding=model.encode([job_requirement]).tolist()
    print("Query embedding length:", len(query_embedding[0])) ##debug

    where_filter = build_filter(role_type, min_experience, location)

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where=where_filter if where_filter else None
    )

    print(f"Job: {job_requirement}")
    if where_filter:
        print(f"Filters: {where_filter}")

     ###### debug
    print("Raw distances:", results["distances"][0])
    print("Raw documents:", results["documents"][0])

    MINIMUM_SIMILARITY = 0.35
    print("Top matches:")
    
    for i ,(doc, distance,meta) in enumerate(zip(results["documents"][0],results["distances"][0],results["metadatas"][0])):

        similarity = 1 - distance
        if similarity >= MINIMUM_SIMILARITY:
            print(f"  Rank {i+1}: {doc[:55]}")
            print(f"           Score: {similarity:.3f} | "
                  f"Experience: {meta['experience_years']}yrs | "
                  f"Location: {meta['location']}")
        else:
            print(f"  Rank {i+1}: No confident match (score: {similarity:.3f})")
    print()


print("=" * 55)
print("EXPERIMENT 3 — Filter by minimum experience")
print("=" * 55)
search_resumes(
    "Looking for a data analyst with SQL skills",
    role_type="data",
    min_experience=3
)

'''

Day 66 — Notes:
1. What is metadata and how is it different from document text?
meta data is used for keyword search , while text data we use semantic search . to get more accurate result we will first filter the text using metadata search and then use semantic search

2. Why can't you do semantic search on metadata?
sematic search only go for the meanings , while we need to filter out using neta data 

3. What metadata would you store for JDs in JobLens — and why?
role_type      →  filter "show me only ML roles"
experience     →  filter "show me 2-4 year roles only"
location       →  filter "Chennai or remote only"
skills         →  filter "must have Python"
company_type   →  filter "startup only, no enterprise" 
salary_range   →  filter "15-25 LPA only"          
remote_ok      →  filter "remote friendly yes/no"   
'''