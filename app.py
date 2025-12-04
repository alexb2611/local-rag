import os
import streamlit as st
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
import tempfile
import shutil
import chromadb
from chromadb.config import Settings
from models_config import get_model_list, get_model_display_names, get_model_config, EMBEDDING_MODEL

# Load environment variables
load_dotenv()

# Chroma persistent directory
CHROMA_PERSIST_DIR = "./chroma_db"

# Helper function to create ChromaDB client with proper settings
def get_chroma_client():
    """Get a ChromaDB client with proper settings for Streamlit"""
    # Ensure directory exists with proper permissions
    if not os.path.exists(CHROMA_PERSIST_DIR):
        os.makedirs(CHROMA_PERSIST_DIR, mode=0o777, exist_ok=True)

    # Create client with explicit settings
    return chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(
            allow_reset=True,
            anonymized_telemetry=False
        )
    )

# Initialize session state (must be done early, before sidebar)
if "messages" not in st.session_state:
    st.session_state.messages = []

if "vectorstores" not in st.session_state:
    st.session_state.vectorstores = {}  # Dictionary: {filename: vectorstore}

if "indexed_pdfs" not in st.session_state:
    st.session_state.indexed_pdfs = []  # List of indexed PDF filenames

if "selected_pdfs" not in st.session_state:
    st.session_state.selected_pdfs = []  # PDFs to search in

if "db_cleared" not in st.session_state:
    st.session_state.db_cleared = False  # Flag to track if DB was just cleared

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0  # Counter to reset file uploader

# Populate indexed_pdfs from database on first load (but not after clearing)
if not st.session_state.indexed_pdfs and not st.session_state.db_cleared:
    db_pdfs = []
    try:
        if os.path.exists(CHROMA_PERSIST_DIR):
            client = get_chroma_client()
            collections = client.list_collections()
            for collection in collections:
                if collection.name.startswith("pdf_"):
                    pdf_name = collection.name.replace("pdf_", "").replace("_", " ") + ".pdf"
                    db_pdfs.append(pdf_name)
                elif collection.name.startswith("md_"):
                    md_name = collection.name.replace("md_", "").replace("_", " ") + ".md"
                    db_pdfs.append(md_name)
    except:
        pass
    st.session_state.indexed_pdfs = db_pdfs
    # Also set selected_pdfs to all indexed PDFs by default
    st.session_state.selected_pdfs = db_pdfs.copy()

# Helper function to get all indexed PDFs
def get_indexed_pdfs_from_chroma():
    """Get list of all PDF and Markdown collections in Chroma database"""
    try:
        if os.path.exists(CHROMA_PERSIST_DIR):
            client = get_chroma_client()
            collections = client.list_collections()
            # Extract file names from collection names (format: pdf_filename or md_filename)
            file_names = []
            for collection in collections:
                if collection.name.startswith("pdf_"):
                    # Convert collection name back to PDF filename
                    file_name = collection.name.replace("pdf_", "").replace("_", " ") + ".pdf"
                    file_names.append(file_name)
                elif collection.name.startswith("md_"):
                    # Convert collection name back to Markdown filename
                    file_name = collection.name.replace("md_", "").replace("_", " ") + ".md"
                    file_names.append(file_name)
            return file_names
        return []
    except Exception as e:
        return []

# Helper function to clear database
def clear_chroma_database():
    """Clear all data from Chroma database by deleting collections, not the database itself"""
    try:
        if os.path.exists(CHROMA_PERSIST_DIR):
            # Get the client and delete all collections
            client = get_chroma_client()
            collections = client.list_collections()

            # Delete each collection
            for collection in collections:
                try:
                    client.delete_collection(name=collection.name)
                except Exception as e:
                    st.warning(f"Could not delete collection {collection.name}: {str(e)}")

            return True
        else:
            # If directory doesn't exist, create it
            os.makedirs(CHROMA_PERSIST_DIR, mode=0o777, exist_ok=True)
            return True
    except Exception as e:
        st.error(f"Error clearing database: {str(e)}")
        return False

