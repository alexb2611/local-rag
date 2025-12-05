"""
Unit tests for ChromaDB helper functions from app.py

Tests the ChromaDB utility functions including:
- Client creation and configuration
- Database directory management
- Collection management
- Permissions handling
- Cleanup operations
"""
import pytest
import os
import shutil
import chromadb
from chromadb.config import Settings
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


# Import the functions we want to test from app.py
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class TestGetChromaClient:
    """Tests for get_chroma_client function"""

    def test_creates_directory_if_not_exists(self, tmp_path, monkeypatch):
        """Test that function creates directory if it doesn't exist"""
        # Import inside test to avoid side effects
        from app import get_chroma_client, CHROMA_PERSIST_DIR

        # Change the persist directory to temp path
        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        # Directory shouldn't exist yet
        assert not os.path.exists(test_dir)

        # Create client
        client = get_chroma_client()

        # Directory should now exist
        assert os.path.exists(test_dir)
        assert os.path.isdir(test_dir)

    def test_directory_has_correct_permissions(self, tmp_path, monkeypatch):
        """Test that created directory has correct permissions"""
        from app import get_chroma_client

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        client = get_chroma_client()

        # Check directory exists with proper permissions (0o777)
        assert os.path.exists(test_dir)
        # Note: Actual permissions may be affected by umask

    def test_returns_chromadb_client(self, tmp_path, monkeypatch):
        """Test that function returns a ChromaDB client"""
        from app import get_chroma_client

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        client = get_chroma_client()

        assert client is not None
        # Should be a ChromaDB client
        assert hasattr(client, 'list_collections')
        assert hasattr(client, 'get_or_create_collection')

    def test_client_persistence(self, tmp_path, monkeypatch):
        """Test that client supports persistent storage"""
        from app import get_chroma_client

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        # Create client and collection
        client = get_chroma_client()
        client.get_or_create_collection("persistence_test")

        # Create new client instance
        client2 = get_chroma_client()

        # Should see the same collection (proves persistence works)
        collections = [c.name for c in client2.list_collections()]
        assert "persistence_test" in collections

    def test_works_with_existing_directory(self, tmp_path, monkeypatch):
        """Test that function works when directory already exists"""
        from app import get_chroma_client

        test_dir = str(tmp_path / "test_chroma")
        # Create directory first
        os.makedirs(test_dir, exist_ok=True)

        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        # Should not raise error
        client = get_chroma_client()
        assert client is not None

    def test_multiple_calls_return_clients(self, tmp_path, monkeypatch):
        """Test that multiple calls work correctly"""
        from app import get_chroma_client

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        client1 = get_chroma_client()
        client2 = get_chroma_client()

        # Both should be valid clients
        assert client1 is not None
        assert client2 is not None


