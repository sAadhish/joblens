from langchain_community.document_loaders import PyPDFLoader,TextLoader
from langchain_core.documents import Document
from config import Config
from logger import logger

class DocumentLoader:

    def load_pdf(self,file_path:str)->list[Document] :
        loader=PyPDFLoader(file_path)
        documents=loader.load()

        logger.info(f"PDF Loaded {len(documents)} pages from {file_path}")

        return documents
    
    def load_text(self,file_path:str)->list[Document]:
        loader=TextLoader(file_path)
        documents=loader.load()
        logger.info(f"TextFile Loaded {len(documents)} pages from {file_path}")
        return documents
    
    def load_from_string(self,text:str,source_label:str)->list[Document]:
        return [Document(page_content=text, metadata={"source":source_label} )]
    

    def load(self,source):

        source = source.lower()

        if source.endswith(".pdf"):
            return self.load_pdf(source)

        elif source.endswith(".txt"):
            return self.load_text(source)

        elif source.endswith(".md"):
            return self.load_text(source)

        else:
            raise ValueError(f"Unsupported file type: {source}")
    

     
    

    






