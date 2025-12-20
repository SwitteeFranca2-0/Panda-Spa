"""
Tests for Customer model and database operations.
Uses DatabaseManagement CRUD methods directly.
"""

import os
import pytest
from datetime import datetime
from database.db_manager import DatabaseManagement
from models.customer import Customer


class TestCustomer:
    """Test suite for Customer model and operations."""
    
    @pytest.fixture
    def test_db_path(self):
        """Provide a test database path."""
        return "test_customer_panda_spa.db"
    
    @pytest.fixture
    def db_manager(self, test_db_path):
        """Create a DatabaseManagement instance for testing."""
        manager = DatabaseManagement(db_path=test_db_path)
        manager.initialize_database()
        yield manager
        # Cleanup
        manager.close()
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    
    def test_customer_creation(self, db_manager):
        """Test creating a customer."""
        customer = Customer(
            name="Bamboo Bear",
            species="Bear",
            contact_info="Bamboo Forest, Section 3",
            notes="Loves hot springs"
        )
        
        # Store values before save
        name = customer.name
        species = customer.species
        contact_info = customer.contact_info
        notes = customer.notes
        
        success = db_manager.save(customer)
        assert success is True
        assert customer.id is not None
        
        # Verify saved values (using stored values since object may be detached)
        assert name == "Bamboo Bear"
        assert species == "Bear"
        
        # Verify via database retrieval
        retrieved = db_manager.get_by_id(Customer, customer.id)
        assert retrieved.name == "Bamboo Bear"
        assert retrieved.species == "Bear"
        assert retrieved.contact_info == "Bamboo Forest, Section 3"
        assert retrieved.notes == "Loves hot springs"
        assert retrieved.total_visits == 0
        assert retrieved.total_spent == 0.0
        assert retrieved.is_active is True
    
    def test_customer_create_method(self, db_manager):
        """Test creating customer using create method."""
        customer = db_manager.create(
            Customer,
            name="Forest Fox",
            species="Fox",
            contact_info="fox@forest.com"
        )
        
        assert customer is not None
        assert customer.id is not None
        assert customer.name == "Forest Fox"
        assert customer.species == "Fox"
    
    def test_customer_retrieval(self, db_manager):
        """Test retrieving a customer by ID."""
        # Create a customer
        customer = db_manager.create(
            Customer,
            name="Deer Friend",
            species="Deer"
        )
        customer_id = customer.id
        
        # Retrieve it
        retrieved = db_manager.get_by_id(Customer, customer_id)
        
        assert retrieved is not None
        assert retrieved.id == customer_id
        assert retrieved.name == "Deer Friend"
        assert retrieved.species == "Deer"
    
    def test_get_all_customers(self, db_manager):
        """Test getting all customers."""
        # Create multiple customers
        db_manager.create(Customer, name="Bear1", species="Bear")
        db_manager.create(Customer, name="Fox1", species="Fox")
        db_manager.create(Customer, name="Deer1", species="Deer")
        
        # Get all
        all_customers = db_manager.get_all(Customer)
        
        assert len(all_customers) >= 3
        names = [c.name for c in all_customers]
        assert "Bear1" in names
        assert "Fox1" in names
        assert "Deer1" in names
    
    def test_find_customers_by_species(self, db_manager):
        """Test finding customers by species."""
        # Create customers of different species
        db_manager.create(Customer, name="Bear1", species="Bear")
        db_manager.create(Customer, name="Bear2", species="Bear")
        db_manager.create(Customer, name="Fox1", species="Fox")
        
        # Find bears
        bears = db_manager.find(Customer, species="Bear")
        
        assert len(bears) == 2
        assert all(c.species == "Bear" for c in bears)
    
    def test_find_customer_by_name(self, db_manager):
        """Test finding customer by name."""
        # Create customer
        db_manager.create(Customer, name="Unique Name", species="Rabbit")
        
        # Find it
        found = db_manager.find_one(Customer, name="Unique Name")
        
        assert found is not None
        assert found.name == "Unique Name"
        assert found.species == "Rabbit"
    
    def test_update_customer(self, db_manager):
        """Test updating a customer."""
        # Create customer
        customer = db_manager.create(
            Customer,
            name="Original Name",
            species="Bear",
            contact_info="old@contact.com"
        )
        customer_id = customer.id
        
        # Update it
        success = db_manager.update(
            customer,
            name="Updated Name",
            contact_info="new@contact.com",
            notes="Updated notes"
        )
        
        assert success is True
        
        # Verify update
        updated = db_manager.get_by_id(Customer, customer_id)
        assert updated.name == "Updated Name"
        assert updated.contact_info == "new@contact.com"
        assert updated.notes == "Updated notes"
    
    def test_delete_customer(self, db_manager):
        """Test deleting a customer."""
        # Create customer
        customer = db_manager.create(
            Customer,
            name="To Delete",
            species="Bear"
        )
        customer_id = customer.id
        
        # Verify it exists
        assert db_manager.get_by_id(Customer, customer_id) is not None
        
        # Delete it
        success = db_manager.delete(customer)
        assert success is True
        
        # Verify it's gone
        assert db_manager.get_by_id(Customer, customer_id) is None
    
    def test_customer_to_dict(self, db_manager):
        """Test customer to_dict method."""
        customer = db_manager.create(
            Customer,
            name="Test Customer",
            species="Bear",
            contact_info="test@test.com",
            notes="Test notes"
        )
        
        customer_dict = customer.to_dict()
        
        assert isinstance(customer_dict, dict)
        assert customer_dict['name'] == "Test Customer"
        assert customer_dict['species'] == "Bear"
        assert customer_dict['contact_info'] == "test@test.com"
        assert customer_dict['notes'] == "Test notes"
        assert customer_dict['total_visits'] == 0
        assert customer_dict['total_spent'] == 0.0
        assert customer_dict['is_active'] is True
        assert 'id' in customer_dict
        assert 'created_at' in customer_dict
    
    def test_customer_count(self, db_manager):
        """Test counting customers."""
        # Create customers
        db_manager.create(Customer, name="Count1", species="Bear")
        db_manager.create(Customer, name="Count2", species="Bear")
        db_manager.create(Customer, name="Count3", species="Fox")
        
        # Count all
        total = db_manager.count(Customer)
        assert total >= 3
        
        # Count by species
        bear_count = db_manager.count(Customer, species="Bear")
        assert bear_count == 2
    
    def test_customer_exists(self, db_manager):
        """Test checking if customer exists."""
        # Create customer
        db_manager.create(Customer, name="Exists", species="Bear")
        
        # Check existence
        assert db_manager.exists(Customer, name="Exists") is True
        assert db_manager.exists(Customer, name="NonExistent") is False
    
    def test_customer_defaults(self, db_manager):
        """Test customer default values."""
        customer = Customer(name="Test", species="Bear")
        
        assert customer.total_visits == 0
        assert customer.total_spent == 0.0
        assert customer.is_active is True
        assert customer.created_at is not None
        assert customer.last_visit is None
    
    def test_customer_inactive(self, db_manager):
        """Test creating inactive customer."""
        customer = db_manager.create(
            Customer,
            name="Inactive",
            species="Bear",
            is_active=False
        )
        
        assert customer.is_active is False
        
        # Verify it's saved
        retrieved = db_manager.get_by_id(Customer, customer.id)
        assert retrieved.is_active is False

