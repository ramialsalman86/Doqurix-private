"""
Doqurix Web - Streamlit Web Interface
A web-based version of the Doqurix Document Analysis application
"""

import streamlit as st
import os
import sys
from pathlib import Path
import time

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Doqurix - Document Intelligence",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI with proper text colors
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global text fix */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main app - light background for readability */
    .stApp {
        background: #f8fafc;
    }
    
    /* Make sure all text is visible */
    .stApp p, .stApp span, .stApp label, .stApp div, .stMarkdown {
        color: #1e293b !important;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(99, 102, 241, 0.25);
        user-select: none;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        cursor: default;
        pointer-events: none;
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        padding: 0;
        cursor: default;
        user-select: none;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9) !important;
        font-size: 1rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
        cursor: default;
        user-select: none;
    }
    
    /* Section titles */
    .section-title {
        color: #1e293b !important;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Card styling */
    .info-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    
    .info-card h3 {
        color: #1e293b !important;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    
    .info-card p {
        color: #64748b !important;
        font-size: 0.95rem;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Answer box styling */
    .answer-box {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border-left: 5px solid #10b981;
        padding: 1.5rem;
        border-radius: 0 16px 16px 0;
        margin: 1rem 0;
    }
    
    .answer-box p {
        color: #065f46 !important;
        font-size: 1rem;
        line-height: 1.7;
        margin: 0;
    }
    
    /* Context box styling */
    .context-box {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border-left: 5px solid #f59e0b;
        padding: 1.25rem;
        border-radius: 0 12px 12px 0;
        margin: 0.75rem 0;
    }
    
    .context-box p {
        color: #92400e !important;
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Status badges */
    .status-ready {
        background: #d1fae5;
        color: #065f46 !important;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    .status-pending {
        background: #fef3c7;
        color: #92400e !important;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    .doc-count {
        background: #e0e7ff;
        color: #3730a3 !important;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white !important;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }
    
    /* Input styling */
    .stTextArea textarea {
        background: white !important;
        color: #1e293b !important;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        font-size: 1rem;
    }
    
    .stTextArea textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    .stTextArea textarea::placeholder {
        color: #94a3b8 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white !important;
    }
    
    /* Document Delete buttons - red styling with clear text */
    [data-testid="stSidebar"] .stButton > button:has(> div > p:contains("Delete")),
    [data-testid="stSidebar"] .stButton > button:has(> div > p:contains("Clear")) {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.25) 0%, rgba(185, 28, 28, 0.3) 100%) !important;
        color: #fecaca !important;
        padding: 6px 12px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        border: 1px solid rgba(220, 38, 38, 0.5) !important;
        margin-top: 0 !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:has(> div > p:contains("Delete")):hover,
    [data-testid="stSidebar"] .stButton > button:has(> div > p:contains("Clear")):hover {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.4) 0%, rgba(185, 28, 28, 0.5) 100%) !important;
        transform: none !important;
    }

    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.1);
        border: 2px dashed rgba(255,255,255,0.3);
        border-radius: 12px;
        padding: 1rem;
    }
    
    [data-testid="stFileUploader"] label {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] div {
        color: #ffffff !important;
    }
    
    /* Uploaded file name in uploader */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
        background: rgba(99, 102, 241, 0.3) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] span,
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] p,
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] div {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stFileUploader"] button {
        background: #6366f1 !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    [data-testid="stFileUploader"] section {
        background: transparent !important;
    }
    
    [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }
    
    /* File size text */
    [data-testid="stFileUploader"] small {
        color: #e2e8f0 !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    
    .stRadio label {
        color: #1e293b !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 12px;
        font-weight: 600;
        color: #1e293b !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Document list item - clear white text - HIGH PRIORITY */
    .loaded-doc-item {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.5) 0%, rgba(139, 92, 246, 0.4) 100%) !important;
        padding: 14px 18px !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
        border: 2px solid rgba(255,255,255,0.4) !important;
    }
    
    .loaded-doc-item .doc-name {
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 6px rgba(0,0,0,0.7) !important;
        letter-spacing: 0.5px !important;
        display: block !important;
    }
    
    /* No documents message - HIGH PRIORITY */
    .no-docs-box {
        background: rgba(100, 116, 139, 0.3) !important;
        border: 2px dashed rgba(255,255,255,0.5) !important;
        border-radius: 10px !important;
        padding: 24px !important;
        text-align: center !important;
        margin: 12px 0 !important;
    }
    
    .no-docs-box .no-docs-title {
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 6px rgba(0,0,0,0.7) !important;
        margin: 0 !important;
        display: block !important;
    }
    
    .no-docs-box .no-docs-subtitle {
        color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        text-shadow: 0 2px 6px rgba(0,0,0,0.7) !important;
        margin: 10px 0 0 0 !important;
        display: block !important;
    }
    
    .doc-item {
        background: rgba(99, 102, 241, 0.3);
        padding: 0.6rem 0.8rem;
        border-radius: 10px;
        margin: 0.4rem 0;
        font-size: 0.9rem;
        color: white !important;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.2);
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-height: 38px;
    }
    
    .doc-item span {
        color: white !important;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .doc-item .del-btn {
        background: rgba(239, 68, 68, 0.3);
        color: #fca5a5 !important;
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 6px;
        padding: 0.25rem 0.5rem;
        cursor: pointer;
        font-size: 0.85rem;
        margin-left: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .doc-item .del-btn:hover {
        background: rgba(239, 68, 68, 0.5);
    }
    
    /* Progress container */
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .progress-title {
        color: white !important;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .progress-status {
        color: rgba(255,255,255,0.8) !important;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    /* Main content buttons - ensure text visibility */
    .stButton > button {
        color: white !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Ensure button text is always white */
    .stButton > button span,
    .stButton > button p {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.documents = []
    st.session_state.chunks_count = 0
    st.session_state.llm = None
    st.session_state.embedder = None
    st.session_state.reranker = None
    st.session_state.collection = None
    st.session_state.chroma_client = None
    st.session_state.bm25_corpus = []
    st.session_state.models_loaded = False
    st.session_state.last_contexts = None
    st.session_state.last_question = None
    st.session_state.last_answer = None


def get_app_paths():
    """Get application paths"""
    appdata = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')))
    user_data_dir = appdata / "Doqurix"
    user_data_dir.mkdir(exist_ok=True)
    
    models_dir = user_data_dir / "models"
    data_dir = user_data_dir / "data"
    vector_store_dir = data_dir / "vector_store"
    
    models_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)
    vector_store_dir.mkdir(exist_ok=True)
    
    return models_dir, data_dir, vector_store_dir


def load_models():
    """Load all AI models"""
    from llama_cpp import Llama
    from sentence_transformers import SentenceTransformer, CrossEncoder
    import chromadb
    from chromadb.config import Settings
    
    models_dir, data_dir, vector_store_dir = get_app_paths()
    
    # Load LLM
    model_path = models_dir / "qwen2.5-1.5b-instruct-q4_k_m.gguf"
    
    if not model_path.exists():
        return None, None, None, None, None, "Model not found"
    
    llm = Llama(
        model_path=str(model_path),
        n_ctx=3072,
        n_threads=os.cpu_count() or 4,
        n_batch=512,
        n_gpu_layers=0,
        verbose=False,
        use_mlock=True
    )
    
    # Load embedder
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Load reranker
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    # Initialize ChromaDB
    chroma_client = chromadb.Client(Settings(
        persist_directory=str(vector_store_dir),
        anonymized_telemetry=False
    ))
    
    try:
        collection = chroma_client.get_collection("documents")
    except:
        collection = chroma_client.create_collection("documents")
    
    return llm, embedder, reranker, chroma_client, collection, None


def extract_text_from_pdf(file):
    """Extract text from uploaded PDF"""
    import PyPDF2
    
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def smart_chunk_text(text, chunk_size=600, overlap=200):
    """Smart text chunking"""
    import re
    
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        words = sentence.split()
        sentence_length = len(words)
        
        if current_length + sentence_length > chunk_size and current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text.strip()) > 100:
                chunks.append(chunk_text)
            
            overlap_sentences = []
            overlap_length = 0
            for s in reversed(current_chunk):
                if overlap_length + len(s.split()) <= overlap:
                    overlap_sentences.insert(0, s)
                    overlap_length += len(s.split())
                else:
                    break
            
            current_chunk = overlap_sentences
            current_length = overlap_length
        
        current_chunk.append(sentence)
        current_length += sentence_length
    
    if current_chunk:
        chunk_text = ' '.join(current_chunk)
        if len(chunk_text.strip()) > 100:
            chunks.append(chunk_text)
    
    return chunks


def add_document_to_db(file_name, text, embedder, collection):
    """Process and add document to vector store"""
    chunks = smart_chunk_text(text)
    
    for i, chunk in enumerate(chunks):
        embedding = embedder.encode(chunk).tolist()
        doc_id = f"{file_name}_{i}_{int(time.time())}"
        collection.add(
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{
                "source": file_name,
                "chunk_id": i,
                "page": i // 3
            }],
            ids=[doc_id]
        )
    
    return len(chunks)


def hybrid_search(question, embedder, collection, bm25_corpus, n_results=15):
    """Perform hybrid search"""
    import numpy as np
    from rank_bm25 import BM25Okapi
    
    collection_data = collection.get()
    if not collection_data['documents']:
        return []
    
    question_embedding = embedder.encode(question).tolist()
    
    num_docs = len(collection_data['documents'])
    query_n = min(n_results, num_docs)
    
    vector_results = collection.query(
        query_embeddings=[question_embedding],
        n_results=query_n
    )
    
    combined_docs = {}
    k = 60
    
    if vector_results['documents'] and vector_results['documents'][0]:
        for rank, (doc, metadata) in enumerate(zip(vector_results['documents'][0], 
                                                     vector_results['metadatas'][0])):
            doc_key = doc[:150]
            if doc_key not in combined_docs:
                combined_docs[doc_key] = {
                    'doc': doc, 
                    'metadata': metadata, 
                    'score': 0
                }
            combined_docs[doc_key]['score'] += 1 / (k + rank)
    
    # BM25 search
    if bm25_corpus and len(bm25_corpus) > 0:
        tokenized_corpus = [doc.lower().split() for doc in bm25_corpus]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = question.lower().split()
        bm25_scores = bm25.get_scores(tokenized_query)
        top_bm25_indices = np.argsort(bm25_scores)[-n_results:][::-1]
        
        all_docs = collection.get()
        for rank, idx in enumerate(top_bm25_indices):
            if idx < len(bm25_corpus):
                doc = bm25_corpus[idx]
                doc_key = doc[:150]
                
                if doc_key not in combined_docs:
                    if idx < len(all_docs['metadatas']):
                        metadata = all_docs['metadatas'][idx]
                        combined_docs[doc_key] = {
                            'doc': doc, 
                            'metadata': metadata, 
                            'score': 0
                        }
                
                if doc_key in combined_docs:
                    combined_docs[doc_key]['score'] += 1 / (k + rank)
    
    sorted_docs = sorted(combined_docs.values(), key=lambda x: x['score'], reverse=True)
    return sorted_docs[:n_results]


def rerank_documents(question, doc_results, reranker, top_k=5):
    """Rerank documents using cross-encoder"""
    if not doc_results:
        return []
    
    documents = [d['doc'] for d in doc_results]
    pairs = [[question, doc] for doc in documents]
    scores = reranker.predict(pairs)
    
    for i, doc_result in enumerate(doc_results):
        doc_result['rerank_score'] = float(scores[i])
        doc_result['final_score'] = (
            0.3 * doc_result['score'] +
            0.7 * doc_result['rerank_score']
        )
    
    reranked = sorted(doc_results, key=lambda x: x['final_score'], reverse=True)
    return reranked[:top_k]


def generate_answer(question, contexts, llm, action='answer'):
    """Generate answer using LLM"""
    num_contexts = 3
    context_text = "\n\n".join([c['doc'] for c in contexts[:num_contexts]])
    
    if action == 'summarize':
        prompt = f"""<|im_start|>system
You are a professional assistant providing clear, well-structured summaries.<|im_end|>
<|im_start|>user
Provide a clear and professional summary of the following content. Use proper paragraphs and avoid bullet points or numbered lists. Write in a natural, flowing narrative style.

Content:
{context_text}

Summary:<|im_end|>
<|im_start|>assistant
"""
    else:
        prompt = f"""<|im_start|>system
You are a professional assistant providing clear, concise answers. Write in complete sentences and paragraphs, not bullet points or lists.<|im_end|>
<|im_start|>user
Based on the following context, answer the question in a clear, professional manner. Write your answer in flowing paragraphs without using bullet points, numbered lists, or special formatting.

Context:
{context_text}

Question: {question}

Answer:<|im_end|>
<|im_start|>assistant
"""
    
    output = llm(
        prompt,
        max_tokens=300,
        temperature=0.7,
        top_p=0.9,
        repeat_penalty=1.1,
        stop=["<|im_end|>", "<|im_start|>"],
        top_k=40
    )
    
    answer = output['choices'][0]['text'].strip()
    return answer


# Main app UI
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>◆ DOQURIX Web</h1>
        <p>AI-Powered Document Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-initialize AI Engine on first load
    if not st.session_state.models_loaded and not st.session_state.get('init_started', False):
        st.session_state.init_started = True
        
        # Show loading in main area
        init_container = st.container()
        with init_container:
            st.markdown("### 🚀 Initializing AI Engine...")
            st.markdown("Please wait while we load the AI models.")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.markdown("**Step 1/4:** Loading language model...")
                progress_bar.progress(10)
                
                llm, embedder, reranker, chroma_client, collection, error = load_models()
                
                if error:
                    st.error(f"❌ {error}. Please run the desktop app first to download models.")
                    st.session_state.init_started = False
                    st.stop()
                
                progress_bar.progress(40)
                status_text.markdown("**Step 2/4:** Loading search engine...")
                
                st.session_state.llm = llm
                st.session_state.embedder = embedder
                progress_bar.progress(60)
                status_text.markdown("**Step 3/4:** Loading ranking engine...")
                
                st.session_state.reranker = reranker
                st.session_state.chroma_client = chroma_client
                st.session_state.collection = collection
                progress_bar.progress(80)
                status_text.markdown("**Step 4/4:** Loading document database...")
                
                # Load existing documents
                all_docs = collection.get()
                if all_docs['documents']:
                    st.session_state.bm25_corpus = all_docs['documents']
                    st.session_state.chunks_count = len(all_docs['documents'])
                    sources = set()
                    for meta in all_docs['metadatas']:
                        if 'source' in meta:
                            sources.add(meta['source'])
                    st.session_state.documents = list(sources)
                
                progress_bar.progress(100)
                status_text.markdown("**✓ AI Engine Ready!**")
                st.session_state.models_loaded = True
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"Failed to load models: {str(e)}")
                st.session_state.init_started = False
                st.stop()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📁 Document Hub")
        st.markdown("---")
        
        # Model status
        if st.session_state.models_loaded:
            st.markdown('<span class="status-ready">✓ AI Engine Ready</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-pending">⏳ Initializing...</span>', unsafe_allow_html=True)
            st.markdown("")
            if st.button("🔄 Retry Initialization", use_container_width=True, key="init_btn"):
                st.session_state.init_started = False
                st.rerun()
        
        st.markdown("---")
        
        # File uploader with clear label
        st.markdown("### 📄 Upload Documents")
        st.markdown("*Drop PDF files below or click to browse*")
        uploaded_files = st.file_uploader(
            "Drop PDF files here or click to browse",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more PDF files to analyze"
        )
        
        # Auto-process uploaded files (no button needed)
        if uploaded_files and st.session_state.models_loaded:
            new_files = [f for f in uploaded_files if f.name not in st.session_state.documents]
            if new_files:
                # Auto-process immediately
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, file in enumerate(new_files):
                    status_text.text(f"📄 Processing: {file.name}")
                    try:
                        # Extract text
                        text = extract_text_from_pdf(file)
                        if text.strip():
                            # Add to database
                            chunks = add_document_to_db(
                                file.name, 
                                text, 
                                st.session_state.embedder, 
                                st.session_state.collection
                            )
                            st.session_state.documents.append(file.name)
                            st.session_state.chunks_count += chunks
                            
                            # Update BM25 corpus
                            all_docs = st.session_state.collection.get()
                            st.session_state.bm25_corpus = all_docs['documents']
                        else:
                            st.warning(f"Could not extract text from {file.name}")
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {str(e)}")
                    
                    progress_bar.progress((i + 1) / len(new_files))
                
                status_text.empty()
                progress_bar.empty()
                st.success(f"✓ Added {len(new_files)} document(s)!")
                time.sleep(0.5)
                st.rerun()
        
        # Show loaded documents
        st.markdown("---")
        st.markdown("### 📚 Loaded Documents")
        
        if st.session_state.documents:
            st.markdown(f'<span class="doc-count">📊 {len(st.session_state.documents)} docs | {st.session_state.chunks_count} chunks</span>', unsafe_allow_html=True)
            st.markdown("")
            
            # Document list with delete buttons - using session state for deletion
            if 'delete_doc' not in st.session_state:
                st.session_state.delete_doc = None
            
            # Handle pending deletion with progress bar
            if st.session_state.delete_doc is not None:
                doc_to_delete = st.session_state.delete_doc
                st.session_state.delete_doc = None
                
                # Show deletion progress
                delete_status = st.empty()
                delete_progress = st.progress(0)
                
                try:
                    delete_status.markdown(f"<p style='color: #fecaca; font-weight: 500;'>🗑️ Deleting: {doc_to_delete}...</p>", unsafe_allow_html=True)
                    delete_progress.progress(20)
                    
                    all_data = st.session_state.collection.get()
                    ids_to_delete = []
                    
                    delete_progress.progress(40)
                    
                    for i, metadata in enumerate(all_data['metadatas']):
                        if metadata.get('source') == doc_to_delete:
                            ids_to_delete.append(all_data['ids'][i])
                    
                    delete_progress.progress(60)
                    
                    if ids_to_delete:
                        st.session_state.collection.delete(ids=ids_to_delete)
                        st.session_state.chunks_count -= len(ids_to_delete)
                    
                    delete_progress.progress(80)
                    
                    st.session_state.documents.remove(doc_to_delete)
                    
                    all_docs = st.session_state.collection.get()
                    st.session_state.bm25_corpus = all_docs['documents'] if all_docs['documents'] else []
                    
                    st.session_state.last_contexts = None
                    st.session_state.last_answer = None
                    
                    delete_progress.progress(100)
                    delete_status.markdown(f"<p style='color: #86efac; font-weight: 600;'>✓ Deleted successfully!</p>", unsafe_allow_html=True)
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    delete_status.empty()
                    delete_progress.empty()
                    st.error(f"Error: {str(e)}")
            
            # Display each document with delete button
            docs_to_display = st.session_state.documents.copy()
            for idx, doc in enumerate(docs_to_display):
                # Truncate long names but keep it readable
                if len(doc) <= 25:
                    display_name = doc
                else:
                    display_name = doc[:22] + "..."
                
                # Document container with name - using CSS class for visibility
                st.markdown(f'''
                    <div class="loaded-doc-item">
                        <span class="doc-name">📄 {display_name}</span>
                    </div>
                ''', unsafe_allow_html=True)
                
                # Delete button - directly trigger deletion
                delete_clicked = st.button("🗑️ Delete", key=f"delete_btn_{idx}_{doc[:10]}", help=f"Remove '{doc}'")
                if delete_clicked:
                    st.session_state.delete_doc = doc
                    st.rerun()
            
            # Spacer before Clear All
            st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
            
            # Clear All with progress
            if st.button("🗑️ Clear All Documents", use_container_width=True, key="clear_all"):
                clear_status = st.empty()
                clear_progress = st.progress(0)
                
                try:
                    clear_status.markdown("<p style='color: #fecaca; font-weight: 500;'>🗑️ Clearing all documents...</p>", unsafe_allow_html=True)
                    clear_progress.progress(25)
                    
                    # Get all IDs and delete
                    all_data = st.session_state.collection.get()
                    clear_progress.progress(50)
                    
                    if all_data['ids']:
                        st.session_state.collection.delete(ids=all_data['ids'])
                    
                    clear_progress.progress(75)
                    
                    # Reset state
                    st.session_state.documents = []
                    st.session_state.chunks_count = 0
                    st.session_state.bm25_corpus = []
                    st.session_state.last_contexts = None
                    st.session_state.last_answer = None
                    
                    clear_progress.progress(100)
                    clear_status.markdown("<p style='color: #86efac; font-weight: 600;'>✓ All documents cleared!</p>", unsafe_allow_html=True)
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    clear_status.empty()
                    clear_progress.empty()
                    st.error(f"Error clearing documents: {str(e)}")
        else:
            # Clear, visible "no documents" message - using CSS class
            st.markdown('''
                <div class="no-docs-box">
                    <span class="no-docs-title">📭 No documents loaded yet</span>
                    <span class="no-docs-subtitle">Upload PDFs above to get started</span>
                </div>
            ''', unsafe_allow_html=True)
        
        # About section
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        **Doqurix Web** v1.0
        
        Upload PDFs and ask questions using AI-powered document analysis.
        """)
    
    # Main content area
    if not st.session_state.models_loaded:
        st.markdown("### 👋 Welcome to Doqurix Web!")
        st.info("👈 Click **Initialize AI Engine** in the sidebar to get started.")
        
        st.markdown("---")
        st.markdown("### ✨ Features")
        
        # Feature cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="info-card">
                <h3>📄 Smart Upload</h3>
                <p>Upload PDF documents and our AI will automatically extract and index the content for intelligent searching.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-card">
                <h3>💬 Natural Q&A</h3>
                <p>Ask questions in natural language and get accurate, context-aware answers from your documents.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="info-card">
                <h3>🎯 Source Tracking</h3>
                <p>See exactly where answers come from with highlighted source passages and page references.</p>
            </div>
            """, unsafe_allow_html=True)
        
        return
    
    # Q&A Interface - Two columns
    col_main, col_context = st.columns([3, 2])
    
    with col_main:
        st.markdown('<div class="section-title">💬 Ask a Question</div>', unsafe_allow_html=True)
        
        # Question input
        question = st.text_area(
            "Your Question",
            placeholder="What would you like to know about your documents?",
            height=100,
            key="question_input"
        )
        
        # Search mode
        search_mode = st.radio(
            "Search Mode",
            ["⚡ Quick (Faster)", "🎯 Detailed (Better)"],
            horizontal=True,
            key="search_mode"
        )
        
        # Action buttons with clear labels
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            ask_button = st.button("🔍 ASK", use_container_width=True, type="primary", key="ask_btn", help="Get an answer to your question")
        
        with col_btn2:
            summarize_button = st.button("📝 SUMMARIZE", use_container_width=True, key="sum_btn", help="Summarize all documents")
        
        # Process question and show answer directly after buttons
        if ask_button or summarize_button:
            # Check if documents are loaded
            collection_data = st.session_state.collection.get()
            has_documents = collection_data['documents'] and len(collection_data['documents']) > 0
            
            if not has_documents:
                st.warning("⚠️ Please upload and process documents first using the sidebar.")
            elif not question.strip() and ask_button:
                st.warning("⚠️ Please enter a question.")
            else:
                mode = "basic" if "Quick" in search_mode else "advanced"
                action = 'summarize' if summarize_button else 'answer'
                query = "Provide a comprehensive summary of all the documents" if summarize_button else question
                
                with st.spinner("🤔 Analyzing your documents..."):
                    try:
                        # Search
                        n_results = 8 if mode == "basic" else 15
                        top_k = 3 if mode == "basic" else 5
                        
                        # Refresh BM25 corpus
                        all_docs = st.session_state.collection.get()
                        st.session_state.bm25_corpus = all_docs['documents']
                        
                        doc_results = hybrid_search(
                            query, 
                            st.session_state.embedder, 
                            st.session_state.collection,
                            st.session_state.bm25_corpus,
                            n_results
                        )
                        
                        if doc_results:
                            # Rerank
                            contexts = rerank_documents(query, doc_results, st.session_state.reranker, top_k)
                            
                            # Generate answer
                            answer = generate_answer(query, contexts, st.session_state.llm, action)
                            
                            # Store in session state
                            st.session_state.last_contexts = contexts
                            st.session_state.last_question = query
                            st.session_state.last_answer = answer
                            st.rerun()
                        else:
                            st.error("❌ No relevant content found in your documents.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        # Display answer directly after buttons
        st.markdown("---")
        st.markdown('<div class="section-title">💡 Answer</div>', unsafe_allow_html=True)
        
        if st.session_state.last_answer:
            st.markdown(f"""
            <div class="answer-box">
                <p>{st.session_state.last_answer}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-card">
                <p>Your answer will appear here after you ask a question.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col_context:
        st.markdown('<div class="section-title">🔍 Source Context</div>', unsafe_allow_html=True)
        
        # Add spacing to align with the text area (matches "Your Question" label height)
        st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
        
        if st.session_state.last_contexts:
            for i, ctx in enumerate(st.session_state.last_contexts, 1):
                source_name = ctx['metadata'].get('source', 'Unknown')
                page_num = ctx['metadata'].get('page', 0)
                
                with st.expander(f"📄 Source {i}: {source_name}", expanded=(i==1)):
                    st.markdown(f"**Page:** ~{page_num}")
                    
                    # Get text and highlight keywords
                    text = ctx['doc'][:600]
                    if len(ctx['doc']) > 600:
                        text += "..."
                    
                    st.markdown(f"""
                    <div class="context-box">
                        <p>{text}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-card">
                <p>Ask a question to see the relevant source passages here.</p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
