"""
Tests for CRUD convenience methods in DatabaseManagement.
"""

import os
import pytest
from sqlalchemy import Column, Integer, String
from database.db_manager import DatabaseManagement
from database.base import Base


# Create a simple test model (not a test class, just a model)
class SimpleTestModel(Base):
    """Simple test model for CRUD testing."""
    __tablename__ = 'test_models'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    value = Column(String(100), nullable=True)


# Alias for easier use
TestModel = SimpleTestModel


class TestCRUDMethods:
    """Test suite for CRUD convenience methods."""
    
    @pytest.fixture
    def test_db_path(self):
        """Provide a test database path."""
        return "test_crud_panda_spa.db"
    
    @pytest.fixture
    def db_manager(self, test_db_path):
        """Create a DatabaseManagement instance for testing."""
        manager = DatabaseManagement(db_path=test_db_path)
        manager.initialize_database()
        # Create test table
        Base.metadata.create_all(bind=manager.engine)
        yield manager
        # Cleanup
        manager.close()
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    
    def test_save(self, db_manager):
        """Test save method."""
        obj = TestModel(name="Test1", value="Value1")
        success = db_manager.save(obj)
        
        assert success is True
        assert obj.id is not None  # ID should be auto-generated
        
        # Verify it was saved
        retrieved = db_manager.get_by_id(TestModel, obj.id)
        assert retrieved is not None
        assert retrieved.name == "Test1"
    
    def test_create(self, db_manager):
        """Test create method."""
        obj = db_manager.create(TestModel, name="Test2", value="Value2")
        
        assert obj is not None
        assert obj.id is not None
        assert obj.name == "Test2"
        
        # Verify it was saved
        retrieved = db_manager.get_by_id(TestModel, obj.id)
        assert retrieved.name == "Test2"
    
    def test_update(self, db_manager):
        """Test update method."""
        # Create an object
        obj = db_manager.create(TestModel, name="Original", value="OriginalValue")
        obj_id = obj.id
        
        # Update it
        success = db_manager.update(obj, name="Updated", value="UpdatedValue")
        
        assert success is True
        
        # Verify update
        updated = db_manager.get_by_id(TestModel, obj_id)
        assert updated.name == "Updated"
        assert updated.value == "UpdatedValue"
    
    def test_delete(self, db_manager):
        """Test delete method."""
        # Create an object
        obj = db_manager.create(TestModel, name="ToDelete", value="DeleteMe")
        obj_id = obj.id
        
        # Verify it exists
        assert db_manager.get_by_id(TestModel, obj_id) is not None
        
        # Delete it
        success = db_manager.delete(obj)
        assert success is True
        
        # Verify it's gone
        assert db_manager.get_by_id(TestModel, obj_id) is None
    
    def test_get_by_id(self, db_manager):
        """Test get_by_id method."""
        # Create an object
        obj = db_manager.create(TestModel, name="GetMe", value="GetValue")
        obj_id = obj.id
        
        # Retrieve it
        retrieved = db_manager.get_by_id(TestModel, obj_id)
        
        assert retrieved is not None
        assert retrieved.id == obj_id
        assert retrieved.name == "GetMe"
        
        # Test non-existent ID
        assert db_manager.get_by_id(TestModel, 99999) is None
    
    def test_get_all(self, db_manager):
        """Test get_all method."""
        # Create multiple objects
        db_manager.create(TestModel, name="All1", value="V1")
        db_manager.create(TestModel, name="All2", value="V2")
        db_manager.create(TestModel, name="All3", value="V3")
        
        # Get all
        all_objects = db_manager.get_all(TestModel)
        
        assert len(all_objects) >= 3
        names = [obj.name for obj in all_objects]
        assert "All1" in names
        assert "All2" in names
        assert "All3" in names
    
    def test_find(self, db_manager):
        """Test find method."""
        # Create objects with different values
        db_manager.create(TestModel, name="Find1", value="Target")
        db_manager.create(TestModel, name="Find2", value="Target")
        db_manager.create(TestModel, name="Find3", value="Other")
        
        # Find by value
        results = db_manager.find(TestModel, value="Target")
        
        assert len(results) == 2
        assert all(obj.value == "Target" for obj in results)
    
    def test_find_one(self, db_manager):
        """Test find_one method."""
        # Create an object
        db_manager.create(TestModel, name="Unique", value="UniqueValue")
        
        # Find it
        result = db_manager.find_one(TestModel, name="Unique")
        
        assert result is not None
        assert result.name == "Unique"
        assert result.value == "UniqueValue"
        
        # Test non-existent
        assert db_manager.find_one(TestModel, name="NonExistent") is None
    
    def test_count(self, db_manager):
        """Test count method."""
        # Create objects
        db_manager.create(TestModel, name="Count1", value="Group1")
        db_manager.create(TestModel, name="Count2", value="Group1")
        db_manager.create(TestModel, name="Count3", value="Group2")
        
        # Count all
        total = db_manager.count(TestModel)
        assert total >= 3
        
        # Count with filter
        group1_count = db_manager.count(TestModel, value="Group1")
        assert group1_count == 2
    
    def test_exists(self, db_manager):
        """Test exists method."""
        # Create an object
        db_manager.create(TestModel, name="Exists", value="Check")
        
        # Check existence
        assert db_manager.exists(TestModel, name="Exists") is True
        assert db_manager.exists(TestModel, name="NonExistent") is False
    
    def test_commit_and_rollback(self, db_manager):
        """Test commit and rollback methods."""
        session = db_manager.get_session()
        
        try:
            # Add object
            obj = TestModel(name="CommitTest", value="Test")
            session.add(obj)
            
            # Flush to get ID
            db_manager.flush(session)
            obj_id = obj.id
            assert obj_id is not None
            
            # Commit
            success = db_manager.commit(session)
            assert success is True
            
            # Verify it's saved
            retrieved = db_manager.get_by_id(TestModel, obj_id)
            assert retrieved is not None
            
            # Test rollback
            session2 = db_manager.get_session()
            obj2 = TestModel(name="RollbackTest", value="Test")
            session2.add(obj2)
            db_manager.rollback(session2)
            session2.close()
            
            # Verify it wasn't saved
            assert db_manager.find_one(TestModel, name="RollbackTest") is None
        finally:
            session.close()
    
    def test_refresh(self, db_manager):
        """Test refresh method."""
        # Create and modify object in another session
        obj = db_manager.create(TestModel, name="Refresh", value="Original")
        obj_id = obj.id
        
        # Modify directly in database using text()
        from sqlalchemy import text
        session = db_manager.get_session()
        try:
            session.execute(
                text("UPDATE test_models SET value = 'Updated' WHERE id = :id"),
                {"id": obj_id}
            )
            session.commit()
        finally:
            session.close()
        
        # Refresh object
        success = db_manager.refresh(obj)
        assert success is True
        assert obj.value == "Updated"
    
    def test_bulk_save(self, db_manager):
        """Test bulk_save method."""
        objects = [
            TestModel(name=f"Bulk{i}", value=f"Value{i}")
            for i in range(5)
        ]
        
        success = db_manager.bulk_save(objects)
        assert success is True
        
        # Verify all were saved
        all_objects = db_manager.get_all(TestModel)
        names = [obj.name for obj in all_objects]
        for i in range(5):
            assert f"Bulk{i}" in names
    
    def test_bulk_delete(self, db_manager):
        """Test bulk_delete method."""
        # Create objects
        objects = [
            db_manager.create(TestModel, name=f"Delete{i}", value=f"V{i}")
            for i in range(3)
        ]
        
        # Verify they exist
        delete_objects = db_manager.find(TestModel, name="Delete0")
        assert len(delete_objects) > 0
        
        # Delete them
        success = db_manager.bulk_delete(objects)
        assert success is True
        
        # Verify they're gone - get IDs before they're detached
        obj_ids = []
        for obj in objects:
            # Get ID before deletion
            session = db_manager.get_session()
            try:
                merged = session.merge(obj)
                obj_ids.append(merged.id)
            finally:
                session.close()
        
        # Now verify they're gone
        for obj_id in obj_ids:
            assert db_manager.get_by_id(TestModel, obj_id) is None