# Page config
st.set_page_config(
    page_title="Document Q&A Assistant",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Question & Answer Assistant")
st.markdown("Upload a document and ask questions about its content!")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")

    # Get available models from config
    available_models = get_model_list()
    model_display_names = get_model_display_names()

    # Create display options for selectbox
    display_options = [model_display_names.get(m, m) for m in available_models]

    selected_display = st.selectbox(
        "Select Model",
        display_options,
        index=0
    )

    # Map back to actual model name
    model_choice = available_models[display_options.index(selected_display)]

    # Show model description if available
    model_config = get_model_config(model_choice)
    if model_config and model_config.get("description"):
        st.caption(model_config["description"])

    st.markdown("---")

    # Indexed PDFs Section
    st.markdown("### 📚 Indexed Documents")
    # Use session state which is updated immediately, rather than querying DB
    indexed_pdfs = st.session_state.indexed_pdfs if st.session_state.indexed_pdfs else []

    if indexed_pdfs:
        st.markdown(f"**Total Documents:** {len(indexed_pdfs)}")

        # PDF filter selection
        st.markdown("**Search in:**")
        search_all = st.checkbox("All PDFs", value=True)

        if search_all:
            st.session_state.selected_pdfs = indexed_pdfs.copy()
        else:
            selected = st.multiselect(
                "Select PDFs to search",
                indexed_pdfs,
                default=st.session_state.selected_pdfs if st.session_state.selected_pdfs else indexed_pdfs
            )
            st.session_state.selected_pdfs = selected

        # List all indexed PDFs
        with st.expander("View all indexed documents"):
            for pdf in indexed_pdfs:
                st.markdown(f"• {pdf}")

        # Clear database button
        st.markdown("---")
        if st.button("🗑️ Clear Database", type="secondary"):
            if st.session_state.get("confirm_clear", False):
                # Clear session state first
                st.session_state.vectorstores = {}
                st.session_state.indexed_pdfs = []
                st.session_state.selected_pdfs = []
                st.session_state.messages = []
                st.session_state.recently_uploaded = []  # Clear upload notifications
                st.session_state.confirm_clear = False
                st.session_state.db_cleared = True  # Mark that DB was cleared
                st.session_state.uploader_key += 1  # Reset file uploader

                # Then clear the database
                if clear_chroma_database():
                    st.success("Database cleared successfully!")
                else:
                    st.warning("Database directory not found or already cleared")

                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ Click again to confirm database deletion")
    else:
        st.info("No documents indexed yet")

    st.markdown("---")
    st.markdown("### About")
    st.markdown("This app uses RAG (Retrieval-Augmented Generation) to answer questions about your documents.")
    st.markdown("1. Upload PDF or Markdown files")
    st.markdown("2. Wait for processing")
    st.markdown("3. Select which documents to search")
    st.markdown("4. Ask questions!")

# Extract text from image-based PDFs using PyMuPDF
def extract_text_with_pymupdf(pdf_path, filename):
    """Extract text from PDF using PyMuPDF (better for image-based PDFs)"""
    from langchain_core.documents import Document
    
    doc = fitz.open(pdf_path)
    pages = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # Create a LangChain Document for each page
        pages.append(Document(
            page_content=text,
            metadata={
                "source": filename,
                "page": page_num
            }
        ))
    
    doc.close()
    return pages

# Initialize model and embeddings
@st.cache_resource
def get_model_and_embeddings(model_name):
    """Initialize the language model and embeddings"""
    # Get embeddings from config
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL["name"], keep_alive=0)

    # Get model configuration
    model_config = get_model_config(model_name)
    provider = model_config["provider"] if model_config else "ollama"

    # Initialize model based on provider
    if provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.error("⚠️ ANTHROPIC_API_KEY not found in environment variables. Please add it to your .env file.")
            st.stop()
        model = ChatAnthropic(model=model_name, anthropic_api_key=api_key)
    elif provider == "ollama":
        # keep_alive=0 unloads the model from GPU memory immediately after use
        model = OllamaLLM(model=model_name, keep_alive=0)
    else:
        st.error(f"⚠️ Unknown provider: {provider}. Please update the get_model_and_embeddings function in app.py.")
        st.stop()

    return model, embeddings

