"""
Supplier model for Panda Spa application.
Represents suppliers for spa expenses (hot water, tea, supplies, etc.).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship

from database.base import Base


class Supplier(Base):
    """
    Supplier model representing vendors for spa expenses.
    
    Attributes:
        id: Unique supplier identifier
        name: Supplier name
        supplier_type: Type of supplier (hot_water, tea, spa_supplies, equipment, other)
        contact_info: Contact information
        address: Supplier address/location
        is_active: Whether supplier is currently used
        created_at: Supplier record creation timestamp
        notes: Additional supplier notes
    """
    
    __tablename__ = 'suppliers'
    
    # Supplier types
    HOT_WATER = "hot_water"
    TEA = "tea"
    SPA_SUPPLIES = "spa_supplies"
    EQUIPMENT = "equipment"
    OTHER = "other"
    
    # Primary fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    supplier_type = Column(String(50), nullable=False)
    contact_info = Column(String(200), nullable=True)
    address = Column(String(300), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationships (backref from FinancialRecord)
    # financial_records - backref from FinancialRecord
    
    def __init__(self, name: str, supplier_type: str, contact_info: str = None,
                 address: str = None, is_active: bool = True, notes: str = None):
        """
        Initialize a new Supplier.
        
        Args:
            name: Supplier name
            supplier_type: Type of supplier
            contact_info: Optional contact information
            address: Optional address
            is_active: Whether supplier is active (default: True)
            notes: Optional notes
        """
        self.name = name
        self.supplier_type = supplier_type
        self.contact_info = contact_info
        self.address = address
        self.is_active = is_active
        self.notes = notes
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    @classmethod
    def get_supplier_types(cls):
        """Get list of valid supplier types."""
        return [cls.HOT_WATER, cls.TEA, cls.SPA_SUPPLIES, cls.EQUIPMENT, cls.OTHER]
    
    def to_dict(self) -> dict:
        """
        Convert supplier to dictionary representation.
        
        Returns:
            Dictionary with all supplier fields
        """
        return {
            'id': self.id,
            'name': self.name,
            'supplier_type': self.supplier_type,
            'contact_info': self.contact_info,
            'address': self.address,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notes': self.notes
        }
    
    def __repr__(self) -> str:
        """String representation of Supplier."""
        return f"<Supplier(id={self.id}, name='{self.name}', type='{self.supplier_type}')>"

