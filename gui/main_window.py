"""
Main Window for Panda Spa application.
Provides navigation and dashboard view.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, date, timedelta
from database.db_manager import DatabaseManagement
from gui.customer_window import CustomerWindow
from gui.service_window import ServiceWindow
from gui.appointment_window import AppointmentWindow
from gui.financial_window import FinancialWindow
from gui.recommendation_window import RecommendationWindow
from gui.feeling_mapping_window import FeelingMappingWindow
from services.financial_service import FinancialService
from services.appointment_service import AppointmentService
from models.customer import Customer
from models.service import Service
from models.appointment import Appointment


class MainWindow:
    """
    Main application window with navigation and dashboard.
    """
    
    def __init__(self, db_manager: DatabaseManagement):
        """
        Initialize main window.
        
        Args:
            db_manager: DatabaseManagement instance
        """
        self.db_manager = db_manager
        self.financial_service = FinancialService(db_manager)
        self.appointment_service = AppointmentService(db_manager)
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("🐼 Panda Spa - Thermal Water Wellness Center")
        self.root.geometry("800x600")
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap('panda.ico')
        except:
            pass  # Icon file not available
        
        self._create_widgets()
        self._update_dashboard()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Configure Treeview style to set row height (prevents overlapping rows)
        style = ttk.Style()
        style.configure("Treeview", rowheight=50)  # Set row height to 50 pixels
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🐼 Panda Spa",
            font=("Arial", 32, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Thermal Water Wellness Center",
            font=("Arial", 14),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitle_label.pack()
        
        # Main container
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Navigation
        nav_frame = ttk.LabelFrame(main_container, text="Navigation", padding="15")
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Navigation buttons
        nav_buttons = [
            ("👥 Manage Customers", self._open_customers),
            ("💆 Manage Services", self._open_services),
            ("📅 Manage Appointments", self._open_appointments),
            ("💰 Financial Management", self._open_financial),
            ("⭐ Service Recommendations", self._open_recommendations),
            ("🎭 Configure Feeling Mappings", self._open_feeling_mappings),
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(
                nav_frame,
                text=text,
                command=command,
                width=25,
                height=2,
                font=("Arial", 11),
                bg="#3498db",
                fg="white",
                relief=tk.FLAT,
                cursor="hand2"
            )
            btn.pack(pady=8)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2980b9"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#3498db"))
        
        # Right panel - Dashboard
        dashboard_frame = ttk.LabelFrame(main_container, text="Dashboard", padding="15")
        dashboard_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Quick stats
        stats_frame = ttk.Frame(dashboard_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Stats cards
        self.stats_cards = {}
        stats_data = [
            ("Total Customers", "customers", "#3498db"),
            ("Active Services", "services", "#2ecc71"),
            ("Today's Appointments", "appointments", "#e74c3c"),
            ("Today's Revenue", "revenue", "#f39c12"),
        ]
        
        for i, (label, key, color) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg=color, relief=tk.RAISED, bd=2)
            card.grid(row=0, column=i, padx=10, sticky=(tk.W, tk.E))
            
            label_widget = tk.Label(
                card,
                text=label,
                font=("Arial", 10),
                bg=color,
                fg="white"
            )
            label_widget.pack(pady=(10, 5))
            
            value_widget = tk.Label(
                card,
                text="0",
                font=("Arial", 18, "bold"),
                bg=color,
                fg="white"
            )
            value_widget.pack(pady=(0, 10))
            
            self.stats_cards[key] = value_widget
        
        # Configure style to prevent row overlap (must be before Treeview creation)
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # Recent appointments
        recent_frame = ttk.LabelFrame(dashboard_frame, text="Today's Appointments", padding="10")
        recent_frame.pack(fill=tk.BOTH, expand=True)
        recent_frame.columnconfigure(0, weight=1)
        recent_frame.rowconfigure(0, weight=1)
        
        # Treeview container frame
        tree_frame = ttk.Frame(recent_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Appointments list
        columns = ('Time', 'Customer', 'Service', 'Status')
        self.appointments_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
        
        self.appointments_tree.heading('Time', text='Time')
        self.appointments_tree.heading('Customer', text='Customer')
        self.appointments_tree.heading('Service', text='Service')
        self.appointments_tree.heading('Status', text='Status')
        
        self.appointments_tree.column('Time', width=120, anchor=tk.CENTER)
        self.appointments_tree.column('Customer', width=150, anchor=tk.W)
        self.appointments_tree.column('Service', width=150, anchor=tk.W)
        self.appointments_tree.column('Status', width=100, anchor=tk.CENTER)
        
        self.appointments_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for appointments
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.appointments_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.appointments_tree.configure(yscrollcommand=scrollbar.set)
        
        # Refresh button
        refresh_btn = tk.Button(
            dashboard_frame,
            text="🔄 Refresh Dashboard",
            command=self._update_dashboard,
            bg="#95a5a6",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2"
        )
        refresh_btn.pack(pady=10)
    
    def _update_dashboard(self):
        """Update dashboard with current statistics."""
        # Update customer count
        customers = self.db_manager.get_all(Customer)
        self.stats_cards['customers'].config(text=str(len(customers)))
        
        # Update active services count
        active_services = self.db_manager.find(Service, is_available=True)
        self.stats_cards['services'].config(text=str(len(active_services)))
        
        # Update today's appointments
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        all_appointments = self.db_manager.get_all(Appointment)
        today_appointments = [
            apt for apt in all_appointments
            if start_of_day <= apt.appointment_datetime <= end_of_day
        ]
        
        self.stats_cards['appointments'].config(text=str(len(today_appointments)))
        
        # Update today's revenue
        today_revenue = self.financial_service.calculate_revenue(start_of_day, end_of_day)
        self.stats_cards['revenue'].config(text=f"${today_revenue:.2f}")
        
        # Update appointments list
        for item in self.appointments_tree.get_children():
            self.appointments_tree.delete(item)
        
        # Sort appointments by time
        today_appointments.sort(key=lambda x: x.appointment_datetime)
        
        for appointment in today_appointments[:10]:  # Show up to 10
            customer = self.db_manager.get_by_id(Customer, appointment.customer_id)
            service = self.db_manager.get_by_id(Service, appointment.service_id)
            
            customer_name = customer.name if customer else f"ID:{appointment.customer_id}"
            service_name = service.name if service else f"ID:{appointment.service_id}"
            time_str = appointment.appointment_datetime.strftime('%H:%M')
            status_display = appointment.status.replace('_', ' ').title()
            
            # Color code by status
            tag = appointment.status
            
            self.appointments_tree.insert('', tk.END, values=(
                time_str,
                customer_name,
                service_name,
                status_display
            ), tags=(tag,))
        
        # Configure tags for colors
        self.appointments_tree.tag_configure('scheduled', foreground='blue')
        self.appointments_tree.tag_configure('completed', foreground='green')
        self.appointments_tree.tag_configure('cancelled', foreground='red')
        self.appointments_tree.tag_configure('no_show', foreground='orange')
    
    def _open_customers(self):
        """Open customer management window."""
        CustomerWindow(self.root, self.db_manager)
    
    def _open_services(self):
        """Open service management window."""
        ServiceWindow(self.root, self.db_manager)
    
    def _open_appointments(self):
        """Open appointment management window."""
        AppointmentWindow(self.root, self.db_manager)
    
    def _open_financial(self):
        """Open financial management window."""
        FinancialWindow(self.root, self.db_manager)
    
    def _open_recommendations(self):
        """Open recommendation window."""
        RecommendationWindow(self.root, self.db_manager)
    
    def _open_feeling_mappings(self):
        """Open feeling-service mapping configuration window."""
        FeelingMappingWindow(self.root, self.db_manager)
    
    def _on_closing(self):
        """Handle window closing."""
        self.db_manager.close()
        self.root.destroy()
    
    def run(self):
        """Start the main application loop."""
        self.root.mainloop()

