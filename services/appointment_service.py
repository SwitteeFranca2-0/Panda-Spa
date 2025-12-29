"""
Appointment Service for business logic.
Handles appointment scheduling, conflict detection, and status management.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from database.db_manager import DatabaseManagement
from models.appointment import Appointment
from models.service import Service
from models.customer import Customer
from services.financial_service import FinancialService
from services.recommendation_service import RecommendationService


class AppointmentService:
    """
    Business logic service for appointment management.
    Handles scheduling, conflict detection, and appointment operations.
    """
    
    def __init__(self, db_manager: DatabaseManagement):
        """
        Initialize appointment service.
        
        Args:
            db_manager: DatabaseManagement instance
        """
        self.db_manager = db_manager
        self.financial_service = FinancialService(db_manager)
        self.recommendation_service = RecommendationService(db_manager)
    
    def create_appointment(self, customer_id: int, service_id: int, 
                          appointment_datetime: datetime,
                          notes: str = None, customer_feeling: str = None) -> Tuple[Optional[Appointment], str]:
        """
        Create a new appointment with conflict checking.
        
        Args:
            customer_id: ID of the customer
            service_id: ID of the service
            appointment_datetime: Scheduled date and time
            notes: Optional notes
            customer_feeling: Optional customer mood/feeling
            
        Returns:
            Tuple of (Appointment if successful, error message if failed)
        """
        # Validate customer exists
        customer = self.db_manager.get_by_id(Customer, customer_id)
        if not customer:
            return None, "Customer not found"
        
        # Validate service exists and is available
        service = self.db_manager.get_by_id(Service, service_id)
        if not service:
            return None, "Service not found"
        
        if not service.is_available:
            return None, "Service is not available"
        
        # Check for conflicts
        conflict = self.check_conflict(service_id, appointment_datetime, service.duration_minutes)
        if conflict:
            return None, f"Time slot conflict: {conflict}"
        
        # Create appointment with service defaults
        appointment = Appointment(
            customer_id=customer_id,
            service_id=service_id,
            appointment_datetime=appointment_datetime,
            duration_minutes=service.duration_minutes,
            price_paid=service.price,
            notes=notes,
            status=Appointment.STATUS_SCHEDULED,
            customer_feeling=customer_feeling
        )
        
        success = self.db_manager.save(appointment)
        if success:
            # Retrieve fresh instance to avoid detached instance issues
            fresh_appointment = self.db_manager.get_by_id(Appointment, appointment.id)
            return fresh_appointment, None
        else:
            return None, "Failed to save appointment"
    
    def check_conflict(self, service_id: int, appointment_datetime: datetime, 
                      duration_minutes: int) -> Optional[str]:
        """
        Check if appointment time conflicts with existing appointments.
        
        Args:
            service_id: ID of the service
            appointment_datetime: Proposed appointment time
            duration_minutes: Duration of the appointment
            
        Returns:
            Error message if conflict found, None otherwise
        """
        # Calculate end time
        end_time = appointment_datetime + timedelta(minutes=duration_minutes)
        
        # Get all scheduled appointments for this service
        scheduled = self.db_manager.find(
            Appointment,
            service_id=service_id,
            status=Appointment.STATUS_SCHEDULED
        )
        
        for existing in scheduled:
            if existing.id == getattr(self, '_current_appointment_id', None):
                continue  # Skip current appointment if updating
            
            existing_end = existing.appointment_datetime + timedelta(minutes=existing.duration_minutes)
            
            # Check for overlap
            if (appointment_datetime < existing_end and end_time > existing.appointment_datetime):
                return f"Conflicts with appointment at {existing.appointment_datetime.strftime('%Y-%m-%d %H:%M')}"
        
        return None
    
    def cancel_appointment(self, appointment_id: int, reason: str = None) -> Tuple[bool, str]:
        """
        Cancel an appointment.
        
        Args:
            appointment_id: ID of appointment to cancel
            reason: Optional cancellation reason
            
        Returns:
            Tuple of (success, error message)
        """
        appointment = self.db_manager.get_by_id(Appointment, appointment_id)
        if not appointment:
            return False, "Appointment not found"
        
        if appointment.status == Appointment.STATUS_CANCELLED:
            return False, "Appointment is already cancelled"
        
        if appointment.status == Appointment.STATUS_COMPLETED:
            return False, "Cannot cancel a completed appointment"
        
        appointment.cancel(reason)
        success = self.db_manager.save(appointment)
        
        if success:
            return True, None
        else:
            return False, "Failed to cancel appointment"
    
    def complete_appointment(self, appointment_id: int) -> Tuple[bool, str]:
        """
        Mark an appointment as completed.
        
        Args:
            appointment_id: ID of appointment to complete
            
        Returns:
            Tuple of (success, error message)
        """
        appointment = self.db_manager.get_by_id(Appointment, appointment_id)
        if not appointment:
            return False, "Appointment not found"
        
        if appointment.status == Appointment.STATUS_COMPLETED:
            return False, "Appointment is already completed"
        
        if appointment.status == Appointment.STATUS_CANCELLED:
            return False, "Cannot complete a cancelled appointment"
        
        # Get customer_id before completing (to avoid detached instance)
        customer_id = appointment.customer_id
        price_paid = appointment.price_paid
        
        appointment.complete()
        success = self.db_manager.save(appointment)
        
        if success:
            # Reload appointment to get completed_at
            completed_appointment = self.db_manager.get_by_id(Appointment, appointment.id)
            
            # Update customer statistics
            customer = self.db_manager.get_by_id(Customer, customer_id)
            if customer:
                customer.total_visits += 1
                customer.total_spent += price_paid
                if completed_appointment and completed_appointment.completed_at:
                    customer.last_visit = completed_appointment.completed_at
                self.db_manager.save(customer)
            
            # Auto-record revenue
            self.financial_service.record_revenue(appointment.id, price_paid)
            
            # Update customer preferences (use the appointment we just completed)
            self.recommendation_service.update_preferences_from_appointment(appointment)
            
            return True, None
        else:
            return False, "Failed to complete appointment"
    
    def get_available_slots(self, service_id: int, date: datetime.date, 
                           start_hour: int = 9, end_hour: int = 17) -> List[datetime]:
        """
        Get available time slots for a service on a given date.
        
        Args:
            service_id: ID of the service
            date: Date to check
            start_hour: Starting hour (default: 9 AM)
            end_hour: Ending hour (default: 5 PM)
            
        Returns:
            List of available datetime slots
        """
        service = self.db_manager.get_by_id(Service, service_id)
        if not service or not service.is_available:
            return []
        
        # Get all scheduled appointments for this service on this date
        scheduled = self.db_manager.find(
            Appointment,
            service_id=service_id,
            status=Appointment.STATUS_SCHEDULED
        )
        
        # Filter to appointments on the target date
        date_appointments = [
            apt for apt in scheduled
            if apt.appointment_datetime.date() == date
        ]
        
        # Generate time slots (every 30 minutes)
        available_slots = []
        current_time = datetime.combine(date, datetime.min.time().replace(hour=start_hour))
        end_time = datetime.combine(date, datetime.min.time().replace(hour=end_hour))
        
        slot_duration = timedelta(minutes=30)
        
        while current_time + timedelta(minutes=service.duration_minutes) <= end_time:
            # Check if this slot conflicts with existing appointments
            slot_end = current_time + timedelta(minutes=service.duration_minutes)
            has_conflict = False
            
            for apt in date_appointments:
                apt_end = apt.appointment_datetime + timedelta(minutes=apt.duration_minutes)
                if current_time < apt_end and slot_end > apt.appointment_datetime:
                    has_conflict = True
                    break
            
            if not has_conflict:
                available_slots.append(current_time)
            
            current_time += slot_duration
        
        return available_slots
    
    def reschedule_appointment(self, appointment_id: int, new_datetime: datetime) -> Tuple[bool, str]:
        """
        Reschedule an appointment to a new time.
        
        Args:
            appointment_id: ID of appointment to reschedule
            new_datetime: New appointment date and time
            
        Returns:
            Tuple of (success, error message)
        """
        appointment = self.db_manager.get_by_id(Appointment, appointment_id)
        if not appointment:
            return False, "Appointment not found"
        
        if appointment.status != Appointment.STATUS_SCHEDULED:
            return False, f"Cannot reschedule {appointment.status} appointment"
        
        # Check for conflicts (excluding current appointment)
        self._current_appointment_id = appointment.id
        conflict = self.check_conflict(
            appointment.service_id,
            new_datetime,
            appointment.duration_minutes
        )
        delattr(self, '_current_appointment_id')
        
        if conflict:
            return False, f"Time slot conflict: {conflict}"
        
        # Update appointment
        success = self.db_manager.update(appointment, appointment_datetime=new_datetime)
        
        if success:
            return True, None
        else:
            return False, "Failed to reschedule appointment"
    
    def get_appointments_by_customer(self, customer_id: int) -> List[Appointment]:
        """Get all appointments for a customer."""
        return self.db_manager.find(Appointment, customer_id=customer_id)
    
    def get_appointments_by_service(self, service_id: int) -> List[Appointment]:
        """Get all appointments for a service."""
        return self.db_manager.find(Appointment, service_id=service_id)
    
    def get_appointments_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Appointment]:
        """Get appointments within a date range."""
        all_appointments = self.db_manager.get_all(Appointment)
        return [
            apt for apt in all_appointments
            if start_date <= apt.appointment_datetime <= end_date
        ]
    
    def get_appointments_by_status(self, status: str) -> List[Appointment]:
        """Get appointments by status."""
        return self.db_manager.find(Appointment, status=status)

