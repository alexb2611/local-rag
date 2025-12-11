import streamlit as st
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import subprocess
import json
import tempfile

# LangChain imports - using modern approach (no deprecated imports)
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Custom CSV processor
from csv_processor import create_time_based_chunks, load_multiple_csv_files, get_data_summary

# Load environment variables
load_dotenv()

# Function to get available Ollama models
@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_ollama_models():
    """Fetch list of installed Ollama models"""
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    # Extract model name (first column)
                    model_name = line.split()[0]
                    models.append(model_name)
            return models if models else ["No models found"]
        else:
            return ["Ollama not available"]
    except Exception as e:
        return [f"Error: {str(e)}"]

# Configuration
CHROMA_DB_PATH = "./chroma_db_timeseries"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"

st.set_page_config(page_title="Time-Series RAG", page_icon="📊", layout="wide")
st.title("📊 Time-Series Data RAG System")
st.markdown("Query your environmental monitoring data using natural language")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Provider selection
    llm_provider = st.radio(
        "Select LLM Provider:",
        ["Claude (Anthropic)", "Ollama (Local)"],
        help="Choose between cloud API (Claude) or local models (Ollama)"
    )

    # Model selection based on provider
    if llm_provider == "Claude (Anthropic)":
        model_choice = "Claude Sonnet 4"
        selected_model = "claude-sonnet-4-20250514"
    else:
        # Get available Ollama models
        available_models = get_ollama_models()

        # Default selection
        default_index = 0
        if "granite4:small-h" in available_models:
            default_index = available_models.index("granite4:small-h")

        selected_model = st.selectbox(
            "Select Ollama Model:",
            available_models,
            index=default_index,
            help="Choose from your installed Ollama models"
        )
        model_choice = f"Ollama ({selected_model})"

    # Display current model info
    st.info(f"🤖 Active Model: **{selected_model}**")

    st.divider()

    # Data loading mode
    data_mode = st.radio(
        "Data Loading Mode:",
        ["Upload Single CSV", "Process Directory"],
        help="Upload one file or process multiple CSV files from a directory"
    )
    
    # Chunking configuration
    hours_per_chunk = st.slider(
        "Hours per chunk:",
        min_value=1,
        max_value=12,
        value=4,
        help="How many hours of data to group together"
    )
    
    st.divider()
    st.markdown("### 💡 Example Queries")
    st.markdown("""
    - What was the temperature trend throughout the day?
    - When was the coldest period?
    - What was the average humidity overnight?
    - How did atmospheric pressure change?
    - Were there any battery issues?
    """)
    
    st.divider()
    st.markdown("### 🗄️ Database Management")
    if st.button("🗑️ Clear Database", type="secondary", use_container_width=True):
        if 'vectorstore' in st.session_state:
            try:
                # Get the collection and delete all documents
                collection = st.session_state['vectorstore']._collection
                # Get all IDs and delete them
                result = collection.get()
                all_ids = result['ids'] if result else []
                
                if all_ids:
                    collection.delete(ids=all_ids)
                    count = len(all_ids)
                    # Clear session state
                    del st.session_state['vectorstore']
                    if 'conversation_history' in st.session_state:
                        st.session_state['conversation_history'] = []
                    if 'query_counter' in st.session_state:
                        st.session_state['query_counter'] = 0
                    # Reset file uploader to clear any previously uploaded file
                    if 'file_uploader_key' in st.session_state:
                        st.session_state['file_uploader_key'] += 1
                    
                    st.success(f"✅ Cleared {count} documents from database")
                    st.rerun()
                else:
                    st.info("Database is already empty")
                    # Still clear session state
                    del st.session_state['vectorstore']
                    if 'conversation_history' in st.session_state:
                        st.session_state['conversation_history'] = []
                    if 'file_uploader_key' in st.session_state:
                        st.session_state['file_uploader_key'] += 1
                    st.rerun()
            except Exception as e:
                st.error(f"Error clearing database: {str(e)}")
        else:
            st.warning("No database loaded to clear")


