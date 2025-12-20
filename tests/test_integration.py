"""
Integration tests for complete workflows.
Tests end-to-end functionality across all components.
"""

import os
import pytest
from datetime import datetime, timedelta
from database.db_manager import DatabaseManagement
from models.customer import Customer
from models.service import Service
from models.appointment import Appointment
from models.financial_record import FinancialRecord
from models.supplier import Supplier
from services.appointment_service import AppointmentService
from services.financial_service import FinancialService


class TestIntegration:
    """Integration test suite for complete workflows."""
    
    @pytest.fixture
    def test_db_path(self):
        """Provide a test database path."""
        return "test_integration_panda_spa.db"
    
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
    def appointment_service(self, db_manager):
        """Create AppointmentService instance."""
        return AppointmentService(db_manager)
    
    @pytest.fixture
    def financial_service(self, db_manager):
        """Create FinancialService instance."""
        return FinancialService(db_manager)
    
    def test_complete_customer_workflow(self, db_manager):
        """Test complete customer management workflow."""
        # Create customer
        customer = db_manager.create(
            Customer,
            name="Integration Test Customer",
            species="Bear",
            contact_info="test@example.com"
        )
        assert customer is not None
        customer_id = customer.id
        
        # Read customer
        retrieved = db_manager.get_by_id(Customer, customer_id)
        assert retrieved.name == "Integration Test Customer"
        
        # Update customer
        success = db_manager.update(retrieved, name="Updated Customer")
        assert success is True
        
        updated = db_manager.get_by_id(Customer, customer_id)
        assert updated.name == "Updated Customer"
        
        # Delete customer
        success = db_manager.delete(updated)
        assert success is True
        
        deleted = db_manager.get_by_id(Customer, customer_id)
        assert deleted is None
    
    def test_complete_service_workflow(self, db_manager):
        """Test complete service management workflow."""
        # Create service
        service = db_manager.create(
            Service,
            name="Integration Test Service",
            service_type=Service.MASSAGE,
            duration_minutes=60,
            price=75.0
        )
        assert service is not None
        service_id = service.id
        
        # Update service
        success = db_manager.update(service, price=85.0)
        assert success is True
        
        # Toggle availability
        success = db_manager.update(service, is_available=False)
        assert success is True
        
        updated = db_manager.get_by_id(Service, service_id)
        assert updated.is_available is False
    
    def test_complete_appointment_workflow(self, appointment_service, financial_service):
        """Test complete appointment workflow from creation to completion."""
        # Create customer and service
        customer = appointment_service.db_manager.create(
            Customer,
            name="Workflow Customer",
            species="Fox"
        )
        
        service = appointment_service.db_manager.create(
            Service,
            name="Workflow Service",
            service_type=Service.THERMAL_BATH,
            duration_minutes=60,
            price=50.0
        )
        
        # Create appointment
        appointment_time = datetime.now() + timedelta(days=1)
        appointment, error = appointment_service.create_appointment(
            customer.id,
            service.id,
            appointment_time
        )
        assert appointment is not None
        assert error is None
        appointment_id = appointment.id
        
        # Verify appointment is scheduled
        retrieved = appointment_service.db_manager.get_by_id(Appointment, appointment_id)
        assert retrieved.status == Appointment.STATUS_SCHEDULED
        
        # Complete appointment
        success, error = appointment_service.complete_appointment(appointment_id)
        assert success is True
        assert error is None
        
        # Verify appointment is completed
        completed = appointment_service.db_manager.get_by_id(Appointment, appointment_id)
        assert completed.status == Appointment.STATUS_COMPLETED
        assert completed.completed_at is not None
        
        # Verify customer stats updated
        updated_customer = appointment_service.db_manager.get_by_id(Customer, customer.id)
        assert updated_customer.total_visits == 1
        assert updated_customer.total_spent == 50.0
        
        # Verify revenue was auto-recorded
        revenue_records = appointment_service.db_manager.find(
            FinancialRecord,
            appointment_id=appointment_id,
            transaction_type=FinancialRecord.REVENUE
        )
        assert len(revenue_records) > 0
        assert revenue_records[0].amount == 50.0
    
    def test_financial_tracking_workflow(self, db_manager, financial_service):
        """Test complete financial tracking workflow."""
        # Create supplier
        supplier = db_manager.create(
            Supplier,
            name="Test Supplier",
            supplier_type=Supplier.TEA
        )
        
        # Record expenses
        expense1, _ = financial_service.record_expense(
            amount=25.0,
            category=FinancialRecord.CATEGORY_TEA,
            description="Tea purchase",
            supplier_id=supplier.id
        )
        assert expense1 is not None
        
        expense2, _ = financial_service.record_expense(
            amount=15.0,
            category=FinancialRecord.CATEGORY_HOT_WATER,
            description="Hot water supply"
        )
        assert expense2 is not None
        
        # Calculate totals
        total_expenses = financial_service.calculate_expenses()
        assert total_expenses >= 40.0
        
        # Get category breakdown
        breakdown = financial_service.get_category_breakdown()
        assert breakdown.get(FinancialRecord.CATEGORY_TEA, 0) >= 25.0
        assert breakdown.get(FinancialRecord.CATEGORY_HOT_WATER, 0) >= 15.0
        
        # Get financial summary
        summary = financial_service.get_financial_summary()
        assert 'revenue' in summary
        assert 'expenses' in summary
        assert 'profit' in summary
        assert summary['expenses'] >= 40.0
    
    def test_data_persistence(self, db_manager):
        """Test that data persists across database connections."""
        # Create data
        customer = db_manager.create(Customer, name="Persistence Test", species="Bear")
        customer_id = customer.id
        
        service = db_manager.create(
            Service,
            name="Persistence Service",
            service_type=Service.MASSAGE,
            duration_minutes=45,
            price=60.0
        )
        service_id = service.id
        
        # Close and reopen database
        db_manager.close()
        
        new_db_manager = DatabaseManagement(db_path=db_manager.db_path)
        new_db_manager.initialize_database()
        
        # Verify data persisted
        retrieved_customer = new_db_manager.get_by_id(Customer, customer_id)
        assert retrieved_customer is not None
        assert retrieved_customer.name == "Persistence Test"
        
        retrieved_service = new_db_manager.get_by_id(Service, service_id)
        assert retrieved_service is not None
        assert retrieved_service.name == "Persistence Service"
        
        new_db_manager.close()
    
    def test_multiple_operations_transaction(self, appointment_service):
        """Test multiple operations in sequence."""
        # Create customer
        customer = appointment_service.db_manager.create(
            Customer,
            name="Multi-Op Customer",
            species="Deer"
        )
        
        # Create multiple services
        service1 = appointment_service.db_manager.create(
            Service,
            name="Service 1",
            service_type=Service.MASSAGE,
            duration_minutes=60,
            price=50.0
        )
        
        service2 = appointment_service.db_manager.create(
            Service,
            name="Service 2",
            service_type=Service.TEA_THERAPY,
            duration_minutes=30,
            price=25.0
        )
        
        # Create multiple appointments
        time1 = datetime.now() + timedelta(days=1, hours=10)
        time2 = datetime.now() + timedelta(days=1, hours=14)
        
        apt1, _ = appointment_service.create_appointment(customer.id, service1.id, time1)
        apt2, _ = appointment_service.create_appointment(customer.id, service2.id, time2)
        
        assert apt1 is not None
        assert apt2 is not None
        
        # Verify both appointments exist
        all_appointments = appointment_service.db_manager.get_all(Appointment)
        assert len(all_appointments) >= 2
        
        # Get customer appointments
        customer_appointments = appointment_service.get_appointments_by_customer(customer.id)
        assert len(customer_appointments) >= 2





