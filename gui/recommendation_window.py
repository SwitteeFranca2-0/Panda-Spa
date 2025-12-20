"""
Recommendation Window for Panda Spa.
Provides GUI for viewing personalized service recommendations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from database.db_manager import DatabaseManagement
from models.customer import Customer
from models.service import Service
from services.recommendation_service import RecommendationService


class RecommendationWindow:
    """
    Window for viewing and booking service recommendations.
    """
    
    def __init__(self, parent: tk.Tk, db_manager: DatabaseManagement):
        """
        Initialize recommendation window.
        
        Args:
            parent: Parent Tkinter window
            db_manager: DatabaseManagement instance
        """
        self.parent = parent
        self.db_manager = db_manager
        self.recommendation_service = RecommendationService(db_manager)
        self.current_customer: Optional[Customer] = None
        
        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title("Panda Spa - Service Recommendations")
        self.window.geometry("900x700")
        
        self._create_widgets()
        self._load_customers()
    
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Customer selection
        selection_frame = ttk.LabelFrame(main_frame, text="Select Customer", padding="10")
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(selection_frame, text="Customer:").pack(side=tk.LEFT, padx=(0, 10))
        self.customer_combo = ttk.Combobox(selection_frame, width=40, state="readonly")
        self.customer_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.customer_combo.bind('<<ComboboxSelected>>', self._on_customer_select)
        
        ttk.Button(selection_frame, text="Get Recommendations", command=self._load_recommendations).pack(side=tk.LEFT)
        
        # Recommendations panel
        rec_frame = ttk.LabelFrame(main_frame, text="Personalized Recommendations", padding="10")
        rec_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Recommendations list
        columns = ('Service', 'Type', 'Price', 'Score', 'Reason')
        self.recommendations_tree = ttk.Treeview(rec_frame, columns=columns, show='headings', height=10)
        
        self.recommendations_tree.heading('Service', text='Service Name')
        self.recommendations_tree.heading('Type', text='Type')
        self.recommendations_tree.heading('Price', text='Price ($)')
        self.recommendations_tree.heading('Score', text='Preference Score')
        self.recommendations_tree.heading('Reason', text='Why Recommended')
        
        self.recommendations_tree.column('Service', width=200)
        self.recommendations_tree.column('Type', width=120)
        self.recommendations_tree.column('Price', width=100)
        self.recommendations_tree.column('Score', width=120)
        self.recommendations_tree.column('Reason', width=300)
        
        self.recommendations_tree.pack(fill=tk.BOTH, expand=True)
        self.recommendations_tree.bind('<Double-1>', self._on_recommendation_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(rec_frame, orient=tk.VERTICAL, command=self.recommendations_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recommendations_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(action_frame, text="Book Selected Service", command=self._book_recommended).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="View Customer History", command=self._view_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="View Popular Services", command=self._view_popular).pack(side=tk.LEFT, padx=5)
        
        # Customer preferences panel
        pref_frame = ttk.LabelFrame(main_frame, text="Customer Preferences", padding="10")
        pref_frame.pack(fill=tk.BOTH, expand=True)
        
        # Preferences list
        pref_columns = ('Service', 'Visits', 'Total Spent', 'Score', 'Last Visit')
        self.preferences_tree = ttk.Treeview(pref_frame, columns=pref_columns, show='headings', height=8)
        
        self.preferences_tree.heading('Service', text='Service Name')
        self.preferences_tree.heading('Visits', text='Visits')
        self.preferences_tree.heading('Total Spent', text='Total Spent ($)')
        self.preferences_tree.heading('Score', text='Preference Score')
        self.preferences_tree.heading('Last Visit', text='Last Visit')
        
        self.preferences_tree.column('Service', width=200)
        self.preferences_tree.column('Visits', width=80)
        self.preferences_tree.column('Total Spent', width=120)
        self.preferences_tree.column('Score', width=120)
        self.preferences_tree.column('Last Visit', width=150)
        
        self.preferences_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for preferences
        pref_scrollbar = ttk.Scrollbar(pref_frame, orient=tk.VERTICAL, command=self.preferences_tree.yview)
        pref_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preferences_tree.configure(yscrollcommand=pref_scrollbar.set)
    
    def _load_customers(self):
        """Load customers into combo box."""
        customers = self.db_manager.get_all(Customer)
        customer_list = [f"{c.id}: {c.name} ({c.species})" for c in customers]
        self.customer_combo['values'] = customer_list
    
    def _on_customer_select(self, event=None):
        """Handle customer selection."""
        self._load_recommendations()
        self._load_customer_preferences()
    
    def _load_recommendations(self):
        """Load recommendations for selected customer."""
        # Clear existing recommendations
        for item in self.recommendations_tree.get_children():
            self.recommendations_tree.delete(item)
        
        if not self.customer_combo.get():
            return
        
        try:
            customer_id = int(self.customer_combo.get().split(':')[0])
            self.current_customer = self.db_manager.get_by_id(Customer, customer_id)
            
            if not self.current_customer:
                return
            
            # Get recommendations
            recommendations = self.recommendation_service.get_recommendations(customer_id, limit=5)
            
            # Add to treeview
            for service, score, reason in recommendations:
                type_display = service.service_type.replace('_', ' ').title()
                
                self.recommendations_tree.insert('', tk.END, values=(
                    service.name,
                    type_display,
                    f"${service.price:.2f}",
                    f"{score:.1f}/10.0",
                    reason
                ), tags=(service.id,))
        except (ValueError, IndexError):
            pass
    
    def _load_customer_preferences(self):
        """Load customer's preference history."""
        # Clear existing preferences
        for item in self.preferences_tree.get_children():
            self.preferences_tree.delete(item)
        
        if not self.current_customer:
            return
        
        # Get customer preferences
        preferences = self.recommendation_service.get_customer_preferences(self.current_customer.id)
        
        # Sort by preference score
        sorted_prefs = sorted(preferences, key=lambda p: p.preference_score, reverse=True)
        
        # Add to treeview
        for pref in sorted_prefs:
            service = self.db_manager.get_by_id(Service, pref.service_id)
            if service:
                last_visit_str = pref.last_visited.strftime('%Y-%m-%d') if pref.last_visited else 'Never'
                
                self.preferences_tree.insert('', tk.END, values=(
                    service.name,
                    pref.visit_count,
                    f"${pref.total_spent:.2f}",
                    f"{pref.preference_score:.1f}/10.0",
                    last_visit_str
                ))
    
    def _on_recommendation_select(self, event):
        """Handle recommendation selection."""
        selection = self.recommendations_tree.selection()
        if selection:
            self._book_recommended()
    
    def _book_recommended(self):
        """Open appointment window to book selected recommendation."""
        selection = self.recommendations_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a recommendation to book!")
            return
        
        if not self.current_customer:
            messagebox.showwarning("Warning", "Please select a customer first!")
            return
        
        item = self.recommendations_tree.item(selection[0])
        service_name = item['values'][0]
        
        # Find service by name
        services = self.db_manager.find(Service, name=service_name)
        if not services:
            messagebox.showerror("Error", "Service not found!")
            return
        
        service = services[0]
        
        # Open appointment window
        appointment_window = AppointmentWindow(self.parent, self.db_manager)
        
        # Pre-fill customer and service
        customer_str = f"{self.current_customer.id}: {self.current_customer.name} ({self.current_customer.species})"
        appointment_window.customer_combo.set(customer_str)
        
        service_str = f"{service.id}: {service.name} (${service.price:.2f})"
        appointment_window.service_combo.set(service_str)
        
        messagebox.showinfo("Success", f"Appointment window opened with {service_name} selected!\nPlease choose a date and time.")
    
    def _view_history(self):
        """View customer's booking history."""
        if not self.current_customer:
            messagebox.showwarning("Warning", "Please select a customer first!")
            return
        
        # Open appointment window filtered to this customer (lazy import)
        from gui.appointment_window import AppointmentWindow
        appointment_window = AppointmentWindow(self.parent, self.db_manager)
        messagebox.showinfo("Info", f"Viewing appointments for {self.current_customer.name}.\nUse filters in the appointment window.")
    
    def _view_popular(self):
        """View popular services overall."""
        # Clear recommendations and show popular services
        for item in self.recommendations_tree.get_children():
            self.recommendations_tree.delete(item)
        
        popular_services = self.recommendation_service._get_popular_services(limit=10)
        
        for service in popular_services:
            type_display = service.service_type.replace('_', ' ').title()
            
            self.recommendations_tree.insert('', tk.END, values=(
                service.name,
                type_display,
                f"${service.price:.2f}",
                "Popular",
                "Popular choice among our guests"
            ))
        
        messagebox.showinfo("Info", "Showing most popular services overall.")