# Process markdown files
def process_markdown(uploaded_file):
    """Process uploaded Markdown file and create vector store"""
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    # Generate collection name from file name
    collection_name = f"md_{uploaded_file.name.replace('.md', '').replace(' ', '_').replace('.', '_')}"

    # Get embeddings
    _, embeddings = get_model_and_embeddings(model_choice)

    # Get ChromaDB client
    client = get_chroma_client()

    # Try to load existing collection first
    try:
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
            client=client
        )
        
        # Check if collection has documents
        collection_count = vectorstore._collection.count()
        if collection_count > 0:
            st.info(f"📚 Loaded existing collection with {collection_count} chunks")
            return vectorstore, collection_count
    except Exception as e:
        # Collection doesn't exist yet, we'll create it
        pass
    
    # Process new markdown file
    with st.spinner("Processing Markdown file..."):
        # Read the markdown content
        content = uploaded_file.getvalue().decode('utf-8')
        
        st.info(f"Loaded markdown file with {len(content)} characters")
        
        # Create a document
        doc = Document(
            page_content=content,
            metadata={
                "source": uploaded_file.name
            }
        )
        
        # Split the document into chunks for better retrieval
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents([doc])
        
        st.info(f"Split into {len(chunks)} chunks")
        
        # Create vector store with Chroma (persistent)
        st.info("Creating embeddings and storing in database...")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
            collection_name=collection_name,
            client=client
        )

        return vectorstore, len(chunks)

# Load and process PDF
def process_pdf(uploaded_file):
    """Process uploaded PDF and create vector store"""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    # Generate collection name from file name
    collection_name = f"pdf_{uploaded_file.name.replace('.pdf', '').replace(' ', '_').replace('.', '_')}"

    # Get embeddings
    _, embeddings = get_model_and_embeddings(model_choice)

    # Get ChromaDB client
    client = get_chroma_client()

    # Try to load existing collection first
    try:
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
            client=client
        )

        # Check if collection has documents
        collection_count = vectorstore._collection.count()
        if collection_count > 0:
            st.info(f"📚 Loaded existing collection with {collection_count} documents")
            return vectorstore, collection_count
    except Exception as e:
        # Collection doesn't exist yet, we'll create it
        pass

    # Process new PDF
    with st.spinner("Processing PDF..."):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            # Load PDF - use load() instead of load_and_split() for better reliability
            loader = PyPDFLoader(tmp_path)
            pages = loader.load()

            # Debug: Check if pages were loaded
            st.info(f"Loaded {len(pages)} pages from PDF")
            if len(pages) == 0:
                st.error("No pages extracted from PDF. The PDF might be image-based or corrupted.")
                return None, 0

            # Check if pages have content
            total_chars = sum(len(page.page_content) for page in pages)
            st.info(f"Total text extracted with PyPDFLoader: {total_chars} characters")

            # If no text extracted, try PyMuPDF as fallback
            if total_chars == 0:
                if PYMUPDF_AVAILABLE:
                    st.warning("⚠️ PyPDFLoader extracted no text. Trying PyMuPDF...")
                    pages = extract_text_with_pymupdf(tmp_path, uploaded_file.name)
                    total_chars = sum(len(page.page_content) for page in pages)
                    st.info(f"Total text extracted with PyMuPDF: {total_chars} characters")
                    
                    if total_chars == 0:
                        st.error("No text content found with either method. The PDF might be image-based and requires OCR.")
                        return None, 0
                else:
                    st.error("No text content found. Install PyMuPDF for better PDF support: pip install pymupdf")
                    return None, 0
            else:
                # Update metadata to use actual filename instead of temp file path
                for page in pages:
                    page.metadata['source'] = uploaded_file.name

            # Split documents into chunks for better retrieval
            # This is crucial for RAG to work well with large documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            chunks = text_splitter.split_documents(pages)
            
            st.info(f"Split into {len(chunks)} chunks for better retrieval")

            # Create vector store with Chroma (persistent)
            st.info("Creating embeddings and storing in database...")
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=CHROMA_PERSIST_DIR,
                collection_name=collection_name,
                client=client
            )

            return vectorstore, len(chunks)

        finally:
            # Clean up temp file
            os.unlink(tmp_path)

