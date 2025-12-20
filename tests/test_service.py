"""
Tests for Service model and database operations.
Uses DatabaseManagement CRUD methods directly.
"""

import os
import pytest
from database.db_manager import DatabaseManagement
from models.service import Service


class TestService:
    """Test suite for Service model and operations."""
    
    @pytest.fixture
    def test_db_path(self):
        """Provide a test database path."""
        return "test_service_panda_spa.db"
    
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
    
    def test_service_creation(self, db_manager):
        """Test creating a service."""
        service = Service(
            name="Hot Spring Bath",
            service_type=Service.THERMAL_BATH,
            duration_minutes=60,
            price=50.0,
            description="Relaxing thermal water bath"
        )
        
        # Store values before save
        name = service.name
        service_type = service.service_type
        
        success = db_manager.save(service)
        assert success is True
        assert service.id is not None
        
        # Verify via database retrieval
        retrieved = db_manager.get_by_id(Service, service.id)
        assert retrieved.name == "Hot Spring Bath"
        assert retrieved.service_type == Service.THERMAL_BATH
        assert retrieved.duration_minutes == 60
        assert retrieved.price == 50.0
        assert retrieved.description == "Relaxing thermal water bath"
        assert retrieved.is_available is True
        assert retrieved.max_capacity == 1
        assert retrieved.popularity_score == 0.0
    
    def test_service_create_method(self, db_manager):
        """Test creating service using create method."""
        service = db_manager.create(
            Service,
            name="Bamboo Massage",
            service_type=Service.MASSAGE,
            duration_minutes=45,
            price=75.0
        )
        
        assert service is not None
        assert service.id is not None
        assert service.name == "Bamboo Massage"
        assert service.service_type == Service.MASSAGE
        assert service.price == 75.0
    
    def test_service_retrieval(self, db_manager):
        """Test retrieving a service by ID."""
        # Create a service
        service = db_manager.create(
            Service,
            name="Tea Therapy Session",
            service_type=Service.TEA_THERAPY,
            duration_minutes=30,
            price=25.0
        )
        service_id = service.id
        
        # Retrieve it
        retrieved = db_manager.get_by_id(Service, service_id)
        
        assert retrieved is not None
        assert retrieved.id == service_id
        assert retrieved.name == "Tea Therapy Session"
        assert retrieved.service_type == Service.TEA_THERAPY
    
    def test_get_all_services(self, db_manager):
        """Test getting all services."""
        # Create multiple services
        db_manager.create(Service, name="Bath1", service_type=Service.THERMAL_BATH, duration_minutes=60, price=50.0)
        db_manager.create(Service, name="Massage1", service_type=Service.MASSAGE, duration_minutes=45, price=75.0)
        db_manager.create(Service, name="Tea1", service_type=Service.TEA_THERAPY, duration_minutes=30, price=25.0)
        
        # Get all
        all_services = db_manager.get_all(Service)
        
        assert len(all_services) >= 3
        names = [s.name for s in all_services]
        assert "Bath1" in names
        assert "Massage1" in names
        assert "Tea1" in names
    
    def test_find_services_by_type(self, db_manager):
        """Test finding services by type."""
        # Create services of different types
        db_manager.create(Service, name="Bath1", service_type=Service.THERMAL_BATH, duration_minutes=60, price=50.0)
        db_manager.create(Service, name="Bath2", service_type=Service.THERMAL_BATH, duration_minutes=90, price=75.0)
        db_manager.create(Service, name="Massage1", service_type=Service.MASSAGE, duration_minutes=45, price=75.0)
        
        # Find thermal baths
        baths = db_manager.find(Service, service_type=Service.THERMAL_BATH)
        
        assert len(baths) == 2
        assert all(s.service_type == Service.THERMAL_BATH for s in baths)
    
    def test_find_available_services(self, db_manager):
        """Test finding available services."""
        # Create available and unavailable services
        db_manager.create(Service, name="Available1", service_type=Service.MASSAGE, duration_minutes=45, price=75.0, is_available=True)
        db_manager.create(Service, name="Unavailable1", service_type=Service.MASSAGE, duration_minutes=45, price=75.0, is_available=False)
        
        # Find available
        available = db_manager.find(Service, is_available=True)
        
        assert len(available) >= 1
        assert all(s.is_available is True for s in available)
    
    def test_update_service(self, db_manager):
        """Test updating a service."""
        # Create service
        service = db_manager.create(
            Service,
            name="Original Service",
            service_type=Service.MASSAGE,
            duration_minutes=45,
            price=75.0
        )
        service_id = service.id
        
        # Update it
        success = db_manager.update(
            service,
            name="Updated Service",
            price=85.0,
            description="Updated description"
        )
        
        assert success is True
        
        # Verify update
        updated = db_manager.get_by_id(Service, service_id)
        assert updated.name == "Updated Service"
        assert updated.price == 85.0
        assert updated.description == "Updated description"
    
    def test_delete_service(self, db_manager):
        """Test deleting a service."""
        # Create service
        service = db_manager.create(
            Service,
            name="To Delete",
            service_type=Service.TEA_THERAPY,
            duration_minutes=30,
            price=25.0
        )
        service_id = service.id
        
        # Verify it exists
        assert db_manager.get_by_id(Service, service_id) is not None
        
        # Delete it
        success = db_manager.delete(service)
        assert success is True
        
        # Verify it's gone
        assert db_manager.get_by_id(Service, service_id) is None
    
    def test_service_to_dict(self, db_manager):
        """Test service to_dict method."""
        service = db_manager.create(
            Service,
            name="Test Service",
            service_type=Service.THERMAL_BATH,
            duration_minutes=60,
            price=50.0,
            description="Test description"
        )
        
        service_dict = service.to_dict()
        
        assert isinstance(service_dict, dict)
        assert service_dict['name'] == "Test Service"
        assert service_dict['service_type'] == Service.THERMAL_BATH
        assert service_dict['duration_minutes'] == 60
        assert service_dict['price'] == 50.0
        assert service_dict['description'] == "Test description"
        assert service_dict['is_available'] is True
        assert service_dict['max_capacity'] == 1
        assert 'id' in service_dict
        assert 'created_at' in service_dict
    
    def test_service_count(self, db_manager):
        """Test counting services."""
        # Create services
        db_manager.create(Service, name="Count1", service_type=Service.THERMAL_BATH, duration_minutes=60, price=50.0)
        db_manager.create(Service, name="Count2", service_type=Service.THERMAL_BATH, duration_minutes=90, price=75.0)
        db_manager.create(Service, name="Count3", service_type=Service.MASSAGE, duration_minutes=45, price=75.0)
        
        # Count all
        total = db_manager.count(Service)
        assert total >= 3
        
        # Count by type
        bath_count = db_manager.count(Service, service_type=Service.THERMAL_BATH)
        assert bath_count == 2
    
    def test_service_defaults(self, db_manager):
        """Test service default values."""
        service = Service(
            name="Test",
            service_type=Service.MASSAGE,
            duration_minutes=45,
            price=75.0
        )
        
        assert service.max_capacity == 1
        assert service.is_available is True
        assert service.popularity_score == 0.0
        assert service.created_at is not None
    
    def test_service_unavailable(self, db_manager):
        """Test creating unavailable service."""
        service = db_manager.create(
            Service,
            name="Unavailable",
            service_type=Service.TEA_THERAPY,
            duration_minutes=30,
            price=25.0,
            is_available=False
        )
        
        assert service.is_available is False
        
        # Verify it's saved
        retrieved = db_manager.get_by_id(Service, service.id)
        assert retrieved.is_available is False
    
    def test_service_max_capacity(self, db_manager):
        """Test service with custom max capacity."""
        service = db_manager.create(
            Service,
            name="Group Bath",
            service_type=Service.THERMAL_BATH,
            duration_minutes=60,
            price=50.0,
            max_capacity=5
        )
        
        assert service.max_capacity == 5
        
        # Verify it's saved
        retrieved = db_manager.get_by_id(Service, service.id)
        assert retrieved.max_capacity == 5
    
    def test_service_get_types(self):
        """Test getting valid service types."""
        types = Service.get_service_types()
        assert Service.THERMAL_BATH in types
        assert Service.MASSAGE in types
        assert Service.TEA_THERAPY in types
        assert len(types) == 3

