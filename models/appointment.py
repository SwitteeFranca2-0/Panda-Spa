"""
Appointment model for Panda Spa application.
Represents bookings made by customers for services.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from database.base import Base
from models.appointment_extra import appointment_extra_association


class Appointment(Base):
    """
    Appointment model representing customer bookings for services.
    
    Attributes:
        id: Unique appointment identifier
        customer_id: Reference to customer
        service_id: Reference to service
        appointment_datetime: Scheduled date and time
        status: Status (scheduled, completed, cancelled, no_show)
        duration_minutes: Actual duration
        price_paid: Amount paid for this appointment
        notes: Appointment-specific notes
        created_at: Appointment creation timestamp
        completed_at: When appointment was completed
        cancelled_at: When appointment was cancelled
        cancellation_reason: Reason for cancellation
    """
    
    __tablename__ = 'appointments'
    
    # Status constants
    STATUS_SCHEDULED = "scheduled"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_NO_SHOW = "no_show"
    
    # Primary fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    
    # Appointment details
    appointment_datetime = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default=STATUS_SCHEDULED)
    duration_minutes = Column(Integer, nullable=False)
    price_paid = Column(Float, nullable=False)
    
    # Notes and metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Customer feeling/mood at time of booking
    customer_feeling = Column(String(50), nullable=True)  # e.g., "stressed", "relaxed", "celebrating", "tired"
    
    # Completion/Cancellation tracking
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(String(200), nullable=True)
    
    # Relationships
    customer = relationship("Customer", backref="appointments")
    service = relationship("Service", backref="appointments")
    extras = relationship("Extra", secondary=appointment_extra_association, backref="appointments")
    
    def __init__(self, customer_id: int, service_id: int, appointment_datetime: datetime,
                 duration_minutes: int = None, price_paid: float = None, notes: str = None,
                 status: str = STATUS_SCHEDULED, customer_feeling: str = None):
        """
        Initialize a new Appointment.
        
        Args:
            customer_id: ID of the customer
            service_id: ID of the service
            appointment_datetime: Scheduled date and time
            duration_minutes: Duration in minutes (defaults to service duration)
            price_paid: Price paid (defaults to service price)
            notes: Optional notes
            status: Appointment status (default: scheduled)
            customer_feeling: Customer's mood/feeling at booking time
        """
        self.customer_id = customer_id
        self.service_id = service_id
        self.appointment_datetime = appointment_datetime
        self.status = status
        self.duration_minutes = duration_minutes or 0
        self.price_paid = price_paid or 0.0
        self.notes = notes
        self.customer_feeling = customer_feeling
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    @classmethod
    def get_statuses(cls):
        """Get list of valid appointment statuses."""
        return [cls.STATUS_SCHEDULED, cls.STATUS_COMPLETED, cls.STATUS_CANCELLED, cls.STATUS_NO_SHOW]
    
    def cancel(self, reason: str = None):
        """Cancel this appointment."""
        self.status = self.STATUS_CANCELLED
        self.cancelled_at = datetime.utcnow()
        if reason:
            self.cancellation_reason = reason
    
    def complete(self):
        """Mark this appointment as completed."""
        self.status = self.STATUS_COMPLETED
        self.completed_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """
        Convert appointment to dictionary representation.
        
        Returns:
            Dictionary with all appointment fields
        """
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'service_id': self.service_id,
            'appointment_datetime': self.appointment_datetime.isoformat() if self.appointment_datetime else None,
            'status': self.status,
            'duration_minutes': self.duration_minutes,
            'price_paid': self.price_paid,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancellation_reason': self.cancellation_reason,
            'customer_feeling': self.customer_feeling
        }
    
    def __repr__(self) -> str:
        """String representation of Appointment."""
        return f"<Appointment(id={self.id}, customer_id={self.customer_id}, service_id={self.service_id}, datetime={self.appointment_datetime}, status='{self.status}')>"





