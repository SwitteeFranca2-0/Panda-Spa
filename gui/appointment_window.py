"""
Appointment Management Window for Panda Spa.
Provides GUI for creating, viewing, editing, and managing appointments.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta, date
from typing import Optional
from database.db_manager import DatabaseManagement
from models.appointment import Appointment
from models.customer import Customer
from models.service import Service
from services.appointment_service import AppointmentService
from services.recommendation_service import RecommendationService
from gui.recommendation_window import RecommendationWindow


class AppointmentWindow:
    """
    Main window for appointment management.
    Provides full CRUD operations for appointments with scheduling logic.
    """
    
    def __init__(self, parent: tk.Tk, db_manager: DatabaseManagement):
        """
        Initialize appointment management window.
        
        Args:
            parent: Parent Tkinter window
            db_manager: DatabaseManagement instance
        """
        self.parent = parent
        self.db_manager = db_manager
        self.appointment_service = AppointmentService(db_manager)
        self.recommendation_service = RecommendationService(db_manager)
        self.current_appointment: Optional[Appointment] = None
        
        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title("Panda Spa - Appointment Management")
        self.window.geometry("1200x800")
        
        self._create_widgets()
        self._load_appointments()
        self._load_customers()
        self._load_services()
    
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Appointment Form
        form_frame = ttk.LabelFrame(main_frame, text="Appointment Information", padding="10")
        form_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Form fields
        ttk.Label(form_frame, text="Customer:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.customer_combo = ttk.Combobox(form_frame, width=28, state="readonly")
        self.customer_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.customer_combo.bind('<<ComboboxSelected>>', self._on_customer_select)
        
        ttk.Label(form_frame, text="Service:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.service_combo = ttk.Combobox(form_frame, width=28, state="readonly")
        self.service_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.service_combo.bind('<<ComboboxSelected>>', self._on_service_select)
        
        ttk.Label(form_frame, text="Date:").grid(row=2, column=0, sticky=tk.W, pady=5)
        date_frame = ttk.Frame(form_frame)
        date_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.date_entry = ttk.Entry(date_frame, width=12)
        self.date_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.date_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        ttk.Button(date_frame, text="Today", command=self._set_today).pack(side=tk.LEFT)
        
        ttk.Label(form_frame, text="Time:").grid(row=3, column=0, sticky=tk.W, pady=5)
        time_frame = ttk.Frame(form_frame)
        time_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.hour_spin = ttk.Spinbox(time_frame, from_=9, to=17, width=5, format="%02.0f")
        self.hour_spin.set(10)
        self.hour_spin.pack(side=tk.LEFT, padx=(0, 2))
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        self.minute_spin = ttk.Spinbox(time_frame, from_=0, to=59, width=5, format="%02.0f", increment=30)
        self.minute_spin.set(0)
        self.minute_spin.pack(side=tk.LEFT, padx=(2, 0))
        
        # Recommendations display
        rec_frame = ttk.Frame(form_frame)
        rec_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.recommendations_label = ttk.Label(rec_frame, text="", foreground="blue", font=("Arial", 9))
        self.recommendations_label.pack(side=tk.LEFT)
        
        ttk.Button(rec_frame, text="View Recommendations", command=self._show_recommendations, width=18).pack(side=tk.LEFT, padx=(10, 0))
        
        # Conflict warning
        self.conflict_label = ttk.Label(form_frame, text="", foreground="red")
        self.conflict_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        ttk.Label(form_frame, text="Notes:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.notes_text = tk.Text(form_frame, width=30, height=4)
        self.notes_text.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Status display
        self.status_label = ttk.Label(form_frame, text="Status: -", font=("Arial", 10, "bold"))
        self.status_label.grid(row=7, column=0, columnspan=2, pady=5)
        
        # Form buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Create", command=self._create_appointment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update", command=self._update_appointment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reschedule", command=self._reschedule_appointment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self._clear_form).pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = ttk.Frame(form_frame)
        action_frame.grid(row=9, column=0, columnspan=2, pady=10)
        
        ttk.Button(action_frame, text="Complete", command=self._complete_appointment).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancel", command=self._cancel_appointment).pack(side=tk.LEFT, padx=5)
        
        # Right panel - Appointment List
        list_frame = ttk.LabelFrame(main_frame, text="Appointments", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Filter frame
        filter_frame = ttk.Frame(list_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        
        ttk.Label(filter_frame, text="Status:").grid(row=0, column=0, padx=(0, 5))
        self.status_filter = ttk.Combobox(filter_frame, width=15, state="readonly")
        self.status_filter['values'] = ['All'] + Appointment.get_statuses()
        self.status_filter.set('All')
        self.status_filter.grid(row=0, column=1, padx=(0, 5))
        self.status_filter.bind('<<ComboboxSelected>>', self._on_filter)
        
        ttk.Label(filter_frame, text="Date:").grid(row=0, column=2, padx=(10, 5))
        self.date_filter = ttk.Entry(filter_frame, width=12)
        self.date_filter.insert(0, date.today().strftime('%Y-%m-%d'))
        self.date_filter.grid(row=0, column=3, padx=(0, 5))
        self.date_filter.bind('<KeyRelease>', self._on_filter)
        
        # Appointment list (Treeview)
        columns = ('ID', 'Customer', 'Service', 'Date/Time', 'Status', 'Price', 'Notes')
        self.appointment_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        self.appointment_tree.heading('ID', text='ID')
        self.appointment_tree.heading('Customer', text='Customer')
        self.appointment_tree.heading('Service', text='Service')
        self.appointment_tree.heading('Date/Time', text='Date/Time')
        self.appointment_tree.heading('Status', text='Status')
        self.appointment_tree.heading('Price', text='Price ($)')
        self.appointment_tree.heading('Notes', text='Notes')
        
        self.appointment_tree.column('ID', width=50)
        self.appointment_tree.column('Customer', width=120)
        self.appointment_tree.column('Service', width=120)
        self.appointment_tree.column('Date/Time', width=150)
        self.appointment_tree.column('Status', width=100)
        self.appointment_tree.column('Price', width=80)
        self.appointment_tree.column('Notes', width=200)
        
        self.appointment_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.appointment_tree.bind('<Double-1>', self._on_appointment_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.appointment_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.appointment_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        action_frame2 = ttk.Frame(list_frame)
        action_frame2.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(action_frame2, text="Edit Selected", command=self._edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame2, text="Refresh", command=self._load_appointments).pack(side=tk.LEFT, padx=5)
    
    def _load_customers(self):
        """Load customers into combo box."""
        customers = self.db_manager.get_all(Customer)
        customer_list = [f"{c.id}: {c.name} ({c.species})" for c in customers]
        self.customer_combo['values'] = customer_list
    
    def _load_services(self):
        """Load services into combo box."""
        services = self.db_manager.find(Service, is_available=True)
        service_list = [f"{s.id}: {s.name} (${s.price:.2f})" for s in services]
        self.service_combo['values'] = service_list
    
    def _load_appointments(self):
        """Load appointments into the treeview."""
        # Clear existing items
        for item in self.appointment_tree.get_children():
            self.appointment_tree.delete(item)
        
        # Get all appointments
        appointments = self.db_manager.get_all(Appointment)
        
        # Apply filters
        status_filter = self.status_filter.get()
        date_filter = self.date_filter.get()
        
        for appointment in appointments:
            # Status filter
            if status_filter != 'All' and appointment.status != status_filter:
                continue
            
            # Date filter
            if date_filter:
                try:
                    filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                    if appointment.appointment_datetime.date() != filter_date:
                        continue
                except ValueError:
                    pass  # Invalid date format, show all
            
            # Get customer and service names
            customer = self.db_manager.get_by_id(Customer, appointment.customer_id)
            service = self.db_manager.get_by_id(Service, appointment.service_id)
            
            customer_name = customer.name if customer else f"ID:{appointment.customer_id}"
            service_name = service.name if service else f"ID:{appointment.service_id}"
            
            # Format datetime
            dt_str = appointment.appointment_datetime.strftime('%Y-%m-%d %H:%M')
            
            # Format status
            status_display = appointment.status.replace('_', ' ').title()
            
            self.appointment_tree.insert('', tk.END, values=(
                appointment.id,
                customer_name,
                service_name,
                dt_str,
                status_display,
                f"${appointment.price_paid:.2f}",
                appointment.notes or ''
            ))
    
    def _on_customer_select(self, event=None):
        """Handle customer selection and show recommendations."""
        self._update_recommendations_display()
    
    def _update_recommendations_display(self):
        """Update recommendations display when customer is selected."""
        if not self.customer_combo.get():
            self.recommendations_label.config(text="")
            return
        
        try:
            customer_id = int(self.customer_combo.get().split(':')[0])
            recommendations = self.recommendation_service.get_recommendations(customer_id, limit=3)
            
            if recommendations:
                rec_text = "💡 Recommendations: " + ", ".join([rec[0].name for rec in recommendations[:2]])
                self.recommendations_label.config(text=rec_text)
            else:
                self.recommendations_label.config(text="")
        except (ValueError, IndexError):
            self.recommendations_label.config(text="")
    
    def _show_recommendations(self):
        """Open recommendation window."""
        if not self.customer_combo.get():
            messagebox.showwarning("Warning", "Please select a customer first!")
            return
        
        RecommendationWindow(self.parent, self.db_manager)
    
    def _on_service_select(self, event=None):
        """Handle service selection and check for conflicts."""
        self._check_conflict()
    
    def _set_today(self):
        """Set date to today."""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        self._check_conflict()
    
    def _check_conflict(self):
        """Check for scheduling conflicts."""
        self.conflict_label.config(text="")
        
        if not self.service_combo.get() or not self.date_entry.get():
            return
        
        try:
            service_id = int(self.service_combo.get().split(':')[0])
            service = self.db_manager.get_by_id(Service, service_id)
            if not service:
                return
            
            # Parse date and time
            date_str = self.date_entry.get()
            hour = int(self.hour_spin.get())
            minute = int(self.minute_spin.get())
            
            appointment_time = datetime.strptime(f"{date_str} {hour:02d}:{minute:02d}", '%Y-%m-%d %H:%M')
            
            # Check conflict (only if not editing current appointment)
            if not self.current_appointment or self.current_appointment.service_id != service_id:
                conflict = self.appointment_service.check_conflict(
                    service_id,
                    appointment_time,
                    service.duration_minutes
                )
                if conflict:
                    self.conflict_label.config(text=f"⚠ {conflict}")
        except (ValueError, IndexError):
            pass
    
    def _on_filter(self, event=None):
        """Handle filter changes."""
        self._load_appointments()
    
    def _clear_form(self):
        """Clear all form fields."""
        self.customer_combo.set('')
        self.service_combo.set('')
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        self.hour_spin.set(10)
        self.minute_spin.set(0)
        self.notes_text.delete('1.0', tk.END)
        self.conflict_label.config(text="")
        self.status_label.config(text="Status: -")
        self.current_appointment = None
    
    def _create_appointment(self):
        """Create a new appointment."""
        # Validate inputs
        if not self.customer_combo.get():
            messagebox.showerror("Error", "Please select a customer!")
            return
        
        if not self.service_combo.get():
            messagebox.showerror("Error", "Please select a service!")
            return
        
        try:
            customer_id = int(self.customer_combo.get().split(':')[0])
            service_id = int(self.service_combo.get().split(':')[0])
            
            # Parse date and time
            date_str = self.date_entry.get()
            hour = int(self.hour_spin.get())
            minute = int(self.minute_spin.get())
            
            appointment_time = datetime.strptime(f"{date_str} {hour:02d}:{minute:02d}", '%Y-%m-%d %H:%M')
            
            # Check if time is in the past
            if appointment_time < datetime.now():
                if not messagebox.askyesno("Confirm", "Appointment time is in the past. Create anyway?"):
                    return
            
            notes = self.notes_text.get('1.0', tk.END).strip() or None
            
            # Create appointment
            appointment, error = self.appointment_service.create_appointment(
                customer_id,
                service_id,
                appointment_time,
                notes
            )
            
            if appointment:
                messagebox.showinfo("Success", "Appointment created successfully!")
                self._clear_form()
                self._load_appointments()
            else:
                messagebox.showerror("Error", f"Failed to create appointment: {error}")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def _update_appointment(self):
        """Update appointment notes."""
        if not self.current_appointment:
            messagebox.showwarning("Warning", "Please select an appointment to update!")
            return
        
        notes = self.notes_text.get('1.0', tk.END).strip() or None
        
        success = self.db_manager.update(self.current_appointment, notes=notes)
        
        if success:
            messagebox.showinfo("Success", "Appointment updated successfully!")
            self._load_appointments()
        else:
            messagebox.showerror("Error", "Failed to update appointment!")
    
    def _reschedule_appointment(self):
        """Reschedule the current appointment."""
        if not self.current_appointment:
            messagebox.showwarning("Warning", "Please select an appointment to reschedule!")
            return
        
        try:
            # Parse date and time
            date_str = self.date_entry.get()
            hour = int(self.hour_spin.get())
            minute = int(self.minute_spin.get())
            
            new_time = datetime.strptime(f"{date_str} {hour:02d}:{minute:02d}", '%Y-%m-%d %H:%M')
            
            success, error = self.appointment_service.reschedule_appointment(
                self.current_appointment.id,
                new_time
            )
            
            if success:
                messagebox.showinfo("Success", "Appointment rescheduled successfully!")
                self._clear_form()
                self._load_appointments()
            else:
                messagebox.showerror("Error", f"Failed to reschedule: {error}")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def _complete_appointment(self):
        """Mark appointment as completed."""
        if not self.current_appointment:
            messagebox.showwarning("Warning", "Please select an appointment!")
            return
        
        success, error = self.appointment_service.complete_appointment(self.current_appointment.id)
        
        if success:
            messagebox.showinfo("Success", "Appointment marked as completed!")
            self._clear_form()
            self._load_appointments()
        else:
            messagebox.showerror("Error", f"Failed to complete appointment: {error}")
    
    def _cancel_appointment(self):
        """Cancel the current appointment."""
        if not self.current_appointment:
            messagebox.showwarning("Warning", "Please select an appointment to cancel!")
            return
        
        reason = simpledialog.askstring("Cancellation Reason", "Enter cancellation reason (optional):")
        
        success, error = self.appointment_service.cancel_appointment(
            self.current_appointment.id,
            reason
        )
        
        if success:
            messagebox.showinfo("Success", "Appointment cancelled successfully!")
            self._clear_form()
            self._load_appointments()
        else:
            messagebox.showerror("Error", f"Failed to cancel appointment: {error}")
    
    def _on_appointment_select(self, event):
        """Handle appointment selection from treeview."""
        selection = self.appointment_tree.selection()
        if not selection:
            return
        
        item = self.appointment_tree.item(selection[0])
        appointment_id = item['values'][0]
        
        # Load appointment
        appointment = self.db_manager.get_by_id(Appointment, appointment_id)
        if appointment:
            self.current_appointment = appointment
            self._populate_form(appointment)
    
    def _edit_selected(self):
        """Edit the selected appointment."""
        selection = self.appointment_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment to edit!")
            return
        
        item = self.appointment_tree.item(selection[0])
        appointment_id = item['values'][0]
        
        # Load appointment
        appointment = self.db_manager.get_by_id(Appointment, appointment_id)
        if appointment:
            self.current_appointment = appointment
            self._populate_form(appointment)
    
    def _populate_form(self, appointment: Appointment):
        """Populate form fields with appointment data."""
        # Set customer
        customer = self.db_manager.get_by_id(Customer, appointment.customer_id)
        if customer:
            customer_str = f"{customer.id}: {customer.name} ({customer.species})"
            self.customer_combo.set(customer_str)
        
        # Set service
        service = self.db_manager.get_by_id(Service, appointment.service_id)
        if service:
            service_str = f"{service.id}: {service.name} (${service.price:.2f})"
            self.service_combo.set(service_str)
        
        # Set date and time
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, appointment.appointment_datetime.strftime('%Y-%m-%d'))
        self.hour_spin.set(appointment.appointment_datetime.hour)
        self.minute_spin.set(appointment.appointment_datetime.minute)
        
        # Set notes
        self.notes_text.delete('1.0', tk.END)
        if appointment.notes:
            self.notes_text.insert('1.0', appointment.notes)
        
        # Set status
        status_display = appointment.status.replace('_', ' ').title()
        self.status_label.config(text=f"Status: {status_display}")
        
        # Check conflict
        self._check_conflict()

