"""
Customer Preference model for Panda Spa application.
Tracks customer preferences for services to enable recommendations.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from database.base import Base


class CustomerPreference(Base):
    """
    Customer Preference model tracking customer service preferences.
    
    Attributes:
        id: Unique preference identifier
        customer_id: Reference to customer
        service_id: Reference to service
        preference_score: Calculated preference score (0-10)
        visit_count: Number of times customer booked this service
        last_visited: Date of last booking for this service
        first_visited: Date of first booking for this service
        average_rating: Average rating if customer rates services
        total_spent: Total amount spent on this service
        preference_factors: Additional preference data (JSON)
        created_at: Preference record creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = 'customer_preferences'
    
    # Primary fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    
    # Preference metrics
    preference_score = Column(Float, nullable=False, default=0.0)
    visit_count = Column(Integer, default=0, nullable=False)
    total_spent = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    first_visited = Column(DateTime, nullable=True)
    last_visited = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional data
    average_rating = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer", backref="preferences")
    service = relationship("Service", backref="preferences")
    
    # Unique constraint: one preference record per customer-service pair
    __table_args__ = (
        UniqueConstraint('customer_id', 'service_id', name='unique_customer_service_preference'),
    )
    
    def __init__(self, customer_id: int, service_id: int, preference_score: float = 0.0):
        """
        Initialize a new CustomerPreference.
        
        Args:
            customer_id: ID of the customer
            service_id: ID of the service
            preference_score: Initial preference score (default: 0.0)
        """
        self.customer_id = customer_id
        self.service_id = service_id
        self.preference_score = preference_score
        self.visit_count = 0
        self.total_spent = 0.0
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    def update_from_appointment(self, appointment_price: float, visit_date: datetime = None):
        """
        Update preference metrics from an appointment.
        
        Args:
            appointment_price: Price paid for the appointment
            visit_date: Date of the visit (default: now)
        """
        if visit_date is None:
            visit_date = datetime.utcnow()
        
        self.visit_count += 1
        self.total_spent += appointment_price
        
        if self.first_visited is None:
            self.first_visited = visit_date
        
        self.last_visited = visit_date
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """
        Convert preference to dictionary representation.
        
        Returns:
            Dictionary with all preference fields
        """
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'service_id': self.service_id,
            'preference_score': self.preference_score,
            'visit_count': self.visit_count,
            'total_spent': self.total_spent,
            'first_visited': self.first_visited.isoformat() if self.first_visited else None,
            'last_visited': self.last_visited.isoformat() if self.last_visited else None,
            'average_rating': self.average_rating,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        """String representation of CustomerPreference."""
        return f"<CustomerPreference(customer_id={self.customer_id}, service_id={self.service_id}, score={self.preference_score:.2f})>"