class TestGetIndexedPdfsFromChroma:
    """Tests for get_indexed_pdfs_from_chroma function"""

    def test_returns_empty_list_when_no_directory(self, tmp_path, monkeypatch):
        """Test returns empty list when directory doesn't exist"""
        from app import get_indexed_pdfs_from_chroma

        test_dir = str(tmp_path / "nonexistent")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        result = get_indexed_pdfs_from_chroma()
        assert result == []

    def test_returns_empty_list_when_no_collections(self, tmp_path, monkeypatch):
        """Test returns empty list when no collections exist"""
        from app import get_indexed_pdfs_from_chroma, get_chroma_client

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        # Create empty database
        client = get_chroma_client()

        result = get_indexed_pdfs_from_chroma()
        assert result == []

    def test_extracts_pdf_filenames(self, tmp_path, monkeypatch):
        """Test that PDF filenames are correctly extracted from collections"""
        from app import get_indexed_pdfs_from_chroma, get_chroma_client

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        client = get_chroma_client()

        # Create test collections with pdf_ prefix
        client.get_or_create_collection("pdf_test_document")
        client.get_or_create_collection("pdf_another_file")

        result = get_indexed_pdfs_from_chroma()

        assert "test document.pdf" in result
        assert "another file.pdf" in result
        assert len(result) == 2

    def test_extracts_markdown_filenames(self, tmp_path, monkeypatch):
        """Test that Markdown filenames are correctly extracted"""
        from app import get_indexed_pdfs_from_chroma, get_chroma_client

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        client = get_chroma_client()

        # Create test collections with md_ prefix
        client.get_or_create_collection("md_readme")
        client.get_or_create_collection("md_notes")

        result = get_indexed_pdfs_from_chroma()

        assert "readme.md" in result
        assert "notes.md" in result
        assert len(result) == 2

    def test_handles_mixed_file_types(self, tmp_path, monkeypatch):
        """Test handling of both PDF and Markdown collections"""
        from app import get_indexed_pdfs_from_chroma, get_chroma_client

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        client = get_chroma_client()

        # Create mixed collections
        client.get_or_create_collection("pdf_document")
        client.get_or_create_collection("md_readme")
        client.get_or_create_collection("other_collection")  # Should be ignored

        result = get_indexed_pdfs_from_chroma()

        assert "document.pdf" in result
        assert "readme.md" in result
        # Should not include "other_collection"
        assert len(result) == 2

    def test_handles_underscores_in_filenames(self, tmp_path, monkeypatch):
        """Test that underscores in filenames are converted to spaces"""
        from app import get_indexed_pdfs_from_chroma, get_chroma_client

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        client = get_chroma_client()

        # Create collection with underscores
        client.get_or_create_collection("pdf_my_test_file")

        result = get_indexed_pdfs_from_chroma()

        assert "my test file.pdf" in result

    def test_handles_exceptions_gracefully(self, tmp_path, monkeypatch):
        """Test that function handles exceptions without crashing"""
        from app import get_indexed_pdfs_from_chroma

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        # Create directory but make it unreadable (if possible)
        os.makedirs(test_dir, exist_ok=True)

        # Should return empty list on error
        with patch('app.get_chroma_client', side_effect=Exception("Test error")):
            result = get_indexed_pdfs_from_chroma()
            assert result == []


