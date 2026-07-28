RULES :
IF U CHANGE ANYTHING WRITE HERE WHAT CHANGE YOU MADE AND WHY.
""Agent till synthesizer is my code 
""SIR WALI COPAT FILE DAAL AUR PHIR CHALA KE DEKH TERE WALA CODE CHAL RHA H YA NHI KYUKI MAINE TRY KIA NHI CHAL RHA THA""

==================compat.py=========================================
"""
Compatibility helpers for LangChain versions.
"""
def _install_stubs():
        pass

======================LOADER.PY============================================================
from langchain_classic.schema import Document
import os
from pypdf import PdfReader
def load_documents(data_dir):
    if not os.path.isdir(data_dir):
        return []
    docs =[]
    for name in sorted(os.listdir(data_dir)):
        path = os.path.join(data_dir, name)
        if name.endswith((".md",".txt")):
            text = open(path, encoding="utf-8").read()
        elif name.endswith(".pdf"):
            reader = PdfReader(path)
            text ="\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            continue
        docs.append(Document(page_content=text, metadata={"source":name}))
    return docs

===========================CHUNKING.PY==========================================
from langchain_classic.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(documents, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = []
    for doc in documents:
        pieces = splitter.split_text(doc.page_content)
        idx = 0
        for piece in pieces:
            if not piece.strip():
                continue
            meta = dict(doc.metadata)
            meta["chunk_index"] = idx
            chunks.append(Document(page_content=piece, metadata=meta))
            idx += 1 
    return chunks

=======================VECTORDB.PY====================================
"""vectordb.py — Task 3: Embeddings + ChromaDB vector store."""


from sklearn.feature_extraction.text import HashingVectorizer
import chromadb 
import uuid
vect = HashingVectorizer(
    n_features=256,
    norm="l2"
)

def embed_text(text):
    vec = vect.transform([text]).toarray().tolist()[0]
    return [float(x) for x in vec]

def embed_texts(texts):
    return vect.transform(texts).toarray().tolist()

def build_store(chunks):
    client = chromadb.Client()
    collection = client.get_or_create_collection(
        name =f"rag_{uuid.uuid4().hex[:8]}"
    )
    docs =[]
    metadatas = []
    embeddings=[]
    ids = []
    
    for i, chunk in enumerate(chunks):
        if chunk.page_content in docs:
            continue
        docs.append(chunk.page_content)
        metadatas.append(chunk.metadata)
        embeddings.append(embed_text(chunk.page_content))
        ids.append(str(i))
    if docs:
        collection.add(
            documents=docs,
            metadatas=metadatas,
            embeddings = embeddings,
            ids = ids
        )
    return collection
def search_store(collection, query, top_k=3):
    if collection.count()==0:
        return []
    results = collection.query(
        query_embeddings = [embed_text(query)],
        n_results=min(top_k, collection.count()),
        include=["documents","metadatas","distances"]
    )
    return [
        {
            "content":doc,
            "metadata": meta,
            "score":round(1-dist/2,4)
        }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
    ]


==================agents.py=================================

from langchain_classic.prompts import PromptTemplate
from .vectordb import search_store

INSUFFICIENT= 'Insufficient Information'

RAG_PROMPT = PromptTemplate(
    input_variables=["context","question"],
    template="""
    context = {context}
    question = {question}
    You should ONLY answer from given context if there is no sufficient data and answer is not found
    return Insufficient Information
    """
)

def build_prompt(context, question):
    return RAG_PROMPT.format(context=context, question)

def get_answer(chunks, question):
    q_words = set(question.lower().split())
    best, best_score = INSUFFICIENT, -1
    for chunk in chunks:
        if type(chunk)==dict:
            content = chunk.get("content", "")
        else:
            content = str(chunk)
        for sentence in content.lower().split():
            s = sentence.strip()
            score = len(q_words & set(s.lower().split()))
            if score>best_score:
                best = s
                best_score = score
    return best

def rag_answer(collection, question, top_k=3):
    res = search_store(collection, question, top_k=top_k)
    if not res:
        return {
            "question":question,
            "answer":INSUFFICIENT,
            "retrieved_sources":[],
            "confidence_score":0.0
        } 
    answer = [r.get("content", "") for r in res]
    sources = sorted([r["metadata"].get("source") for r in res])
    score = sum(r.get("score") for r in res) / len(res)
    return {
        "question":question,
        "answer":answer,
        "retrieved_sources":sources,
        "confidence_score":score
    }

DOMAIN_KEYWORDS = {"patient", "doctor", "medicine", "pharmacy", "insurance", "emergency", "admission", "hospital", "ice", "treatment"}

def needs_retrieval(question):
    q_words = set(question.lower().split())
    return bool(q_words & DOMAIN_KEYWORDS)

def agentic_answer(collection, question):
    if not needs_retrieval(question):
        return {
            "question":question,
            "decision":"direct",
            "answer":"Please ask about hospital policies and procedures.",
            "sources":[],
            "grounded":False
        }
    answer = rag_answer(collection, question)
    return {
            "question":question,
            "decision":"retrieve",
            "answer":answer.get("answer"),
            "sources":answer.get("retrieved_sources"),
            "grounded":answer.get("confidence_score")>=0.5
    }

def planner(question):
    li = []
    for subq in question.split(" and "):
        for s in subq.split("?"):
            li.append(s)
    return li

def worker(collection, sub_query):
    results = agentic_answer(collection, sub_query)
    return {
        "sub_query":sub_query,
        "answer":results.get("answer"),
        "sources":results.get("sources")
    }

def synthesizer(worker_results):
    final_answer = ""
    sources = []
    for d in worker_results:
        final_answer = final_answer + " " +d.get("answer")
        sources.append(d.get("sources"))
    li = []
    for sr in sources:
        for s in sr:
            li.append(s)
    return {
        "final_answer":final_answer,
        "sources":sorted(li)
    }

=====================================================================23-test-cases-==============

PERMISSIONS = {
    "planner": ["plan"],
    "worker" : ["retrieve", "answer"],
    "synthesizer": ["synthesize"]
}
def is_allowed(agent,action):
    return action in PERMISSIONS.get(agent,[])
def validate_answer(answer,context):
    if not context:
        return {"is_grounded":False,"confidence":0.0}
    a=answer.lower().split()
    c=context.lower().split()
    conf=sum(w in c for w in a)/len(a)
    return {
        "is_confidence":conf>=0.5,
        "confidence":conf
    }


def run_workflow(collection, question: str) -> Dict[str, Any]:
    trace       = []
    message_log = []
    # Step 1 — planner
    sub_queries = planner(question)
    trace.append({"node": "planner", "sub_queries": sub_queries})
    # Step 2 — workers
    worker_results = []
    for sq in sub_queries:
        message_log.append({"from": "planner", "to": "worker", "content": sq})
        result = worker(collection, sq)
        worker_results.append(result)
        trace.append({"node": "worker", "sub_query": sq})
        message_log.append({"from": "worker", "to": "synthesizer", "content": result["answer"]})
    # Step 3 — synthesizer
    synth = synthesizer(worker_results)
    trace.append({"node": "synthesizer"})
    # Step 4 — validate (inline word overlap)
    context    = " ".join(w.get("answer", "") for w in worker_results)
    a_words    = set(synth["final_answer"].lower().split())
    c_words    = set(context.lower().split())
    confidence = round(len(a_words & c_words) / len(a_words), 2) if a_words else 0.0
    validation = {"is_grounded": confidence >= 0.5, "confidence": min(confidence, 1.0)}
    return {"question": question, "final_answer": synth["final_answer"],
            "sources": synth["sources"], "trace": trace,
            "message_log": message_log, "validation": validation}
===============api.py=============================
import os

from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel

from src.loader import load_documents
from src.chunking import chunk_documents
from src.vectordb import build_store
from src.agents import rag_answer
from src.agents import run_workflow

app = FastAPI()
def build_pipeline(data_dir="data"):
    docs = load_documents(data_dir)
    chunks = chunk_documents(docs)
    return build_store(chunks), len(chunks)

COLLECTION, CHUNK_COUNT = build_pipeline()

class IngestRequest(BaseModel):
    data_dir: str

class QuestionRequest(BaseModel):
    question: str

@app.get("/health")
def health():
    return {
        "status": "running",
        "indexed": CHUNK_COUNT
    }

@app.post("/ingest")
def ingest(req: IngestRequest):
    global COLLECTION
    global CHUNK_COUNT

    if not req.data_dir.strip():
        raise HTTPException(
            status_code=400,
            detail="invalid directory"
        )

    docs = load_documents(req.data_dir)

    if not docs:
        raise HTTPException(
            status_code=400,
            detail="empty directory"
        )

    chunks = chunk_documents(docs)

    COLLECTION = build_store(chunks)
    CHUNK_COUNT = len(chunks)

    return {
        "chunks_indexed": CHUNK_COUNT
    }


@app.post("/ask")
def ask(req: QuestionRequest):
    if not req.question.strip():
        raise HTTPException(
            status_code=400,
            detail="empty query"
        )

    return rag_answer(
        COLLECTION,
        req.question
    )


@app.post("/workflow")
def workflow(req: QuestionRequest):
    if not req.question.strip():
        raise HTTPException(
            status_code=400,
            detail="empty query"
        )

    return run_workflow(
        COLLECTION,
        req.question
    )
    
=====================api.py======================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .agents import rag_answer, run_workflow
from .chunking import chunk_documents
from .loader import load_documents
from .vectordb import build_store

app = FastAPI(title="Enterprise RAG API")

# Shared state
_col   = None
_count = 0


def _build(data_dir: str = "data"):
    global _col, _count
    chunks = chunk_documents(load_documents(data_dir))
    _col   = build_store(chunks)
    _count = _col.count()


_build("data")


class IngestRequest(BaseModel):
    data_dir: str = "data"

class AskRequest(BaseModel):
    question: str

class WorkflowRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "running", "indexed": _count}


@app.post("/ingest")
def ingest(request: IngestRequest):
    if not request.data_dir.strip():
        raise HTTPException(status_code=400, detail="data_dir cannot be empty")
    _build(request.data_dir)
    return {"chunks_indexed": _count}


@app.post("/ask")
def ask(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    return rag_answer(_col, request.question)


@app.post("/workflow")
def workflow(request: WorkflowRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    return run_workflow(_col, request.question)

    
