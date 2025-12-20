"""
Tests for Appointment model, service, and database operations.
"""

import os
import pytest
from datetime import datetime, timedelta, date
from database.db_manager import DatabaseManagement
from models.appointment import Appointment
from models.customer import Customer
from models.service import Service
from services.appointment_service import AppointmentService


class TestAppointment:
    """Test suite for Appointment model and operations."""
    
    @pytest.fixture
    def test_db_path(self):
        """Provide a test database path."""
        return "test_appointment_panda_spa.db"
    
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
    def sample_customer(self, db_manager):
        """Create a sample customer for testing."""
        return db_manager.create(
            Customer,
            name="Test Customer",
            species="Bear"
        )
    
    @pytest.fixture
    def sample_service(self, db_manager):
        """Create a sample service for testing."""
        return db_manager.create(
            Service,
            name="Test Service",
            service_type=Service.MASSAGE,
            duration_minutes=60,
            price=50.0
        )
    
    @pytest.fixture
    def appointment_service(self, db_manager):
        """Create AppointmentService instance."""
        return AppointmentService(db_manager)
    
    def test_appointment_creation(self, db_manager, sample_customer, sample_service):
        """Test creating an appointment."""
        appointment_time = datetime.now() + timedelta(days=1)
        
        appointment = Appointment(
            customer_id=sample_customer.id,
            service_id=sample_service.id,
            appointment_datetime=appointment_time,
            duration_minutes=sample_service.duration_minutes,
            price_paid=sample_service.price
        )
        
        success = db_manager.save(appointment)
        assert success is True
        assert appointment.id is not None
        
        # Verify via database retrieval (object may be detached)
        retrieved = db_manager.get_by_id(Appointment, appointment.id)
        assert retrieved is not None
        assert retrieved.customer_id == sample_customer.id
        assert retrieved.service_id == sample_service.id
        assert retrieved.status == Appointment.STATUS_SCHEDULED
    
    def test_appointment_service_create(self, appointment_service, sample_customer, sample_service):
        """Test creating appointment via AppointmentService."""
        appointment_time = datetime.now() + timedelta(days=1)
        
        appointment, error = appointment_service.create_appointment(
            sample_customer.id,
            sample_service.id,
            appointment_time
        )
        
        assert appointment is not None
        assert error is None
        
        # Verify via database retrieval (object may be detached)
        retrieved = appointment_service.db_manager.get_by_id(Appointment, appointment.id)
        assert retrieved is not None
        assert retrieved.customer_id == sample_customer.id
        assert retrieved.service_id == sample_service.id
        assert retrieved.status == Appointment.STATUS_SCHEDULED
    
    def test_appointment_service_conflict_detection(self, appointment_service, sample_customer, sample_service):
        """Test conflict detection."""
        appointment_time = datetime.now() + timedelta(days=1)
        
        # Create first appointment
        apt1, _ = appointment_service.create_appointment(
            sample_customer.id,
            sample_service.id,
            appointment_time
        )
        assert apt1 is not None
        
        # Try to create overlapping appointment
        overlapping_time = appointment_time + timedelta(minutes=30)
        apt2, error = appointment_service.create_appointment(
            sample_customer.id,
            sample_service.id,
            overlapping_time
        )
        
        assert apt2 is None
        assert error is not None
        assert "conflict" in error.lower()
    
    def test_appointment_cancel(self, appointment_service, sample_customer, sample_service):
        """Test cancelling an appointment."""
        appointment_time = datetime.now() + timedelta(days=1)
        
        appointment, _ = appointment_service.create_appointment(
            sample_customer.id,
            sample_service.id,
            appointment_time
        )
        
        # Cancel it
        success, error = appointment_service.cancel_appointment(appointment.id, "Test cancellation")
        
        assert success is True
        assert error is None
        
        # Verify cancellation
        cancelled = appointment_service.db_manager.get_by_id(Appointment, appointment.id)
        assert cancelled.status == Appointment.STATUS_CANCELLED
        assert cancelled.cancelled_at is not None
        assert cancelled.cancellation_reason == "Test cancellation"
    
    def test_appointment_complete(self, appointment_service, sample_customer, sample_service):
        """Test completing an appointment."""
        appointment_time = datetime.now() - timedelta(hours=1)  # Past appointment
        
        appointment, _ = appointment_service.create_appointment(
            sample_customer.id,
            sample_service.id,
            appointment_time
        )
        
        # Complete it
        success, error = appointment_service.complete_appointment(appointment.id)
        
        assert success is True
        assert error is None
        
        # Verify completion
        completed = appointment_service.db_manager.get_by_id(Appointment, appointment.id)
        assert completed.status == Appointment.STATUS_COMPLETED
        assert completed.completed_at is not None
        
        # Verify customer stats updated
        customer = appointment_service.db_manager.get_by_id(Customer, sample_customer.id)
        assert customer.total_visits == 1
        assert customer.total_spent == sample_service.price
        assert customer.last_visit is not None
    
    def test_get_available_slots(self, appointment_service, sample_customer, sample_service):
        """Test getting available time slots."""
        test_date = date.today() + timedelta(days=1)
        
        # Get available slots
        slots = appointment_service.get_available_slots(
            sample_service.id,
            test_date
        )
        
        assert len(slots) > 0
        assert all(isinstance(slot, datetime) for slot in slots)
    
    def test_reschedule_appointment(self, appointment_service, sample_customer, sample_service):
        """Test rescheduling an appointment."""
        original_time = datetime.now() + timedelta(days=1)
        
        appointment, _ = appointment_service.create_appointment(
            sample_customer.id,
            sample_service.id,
            original_time
        )
        
        # Reschedule
        new_time = original_time + timedelta(hours=2)
        success, error = appointment_service.reschedule_appointment(appointment.id, new_time)
        
        assert success is True
        assert error is None
        
        # Verify reschedule
        rescheduled = appointment_service.db_manager.get_by_id(Appointment, appointment.id)
        assert rescheduled.appointment_datetime == new_time
    
    def test_get_appointments_by_customer(self, appointment_service, sample_customer, sample_service):
        """Test getting appointments by customer."""
        # Create multiple appointments
        time1 = datetime.now() + timedelta(days=1)
        time2 = datetime.now() + timedelta(days=2)
        
        apt1, _ = appointment_service.create_appointment(sample_customer.id, sample_service.id, time1)
        apt2, _ = appointment_service.create_appointment(sample_customer.id, sample_service.id, time2)
        
        # Get customer appointments
        appointments = appointment_service.get_appointments_by_customer(sample_customer.id)
        
        assert len(appointments) >= 2
        assert any(apt.id == apt1.id for apt in appointments)
        assert any(apt.id == apt2.id for apt in appointments)
    
    def test_get_appointments_by_status(self, appointment_service, sample_customer, sample_service):
        """Test getting appointments by status."""
        time1 = datetime.now() + timedelta(days=1)
        time2 = datetime.now() + timedelta(days=2)
        
        apt1, _ = appointment_service.create_appointment(sample_customer.id, sample_service.id, time1)
        apt2, _ = appointment_service.create_appointment(sample_customer.id, sample_service.id, time2)
        
        # Complete one
        appointment_service.complete_appointment(apt1.id)
        
        # Get scheduled
        scheduled = appointment_service.get_appointments_by_status(Appointment.STATUS_SCHEDULED)
        assert len(scheduled) >= 1
        assert any(apt.id == apt2.id for apt in scheduled)
        
        # Get completed
        completed = appointment_service.get_appointments_by_status(Appointment.STATUS_COMPLETED)
        assert len(completed) >= 1
        assert any(apt.id == apt1.id for apt in completed)
    
    def test_appointment_to_dict(self, db_manager, sample_customer, sample_service):
        """Test appointment to_dict method."""
        appointment_time = datetime.now() + timedelta(days=1)
        
        appointment = db_manager.create(
            Appointment,
            customer_id=sample_customer.id,
            service_id=sample_service.id,
            appointment_datetime=appointment_time,
            duration_minutes=60,
            price_paid=50.0,
            notes="Test notes"
        )
        
        appointment_dict = appointment.to_dict()
        
        assert isinstance(appointment_dict, dict)
        assert appointment_dict['customer_id'] == sample_customer.id
        assert appointment_dict['service_id'] == sample_service.id
        assert appointment_dict['status'] == Appointment.STATUS_SCHEDULED
        assert appointment_dict['duration_minutes'] == 60
        assert appointment_dict['price_paid'] == 50.0
        assert appointment_dict['notes'] == "Test notes"
        assert 'id' in appointment_dict
        assert 'appointment_datetime' in appointment_dict
    
    def test_appointment_status_constants(self):
        """Test appointment status constants."""
        assert Appointment.STATUS_SCHEDULED == "scheduled"
        assert Appointment.STATUS_COMPLETED == "completed"
        assert Appointment.STATUS_CANCELLED == "cancelled"
        assert Appointment.STATUS_NO_SHOW == "no_show"
        
        statuses = Appointment.get_statuses()
        assert len(statuses) == 4
        assert Appointment.STATUS_SCHEDULED in statuses

