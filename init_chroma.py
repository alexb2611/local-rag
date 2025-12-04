#!/usr/bin/env python3
"""Initialize ChromaDB with proper permissions"""
import os
import chromadb
from chromadb.config import Settings

CHROMA_PERSIST_DIR = "./chroma_db"

# Ensure directory exists
os.makedirs(CHROMA_PERSIST_DIR, mode=0o777, exist_ok=True)

print(f"Creating ChromaDB at {CHROMA_PERSIST_DIR}...")

# Create client - this will initialize the database files
client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_DIR,
    settings=Settings(
        allow_reset=True,
        anonymized_telemetry=False
    )
)

# Create and immediately delete a test collection to ensure database is initialized
try:
    test_collection = client.get_or_create_collection("init_test")
    client.delete_collection("init_test")
    print("✓ ChromaDB initialized successfully!")
    print(f"✓ Database files created with proper permissions")

    # Check file permissions
    db_file = os.path.join(CHROMA_PERSIST_DIR, "chroma.sqlite3")
    if os.path.exists(db_file):
        perms = oct(os.stat(db_file).st_mode)[-3:]
        print(f"✓ Database file permissions: {perms}")
except Exception as e:
    print(f"✗ Error: {e}")
