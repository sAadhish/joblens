import re
import pdfplumber
import urllib.request
from pathlib import Path
from joblens.logger import logger


#Clean Text

def clean_text(text:str) ->str:
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    return text.strip()


# Load Text File
def load_text_file(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text=f.read()

    cleaned = clean_text(raw_text)
    logger.info(f"Text Loader Extracted {len(cleaned)} characters from {file_path}")
    return cleaned


# Load pdf

def load_pdf(file_path: str) -> str:
    path=Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not Found: {file_path}")
    if path.suffix.lower()!= ".pdf":
        raise ValueError(f"Expected .pdf file, got {path.suffix}")
    
    full_text=[]
    with pdfplumber.open(file_path) as pdf:
        total_pages = len(pdf.pages)

    for page_num,page in enumerate(pdf.pages,1):
         page_text = page.extract_text()

         if page_text:
             full_text.append(f"[Page {page_num}]\n{page_text.strip()}")
         else :
             logger.warning(f"PDFLoader: page {page_num} has no extractable text")
    
    if not full_text:
        raise ValueError("No text extracted — PDF may be entirely scanned images")
    
    raw_text = "\n\n".join(full_text)
    cleaned = clean_text(raw_text)
    logger.info(f"PDFLoader extracted {len(cleaned)} characters "
                f"from {len(full_text)}/{total_pages} pages")
    return cleaned

# weburl

def load_webpage(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        raise ValueError("Invalid URL — must start with http:// or https://")

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
        text = re.sub(r"<[^>]+>", " ", html)
    except Exception as e:
        raise RuntimeError(f"Failed to load webpage {url}: {e}")

    cleaned = clean_text(text)
    logger.info(f"WebLoader extracted {len(cleaned)} characters from {url}")
    return cleaned


def load_document(source: str) -> str:

    if source.startswith(("http://", "https://")):
        return load_webpage(source)

    path = Path(source)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return load_pdf(source)
    elif suffix in [".txt", ".md"]:
        return load_text_file(source)
    else:
        raise ValueError(f"Unsupported source type: {suffix}")

            

