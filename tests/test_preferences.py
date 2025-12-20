"""
Tests for Customer Preference model and Recommendation Service.
"""

import os
import pytest
from datetime import datetime, timedelta
from database.db_manager import DatabaseManagement
from models.customer_preference import CustomerPreference
from models.customer import Customer
from models.service import Service
from models.appointment import Appointment
from services.recommendation_service import RecommendationService
from services.appointment_service import AppointmentService


class TestPreferences:
    """Test suite for Customer Preference and Recommendation Service."""
    
    @pytest.fixture
    def test_db_path(self):
        """Provide a test database path."""
        return "test_preferences_panda_spa.db"
    
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
    
    @pytest.fixture
    def recommendation_service(self, db_manager):
        """Create RecommendationService instance."""
        return RecommendationService(db_manager)
    
    @pytest.fixture
    def sample_customer(self, db_manager):
        """Create a sample customer."""
        return db_manager.create(Customer, name="Test Customer", species="Bear")
    
    @pytest.fixture
    def sample_services(self, db_manager):
        """Create sample services."""
        service1 = db_manager.create(
            Service,
            name="Massage",
            service_type=Service.MASSAGE,
            duration_minutes=60,
            price=50.0
        )
        service2 = db_manager.create(
            Service,
            name="Bath",
            service_type=Service.THERMAL_BATH,
            duration_minutes=90,
            price=75.0
        )
        service3 = db_manager.create(
            Service,
            name="Tea",
            service_type=Service.TEA_THERAPY,
            duration_minutes=30,
            price=25.0
        )
        return [service1, service2, service3]
    
    def test_preference_creation(self, db_manager, sample_customer, sample_services):
        """Test creating a customer preference."""
        preference = db_manager.create(
            CustomerPreference,
            customer_id=sample_customer.id,
            service_id=sample_services[0].id,
            preference_score=5.0
        )
        
        assert preference is not None
        assert preference.customer_id == sample_customer.id
        assert preference.service_id == sample_services[0].id
        assert preference.preference_score == 5.0
        assert preference.visit_count == 0
    
    def test_preference_update_from_appointment(self, db_manager, sample_customer, sample_services):
        """Test updating preference from appointment."""
        preference = db_manager.create(
            CustomerPreference,
            customer_id=sample_customer.id,
            service_id=sample_services[0].id
        )
        
        # Update from appointment
        appointment_price = 50.0
        visit_date = datetime.now()
        preference.update_from_appointment(appointment_price, visit_date)
        db_manager.save(preference)
        
        # Verify update
        updated = db_manager.get_by_id(CustomerPreference, preference.id)
        assert updated.visit_count == 1
        assert updated.total_spent == 50.0
        assert updated.last_visited is not None
    
    def test_recommendation_service_update_preferences(self, recommendation_service, db_manager, sample_customer, sample_services):
        """Test updating preferences via RecommendationService."""
        # Create completed appointment
        appointment = db_manager.create(
            Appointment,
            customer_id=sample_customer.id,
            service_id=sample_services[0].id,
            appointment_datetime=datetime.now() - timedelta(hours=1),
            duration_minutes=60,
            price_paid=50.0,
            status=Appointment.STATUS_COMPLETED
        )
        appointment.completed_at = datetime.now()
        db_manager.save(appointment)
        
        # Update preferences
        success = recommendation_service.update_preferences_from_appointment(appointment)
        assert success is True
        
        # Verify preference was created/updated
        preference = recommendation_service.db_manager.find_one(
            CustomerPreference,
            customer_id=sample_customer.id,
            service_id=sample_services[0].id
        )
        assert preference is not None
        assert preference.visit_count == 1
        assert preference.total_spent == 50.0
    
    def test_calculate_preference_score(self, recommendation_service, db_manager, sample_customer, sample_services):
        """Test preference score calculation."""
        preference = db_manager.create(
            CustomerPreference,
            customer_id=sample_customer.id,
            service_id=sample_services[0].id
        )
        
        # Add multiple visits
        for i in range(3):
            preference.update_from_appointment(50.0, datetime.now() - timedelta(days=i))
        
        # Calculate score
        score = recommendation_service._calculate_preference_score(preference)
        
        assert 0.0 <= score <= 10.0
        assert score > 0  # Should have some score with visits
    
    def test_get_recommendations(self, recommendation_service, db_manager, sample_customer, sample_services):
        """Test getting recommendations for a customer."""
        # Create some preferences
        pref1 = db_manager.create(
            CustomerPreference,
            customer_id=sample_customer.id,
            service_id=sample_services[0].id,
            preference_score=8.0
        )
        pref1.visit_count = 5
        db_manager.save(pref1)
        
        # Get recommendations
        recommendations = recommendation_service.get_recommendations(sample_customer.id, limit=3)
        
        assert len(recommendations) > 0
        assert all(isinstance(rec[0], Service) for rec in recommendations)
        assert all(isinstance(rec[1], (int, float)) for rec in recommendations)
        assert all(isinstance(rec[2], str) for rec in recommendations)
    
    def test_get_popular_services(self, recommendation_service, db_manager, sample_services):
        """Test getting popular services."""
        # Create preferences for services
        customer1 = db_manager.create(Customer, name="C1", species="Bear")
        customer2 = db_manager.create(Customer, name="C2", species="Fox")
        
        # Service 1 has more visits
        pref1 = db_manager.create(
            CustomerPreference,
            customer_id=customer1.id,
            service_id=sample_services[0].id
        )
        pref1.visit_count = 10
        db_manager.save(pref1)
        
        pref2 = db_manager.create(
            CustomerPreference,
            customer_id=customer2.id,
            service_id=sample_services[0].id
        )
        pref2.visit_count = 5
        db_manager.save(pref2)
        
        # Service 2 has fewer visits
        pref3 = db_manager.create(
            CustomerPreference,
            customer_id=customer1.id,
            service_id=sample_services[1].id
        )
        pref3.visit_count = 2
        db_manager.save(pref3)
        
        # Get popular services
        popular = recommendation_service._get_popular_services(limit=2)
        
        assert len(popular) > 0
        # Service 1 should be more popular
        assert popular[0].id == sample_services[0].id
    
    def test_get_top_preferences(self, recommendation_service, db_manager, sample_customer, sample_services):
        """Test getting top preferences for a customer."""
        # Create multiple preferences with different scores
        pref1 = db_manager.create(
            CustomerPreference,
            customer_id=sample_customer.id,
            service_id=sample_services[0].id,
            preference_score=8.0
        )
        
        pref2 = db_manager.create(
            CustomerPreference,
            customer_id=sample_customer.id,
            service_id=sample_services[1].id,
            preference_score=5.0
        )
        
        pref3 = db_manager.create(
            CustomerPreference,
            customer_id=sample_customer.id,
            service_id=sample_services[2].id,
            preference_score=2.0
        )
        
        # Get top preferences
        top = recommendation_service.get_top_preferences(sample_customer.id, limit=2)
        
        assert len(top) == 2
        assert top[0].preference_score >= top[1].preference_score
        assert top[0].service_id == sample_services[0].id
    
    def test_preference_to_dict(self, db_manager, sample_customer, sample_services):
        """Test preference to_dict method."""
        preference = db_manager.create(
            CustomerPreference,
            customer_id=sample_customer.id,
            service_id=sample_services[0].id,
            preference_score=7.5
        )
        
        pref_dict = preference.to_dict()
        
        assert isinstance(pref_dict, dict)
        assert pref_dict['customer_id'] == sample_customer.id
        assert pref_dict['service_id'] == sample_services[0].id
        assert pref_dict['preference_score'] == 7.5
        assert 'visit_count' in pref_dict
        assert 'total_spent' in pref_dict

