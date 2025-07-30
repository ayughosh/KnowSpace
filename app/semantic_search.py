import os
import pickle
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

#choose a small, local embedding model

EMBED_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
INDEX_PATH=os.path.join(os.path.dirname(__file__), "faiss_index")
MAPPING_PATH=os.path.join(os.path.dirname(__file__),"id_map.pkl")

class SemanticIndex:
    def __init__(self):
        self.embeddings=HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
        #load or initialize index + id --> DB-id map
        if os.path.exists(INDEX_PATH) and os.path.exists(MAPPING_PATH):
            self.vectorstore=FAISS.load_local(INDEX_PATH,self.embeddings)
            with open(MAPPING_PATH,"rb") as f:
                self.id_map=pickle.load(f)
        else:
            self.vectorstore=FAISS(self.embeddings.embed_query,embeddings=self.embeddings)
            self.id_map={}
            
    def add(self, entry_id:int, text:str):
        vec_id=str(entry_id)
        self.vectorstore.add_texts([text],ids=[vec_id])
        self.id_map[vec_id]=entry_id
        self._persist()
        
    def search(self, query:str, k:int=5):
        docs=self.vectorstore.similarity_search(query,k=k)
        #retrieve original DB ids
        return[(self.id_map[hit.metadata["id"]],hit.page_content) for hit in docs]
    
    def _persist(self):
        os.makedirs(INDEX_PATH,exist_ok=True)
        self.vectorstore.save_local(INDEX_PATH)
        with open(MAPPING_PATH,"wb") as f:
            pickle.dump(self.id_map,f)
            
# expose a singleton
semantic_index = SemanticIndex()