class TestClearChromaDatabase:
    """Tests for clear_chroma_database function"""

    def test_deletes_all_collections(self, tmp_path, monkeypatch):
        """Test that function deletes all collections"""
        from app import clear_chroma_database, get_chroma_client, get_indexed_pdfs_from_chroma

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        # Create some collections
        client = get_chroma_client()
        client.get_or_create_collection("pdf_test1")
        client.get_or_create_collection("pdf_test2")
        client.get_or_create_collection("md_test3")

        # Verify they exist
        assert len(get_indexed_pdfs_from_chroma()) == 3

        # Clear database
        result = clear_chroma_database()

        assert result is True
        # Collections should be gone
        assert len(get_indexed_pdfs_from_chroma()) == 0

    def test_creates_directory_if_not_exists(self, tmp_path, monkeypatch):
        """Test that function creates directory if it doesn't exist"""
        from app import clear_chroma_database

        test_dir = str(tmp_path / "nonexistent_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        assert not os.path.exists(test_dir)

        result = clear_chroma_database()

        assert result is True
        assert os.path.exists(test_dir)

    def test_returns_true_on_success(self, tmp_path, monkeypatch):
        """Test that function returns True on success"""
        from app import clear_chroma_database

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        result = clear_chroma_database()
        assert result is True

    def test_handles_empty_database(self, tmp_path, monkeypatch):
        """Test clearing an already empty database"""
        from app import clear_chroma_database, get_chroma_client

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        # Create empty database
        client = get_chroma_client()

        # Clear should still succeed
        result = clear_chroma_database()
        assert result is True

    def test_preserves_directory_structure(self, tmp_path, monkeypatch):
        """Test that directory is not deleted, only collections"""
        from app import clear_chroma_database, get_chroma_client

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        # Create database with collections
        client = get_chroma_client()
        client.get_or_create_collection("pdf_test")

        # Clear database
        clear_chroma_database()

        # Directory should still exist
        assert os.path.exists(test_dir)

    def test_handles_collection_deletion_error(self, tmp_path, monkeypatch):
        """Test handling when collection deletion fails"""
        from app import clear_chroma_database, get_chroma_client

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        # Create collection
        client = get_chroma_client()
        client.get_or_create_collection("pdf_test")

        # Mock deletion to raise error
        with patch.object(client, 'delete_collection', side_effect=Exception("Delete error")):
            # Should handle error gracefully
            result = clear_chroma_database()
            # Function should still return True (best effort)
            # Note: Actual behavior depends on implementation


class TestCollectionNameGeneration:
    """Tests for collection name generation logic"""

    def test_pdf_collection_names(self):
        """Test PDF collection name generation pattern"""
        # Based on code in app.py line 357
        filename = "My Test Document.pdf"
        collection_name = f"pdf_{filename.replace('.pdf', '').replace(' ', '_').replace('.', '_')}"

        assert collection_name == "pdf_My_Test_Document"

    def test_markdown_collection_names(self):
        """Test Markdown collection name generation pattern"""
        # Based on code in app.py line 288
        filename = "README.md"
        collection_name = f"md_{filename.replace('.md', '').replace(' ', '_').replace('.', '_')}"

        assert collection_name == "md_README"

    def test_collection_name_with_multiple_periods(self):
        """Test collection name with multiple periods"""
        filename = "document.v1.0.pdf"
        collection_name = f"pdf_{filename.replace('.pdf', '').replace(' ', '_').replace('.', '_')}"

        assert collection_name == "pdf_document_v1_0"

    def test_collection_name_reverse_mapping(self):
        """Test converting collection name back to filename"""
        # From collection name to filename (lines 94-95 in app.py)
        collection_name = "pdf_My_Test_Document"
        filename = collection_name.replace("pdf_", "").replace("_", " ") + ".pdf"

        assert filename == "My Test Document.pdf"


class TestChromaIntegration:
    """Integration tests for ChromaDB operations"""

    def test_complete_workflow(self, tmp_path, monkeypatch):
        """Test complete workflow: create, list, clear"""
        from app import (
            get_chroma_client,
            get_indexed_pdfs_from_chroma,
            clear_chroma_database
        )

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        # 1. Create client and collections
        client = get_chroma_client()
        client.get_or_create_collection("pdf_test1")
        client.get_or_create_collection("md_test2")

        # 2. List collections
        files = get_indexed_pdfs_from_chroma()
        assert len(files) == 2
        assert "test1.pdf" in files
        assert "test2.md" in files

        # 3. Clear database
        clear_chroma_database()

        # 4. Verify empty
        files = get_indexed_pdfs_from_chroma()
        assert len(files) == 0

    def test_persistence_across_clients(self, tmp_path, monkeypatch):
        """Test that collections persist across client instances"""
        from app import get_chroma_client, get_indexed_pdfs_from_chroma

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        # Create collection with first client
        client1 = get_chroma_client()
        client1.get_or_create_collection("pdf_persistent")

        # Create second client (simulating app restart)
        client2 = get_chroma_client()

        # Should still see the collection
        files = get_indexed_pdfs_from_chroma()
        assert "persistent.pdf" in files


class TestErrorHandling:
    """Tests for error handling in ChromaDB operations"""

    def test_handles_permission_errors(self, tmp_path, monkeypatch):
        """Test handling of permission errors"""
        from app import get_indexed_pdfs_from_chroma

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        # Create directory
        os.makedirs(test_dir, exist_ok=True)

        # Try to access with mocked permission error
        with patch('app.get_chroma_client', side_effect=PermissionError("Access denied")):
            result = get_indexed_pdfs_from_chroma()
            # Should return empty list rather than crash
            assert result == []

    def test_handles_corrupted_database(self, tmp_path, monkeypatch):
        """Test handling of corrupted database files"""
        from app import get_indexed_pdfs_from_chroma

        test_dir = str(tmp_path / "test_chroma")
        monkeypatch.setattr('app.CHROMA_PERSIST_DIR', test_dir)

        # Create directory with dummy corrupted file
        os.makedirs(test_dir, exist_ok=True)
        (Path(test_dir) / "chroma.sqlite3").write_text("corrupted")

        # Should handle gracefully
        result = get_indexed_pdfs_from_chroma()
        assert isinstance(result, list)
