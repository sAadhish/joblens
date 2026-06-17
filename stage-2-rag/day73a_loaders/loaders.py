import re 
import pdfplumber 
from pathlib import Path
import urllib.request


# -------------------------------------------------------
# SHARED — Text Cleaner
# Every loader calls this before returning
# Written once, used by all
# -------------------------------------------------------


#Clean text
def clean_text(text: str) ->str:

    # Multiple spaces → single space
    text =re.sub(r" {2,}" , " ",text)
    # More than 2 newlines → exactly 2 (preserve paragraphs)
    text=re.sub(r"\n{3,}","\n\n",text)
    # Remove non-printable characters
    text = re.sub(r"[^\x20-\x7E\n]"," ",text)
    # Remove PDF bullet artifacts
    text = re.sub(r'\(cid:\d+\)', '', text)

    return text.strip()


# -------------------------------------------------------
# LOADER 1 — Plain Text
# -------------------------------------------------------
def load_text_file(file_path:str)-> str:

#validate
    path=Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found : {file_path}")
    
    # Open and Extract
    with open(file_path,"r",encoding="utf-8") as f:
        raw_text=f.read()

    #clean and return
    cleaned =clean_text(raw_text)
    print(f"[TextLoader] Extracted {len(cleaned)} characters")
    return cleaned


# -------------------------------------------------------
# LOADER 2 — PDF 
# -------------------------------------------------------

def load_pdf(file_path : str) -> str:

    #validate
    path =Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found : {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected .pdf file, got: {path.suffix}")
    
    #open and extract
    full_text=[]

    with pdfplumber.open(file_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"[PDFLoader] Found {total_pages} pages")
    
        for page_num , page in enumerate(pdf.pages,1):
            #extract text from pages
            page_text = page.extract_text()

            if page_text:
                full_text.append(page_text.strip())

            else:
                print(f"[PDFLoader] Warning: Page {page_num} has no text "
                      f"(possibly scanned image — skipping)")
                
    if not full_text:
        raise ValueError("No text extracted — PDF may be entirely scanned images")
    
    #join all the pages extracted 
    #clean and return 
    raw_text="\n\n".join(full_text)
    cleaned = clean_text(raw_text)
   # print(full_text)
    print(f"[PDFLoader] Extracted {len(cleaned)} characters "
          f"from {len(full_text)}/{total_pages} pages")
    return cleaned

# -------------------------------------------------------
# LOADER 3 — Web Page
# -------------------------------------------------------

def load_webpage(url: str) -> str:
    """
    Fetches a webpage and returns plain text.
    Strips all HTML tags.
    
    Pattern: Open → Extract → Clean → Return
    Same as every other loader.
    """

    # Step 1 — Validate
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid URL — must start with http:// or https://")

    # Step 2 — Fetch and extract
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        request = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(request, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")

        # Strip HTML tags — everything between < and >
        text = re.sub(r"<[^>]+>", " ", html)

    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error loading {url}: {e}")

    # Step 3 — Clean and return
    cleaned = clean_text(text)
    print(f"[WebLoader] Extracted {len(cleaned)} characters from {url}")
    return cleaned

# -------------------------------------------------------
# UNIVERSAL LOADER — single entry point
# This is the only function other modules should call
# It detects source type and routes to correct loader
# -------------------------------------------------------

def load_document(source:str) ->str:
    #web loader
    if source.startswith(("http://", "https://")):
        return load_webpage(source)

    path = Path(source)
    suffix=path.suffix.lower()
    #pdf
    if suffix ==".pdf":
        return load_pdf(source)
    #text 
    elif suffix in [".txt",".md"]:
        return load_text_file(source)
    
    else:
        raise ValueError(
            f"Unsupported source type: {suffix}\n"
            f"Supported: .pdf, .txt, .md, http/https URLs"
        )