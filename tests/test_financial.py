"""
Tests for Financial models and service.
"""

import os
import pytest
from datetime import datetime, timedelta
from database.db_manager import DatabaseManagement
from models.financial_record import FinancialRecord
from models.supplier import Supplier
from models.appointment import Appointment
from models.customer import Customer
from models.service import Service
from services.financial_service import FinancialService


class TestFinancial:
    """Test suite for Financial models and operations."""
    
    @pytest.fixture
    def test_db_path(self):
        """Provide a test database path."""
        return "test_financial_panda_spa.db"
    
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
    def financial_service(self, db_manager):
        """Create FinancialService instance."""
        return FinancialService(db_manager)
    
    @pytest.fixture
    def sample_supplier(self, db_manager):
        """Create a sample supplier."""
        return db_manager.create(
            Supplier,
            name="Bamboo Tea Co.",
            supplier_type=Supplier.TEA
        )
    
    @pytest.fixture
    def sample_appointment(self, db_manager):
        """Create a sample completed appointment."""
        customer = db_manager.create(Customer, name="Test", species="Bear")
        service = db_manager.create(Service, name="Test Service", service_type=Service.MASSAGE, duration_minutes=60, price=50.0)
        appointment = db_manager.create(
            Appointment,
            customer_id=customer.id,
            service_id=service.id,
            appointment_datetime=datetime.now() - timedelta(hours=1),
            duration_minutes=60,
            price_paid=50.0,
            status=Appointment.STATUS_COMPLETED
        )
        appointment.completed_at = datetime.now()
        db_manager.save(appointment)
        return appointment
    
    def test_supplier_creation(self, db_manager):
        """Test creating a supplier."""
        supplier = db_manager.create(
            Supplier,
            name="Hot Springs Supply",
            supplier_type=Supplier.HOT_WATER,
            contact_info="supply@hotsprings.com"
        )
        
        assert supplier is not None
        assert supplier.id is not None
        assert supplier.name == "Hot Springs Supply"
        assert supplier.supplier_type == Supplier.HOT_WATER
    
    def test_financial_record_revenue(self, db_manager, sample_appointment):
        """Test creating a revenue record."""
        record = db_manager.create(
            FinancialRecord,
            transaction_type=FinancialRecord.REVENUE,
            amount=50.0,
            description="Service revenue",
            category=FinancialRecord.CATEGORY_SERVICE_REVENUE,
            appointment_id=sample_appointment.id
        )
        
        assert record is not None
        assert record.transaction_type == FinancialRecord.REVENUE
        assert record.amount == 50.0
        assert record.appointment_id == sample_appointment.id
    
    def test_financial_record_expense(self, db_manager, sample_supplier):
        """Test creating an expense record."""
        record = db_manager.create(
            FinancialRecord,
            transaction_type=FinancialRecord.EXPENSE,
            amount=25.0,
            description="Tea supplies",
            category=FinancialRecord.CATEGORY_TEA,
            supplier_id=sample_supplier.id
        )
        
        assert record is not None
        assert record.transaction_type == FinancialRecord.EXPENSE
        assert record.amount == 25.0
        assert record.supplier_id == sample_supplier.id
    
    def test_financial_service_record_revenue(self, financial_service, sample_appointment):
        """Test recording revenue via FinancialService."""
        # Reload appointment to get price_paid
        appointment = financial_service.db_manager.get_by_id(Appointment, sample_appointment.id)
        expected_amount = appointment.price_paid if appointment else 50.0
        
        record, error = financial_service.record_revenue(sample_appointment.id)
        
        assert record is not None
        assert error is None
        
        # Verify via database retrieval (object may be detached)
        retrieved = financial_service.db_manager.get_by_id(FinancialRecord, record.id)
        assert retrieved is not None
        assert retrieved.transaction_type == FinancialRecord.REVENUE
        assert retrieved.amount == expected_amount
    
    def test_financial_service_record_expense(self, financial_service, sample_supplier):
        """Test recording expense via FinancialService."""
        record, error = financial_service.record_expense(
            amount=30.0,
            category=FinancialRecord.CATEGORY_TEA,
            description="Tea purchase",
            supplier_id=sample_supplier.id
        )
        
        assert record is not None
        assert error is None
        
        # Verify via database retrieval (object may be detached)
        retrieved = financial_service.db_manager.get_by_id(FinancialRecord, record.id)
        assert retrieved is not None
        assert retrieved.transaction_type == FinancialRecord.EXPENSE
        assert retrieved.amount == 30.0
    
    def test_calculate_revenue(self, financial_service, sample_appointment):
        """Test calculating revenue."""
        # Record some revenue
        financial_service.record_revenue(sample_appointment.id, 50.0)
        
        revenue = financial_service.calculate_revenue()
        assert revenue >= 50.0
    
    def test_calculate_expenses(self, financial_service, sample_supplier):
        """Test calculating expenses."""
        # Record some expenses
        financial_service.record_expense(20.0, FinancialRecord.CATEGORY_TEA, "Tea", sample_supplier.id)
        financial_service.record_expense(15.0, FinancialRecord.CATEGORY_HOT_WATER, "Hot water")
        
        expenses = financial_service.calculate_expenses()
        assert expenses >= 35.0
    
    def test_calculate_profit(self, financial_service, sample_appointment, sample_supplier):
        """Test calculating profit."""
        # Record revenue and expenses
        financial_service.record_revenue(sample_appointment.id, 50.0)
        financial_service.record_expense(20.0, FinancialRecord.CATEGORY_TEA, "Tea", sample_supplier.id)
        
        profit = financial_service.calculate_profit()
        assert profit >= 30.0  # 50 - 20
    
    def test_get_category_breakdown(self, financial_service, sample_supplier):
        """Test getting category breakdown."""
        # Record expenses in different categories
        financial_service.record_expense(20.0, FinancialRecord.CATEGORY_TEA, "Tea", sample_supplier.id)
        financial_service.record_expense(15.0, FinancialRecord.CATEGORY_HOT_WATER, "Hot water")
        financial_service.record_expense(10.0, FinancialRecord.CATEGORY_TEA, "More tea", sample_supplier.id)
        
        breakdown = financial_service.get_category_breakdown()
        assert breakdown.get(FinancialRecord.CATEGORY_TEA, 0) >= 30.0
        assert breakdown.get(FinancialRecord.CATEGORY_HOT_WATER, 0) >= 15.0
    
    def test_get_financial_summary(self, financial_service, sample_appointment, sample_supplier):
        """Test getting financial summary."""
        # Record some transactions
        financial_service.record_revenue(sample_appointment.id, 50.0)
        financial_service.record_expense(20.0, FinancialRecord.CATEGORY_TEA, "Tea", sample_supplier.id)
        
        summary = financial_service.get_financial_summary()
        
        assert 'revenue' in summary
        assert 'expenses' in summary
        assert 'profit' in summary
        assert 'category_breakdown' in summary
        assert summary['revenue'] >= 50.0
        assert summary['expenses'] >= 20.0
        assert summary['profit'] >= 30.0
    
    def test_supplier_to_dict(self, db_manager):
        """Test supplier to_dict method."""
        supplier = db_manager.create(
            Supplier,
            name="Test Supplier",
            supplier_type=Supplier.SPA_SUPPLIES
        )
        
        supplier_dict = supplier.to_dict()
        assert isinstance(supplier_dict, dict)
        assert supplier_dict['name'] == "Test Supplier"
        assert supplier_dict['supplier_type'] == Supplier.SPA_SUPPLIES
    
    def test_financial_record_to_dict(self, db_manager):
        """Test financial record to_dict method."""
        record = db_manager.create(
            FinancialRecord,
            transaction_type=FinancialRecord.EXPENSE,
            amount=25.0,
            description="Test expense",
            category=FinancialRecord.CATEGORY_SUPPLIES
        )
        
        record_dict = record.to_dict()
        assert isinstance(record_dict, dict)
        assert record_dict['transaction_type'] == FinancialRecord.EXPENSE
        assert record_dict['amount'] == 25.0
        assert record_dict['category'] == FinancialRecord.CATEGORY_SUPPLIES