# Create combined retriever from multiple vectorstores
class CombinedRetriever:
    """Custom retriever that searches across multiple vectorstores"""
    def __init__(self, retrievers):
        self.retrievers = retrievers

    def invoke(self, query):
        """Retrieve documents from all retrievers and combine results"""
        # Handle both string queries and dict inputs
        if isinstance(query, dict):
            query = query.get("question", query.get("input", ""))
        
        all_docs = []
        for retriever in self.retrievers:
            try:
                docs = retriever.invoke(query)
                all_docs.extend(docs)
            except:
                pass
        return all_docs

    def get_relevant_documents(self, query):
        """For compatibility with older LangChain versions"""
        return self.invoke(query)
    
    def __or__(self, other):
        """Support pipe operator for LangChain LCEL"""
        from langchain_core.runnables import RunnableLambda
        return RunnableLambda(self.invoke) | other

def create_combined_retriever(vectorstores_dict, selected_pdf_names):
    """Create a retriever that searches across selected PDFs"""
    from langchain_core.runnables import RunnableLambda
    
    retrievers = []
    for pdf_name in selected_pdf_names:
        if pdf_name in vectorstores_dict:
            # Increase k to retrieve more chunks (default is 4, we use 15)
            # Use MMR for better diversity of retrieved chunks
            retrievers.append(vectorstores_dict[pdf_name].as_retriever(
                search_type="mmr",
                search_kwargs={"k": 15, "fetch_k": 30}
            ))

    if len(retrievers) == 0:
        return None
    elif len(retrievers) == 1:
        return retrievers[0]
    else:
        # Combine multiple retrievers and wrap in RunnableLambda
        combined = CombinedRetriever(retrievers)
        return RunnableLambda(combined.invoke)

# Create RAG chain
def create_rag_chain(retriever, model):
    """Create the RAG chain for question answering with source tracking"""
    if retriever is None:
        return None

    template = """
Answer the question based on the context below.
If you can't answer the question, reply "I don't know".

Context: {context}

Question: {question}
"""

    prompt = PromptTemplate.from_template(template)

    # Function to format documents for context
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Chain that returns both answer and sources
    chain = (
        {
            "context": itemgetter("question") | retriever | format_docs,
            "question": itemgetter("question"),
            "source_documents": itemgetter("question") | retriever
        }
        | RunnablePassthrough.assign(answer=prompt | model)
    )

    return chain

