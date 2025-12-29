"""
Service Management Window for Panda Spa.
Provides GUI for creating, viewing, editing, and deleting services.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from database.db_manager import DatabaseManagement
from models.service import Service


class ServiceWindow:
    """
    Main window for service management.
    Provides full CRUD operations for services.
    """
    
    def __init__(self, parent: tk.Tk, db_manager: DatabaseManagement):
        """
        Initialize service management window.
        
        Args:
            parent: Parent Tkinter window
            db_manager: DatabaseManagement instance
        """
        self.parent = parent
        self.db_manager = db_manager
        self.current_service: Optional[Service] = None
        
        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title("Panda Spa - Service Management")
        self.window.geometry("1000x700")
        
        self._create_widgets()
        self._load_services()
    
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Configure Treeview style to set row height (prevents overlapping rows)
        style = ttk.Style()
        style.configure("Treeview", rowheight=50)  # Set row height to 50 pixels
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Service Form
        form_frame = ttk.LabelFrame(main_frame, text="Service Information", padding="10")
        form_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Form fields
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(form_frame, text="Service Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.type_combo = ttk.Combobox(form_frame, width=27, state="readonly")
        self.type_combo['values'] = Service.get_service_types()
        self.type_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(form_frame, text="Duration (minutes):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.duration_entry = ttk.Entry(form_frame, width=30)
        self.duration_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(form_frame, text="Price ($):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.price_entry = ttk.Entry(form_frame, width=30)
        self.price_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(form_frame, text="Max Capacity:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.capacity_entry = ttk.Entry(form_frame, width=30)
        self.capacity_entry.insert(0, "1")
        self.capacity_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(form_frame, text="Description:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.description_text = tk.Text(form_frame, width=30, height=5)
        self.description_text.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        self.is_available_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Available", variable=self.is_available_var).grid(
            row=6, column=1, sticky=tk.W, pady=5, padx=(5, 0)
        )
        
        # Form buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Create New", command=self._create_service).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update", command=self._update_service).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self._clear_form).pack(side=tk.LEFT, padx=5)
        
        # Right panel - Service List
        list_frame = ttk.LabelFrame(main_frame, text="Services", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Search/Filter frame
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.search_entry.bind('<KeyRelease>', self._on_search)
        
        ttk.Label(search_frame, text="Type:").grid(row=0, column=2, padx=(10, 5))
        self.type_filter = ttk.Combobox(search_frame, width=15, state="readonly")
        self.type_filter['values'] = ['All'] + Service.get_service_types()
        self.type_filter.set('All')
        self.type_filter.grid(row=0, column=3, padx=(0, 5))
        self.type_filter.bind('<<ComboboxSelected>>', self._on_filter)
        
        # Service list (Treeview)
        columns = ('ID', 'Name', 'Type', 'Duration', 'Price', 'Capacity', 'Available', 'Popularity')
        self.service_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.service_tree.heading('ID', text='ID')
        self.service_tree.heading('Name', text='Name')
        self.service_tree.heading('Type', text='Type')
        self.service_tree.heading('Duration', text='Duration (min)')
        self.service_tree.heading('Price', text='Price ($)')
        self.service_tree.heading('Capacity', text='Capacity')
        self.service_tree.heading('Available', text='Available')
        self.service_tree.heading('Popularity', text='Popularity')
        
        self.service_tree.column('ID', width=50)
        self.service_tree.column('Name', width=150)
        self.service_tree.column('Type', width=100)
        self.service_tree.column('Duration', width=80)
        self.service_tree.column('Price', width=80)
        self.service_tree.column('Capacity', width=70)
        self.service_tree.column('Available', width=70)
        self.service_tree.column('Popularity', width=80)
        
        self.service_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.service_tree.bind('<Double-1>', self._on_service_select)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.service_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.service_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        action_frame = ttk.Frame(list_frame)
        action_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(action_frame, text="Edit Selected", command=self._edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Toggle Availability", command=self._toggle_availability).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete Selected", command=self._delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refresh", command=self._load_services).pack(side=tk.LEFT, padx=5)
    
    def _load_services(self):
        """Load all services into the treeview."""
        # Clear existing items
        for item in self.service_tree.get_children():
            self.service_tree.delete(item)
        
        # Get all services
        services = self.db_manager.get_all(Service)
        
        # Add to treeview
        for service in services:
            # Format service type for display
            type_display = service.service_type.replace('_', ' ').title()
            
            self.service_tree.insert('', tk.END, values=(
                service.id,
                service.name,
                type_display,
                service.duration_minutes,
                f"${service.price:.2f}",
                service.max_capacity,
                'Yes' if service.is_available else 'No',
                f"{service.popularity_score:.1f}"
            ))
    
    def _on_search(self, event=None):
        """Handle search text change."""
        search_text = self.search_entry.get().lower()
        type_filter = self.type_filter.get()
        
        # Clear treeview
        for item in self.service_tree.get_children():
            self.service_tree.delete(item)
        
        # Get services
        if type_filter == 'All':
            services = self.db_manager.get_all(Service)
        else:
            services = self.db_manager.find(Service, service_type=type_filter)
        
        # Filter by search text
        for service in services:
            if search_text in service.name.lower() or \
               (service.description and search_text in service.description.lower()):
                type_display = service.service_type.replace('_', ' ').title()
                self.service_tree.insert('', tk.END, values=(
                    service.id,
                    service.name,
                    type_display,
                    service.duration_minutes,
                    f"${service.price:.2f}",
                    service.max_capacity,
                    'Yes' if service.is_available else 'No',
                    f"{service.popularity_score:.1f}"
                ))
    
    def _on_filter(self, event=None):
        """Handle type filter change."""
        self._on_search()
    
    def _clear_form(self):
        """Clear all form fields."""
        self.name_entry.delete(0, tk.END)
        self.type_combo.set('')
        self.duration_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.capacity_entry.delete(0, tk.END)
        self.capacity_entry.insert(0, "1")
        self.description_text.delete('1.0', tk.END)
        self.is_available_var.set(True)
        self.current_service = None
    
    def _create_service(self):
        """Create a new service."""
        # Validate inputs
        name = self.name_entry.get().strip()
        service_type = self.type_combo.get()
        duration_str = self.duration_entry.get().strip()
        price_str = self.price_entry.get().strip()
        capacity_str = self.capacity_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Name is required!")
            return
        
        if not service_type:
            messagebox.showerror("Error", "Service type is required!")
            return
        
        try:
            duration = int(duration_str)
            if duration <= 0:
                raise ValueError("Duration must be positive")
        except ValueError:
            messagebox.showerror("Error", "Duration must be a positive integer!")
            return
        
        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            messagebox.showerror("Error", "Price must be a positive number!")
            return
        
        try:
            capacity = int(capacity_str) if capacity_str else 1
            if capacity <= 0:
                raise ValueError("Capacity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Max capacity must be a positive integer!")
            return
        
        # Create service
        service = self.db_manager.create(
            Service,
            name=name,
            service_type=service_type,
            duration_minutes=duration,
            price=price,
            max_capacity=capacity,
            description=self.description_text.get('1.0', tk.END).strip() or None,
            is_available=self.is_available_var.get()
        )
        
        if service:
            messagebox.showinfo("Success", f"Service '{name}' created successfully!")
            self._clear_form()
            self._load_services()
        else:
            messagebox.showerror("Error", "Failed to create service!")
    
    def _update_service(self):
        """Update the current service."""
        if not self.current_service:
            messagebox.showwarning("Warning", "Please select a service to update!")
            return
        
        # Validate inputs (same as create)
        name = self.name_entry.get().strip()
        service_type = self.type_combo.get()
        duration_str = self.duration_entry.get().strip()
        price_str = self.price_entry.get().strip()
        capacity_str = self.capacity_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Name is required!")
            return
        
        if not service_type:
            messagebox.showerror("Error", "Service type is required!")
            return
        
        try:
            duration = int(duration_str)
            if duration <= 0:
                raise ValueError("Duration must be positive")
        except ValueError:
            messagebox.showerror("Error", "Duration must be a positive integer!")
            return
        
        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            messagebox.showerror("Error", "Price must be a positive number!")
            return
        
        try:
            capacity = int(capacity_str) if capacity_str else 1
            if capacity <= 0:
                raise ValueError("Capacity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Max capacity must be a positive integer!")
            return
        
        # Update service
        success = self.db_manager.update(
            self.current_service,
            name=name,
            service_type=service_type,
            duration_minutes=duration,
            price=price,
            max_capacity=capacity,
            description=self.description_text.get('1.0', tk.END).strip() or None,
            is_available=self.is_available_var.get()
        )
        
        if success:
            messagebox.showinfo("Success", f"Service '{name}' updated successfully!")
            self._clear_form()
            self._load_services()
        else:
            messagebox.showerror("Error", "Failed to update service!")
    
    def _on_service_select(self, event):
        """Handle service selection from treeview."""
        selection = self.service_tree.selection()
        if not selection:
            return
        
        item = self.service_tree.item(selection[0])
        service_id = item['values'][0]
        
        # Load service
        service = self.db_manager.get_by_id(Service, service_id)
        if service:
            self.current_service = service
            self._populate_form(service)
    
    def _edit_selected(self):
        """Edit the selected service."""
        selection = self.service_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a service to edit!")
            return
        
        item = self.service_tree.item(selection[0])
        service_id = item['values'][0]
        
        # Load service
        service = self.db_manager.get_by_id(Service, service_id)
        if service:
            self.current_service = service
            self._populate_form(service)
    
    def _populate_form(self, service: Service):
        """Populate form fields with service data."""
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, service.name)
        
        self.type_combo.set(service.service_type)
        
        self.duration_entry.delete(0, tk.END)
        self.duration_entry.insert(0, str(service.duration_minutes))
        
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, str(service.price))
        
        self.capacity_entry.delete(0, tk.END)
        self.capacity_entry.insert(0, str(service.max_capacity))
        
        self.description_text.delete('1.0', tk.END)
        if service.description:
            self.description_text.insert('1.0', service.description)
        
        self.is_available_var.set(service.is_available)
    
    def _toggle_availability(self):
        """Toggle availability of selected service."""
        selection = self.service_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a service!")
            return
        
        item = self.service_tree.item(selection[0])
        service_id = item['values'][0]
        service_name = item['values'][1]
        
        # Load service
        service = self.db_manager.get_by_id(Service, service_id)
        if service:
            new_status = not service.is_available
            success = self.db_manager.update(service, is_available=new_status)
            if success:
                status_text = "available" if new_status else "unavailable"
                messagebox.showinfo("Success", f"Service '{service_name}' is now {status_text}!")
                self._load_services()
            else:
                messagebox.showerror("Error", "Failed to update service availability!")
    
    def _delete_selected(self):
        """Delete the selected service."""
        selection = self.service_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a service to delete!")
            return
        
        item = self.service_tree.item(selection[0])
        service_id = item['values'][0]
        service_name = item['values'][1]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete service '{service_name}'?"):
            return
        
        # Load and delete service
        service = self.db_manager.get_by_id(Service, service_id)
        if service:
            success = self.db_manager.delete(service)
            if success:
                messagebox.showinfo("Success", f"Service '{service_name}' deleted successfully!")
                self._clear_form()
                self._load_services()
            else:
                messagebox.showerror("Error", "Failed to delete service!")

