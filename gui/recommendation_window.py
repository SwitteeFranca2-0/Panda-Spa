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
        self._show_welcome_message()
    
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Configure Treeview style to set row height (prevents overlapping rows)
        style = ttk.Style()
        style.configure("Treeview", rowheight=50)  # Set row height to 50 pixels
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
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
        
        ttk.Button(selection_frame, text="Get Recommendations", command=self._load_recommendations).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(selection_frame, text="Clear Selection", command=self._clear_selection).pack(side=tk.LEFT)
        
        # Recommendations panel
        rec_frame = ttk.LabelFrame(main_frame, text="Personalized Recommendations", padding="10")
        rec_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        rec_frame.columnconfigure(0, weight=1)
        rec_frame.rowconfigure(0, weight=1)
        
        # Treeview container with scrollbar
        rec_tree_frame = ttk.Frame(rec_frame)
        rec_tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        rec_tree_frame.columnconfigure(0, weight=1)
        rec_tree_frame.rowconfigure(0, weight=1)
        
        # Recommendations list
        columns = ('Service', 'Type', 'Price', 'Score', 'Reason')
        self.recommendations_tree = ttk.Treeview(rec_tree_frame, columns=columns, show='headings', height=8)
        
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
        
        self.recommendations_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.recommendations_tree.bind('<Double-1>', self._on_recommendation_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(rec_tree_frame, orient=tk.VERTICAL, command=self.recommendations_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.recommendations_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(action_frame, text="📅 Book Selected Service", command=self._book_recommended).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📋 View Customer History", command=self._view_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="⭐ View Popular Services", command=self._view_popular).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🔄 Refresh", command=self._refresh_all).pack(side=tk.LEFT, padx=5)
        
        # Customer preferences panel
        pref_frame = ttk.LabelFrame(main_frame, text="Customer Preferences", padding="10")
        pref_frame.pack(fill=tk.BOTH, expand=True)
        pref_frame.columnconfigure(0, weight=1)
        pref_frame.rowconfigure(0, weight=1)
        
        # Treeview container with scrollbar
        pref_tree_frame = ttk.Frame(pref_frame)
        pref_tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        pref_tree_frame.columnconfigure(0, weight=1)
        pref_tree_frame.rowconfigure(0, weight=1)
        
        # Preferences list
        pref_columns = ('Service', 'Visits', 'Total Spent', 'Score', 'Last Visit')
        self.preferences_tree = ttk.Treeview(pref_tree_frame, columns=pref_columns, show='headings', height=8)
        
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
        
        self.preferences_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for preferences
        pref_scrollbar = ttk.Scrollbar(pref_tree_frame, orient=tk.VERTICAL, command=self.preferences_tree.yview)
        pref_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.preferences_tree.configure(yscrollcommand=pref_scrollbar.set)
    
    def _load_customers(self):
        """Load customers into combo box."""
        customers = self.db_manager.get_all(Customer)
        customer_list = [f"{c.id}: {c.name} ({c.species})" for c in customers]
        self.customer_combo['values'] = customer_list
    
    def _show_welcome_message(self):
        """Show welcome message in recommendations tree."""
        self.recommendations_tree.insert('', tk.END, values=(
            "Select a customer to see recommendations",
            "",
            "",
            "",
            "Choose a customer from the dropdown above"
        ))
    
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
            
            if not recommendations:
                # Show message if no recommendations available
                self.recommendations_tree.insert('', tk.END, values=(
                    "No recommendations available",
                    "",
                    "",
                    "",
                    "Try completing some appointments first to build preferences"
                ))
                return
            
            # Add to treeview
            for service, score, reason in recommendations:
                type_display = service.service_type.replace('_', ' ').title()
                
                # Color code by score
                tag = 'high_score' if score >= 5.0 else 'medium_score' if score >= 2.0 else 'low_score'
                
                self.recommendations_tree.insert('', tk.END, values=(
                    service.name,
                    type_display,
                    f"${service.price:.2f}",
                    f"{score:.1f}/10.0",
                    reason
                ), tags=(service.id, tag))
            
            # Configure tags for colors
            self.recommendations_tree.tag_configure('high_score', foreground='green')
            self.recommendations_tree.tag_configure('medium_score', foreground='blue')
            self.recommendations_tree.tag_configure('low_score', foreground='gray')
        except (ValueError, IndexError) as e:
            messagebox.showerror("Error", f"Failed to load recommendations: {e}")
    
    def _load_customer_preferences(self):
        """Load customer's preference history."""
        # Clear existing preferences
        for item in self.preferences_tree.get_children():
            self.preferences_tree.delete(item)
        
        if not self.current_customer:
            return
        
        # Get customer preferences
        preferences = self.recommendation_service.get_customer_preferences(self.current_customer.id)
        
        if not preferences:
            # Show message if no preferences
            self.preferences_tree.insert('', tk.END, values=(
                "No preferences yet",
                "",
                "",
                "",
                "Complete appointments to build preferences"
            ))
            return
        
        # Sort by preference score
        sorted_prefs = sorted(preferences, key=lambda p: p.preference_score, reverse=True)
        
        # Add to treeview
        for pref in sorted_prefs:
            service = self.db_manager.get_by_id(Service, pref.service_id)
            if service:
                last_visit_str = pref.last_visited.strftime('%Y-%m-%d') if pref.last_visited else 'Never'
                
                # Color code by score
                tag = 'high_score' if pref.preference_score >= 5.0 else 'medium_score' if pref.preference_score >= 2.0 else 'low_score'
                
                self.preferences_tree.insert('', tk.END, values=(
                    service.name,
                    pref.visit_count,
                    f"${pref.total_spent:.2f}",
                    f"{pref.preference_score:.1f}/10.0",
                    last_visit_str
                ), tags=(tag,))
        
        # Configure tags for colors
        self.preferences_tree.tag_configure('high_score', foreground='green')
        self.preferences_tree.tag_configure('medium_score', foreground='blue')
        self.preferences_tree.tag_configure('low_score', foreground='gray')
    
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
        
        # Open appointment window (lazy import to avoid circular dependency)
        from gui.appointment_window import AppointmentWindow
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
        
        if not popular_services:
            self.recommendations_tree.insert('', tk.END, values=(
                "No popular services yet",
                "",
                "",
                "",
                "Services will appear here as customers book them"
            ))
            messagebox.showinfo("Info", "No popular services data available yet.")
            return
        
        for service in popular_services:
            type_display = service.service_type.replace('_', ' ').title()
            
            self.recommendations_tree.insert('', tk.END, values=(
                service.name,
                type_display,
                f"${service.price:.2f}",
                "Popular",
                "Popular choice among our guests"
            ), tags=('popular',))
        
        self.recommendations_tree.tag_configure('popular', foreground='orange')
        messagebox.showinfo("Info", f"Showing {len(popular_services)} most popular services overall.")
    
    def _refresh_all(self):
        """Refresh recommendations and preferences."""
        if self.current_customer:
            self._load_recommendations()
            self._load_customer_preferences()
        else:
            messagebox.showwarning("Warning", "Please select a customer first!")
    
    def _clear_selection(self):
        """Clear customer selection and reset views."""
        self.customer_combo.set('')
        self.current_customer = None
        
        # Clear recommendations
        for item in self.recommendations_tree.get_children():
            self.recommendations_tree.delete(item)
        
        # Clear preferences
        for item in self.preferences_tree.get_children():
            self.preferences_tree.delete(item)
        
        # Show welcome message
        self.recommendations_tree.insert('', tk.END, values=(
            "Select a customer to see recommendations",
            "",
            "",
            "",
            "Choose a customer from the dropdown above"
        ))