# CSS to hide file uploader list and show custom fade-out messages
st.markdown("""
<style>
/* Hide only the uploaded files list section, not the upload button */
[data-testid="stFileUploader"] section[data-testid="stFileUploaderFileData"] {
    display: none !important;
}

/* Also try alternate selector */
[data-testid="stFileUploader"] ul {
    display: none !important;
}

/* Fade out animation for success messages */
@keyframes fadeOut {
    0% { opacity: 1; }
    75% { opacity: 1; }
    100% { opacity: 0; }
}

.upload-success {
    animation: fadeOut 3.5s ease-out forwards;
    padding: 0.75rem 1rem;
    background-color: #d1e7dd;
    color: #0f5132;
    border-left: 4px solid #198754;
    margin-bottom: 0.5rem;
    border-radius: 4px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# Initialize upload state tracking
if "recently_uploaded" not in st.session_state:
    st.session_state.recently_uploaded = []

# File upload section
uploaded_files = st.file_uploader(
    "Upload your PDF(s) or Markdown file(s)",
    type=["pdf", "md"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.uploader_key}"
)

# Show recently uploaded files with auto-fade
if st.session_state.recently_uploaded:
    for pdf_name in st.session_state.recently_uploaded:
        st.markdown(f'<div class="upload-success">✅ {pdf_name} uploaded and processed!</div>', unsafe_allow_html=True)

    # Schedule clearing of the list (will happen on next interaction after fade completes)
    # We use a callback approach via session state
    if "clear_upload_messages" not in st.session_state:
        st.session_state.clear_upload_messages = True

# Clear upload messages if flagged (happens after fade animation on next interaction)
if st.session_state.get("clear_upload_messages", False) and not uploaded_files:
    st.session_state.recently_uploaded = []
    st.session_state.clear_upload_messages = False

# Load existing vectorstores from Chroma
if not st.session_state.vectorstores:
    indexed_files = get_indexed_pdfs_from_chroma()
    if indexed_files:
        _, embeddings = get_model_and_embeddings(model_choice)
        client = get_chroma_client()
        for file_name in indexed_files:
            # Determine collection prefix based on file extension
            if file_name.endswith('.pdf'):
                collection_name = f"pdf_{file_name.replace('.pdf', '').replace(' ', '_').replace('.', '_')}"
            elif file_name.endswith('.md'):
                collection_name = f"md_{file_name.replace('.md', '').replace(' ', '_').replace('.', '_')}"
            else:
                continue

            try:
                vectorstore = Chroma(
                    collection_name=collection_name,
                    embedding_function=embeddings,
                    persist_directory=CHROMA_PERSIST_DIR,
                    client=client
                )
                st.session_state.vectorstores[file_name] = vectorstore
                if file_name not in st.session_state.indexed_pdfs:
                    st.session_state.indexed_pdfs.append(file_name)
                # Also add to selected PDFs if not already there
                if file_name not in st.session_state.selected_pdfs:
                    st.session_state.selected_pdfs.append(file_name)
            except:
                pass

# Process uploaded files
if uploaded_files:
    newly_uploaded = False
    for uploaded_file in uploaded_files:
        # Check if this file is already processed
        if uploaded_file.name not in st.session_state.indexed_pdfs:
            # Reset the cleared flag since we're adding new content
            st.session_state.db_cleared = False

            # Determine file type and process accordingly
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'md':
                # Process markdown file
                vectorstore, num_chunks = process_markdown(uploaded_file)
            elif file_extension == 'pdf':
                # Process PDF file
                vectorstore, num_chunks = process_pdf(uploaded_file)
            else:
                st.error(f"Unsupported file type: {file_extension}")
                continue
            
            # Check if processing was successful
            if vectorstore is None:
                st.error(f"Failed to process {uploaded_file.name}. Please check if it's a valid file with extractable text.")
                continue
            
            st.session_state.vectorstores[uploaded_file.name] = vectorstore
            st.session_state.indexed_pdfs.append(uploaded_file.name)

            # Add to selected PDFs automatically
            if uploaded_file.name not in st.session_state.selected_pdfs:
                st.session_state.selected_pdfs.append(uploaded_file.name)

            # Add to recently uploaded for fade-out display
            if uploaded_file.name not in st.session_state.recently_uploaded:
                st.session_state.recently_uploaded.append(uploaded_file.name)

            newly_uploaded = True

    # Rerun to refresh sidebar with new PDFs and show fade-out messages
    if newly_uploaded:
        st.rerun()

# Display chat interface if there are any indexed PDFs
if st.session_state.indexed_pdfs:
    st.markdown("---")

    # Show which PDFs are being searched
    if st.session_state.selected_pdfs:
        if len(st.session_state.selected_pdfs) == len(st.session_state.indexed_pdfs):
            st.subheader(f"Ask questions about your documents ({len(st.session_state.indexed_pdfs)} PDFs)")
        else:
            st.subheader(f"Ask questions (searching {len(st.session_state.selected_pdfs)} of {len(st.session_state.indexed_pdfs)} PDFs)")
    else:
        st.warning("⚠️ Please select at least one document to search in the sidebar")
        st.stop()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Display sources if this is an assistant message with sources
            if message["role"] == "assistant" and "sources" in message:
                sources = message["sources"]
                if sources:
                    st.markdown("---")
                    st.markdown("**📚 Sources:**")
                    for source in sources:
                        pages_str = ', '.join(map(str, source['pages']))
                        st.markdown(f"• *{source['file']}* - Pages: {pages_str}")

    # Chat input
    if prompt := st.chat_input("What would you like to know about these documents?"):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.status("Thinking...", expanded=True) as status:
                try:
                    # Create combined retriever from selected PDFs
                    model, _ = get_model_and_embeddings(model_choice)
                    retriever = create_combined_retriever(st.session_state.vectorstores, st.session_state.selected_pdfs)
                    chain = create_rag_chain(retriever, model)

                    if chain is None:
                        st.error("No documents selected. Please select at least one PDF in the sidebar.")
                        st.stop()

                    response = chain.invoke({"question": prompt})

                    # Extract answer and sources
                    answer_obj = response.get('answer')
                    source_documents = response.get('source_documents', [])

                    # Handle different response types for answer
                    if hasattr(answer_obj, 'content'):
                        answer = answer_obj.content
                    else:
                        answer = str(answer_obj)

                    # Group sources by PDF
                    sources_by_pdf = {}
                    if source_documents:
                        for doc in source_documents:
                            if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                                # Extract PDF filename from source path
                                source_path = doc.metadata['source']
                                pdf_name = os.path.basename(source_path)
                                page_num = doc.metadata.get('page', 0) + 1  # +1 for human-readable

                                if pdf_name not in sources_by_pdf:
                                    sources_by_pdf[pdf_name] = {'pages': set(), 'docs': []}
                                sources_by_pdf[pdf_name]['pages'].add(page_num)
                                sources_by_pdf[pdf_name]['docs'].append(doc)

                    status.update(label="Complete!", state="complete")

                    # Display answer (inside status block)
                    st.markdown(answer)

                    # Display sources grouped by PDF (inside status block)
                    if source_documents:
                        st.markdown("---")
                        st.markdown("**📚 Sources:**")

                        # Display sources by PDF
                        for pdf_name, info in sources_by_pdf.items():
                            pages_list = sorted(list(info['pages']))
                            st.markdown(f"• *{pdf_name}* - Pages: {', '.join(map(str, pages_list))}")

                        # Show source snippets in expander
                        with st.expander("📄 View source excerpts"):
                            for pdf_name, info in sources_by_pdf.items():
                                st.markdown(f"**{pdf_name}**")
                                for i, doc in enumerate(info['docs'], 1):
                                    page_num = doc.metadata.get('page', 0) + 1
                                    st.markdown(f"*Page {page_num}:*")
                                    st.markdown(f"> {doc.page_content[:300]}{'...' if len(doc.page_content) > 300 else ''}")
                                    if i < len(info['docs']):
                                        st.markdown("")
                                if pdf_name != list(sources_by_pdf.keys())[-1]:
                                    st.markdown("---")

                    # Store in session state
                    sources_list = []
                    if source_documents:
                        for pdf_name, info in sources_by_pdf.items():
                            sources_list.append({
                                "file": pdf_name,
                                "pages": sorted(list(info['pages']))
                            })

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources_list
                    })

                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    status.update(label="Error occurred", state="error")

    # Add a button to clear chat history
    if st.session_state.messages:
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

else:
    st.info("👆 Please upload a PDF or Markdown file to get started!")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit, LangChain, Ollama and Chroma")
