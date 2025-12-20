"""
Financial Record model for Panda Spa application.
Tracks revenue and expenses for financial management.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, CheckConstraint
from sqlalchemy.orm import relationship

from database.base import Base


class FinancialRecord(Base):
    """
    Financial Record model representing revenue and expenses.
    
    Attributes:
        id: Unique financial record identifier
        transaction_type: Type (revenue or expense)
        amount: Transaction amount (always positive)
        description: Description of transaction
        category: Category (service_revenue, hot_water, tea, supplies, etc.)
        supplier_id: Reference to supplier (for expenses)
        appointment_id: Reference to appointment (for revenue)
        transaction_date: When transaction occurred
        created_at: Record creation timestamp
        receipt_number: Receipt or invoice number
        notes: Additional transaction notes
    """
    
    __tablename__ = 'financial_records'
    
    # Transaction types
    REVENUE = "revenue"
    EXPENSE = "expense"
    
    # Categories
    CATEGORY_SERVICE_REVENUE = "service_revenue"
    CATEGORY_HOT_WATER = "hot_water"
    CATEGORY_TEA = "tea"
    CATEGORY_SUPPLIES = "supplies"
    CATEGORY_EQUIPMENT = "equipment"
    CATEGORY_MAINTENANCE = "maintenance"
    CATEGORY_OTHER = "other"
    
    # Primary fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_type = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(500), nullable=False)
    category = Column(String(50), nullable=False)
    
    # References
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=True)
    
    # Metadata
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    receipt_number = Column(String(50), nullable=True, unique=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    supplier = relationship("Supplier", backref="financial_records")
    appointment = relationship("Appointment", backref="financial_record")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_amount_positive'),
    )
    
    def __init__(self, transaction_type: str, amount: float, description: str, category: str,
                 supplier_id: int = None, appointment_id: int = None,
                 transaction_date: datetime = None, receipt_number: str = None, notes: str = None):
        """
        Initialize a new FinancialRecord.
        
        Args:
            transaction_type: Type (revenue or expense)
            amount: Transaction amount (must be > 0)
            description: Description of transaction
            category: Category
            supplier_id: Optional supplier ID (for expenses)
            appointment_id: Optional appointment ID (for revenue)
            transaction_date: When transaction occurred (default: now)
            receipt_number: Optional receipt number
            notes: Optional notes
        """
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description
        self.category = category
        self.supplier_id = supplier_id
        self.appointment_id = appointment_id
        self.receipt_number = receipt_number
        self.notes = notes
        
        if transaction_date:
            self.transaction_date = transaction_date
        else:
            self.transaction_date = datetime.utcnow()
        
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    @classmethod
    def get_transaction_types(cls):
        """Get list of valid transaction types."""
        return [cls.REVENUE, cls.EXPENSE]
    
    @classmethod
    def get_categories(cls):
        """Get list of valid categories."""
        return [
            cls.CATEGORY_SERVICE_REVENUE,
            cls.CATEGORY_HOT_WATER,
            cls.CATEGORY_TEA,
            cls.CATEGORY_SUPPLIES,
            cls.CATEGORY_EQUIPMENT,
            cls.CATEGORY_MAINTENANCE,
            cls.CATEGORY_OTHER
        ]
    
    def to_dict(self) -> dict:
        """
        Convert financial record to dictionary representation.
        
        Returns:
            Dictionary with all financial record fields
        """
        return {
            'id': self.id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'description': self.description,
            'category': self.category,
            'supplier_id': self.supplier_id,
            'appointment_id': self.appointment_id,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'receipt_number': self.receipt_number,
            'notes': self.notes
        }
    
    def __repr__(self) -> str:
        """String representation of FinancialRecord."""
        return f"<FinancialRecord(id={self.id}, type='{self.transaction_type}', amount=${self.amount}, category='{self.category}')>"