# Initialize LLM based on selection
@st.cache_resource
def get_llm(provider, model_name):
    """Initialize the selected LLM"""
    if provider == "Claude (Anthropic)":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.error("ANTHROPIC_API_KEY not found in environment variables!")
            st.stop()
        return ChatAnthropic(
            model=model_name,
            anthropic_api_key=api_key,
            max_tokens=2000
        )
    else:  # Ollama
        return ChatOllama(
            model=model_name,
            base_url="http://127.0.0.1:11434"
        )

# Initialize embeddings
@st.cache_resource
def get_embeddings():
    """Initialize Ollama embeddings"""
    return OllamaEmbeddings(
        model=OLLAMA_EMBEDDING_MODEL,
        base_url="http://127.0.0.1:11434"
    )

# Create or load vector store
def create_vector_store(documents):
    """Create a vector store from documents"""
    embeddings = get_embeddings()
    
    # Create new vector store
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    
    return vectorstore

# Load existing vector store
def load_vector_store():
    """Load existing vector store"""
    embeddings = get_embeddings()
    
    if os.path.exists(CHROMA_DB_PATH):
        vectorstore = Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=embeddings
        )
        # Check if it has any documents
        try:
            doc_count = vectorstore._collection.count()
            if doc_count > 0:
                return vectorstore, doc_count
            else:
                return None, 0
        except:
            return vectorstore, None
    return None, 0

# Create RAG chain using modern LCEL approach
def create_rag_chain(vectorstore, llm):
    """Create a RAG chain using the vector store and LLM"""
    
    # Create retriever with MMR search
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 50,          # Number of chunks to retrieve (increased for better coverage)
            "fetch_k": 100    # Number of candidates for MMR
        }
    )
    
    # Create prompt template
    template = """You are an expert at analyzing environmental monitoring data from LoRa sensors.

Use the following pieces of time-series data to answer the question. The data includes temperature, 
humidity, pressure, battery status, and signal quality (RSSI/SNR) measurements.

Context (time-series data chunks):
{context}

Question: {question}

Instructions:
- Provide specific values, time ranges, and trends from the data
- When discussing trends, mention the specific time periods
- Include relevant statistics (min, max, average) when available
- If the question asks about a specific time period, focus on that period
- If data is insufficient, say so clearly

Answer:"""

    prompt = ChatPromptTemplate.from_template(template)
    
    # Format documents function
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Create the chain using LCEL (LangChain Expression Language)
    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain, retriever

