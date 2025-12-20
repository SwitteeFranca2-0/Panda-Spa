"""
Recommendation Service for business logic.
Handles customer preference learning and service recommendations.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from database.db_manager import DatabaseManagement
from models.customer_preference import CustomerPreference
from models.appointment import Appointment
from models.service import Service
from models.customer import Customer


class RecommendationService:
    """
    Business logic service for customer preferences and recommendations.
    Learns from customer behavior and provides personalized service suggestions.
    """
    
    def __init__(self, db_manager: DatabaseManagement):
        """
        Initialize recommendation service.
        
        Args:
            db_manager: DatabaseManagement instance
        """
        self.db_manager = db_manager
    
    def update_preferences_from_appointment(self, appointment: Appointment) -> bool:
        """
        Update customer preferences based on a completed appointment.
        
        Args:
            appointment: Completed appointment (may be detached)
            
        Returns:
            True if preferences updated successfully
        """
        # Reload appointment to ensure we have all values
        appointment_id = appointment.id
        fresh_appointment = self.db_manager.get_by_id(Appointment, appointment_id)
        if not fresh_appointment:
            return False
        
        # Get values from fresh appointment
        customer_id = fresh_appointment.customer_id
        service_id = fresh_appointment.service_id
        price_paid = fresh_appointment.price_paid
        completed_at = fresh_appointment.completed_at
        appointment_datetime = fresh_appointment.appointment_datetime
        
        # Get or create preference record
        preference = self.db_manager.find_one(
            CustomerPreference,
            customer_id=customer_id,
            service_id=service_id
        )
        
        if not preference:
            # Create new preference
            preference = CustomerPreference(
                customer_id=customer_id,
                service_id=service_id,
                preference_score=0.0
            )
            self.db_manager.save(preference)
            # Reload to get ID
            preference = self.db_manager.find_one(
                CustomerPreference,
                customer_id=customer_id,
                service_id=service_id
            )
        
        if preference:
            # Update preference metrics
            visit_date = completed_at or appointment_datetime
            preference.update_from_appointment(price_paid, visit_date)
            
            # Recalculate preference score
            preference.preference_score = self._calculate_preference_score(preference)
            
            return self.db_manager.save(preference)
        
        return False
    
    def _calculate_preference_score(self, preference: CustomerPreference) -> float:
        """
        Calculate preference score based on various factors.
        
        Args:
            preference: CustomerPreference object
            
        Returns:
            Preference score (0.0 - 10.0)
        """
        score = 0.0
        
        # Factor 1: Visit frequency (0-4 points)
        # More visits = higher score
        if preference.visit_count > 0:
            visit_score = min(4.0, preference.visit_count * 0.5)
            score += visit_score
        
        # Factor 2: Recency (0-3 points)
        # More recent visits = higher score
        if preference.last_visited:
            days_since = (datetime.utcnow() - preference.last_visited).days
            if days_since <= 7:
                recency_score = 3.0
            elif days_since <= 30:
                recency_score = 2.0
            elif days_since <= 90:
                recency_score = 1.0
            else:
                recency_score = 0.5
            score += recency_score
        
        # Factor 3: Spending (0-2 points)
        # Higher spending = higher preference
        if preference.total_spent > 0:
            # Normalize spending (assume $100+ is high)
            spending_score = min(2.0, preference.total_spent / 50.0)
            score += spending_score
        
        # Factor 4: Rating (0-1 point)
        # If customer rates services
        if preference.average_rating:
            rating_score = (preference.average_rating - 1.0) / 4.0  # Scale 1-5 to 0-1
            score += rating_score
        
        # Cap at 10.0
        return min(10.0, score)
    
    def get_recommendations(self, customer_id: int, limit: int = 3) -> List[Tuple[Service, float, str]]:
        """
        Get personalized service recommendations for a customer.
        
        Args:
            customer_id: ID of the customer
            limit: Maximum number of recommendations (default: 3)
            
        Returns:
            List of tuples: (Service, preference_score, reason)
        """
        # Get customer's existing preferences
        customer_preferences = self.db_manager.find(
            CustomerPreference,
            customer_id=customer_id
        )
        
        # Get all available services
        available_services = self.db_manager.find(Service, is_available=True)
        
        recommendations = []
        
        # Strategy 1: Recommend based on customer's past preferences
        if customer_preferences:
            # Sort by preference score
            sorted_prefs = sorted(
                customer_preferences,
                key=lambda p: p.preference_score,
                reverse=True
            )
            
            for pref in sorted_prefs[:limit]:
                service = self.db_manager.get_by_id(Service, pref.service_id)
                if service and service.is_available:
                    reason = self._get_recommendation_reason(customer_id, pref.service_id, "preference")
                    recommendations.append((service, pref.preference_score, reason))
        
        # Strategy 2: If not enough recommendations, add popular services
        if len(recommendations) < limit:
            popular_services = self._get_popular_services(limit - len(recommendations))
            for service in popular_services:
                # Check if already recommended
                if not any(rec[0].id == service.id for rec in recommendations):
                    reason = self._get_recommendation_reason(customer_id, service.id, "popular")
                    recommendations.append((service, 0.0, reason))
        
        # Strategy 3: If still not enough, add complementary services
        if len(recommendations) < limit and customer_preferences:
            # Get services that complement customer's preferred services
            preferred_service_ids = [p.service_id for p in customer_preferences[:2]]
            complementary = self._get_complementary_services(preferred_service_ids, limit - len(recommendations))
            for service in complementary:
                if not any(rec[0].id == service.id for rec in recommendations):
                    reason = self._get_recommendation_reason(customer_id, service.id, "complementary")
                    recommendations.append((service, 0.0, reason))
        
        return recommendations[:limit]
    
    def _get_recommendation_reason(self, customer_id: int, service_id: int, reason_type: str) -> str:
        """
        Generate a human-readable reason for recommendation.
        
        Args:
            customer_id: ID of the customer
            service_id: ID of the service
            reason_type: Type of reason (preference, popular, complementary)
            
        Returns:
            Reason string
        """
        service = self.db_manager.get_by_id(Service, service_id)
        if not service:
            return "Recommended service"
        
        if reason_type == "preference":
            preference = self.db_manager.find_one(
                CustomerPreference,
                customer_id=customer_id,
                service_id=service_id
            )
            if preference:
                if preference.visit_count > 3:
                    return f"You've booked this {preference.visit_count} times - a favorite!"
                elif preference.visit_count > 1:
                    return f"You've enjoyed this before ({preference.visit_count} visits)"
                else:
                    return "Based on your past booking"
        
        elif reason_type == "popular":
            return "Popular choice among our guests"
        
        elif reason_type == "complementary":
            return "Complements your preferred services"
        
        return "Recommended for you"
    
    def _get_popular_services(self, limit: int = 5) -> List[Service]:
        """
        Get most popular services overall.
        
        Args:
            limit: Maximum number of services to return
            
        Returns:
            List of popular services
        """
        # Get all preferences and count visits per service
        all_preferences = self.db_manager.get_all(CustomerPreference)
        
        service_visits = {}
        for pref in all_preferences:
            service_visits[pref.service_id] = service_visits.get(pref.service_id, 0) + pref.visit_count
        
        # Sort by visit count
        sorted_services = sorted(service_visits.items(), key=lambda x: x[1], reverse=True)
        
        # Get service objects
        popular_services = []
        for service_id, _ in sorted_services[:limit]:
            service = self.db_manager.get_by_id(Service, service_id)
            if service and service.is_available:
                popular_services.append(service)
        
        return popular_services
    
    def _get_complementary_services(self, service_ids: List[int], limit: int = 3) -> List[Service]:
        """
        Get services that complement the given services.
        
        Args:
            service_ids: List of service IDs
            limit: Maximum number of services to return
            
        Returns:
            List of complementary services
        """
        # Simple strategy: if customer likes thermal baths, suggest massages
        # If customer likes massages, suggest tea therapy
        complementary_map = {
            Service.THERMAL_BATH: [Service.MASSAGE, Service.TEA_THERAPY],
            Service.MASSAGE: [Service.TEA_THERAPY, Service.THERMAL_BATH],
            Service.TEA_THERAPY: [Service.MASSAGE, Service.THERMAL_BATH]
        }
        
        complementary_services = []
        for service_id in service_ids:
            service = self.db_manager.get_by_id(Service, service_id)
            if service and service.service_type in complementary_map:
                for comp_type in complementary_map[service.service_type]:
                    comp_services = self.db_manager.find(Service, service_type=comp_type, is_available=True)
                    for comp_service in comp_services[:limit]:
                        if comp_service.id not in [s.id for s in complementary_services]:
                            complementary_services.append(comp_service)
                            if len(complementary_services) >= limit:
                                return complementary_services
        
        return complementary_services[:limit]
    
    def get_customer_preferences(self, customer_id: int) -> List[CustomerPreference]:
        """
        Get all preferences for a customer.
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            List of CustomerPreference objects
        """
        return self.db_manager.find(CustomerPreference, customer_id=customer_id)
    
    def get_top_preferences(self, customer_id: int, limit: int = 5) -> List[CustomerPreference]:
        """
        Get top N preferred services for a customer.
        
        Args:
            customer_id: ID of the customer
            limit: Maximum number of preferences to return
            
        Returns:
            List of CustomerPreference objects sorted by score
        """
        preferences = self.get_customer_preferences(customer_id)
        sorted_prefs = sorted(
            preferences,
            key=lambda p: p.preference_score,
            reverse=True
        )
        return sorted_prefs[:limit]

