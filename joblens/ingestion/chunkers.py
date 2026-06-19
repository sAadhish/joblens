import nltk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from joblens.logger import logger


try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")
    nltk.download("punkt_tab")


#Paragraph Chunking

## split long paragraphs if exceeds max chunk
def _split_long_paragraph(text : str,max_size: int)->list[str]:
    sentences = nltk.sent_tokenize(text)
    chunks=[]
    current=""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <=max_size:
            current +=" " + sentence
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence
    if current.strip():
        chunks.append(current.strip())
    return chunks

# Paragraph splitting

def chunk_by_paragraph(
        text: str,
        min_chunk_size: int = 100,
        max_chunk_size: int = 800,
        overlap_sentences: int = 1
)-> list[dict]:
    raw_paragraph =text.split("\n\n")
    chunks = []
    previous_sentences = []
    