# Main app logic
def main():
    llm = get_llm(llm_provider, selected_model)
    
    # Data loading section
    if data_mode == "Upload Single CSV":
        st.header("📤 Upload CSV File")
        # Initialize file uploader key for clearing after database reset
        if 'file_uploader_key' not in st.session_state:
            st.session_state['file_uploader_key'] = 0
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file (format: lora_data_YYYY-MM-DD.csv)",
            type=["csv"],
            key=f"file_uploader_{st.session_state['file_uploader_key']}"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily (cross-platform)
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Show data preview
            df = pd.read_csv(temp_path)
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Process button
            if st.button("🔄 Process and Index Data", type="primary"):
                with st.spinner("Processing CSV file..."):
                    # Create chunks
                    documents = create_time_based_chunks(temp_path, hours_per_chunk=hours_per_chunk)
                    
                    if documents:
                        st.success(f"✅ Created {len(documents)} time-based chunks")
                        
                        # Create vector store
                        with st.spinner("Creating vector store..."):
                            vectorstore = create_vector_store(documents)
                            st.session_state['vectorstore'] = vectorstore
                            st.success("✅ Vector store created successfully!")
                    else:
                        st.error("❌ Failed to create chunks from CSV")
    
    else:  # Process Directory
        st.header("📁 Process Multiple CSV Files")
        directory_path = st.text_input(
            "Enter directory path containing CSV files:",
            placeholder="/path/to/csv/files"
        )
        
        if directory_path and st.button("🔄 Process Directory", type="primary"):
            if os.path.exists(directory_path):
                with st.spinner("Processing multiple CSV files..."):
                    documents = load_multiple_csv_files(directory_path, hours_per_chunk=hours_per_chunk)
                    
                    if documents:
                        st.success(f"✅ Created {len(documents)} chunks from directory")
                        
                        # Show summary
                        summary = get_data_summary(documents)
                        st.subheader("📊 Data Summary")
                        st.text(summary)
                        
                        # Create vector store
                        with st.spinner("Creating vector store..."):
                            vectorstore = create_vector_store(documents)
                            st.session_state['vectorstore'] = vectorstore
                            st.success("✅ Vector store created successfully!")
                    else:
                        st.error("❌ No valid CSV files found in directory")
            else:
                st.error("❌ Directory does not exist")
    
    # Query section
    if 'vectorstore' not in st.session_state:
        # Try to load existing vector store
        vectorstore, doc_count = load_vector_store()
        if vectorstore and doc_count and doc_count > 0:
            st.session_state['vectorstore'] = vectorstore
            st.info(f"ℹ️ Loaded existing vector store ({doc_count} documents)")
    
    if 'vectorstore' in st.session_state:
        st.header("💬 Ask Questions")
        
        # Initialize conversation history in session state
        if 'conversation_history' not in st.session_state:
            st.session_state['conversation_history'] = []
        
        # Create RAG chain
        chain, retriever = create_rag_chain(st.session_state['vectorstore'], llm)
        
        # Display conversation history
        if st.session_state['conversation_history']:
            st.subheader("📜 Conversation History")
            
            for i, (q, a, docs) in enumerate(st.session_state['conversation_history']):
                with st.container():
                    st.markdown(f"**Q{i+1}:** {q}")
                    st.markdown(f"**A{i+1}:** {a}")
                    
                    # Show source documents for this Q&A
                    with st.expander(f"📄 Source Data for Q{i+1}"):
                        for j, doc in enumerate(docs, 1):
                            st.markdown(f"**Chunk {j}:**")
                            st.markdown(f"- **Time Range:** {doc.metadata.get('start_time', 'N/A')} to {doc.metadata.get('end_time', 'N/A')}")
                            st.markdown(f"- **Date:** {doc.metadata.get('date', 'N/A')}")
                            st.text(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content)
                            if j < len(docs):
                                st.divider()
                    
                    st.markdown("---")
            
            # Clear history button
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🗑️ Clear History"):
                    st.session_state['conversation_history'] = []
                    st.rerun()
        
        # Initialize submission counter for widget key rotation
        if 'query_counter' not in st.session_state:
            st.session_state['query_counter'] = 0
        
        # Initialize processing flag
        if 'processing_query' not in st.session_state:
            st.session_state['processing_query'] = False
        
        # Only show input form if not currently processing
        if not st.session_state['processing_query']:
            # Query input - key changes after each submission to force reset
            query = st.text_input(
                "Enter your question:",
                placeholder="What was the temperature trend during the morning?",
                key=f"query_input_{st.session_state['query_counter']}",
                label_visibility="visible"
            )
            
            # Submit button
            submit_button = st.button("Ask Question", type="primary")
            
            if submit_button and query:
                # Set processing flag to hide this section during rerun
                st.session_state['processing_query'] = True
                
                with st.spinner("Analyzing data..."):
                    # Get answer and source docs
                    answer = chain.invoke(query)
                    docs = retriever.invoke(query)
                    
                    # Add to conversation history
                    st.session_state['conversation_history'].append((query, answer, docs))
                    
                    # Increment counter to create new widget with fresh key
                    st.session_state['query_counter'] += 1
                    
                    # Clear processing flag
                    st.session_state['processing_query'] = False
                    
                    # Rerun to show updated history
                    st.rerun()
        else:
            # Show processing message if flag is set
            st.info("Processing your question...")

if __name__ == "__main__":
    main()
