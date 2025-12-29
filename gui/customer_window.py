"""
Customer Management Window for Panda Spa.
Provides GUI for creating, viewing, editing, and deleting customers.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from database.db_manager import DatabaseManagement
from models.customer import Customer


class CustomerWindow:
    """
    Main window for customer management.
    Provides full CRUD operations for customers.
    """
    
    def __init__(self, parent: tk.Tk, db_manager: DatabaseManagement):
        """
        Initialize customer management window.
        
        Args:
            parent: Parent Tkinter window
            db_manager: DatabaseManagement instance
        """
        self.parent = parent
        self.db_manager = db_manager
        self.current_customer: Optional[Customer] = None
        
        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title("Panda Spa - Customer Management")
        self.window.geometry("900x700")
        
        self._create_widgets()
        self._load_customers()
    
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Configure Treeview style to set row height (prevents overlapping rows)
        style = ttk.Style()
        style.configure("Treeview", rowheight=50)  # Set row height to 30 pixels
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Customer Form
        form_frame = ttk.LabelFrame(main_frame, text="Customer Information", padding="10")
        form_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Form fields
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=25)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(form_frame, text="Species:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.species_entry = ttk.Entry(form_frame, width=25)
        self.species_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(form_frame, text="Contact Info:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.contact_entry = ttk.Entry(form_frame, width=25)
        self.contact_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(form_frame, text="Notes:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.notes_text = tk.Text(form_frame, width=25, height=5)
        self.notes_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        self.is_active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Active", variable=self.is_active_var).grid(
            row=4, column=1, sticky=tk.W, pady=5, padx=(5, 0)
        )
        
        # Form buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Create New", command=self._create_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update", command=self._update_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self._clear_form).pack(side=tk.LEFT, padx=5)
        
        # Right panel - Customer List
        list_frame = ttk.LabelFrame(main_frame, text="Customers", padding="10")
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
        
        ttk.Label(search_frame, text="Species:").grid(row=0, column=2, padx=(10, 5))
        self.species_filter = ttk.Combobox(search_frame, width=15, state="readonly")
        self.species_filter['values'] = ['All', 'Bear', 'Fox', 'Deer', 'Rabbit', 'Other']
        self.species_filter.set('All')
        self.species_filter.grid(row=0, column=3, padx=(0, 5))
        self.species_filter.bind('<<ComboboxSelected>>', self._on_filter)
        
        # Treeview container frame
        tree_frame = ttk.Frame(list_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Customer list (Treeview)
        columns = ('ID', 'Name', 'Species', 'Contact', 'Visits', 'Spent', 'Active')
        self.customer_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns with proper spacing
        self.customer_tree.heading('ID', text='ID')
        self.customer_tree.heading('Name', text='Name')
        self.customer_tree.heading('Species', text='Species')
        self.customer_tree.heading('Contact', text='Contact')
        self.customer_tree.heading('Visits', text='Visits')
        self.customer_tree.heading('Spent', text='Spent')
        self.customer_tree.heading('Active', text='Active')
        
        self.customer_tree.column('ID', width=50, anchor=tk.CENTER, minwidth=50)
        self.customer_tree.column('Name', width=120, anchor=tk.W, minwidth=100)
        self.customer_tree.column('Species', width=80, anchor=tk.W, minwidth=70)
        self.customer_tree.column('Contact', width=150, anchor=tk.W, minwidth=120)
        self.customer_tree.column('Visits', width=60, anchor=tk.CENTER, minwidth=50)
        self.customer_tree.column('Spent', width=80, anchor=tk.E, minwidth=70)
        self.customer_tree.column('Active', width=60, anchor=tk.CENTER, minwidth=50)
        self.customer_tree.column('#0', width=0, stretch=tk.NO)  # Hide the tree column
        
        self.customer_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.customer_tree.bind('<Double-1>', self._on_customer_select)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.customer_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.customer_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        action_frame = ttk.Frame(list_frame)
        action_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(action_frame, text="Edit Selected", command=self._edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete Selected", command=self._delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refresh", command=self._load_customers).pack(side=tk.LEFT, padx=5)
    
    def _load_customers(self):
        """Load all customers into the treeview."""
        # Clear existing items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        # Get all customers
        customers = self.db_manager.get_all(Customer)
        
        # Add to treeview
        for customer in customers:
            self.customer_tree.insert('', tk.END, values=(
                customer.id,
                customer.name,
                customer.species,
                customer.contact_info or '',
                customer.total_visits,
                f"${customer.total_spent:.2f}",
                'Yes' if customer.is_active else 'No'
            ))
    
    def _on_search(self, event=None):
        """Handle search text change."""
        search_text = self.search_entry.get().lower()
        species_filter = self.species_filter.get()
        
        # Clear treeview
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        # Get all customers
        if species_filter == 'All':
            customers = self.db_manager.get_all(Customer)
        else:
            customers = self.db_manager.find(Customer, species=species_filter)
        
        # Filter by search text
        for customer in customers:
            if search_text in customer.name.lower() or \
               (customer.contact_info and search_text in customer.contact_info.lower()):
                self.customer_tree.insert('', tk.END, values=(
                    customer.id,
                    customer.name,
                    customer.species,
                    customer.contact_info or '',
                    customer.total_visits,
                    f"${customer.total_spent:.2f}",
                    'Yes' if customer.is_active else 'No'
                ))
    
    def _on_filter(self, event=None):
        """Handle species filter change."""
        self._on_search()
    
    def _clear_form(self):
        """Clear all form fields."""
        self.name_entry.delete(0, tk.END)
        self.species_entry.delete(0, tk.END)
        self.contact_entry.delete(0, tk.END)
        self.notes_text.delete('1.0', tk.END)
        self.is_active_var.set(True)
        self.current_customer = None
    
    def _create_customer(self):
        """Create a new customer."""
        # Validate inputs
        name = self.name_entry.get().strip()
        species = self.species_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Name is required!")
            return
        
        if not species:
            messagebox.showerror("Error", "Species is required!")
            return
        
        # Create customer
        customer = self.db_manager.create(
            Customer,
            name=name,
            species=species,
            contact_info=self.contact_entry.get().strip() or None,
            notes=self.notes_text.get('1.0', tk.END).strip() or None,
            is_active=self.is_active_var.get()
        )
        
        if customer:
            messagebox.showinfo("Success", f"Customer '{name}' created successfully!")
            self._clear_form()
            self._load_customers()
        else:
            messagebox.showerror("Error", "Failed to create customer!")
    
    def _update_customer(self):
        """Update the current customer."""
        if not self.current_customer:
            messagebox.showwarning("Warning", "Please select a customer to update!")
            return
        
        # Validate inputs
        name = self.name_entry.get().strip()
        species = self.species_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Name is required!")
            return
        
        if not species:
            messagebox.showerror("Error", "Species is required!")
            return
        
        # Update customer
        success = self.db_manager.update(
            self.current_customer,
            name=name,
            species=species,
            contact_info=self.contact_entry.get().strip() or None,
            notes=self.notes_text.get('1.0', tk.END).strip() or None,
            is_active=self.is_active_var.get()
        )
        
        if success:
            messagebox.showinfo("Success", f"Customer '{name}' updated successfully!")
            self._clear_form()
            self._load_customers()
        else:
            messagebox.showerror("Error", "Failed to update customer!")
    
    def _on_customer_select(self, event):
        """Handle customer selection from treeview."""
        selection = self.customer_tree.selection()
        if not selection:
            return
        
        item = self.customer_tree.item(selection[0])
        customer_id = item['values'][0]
        
        # Load customer
        customer = self.db_manager.get_by_id(Customer, customer_id)
        if customer:
            self.current_customer = customer
            self._populate_form(customer)
    
    def _edit_selected(self):
        """Edit the selected customer."""
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to edit!")
            return
        
        item = self.customer_tree.item(selection[0])
        customer_id = item['values'][0]
        
        # Load customer
        customer = self.db_manager.get_by_id(Customer, customer_id)
        if customer:
            self.current_customer = customer
            self._populate_form(customer)
    
    def _populate_form(self, customer: Customer):
        """Populate form fields with customer data."""
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, customer.name)
        
        self.species_entry.delete(0, tk.END)
        self.species_entry.insert(0, customer.species)
        
        self.contact_entry.delete(0, tk.END)
        if customer.contact_info:
            self.contact_entry.insert(0, customer.contact_info)
        
        self.notes_text.delete('1.0', tk.END)
        if customer.notes:
            self.notes_text.insert('1.0', customer.notes)
        
        self.is_active_var.set(customer.is_active)
    
    def _delete_selected(self):
        """Delete the selected customer."""
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to delete!")
            return
        
        item = self.customer_tree.item(selection[0])
        customer_id = item['values'][0]
        customer_name = item['values'][1]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete customer '{customer_name}'?"):
            return
        
        # Load and delete customer
        customer = self.db_manager.get_by_id(Customer, customer_id)
        if customer:
            success = self.db_manager.delete(customer)
            if success:
                messagebox.showinfo("Success", f"Customer '{customer_name}' deleted successfully!")
                self._clear_form()
                self._load_customers()
            else:
                messagebox.showerror("Error", "Failed to delete customer!")

