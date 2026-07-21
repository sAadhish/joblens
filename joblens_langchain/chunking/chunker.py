from loader.loader import DocumentLoader
from config import Config
from models.schemas import DocumentChunk
from langchain_text_splitters import RecursiveCharacterTextSplitter
from logger import logger


class TextChunker:

    def __init__(self,chunk_size=Config.CHUNK_SIZE,chunk_overlap=Config.CHUNK_OVERLAP): 
        self.splitter=RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )
        

    def chunk(self,documents,source_label:str)-> list[DocumentChunk]:
        chunks=self.splitter.split_documents(documents)
        result=[]

        for i , chunk in enumerate(chunks):
            result.append(
                DocumentChunk(
                    text=chunk.page_content,
                    source_label=source_label,
                    chunk_index=i,
                    char_count=len(chunk.page_content),
                    strategy="recursive"
                )
            )

            logger.info(f"Created {len(result)} chunks")

        return result

        
        


