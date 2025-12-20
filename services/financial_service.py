"""
Financial Service for business logic.
Handles financial calculations, revenue/expense tracking, and reporting.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database.db_manager import DatabaseManagement
from models.financial_record import FinancialRecord
from models.appointment import Appointment
from models.customer import Customer


class FinancialService:
    """
    Business logic service for financial management.
    Handles revenue, expenses, profit calculations, and financial reporting.
    """
    
    def __init__(self, db_manager: DatabaseManagement):
        """
        Initialize financial service.
        
        Args:
            db_manager: DatabaseManagement instance
        """
        self.db_manager = db_manager
    
    def record_revenue(self, appointment_id: int, amount: float = None,
                      description: str = None) -> tuple[Optional[FinancialRecord], str]:
        """
        Record revenue from a completed appointment.
        
        Args:
            appointment_id: ID of the appointment
            amount: Revenue amount (defaults to appointment price)
            description: Optional description
            
        Returns:
            Tuple of (FinancialRecord if successful, error message if failed)
        """
        appointment = self.db_manager.get_by_id(Appointment, appointment_id)
        if not appointment:
            return None, "Appointment not found"
        
        # Get values before object becomes detached
        price_paid = appointment.price_paid
        customer_id = appointment.customer_id
        completed_at = appointment.completed_at
        appointment_datetime = appointment.appointment_datetime
        
        if amount is None:
            amount = price_paid
        
        if description is None:
            customer = self.db_manager.get_by_id(Customer, customer_id)
            customer_name = customer.name if customer else f"Customer {customer_id}"
            description = f"Service revenue from appointment #{appointment_id} - {customer_name}"
        
        financial_record = FinancialRecord(
            transaction_type=FinancialRecord.REVENUE,
            amount=amount,
            description=description,
            category=FinancialRecord.CATEGORY_SERVICE_REVENUE,
            appointment_id=appointment_id,
            transaction_date=completed_at or appointment_datetime
        )
        
        success = self.db_manager.save(financial_record)
        if success:
            # Retrieve fresh instance to avoid detached instance issues
            fresh_record = self.db_manager.get_by_id(FinancialRecord, financial_record.id)
            return fresh_record, None
        else:
            return None, "Failed to save financial record"
    
    def record_expense(self, amount: float, category: str, description: str,
                      supplier_id: int = None, receipt_number: str = None,
                      notes: str = None) -> tuple[Optional[FinancialRecord], str]:
        """
        Record an expense.
        
        Args:
            amount: Expense amount
            category: Expense category
            description: Description of expense
            supplier_id: Optional supplier ID
            receipt_number: Optional receipt number
            notes: Optional notes
            
        Returns:
            Tuple of (FinancialRecord if successful, error message if failed)
        """
        if amount <= 0:
            return None, "Amount must be positive"
        
        if category not in FinancialRecord.get_categories():
            return None, f"Invalid category. Must be one of: {FinancialRecord.get_categories()}"
        
        financial_record = FinancialRecord(
            transaction_type=FinancialRecord.EXPENSE,
            amount=amount,
            description=description,
            category=category,
            supplier_id=supplier_id,
            receipt_number=receipt_number,
            notes=notes
        )
        
        success = self.db_manager.save(financial_record)
        if success:
            return financial_record, None
        else:
            return None, "Failed to save financial record"
    
    def calculate_revenue(self, start_date: datetime = None, end_date: datetime = None) -> float:
        """
        Calculate total revenue for a date range.
        
        Args:
            start_date: Start date (default: beginning of time)
            end_date: End date (default: now)
            
        Returns:
            Total revenue amount
        """
        if end_date is None:
            end_date = datetime.now()
        
        revenue_records = self.db_manager.find(
            FinancialRecord,
            transaction_type=FinancialRecord.REVENUE
        )
        
        total = 0.0
        for record in revenue_records:
            if start_date and record.transaction_date < start_date:
                continue
            if record.transaction_date > end_date:
                continue
            total += record.amount
        
        return total
    
    def calculate_expenses(self, start_date: datetime = None, end_date: datetime = None) -> float:
        """
        Calculate total expenses for a date range.
        
        Args:
            start_date: Start date (default: beginning of time)
            end_date: End date (default: now)
            
        Returns:
            Total expenses amount
        """
        if end_date is None:
            end_date = datetime.now()
        
        expense_records = self.db_manager.find(
            FinancialRecord,
            transaction_type=FinancialRecord.EXPENSE
        )
        
        total = 0.0
        for record in expense_records:
            if start_date and record.transaction_date < start_date:
                continue
            if record.transaction_date > end_date:
                continue
            total += record.amount
        
        return total
    
    def calculate_profit(self, start_date: datetime = None, end_date: datetime = None) -> float:
        """
        Calculate net profit (revenue - expenses) for a date range.
        
        Args:
            start_date: Start date (default: beginning of time)
            end_date: End date (default: now)
            
        Returns:
            Net profit amount
        """
        revenue = self.calculate_revenue(start_date, end_date)
        expenses = self.calculate_expenses(start_date, end_date)
        return revenue - expenses
    
    def get_category_breakdown(self, start_date: datetime = None, 
                               end_date: datetime = None) -> Dict[str, float]:
        """
        Get expense breakdown by category.
        
        Args:
            start_date: Start date (default: beginning of time)
            end_date: End date (default: now)
            
        Returns:
            Dictionary mapping category to total amount
        """
        if end_date is None:
            end_date = datetime.now()
        
        expense_records = self.db_manager.find(
            FinancialRecord,
            transaction_type=FinancialRecord.EXPENSE
        )
        
        breakdown = {}
        for record in expense_records:
            if start_date and record.transaction_date < start_date:
                continue
            if record.transaction_date > end_date:
                continue
            
            category = record.category
            breakdown[category] = breakdown.get(category, 0.0) + record.amount
        
        return breakdown
    
    def get_financial_summary(self, start_date: datetime = None,
                             end_date: datetime = None) -> Dict:
        """
        Get complete financial summary for a date range.
        
        Args:
            start_date: Start date (default: beginning of time)
            end_date: End date (default: now)
            
        Returns:
            Dictionary with revenue, expenses, profit, and category breakdown
        """
        revenue = self.calculate_revenue(start_date, end_date)
        expenses = self.calculate_expenses(start_date, end_date)
        profit = revenue - expenses
        category_breakdown = self.get_category_breakdown(start_date, end_date)
        
        return {
            'revenue': revenue,
            'expenses': expenses,
            'profit': profit,
            'category_breakdown': category_breakdown,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else datetime.now().isoformat()
        }
    
    def get_revenue_by_date_range(self, start_date: datetime, end_date: datetime) -> List[FinancialRecord]:
        """Get revenue records within a date range."""
        all_revenue = self.db_manager.find(FinancialRecord, transaction_type=FinancialRecord.REVENUE)
        return [
            record for record in all_revenue
            if start_date <= record.transaction_date <= end_date
        ]
    
    def get_expenses_by_date_range(self, start_date: datetime, end_date: datetime) -> List[FinancialRecord]:
        """Get expense records within a date range."""
        all_expenses = self.db_manager.find(FinancialRecord, transaction_type=FinancialRecord.EXPENSE)
        return [
            record for record in all_expenses
            if start_date <= record.transaction_date <= end_date
        ]

