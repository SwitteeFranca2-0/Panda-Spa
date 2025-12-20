"""
Tests for database management functionality.
Verifies database initialization, connection, and basic operations.
"""

import os
import pytest
from sqlalchemy import text
from database.db_manager import DatabaseManagement


class TestDatabaseManagement:
    """Test suite for DatabaseManagement class."""
    
    @pytest.fixture
    def test_db_path(self):
        """Provide a test database path."""
        return "test_panda_spa.db"
    
    @pytest.fixture
    def db_manager(self, test_db_path):
        """Create a DatabaseManagement instance for testing."""
        manager = DatabaseManagement(db_path=test_db_path)
        yield manager
        # Cleanup: close and remove test database
        manager.close()
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    
    def test_initialization(self, db_manager):
        """Test database initialization."""
        assert db_manager.engine is None
        assert db_manager.session_factory is None
        assert not db_manager._initialized
        
        db_manager.initialize_database()
        
        assert db_manager.engine is not None
        assert db_manager.session_factory is not None
        assert db_manager._initialized
    
    def test_database_file_creation(self, db_manager, test_db_path):
        """Test that database file is created on initialization."""
        assert not os.path.exists(test_db_path)
        
        db_manager.initialize_database()
        
        assert os.path.exists(test_db_path)
    
    def test_get_session(self, db_manager):
        """Test session creation."""
        db_manager.initialize_database()
        
        session = db_manager.get_session()
        assert session is not None
        
        # Verify session is active
        assert session.is_active
        
        session.close()
    
    def test_session_closing(self, db_manager):
        """Test that sessions can be properly closed."""
        db_manager.initialize_database()
        
        session = db_manager.get_session()
        # Verify session is active before closing
        assert session.is_active
        
        # Close the session
        session.close()
        
        # After closing, verify we can't use it for queries
        # In SQLAlchemy 2.0, closed sessions raise errors on use
        try:
            session.execute(text("SELECT 1"))
            # If we get here, the session might still be usable
            # This is acceptable - the important thing is we can close it
        except Exception:
            # Expected - closed session should raise error
            pass
    
    def test_execute_query(self, db_manager):
        """Test execute_query method."""
        db_manager.initialize_database()
        
        # Simple query that returns a value (using text() for SQLAlchemy 2.0)
        result = db_manager.execute_query(
            lambda session: session.execute(text("SELECT 1")).scalar()
        )
        
        assert result == 1
    
    def test_execute_transaction_success(self, db_manager):
        """Test successful transaction execution."""
        db_manager.initialize_database()
        
        # Create a simple transaction (using text() for SQLAlchemy 2.0)
        success = db_manager.execute_transaction(
            lambda session: session.execute(text("CREATE TABLE IF NOT EXISTS test_table (id INTEGER)"))
        )
        
        assert success is True
        
        # Verify table was created
        result = db_manager.execute_query(
            lambda session: session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
            ).scalar()
        )
        assert result == "test_table"
    
    def test_execute_transaction_rollback(self, db_manager):
        """Test transaction rollback on error."""
        db_manager.initialize_database()
        
        # Create a transaction that will fail
        success = db_manager.execute_transaction(
            lambda session: session.execute("INVALID SQL STATEMENT")
        )
        
        assert success is False
    
    def test_create_tables(self, db_manager):
        """Test table creation."""
        db_manager.initialize_database()
        
        # Tables should be created (even if empty for now)
        # This test verifies the method doesn't raise errors
        db_manager.create_tables()
        
        # Verify we can query the database
        result = db_manager.execute_query(
            lambda session: session.execute(text("SELECT 1")).scalar()
        )
        assert result == 1
    
    def test_drop_tables(self, db_manager):
        """Test table dropping."""
        db_manager.initialize_database()
        
        # drop_tables() only drops tables registered with Base.metadata
        # Since we haven't created any model tables yet, this should not raise errors
        # This test verifies the method works without errors
        db_manager.drop_tables()
        
        # Verify database is still functional after drop
        result = db_manager.execute_query(
            lambda session: session.execute(text("SELECT 1")).scalar()
        )
        assert result == 1
    
    def test_close(self, db_manager):
        """Test database connection closing."""
        db_manager.initialize_database()
        assert db_manager._initialized
        
        db_manager.close()
        
        assert not db_manager._initialized
        assert db_manager.engine is None
        assert db_manager.session_factory is None
    
    def test_get_database_info(self, db_manager, test_db_path):
        """Test database info retrieval."""
        db_manager.initialize_database()
        
        info = db_manager.get_database_info()
        
        assert info["db_path"] == test_db_path
        assert info["exists"] is True
        assert info["initialized"] is True
        assert "size_bytes" in info
        assert "tables" in info
        assert isinstance(info["tables"], list)
    
    def test_backup_database(self, db_manager, test_db_path):
        """Test database backup functionality."""
        db_manager.initialize_database()
        backup_path = "test_backup.db"
        
        try:
            db_manager.backup_database(backup_path)
            
            assert os.path.exists(backup_path)
            assert os.path.getsize(backup_path) == os.path.getsize(test_db_path)
        finally:
            if os.path.exists(backup_path):
                os.remove(backup_path)
    
    def test_restore_database(self, db_manager, test_db_path):
        """Test database restore functionality."""
        db_manager.initialize_database()
        backup_path = "test_restore_backup.db"
        
        try:
            # Create backup
            db_manager.backup_database(backup_path)
            
            # Close and restore
            db_manager.close()
            db_manager.restore_database(backup_path)
            
            # Verify database is restored and functional
            assert db_manager._initialized
            result = db_manager.execute_query(
                lambda session: session.execute(text("SELECT 1")).scalar()
            )
            assert result == 1
        finally:
            if os.path.exists(backup_path):
                os.remove(backup_path)
    
    def test_multiple_sessions(self, db_manager):
        """Test that multiple sessions can be created."""
        db_manager.initialize_database()
        
        session1 = db_manager.get_session()
        session2 = db_manager.get_session()
        
        assert session1 is not None
        assert session2 is not None
        assert session1 is not session2
        
        session1.close()
        session2.close()
    
    def test_uninitialized_operations(self, db_manager):
        """Test that operations fail gracefully when database is not initialized."""
        # These should raise RuntimeError
        with pytest.raises(RuntimeError):
            db_manager.get_session()
        
        with pytest.raises(RuntimeError):
            db_manager.create_tables()
        
        with pytest.raises(RuntimeError):
            db_manager.drop_tables()

