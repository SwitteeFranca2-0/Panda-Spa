"""
Appointment Management Window for Panda Spa.
Provides GUI for creating, viewing, editing, and managing appointments with mood-based recommendations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from typing import Optional, List
from database.db_manager import DatabaseManagement
from models.appointment import Appointment
from models.customer import Customer
from models.service import Service
from models.extra import Extra
from services.appointment_service import AppointmentService
from services.mood_recommendation_service import MoodRecommendationService
from services.recommendation_service import RecommendationService


class AppointmentWindow:
    """
    Main window for appointment management.
    Provides full CRUD operations with mood-based recommendations.
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
        self.mood_service = MoodRecommendationService(db_manager)
        self.recommendation_service = RecommendationService(db_manager)
        self.current_appointment: Optional[Appointment] = None
        self.selected_extras: List[Extra] = []
        
        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title("Panda Spa - Appointment Management")
        self.window.geometry("1200x800")
        
        self._create_widgets()
        self._load_appointments()
    
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Configure Treeview style
        style = ttk.Style()
        style.configure("Treeview", rowheight=50)
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Appointment Form with Mood Recommendations
        form_frame = ttk.LabelFrame(main_frame, text="Create/Edit Appointment", padding="10")
        form_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Mood/Feeling Selection
        mood_frame = ttk.LabelFrame(form_frame, text="How are you feeling today?", padding="10")
        mood_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(mood_frame, text="Feeling:").pack(side=tk.LEFT, padx=(0, 10))
        self.feeling_combo = ttk.Combobox(mood_frame, width=25, state="readonly")
        self.feeling_combo['values'] = self.mood_service.get_available_feelings()
        self.feeling_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.feeling_combo.bind('<<ComboboxSelected>>', self._on_feeling_select)
        
        ttk.Button(mood_frame, text="Get Recommendations", command=self._load_mood_recommendations).pack(side=tk.LEFT)
        
        # Mood-based recommendations display
        rec_frame = ttk.Frame(form_frame)
        rec_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.recommendations_label = ttk.Label(rec_frame, text="", foreground="blue", font=("Arial", 9), wraplength=300)
        self.recommendations_label.pack(side=tk.LEFT)
        
        # Recommended services (will be populated when feeling is selected)
        self.rec_services_frame = ttk.LabelFrame(form_frame, text="Recommended Services", padding="5")
        self.rec_services_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Form fields
        ttk.Label(form_frame, text="Customer:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.customer_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.customer_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.customer_combo.bind('<<ComboboxSelected>>', self._on_customer_select)
        
        ttk.Label(form_frame, text="Service:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.service_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.service_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.service_combo.bind('<<ComboboxSelected>>', self._on_service_select)
        
        ttk.Label(form_frame, text="Date:").grid(row=5, column=0, sticky=tk.W, pady=5)
        date_frame = ttk.Frame(form_frame)
        date_frame.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        self.date_entry = ttk.Entry(date_frame, width=12)
        self.date_entry.pack(side=tk.LEFT)
        self.date_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        
        ttk.Label(form_frame, text="Time (HH:MM):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.time_entry = ttk.Entry(form_frame, width=30)
        self.time_entry.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.time_entry.insert(0, "10:00")
        
        # Extras selection
        extras_frame = ttk.LabelFrame(form_frame, text="Add Extras (Optional)", padding="5")
        extras_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.extras_listbox = tk.Listbox(extras_frame, height=4, selectmode=tk.MULTIPLE)
        self.extras_listbox.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Notes:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.notes_text = tk.Text(form_frame, width=25, height=4)
        self.notes_text.grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Conflict warning
        self.conflict_label = ttk.Label(form_frame, text="", foreground="red", font=("Arial", 9))
        self.conflict_label.grid(row=9, column=0, columnspan=2, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Create Appointment", command=self._create_appointment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Appointment", command=self._update_appointment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self._clear_form).pack(side=tk.LEFT, padx=5)
        
        # Right panel - Appointments List
        list_frame = ttk.LabelFrame(main_frame, text="Appointments", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Filters
        filter_frame = ttk.Frame(list_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(filter_frame, text="Today", command=lambda: self._filter_appointments("today")).pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_frame, text="This Week", command=lambda: self._filter_appointments("week")).pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_frame, text="All", command=lambda: self._filter_appointments("all")).pack(side=tk.LEFT, padx=2)
        
        # Treeview container
        tree_frame = ttk.Frame(list_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Appointments list
        columns = ('ID', 'Date', 'Time', 'Customer', 'Service', 'Status', 'Feeling')
        self.appointments_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.appointments_tree.heading(col, text=col)
            self.appointments_tree.column(col, width=100, anchor=tk.CENTER)
        
        self.appointments_tree.column('ID', width=50)
        self.appointments_tree.column('Date', width=100)
        self.appointments_tree.column('Time', width=80)
        self.appointments_tree.column('Customer', width=120)
        self.appointments_tree.column('Service', width=150)
        self.appointments_tree.column('Status', width=100)
        self.appointments_tree.column('Feeling', width=100)
        
        self.appointments_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.appointments_tree.bind('<Double-1>', self._on_appointment_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.appointments_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.appointments_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons for list
        action_frame = ttk.Frame(list_frame)
        action_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(action_frame, text="Complete Appointment", command=self._complete_appointment).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancel Appointment", command=self._cancel_appointment).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete Appointment", command=self._delete_appointment).pack(side=tk.LEFT, padx=5)
        
        # Load data
        self._load_customers()
        self._load_services()
        self._load_extras()
    
    def _load_customers(self):
        """Load customers into combo box."""
        customers = self.db_manager.get_all(Customer)
        customer_list = [f"{c.id}: {c.name} ({c.species})" for c in customers]
        self.customer_combo['values'] = customer_list
    
    def _load_services(self):
        """Load available services into combo box."""
        services = self.db_manager.find(Service, is_available=True)
        service_list = [f"{s.id}: {s.name} (${s.price:.2f})" for s in services]
        self.service_combo['values'] = service_list
    
    def _load_extras(self):
        """Load available extras into listbox."""
        self.extras_listbox.delete(0, tk.END)
        extras = self.db_manager.find(Extra, is_available=True)
        for extra in extras:
            self.extras_listbox.insert(tk.END, f"{extra.name} (+${extra.price:.2f})")
    
    def _on_feeling_select(self, event=None):
        """Handle feeling selection and load recommendations."""
        self._load_mood_recommendations()
    
    def _load_mood_recommendations(self):
        """Load mood-based recommendations."""
        feeling = self.feeling_combo.get()
        if not feeling:
            return
        
        # Clear previous recommendations
        for widget in self.rec_services_frame.winfo_children():
            widget.destroy()
        
        # Get recommendations
        recs = self.mood_service.get_recommendations_by_feeling(feeling)
        
        if recs['services']:
            self.recommendations_label.config(text=recs['message'], foreground="blue")
            
            # Display recommended services as buttons
            for service in recs['services']:
                btn_frame = ttk.Frame(self.rec_services_frame)
                btn_frame.pack(fill=tk.X, pady=2)
                
                btn_text = f"{service.name} (${service.price:.2f})"
                btn = ttk.Button(btn_frame, text=btn_text, 
                               command=lambda s=service: self._select_recommended_service(s))
                btn.pack(side=tk.LEFT, padx=5)
                
                # Show recommended extras for this service
                if service.id in recs['extras_by_service']:
                    extras = recs['extras_by_service'][service.id]
                    extras_text = ", ".join([e.name for e in extras[:2]])
                    ttk.Label(btn_frame, text=f"Extras: {extras_text}", font=("Arial", 8), foreground="gray").pack(side=tk.LEFT)
        else:
            self.recommendations_label.config(text="No recommendations available. Please ensure services are available.", foreground="gray")
    
    def _select_recommended_service(self, service: Service):
        """Select a recommended service."""
        service_str = f"{service.id}: {service.name} (${service.price:.2f})"
        self.service_combo.set(service_str)
        self._on_service_select()
        
        # Load recommended extras for this service
        feeling = self.feeling_combo.get()
        if feeling:
            extras = self.mood_service.get_extras_for_service_and_feeling(service.id, feeling)
            if extras:
                # Select recommended extras in listbox
                all_extras = self.db_manager.find(Extra, is_available=True)
                for i, extra in enumerate(all_extras):
                    if extra in extras:
                        self.extras_listbox.selection_set(i)
    
    def _on_customer_select(self, event=None):
        """Handle customer selection and show recommendations."""
        self._update_recommendations_display()
    
    def _update_recommendations_display(self):
        """Update recommendations display when customer is selected."""
        if not self.customer_combo.get():
            return
        
        try:
            customer_id = int(self.customer_combo.get().split(':')[0])
            recommendations = self.recommendation_service.get_recommendations(customer_id, limit=3)
            
            if recommendations:
                rec_names = []
                for rec in recommendations[:2]:
                    service_name = rec[0].name
                    score = rec[1]
                    if score > 0:
                        rec_names.append(f"{service_name} ({score:.1f}/10)")
                    else:
                        rec_names.append(service_name)
                rec_text = "💡 Recommendations: " + ", ".join(rec_names)
                self.recommendations_label.config(text=rec_text, foreground="blue")
        except (ValueError, IndexError):
            pass
    
    def _on_service_select(self, event=None):
        """Handle service selection and update extras."""
        # Update extras list based on service compatibility
        if not self.service_combo.get():
            return
        
        try:
            service_id = int(self.service_combo.get().split(':')[0])
            service = self.db_manager.get_by_id(Service, service_id)
            if service:
                # Filter extras by compatibility
                self._load_extras()  # Reload all extras
                # Could add filtering logic here if needed
        except (ValueError, IndexError):
            pass
    
    def _load_appointments(self):
        """Load appointments into treeview."""
        for item in self.appointments_tree.get_children():
            self.appointments_tree.delete(item)
        
        appointments = self.db_manager.get_all(Appointment)
        appointments.sort(key=lambda x: x.appointment_datetime, reverse=True)
        
        for appointment in appointments:
            customer = self.db_manager.get_by_id(Customer, appointment.customer_id)
            service = self.db_manager.get_by_id(Service, appointment.service_id)
            
            customer_name = customer.name if customer else f"ID:{appointment.customer_id}"
            service_name = service.name if service else f"ID:{appointment.service_id}"
            date_str = appointment.appointment_datetime.strftime('%Y-%m-%d')
            time_str = appointment.appointment_datetime.strftime('%H:%M')
            status_display = appointment.status.replace('_', ' ').title()
            feeling = appointment.customer_feeling or "N/A"
            
            tag = appointment.status
            self.appointments_tree.insert('', tk.END, values=(
                appointment.id,
                date_str,
                time_str,
                customer_name,
                service_name,
                status_display,
                feeling
            ), tags=(tag,))
        
        # Configure tags
        self.appointments_tree.tag_configure('scheduled', foreground='blue')
        self.appointments_tree.tag_configure('completed', foreground='green')
        self.appointments_tree.tag_configure('cancelled', foreground='red')
        self.appointments_tree.tag_configure('no_show', foreground='orange')
    
    def _filter_appointments(self, filter_type: str):
        """Filter appointments by date range."""
        self._load_appointments()  # Reload all for now
        # Could add date filtering logic here
    
    def _on_appointment_select(self, event):
        """Handle appointment selection from list."""
        selection = self.appointments_tree.selection()
        if not selection:
            return
        
        item = self.appointments_tree.item(selection[0])
        appointment_id = int(item['values'][0])
        self.current_appointment = self.db_manager.get_by_id(Appointment, appointment_id)
        
        if self.current_appointment:
            self._load_appointment_to_form()
    
    def _load_appointment_to_form(self):
        """Load selected appointment into form."""
        if not self.current_appointment:
            return
        
        # Load customer
        customer = self.db_manager.get_by_id(Customer, self.current_appointment.customer_id)
        if customer:
            customer_str = f"{customer.id}: {customer.name} ({customer.species})"
            self.customer_combo.set(customer_str)
        
        # Load service
        service = self.db_manager.get_by_id(Service, self.current_appointment.service_id)
        if service:
            service_str = f"{service.id}: {service.name} (${service.price:.2f})"
            self.service_combo.set(service_str)
        
        # Load date and time
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, self.current_appointment.appointment_datetime.strftime('%Y-%m-%d'))
        
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, self.current_appointment.appointment_datetime.strftime('%H:%M'))
        
        # Load feeling
        if self.current_appointment.customer_feeling:
            self.feeling_combo.set(self.current_appointment.customer_feeling)
        
        # Load notes
        self.notes_text.delete('1.0', tk.END)
        if self.current_appointment.notes:
            self.notes_text.insert('1.0', self.current_appointment.notes)
    
    def _create_appointment(self):
        """Create a new appointment."""
        try:
            # Get customer
            if not self.customer_combo.get():
                messagebox.showerror("Error", "Please select a customer!")
                return
            
            customer_id = int(self.customer_combo.get().split(':')[0])
            
            # Get service
            if not self.service_combo.get():
                messagebox.showerror("Error", "Please select a service!")
                return
            
            service_id = int(self.service_combo.get().split(':')[0])
            
            # Get date and time
            date_str = self.date_entry.get()
            time_str = self.time_entry.get()
            appointment_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            # Get feeling
            feeling = self.feeling_combo.get() or None
            
            # Get notes
            notes = self.notes_text.get('1.0', tk.END).strip()
            
            # Create appointment
            appointment, error = self.appointment_service.create_appointment(
                customer_id, service_id, appointment_datetime, notes, feeling
            )
            
            if error:
                messagebox.showerror("Error", error)
                return
            
            # Add extras
            selected_indices = self.extras_listbox.curselection()
            if selected_indices:
                all_extras = self.db_manager.find(Extra, is_available=True)
                for idx in selected_indices:
                    extra = all_extras[idx]
                    appointment.extras.append(extra)
                    appointment.price_paid += extra.price
                    appointment.duration_minutes += extra.duration_minutes
                self.db_manager.save(appointment)
            
            messagebox.showinfo("Success", "Appointment created successfully!")
            self._clear_form()
            self._load_appointments()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create appointment: {e}")
    
    def _update_appointment(self):
        """Update existing appointment."""
        if not self.current_appointment:
            messagebox.showwarning("Warning", "Please select an appointment to update!")
            return
        
        # Similar to create, but update existing appointment
        messagebox.showinfo("Info", "Update functionality - to be implemented")
    
    def _complete_appointment(self):
        """Mark selected appointment as completed."""
        selection = self.appointments_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment!")
            return
        
        item = self.appointments_tree.item(selection[0])
        appointment_id = int(item['values'][0])
        
        success, error = self.appointment_service.complete_appointment(appointment_id)
        if success:
            messagebox.showinfo("Success", "Appointment marked as completed!")
            self._load_appointments()
        else:
            messagebox.showerror("Error", error)
    
    def _cancel_appointment(self):
        """Cancel selected appointment."""
        selection = self.appointments_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment!")
            return
        
        item = self.appointments_tree.item(selection[0])
        appointment_id = int(item['values'][0])
        
        from tkinter import simpledialog
        reason = simpledialog.askstring("Cancel Appointment", "Reason for cancellation:")
        if reason:
            success, error = self.appointment_service.cancel_appointment(appointment_id, reason)
            if success:
                messagebox.showinfo("Success", "Appointment cancelled!")
                self._load_appointments()
            else:
                messagebox.showerror("Error", error)
    
    def _delete_appointment(self):
        """Delete selected appointment."""
        selection = self.appointments_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment!")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this appointment?"):
            return
        
        item = self.appointments_tree.item(selection[0])
        appointment_id = int(item['values'][0])
        
        appointment = self.db_manager.get_by_id(Appointment, appointment_id)
        if appointment:
            self.db_manager.delete(appointment)
            messagebox.showinfo("Success", "Appointment deleted!")
            self._load_appointments()
    
    def _clear_form(self):
        """Clear the appointment form."""
        self.customer_combo.set('')
        self.service_combo.set('')
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, "10:00")
        self.feeling_combo.set('')
        self.notes_text.delete('1.0', tk.END)
        self.extras_listbox.selection_clear(0, tk.END)
        self.current_appointment = None
        self.conflict_label.config(text="")
        
        # Clear recommendations
        for widget in self.rec_services_frame.winfo_children():
            widget.destroy()
        self.recommendations_label.config(text="")

