"""
Feeling-Service Mapping Configuration Window.
Allows customization of which services are recommended for each feeling.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from database.db_manager import DatabaseManagement
from models.feeling_service_mapping import FeelingServiceMapping
from models.service import Service
from services.mood_recommendation_service import MoodRecommendationService


class FeelingMappingWindow:
    """
    Window for managing feeling-to-service mappings.
    Allows customization of recommendations.
    """
    
    def __init__(self, parent: tk.Tk, db_manager: DatabaseManagement):
        """
        Initialize feeling mapping window.
        
        Args:
            parent: Parent Tkinter window
            db_manager: DatabaseManagement instance
        """
        self.parent = parent
        self.db_manager = db_manager
        self.mood_service = MoodRecommendationService(db_manager)
        self.current_feeling: Optional[str] = None
        self.current_mapping: Optional[FeelingServiceMapping] = None
        
        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title("Panda Spa - Feeling-Service Mapping Configuration")
        self.window.geometry("1000x700")
        
        self._create_widgets()
        self._load_feelings()
        self._load_services()
    
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Configure Treeview style
        style = ttk.Style()
        style.configure("Treeview", rowheight=40)
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Configuration Form
        form_frame = ttk.LabelFrame(main_frame, text="Configure Feeling-Service Mapping", padding="10")
        form_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Feeling selection
        ttk.Label(form_frame, text="Feeling/Mood:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.feeling_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.feeling_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.feeling_combo.bind('<<ComboboxSelected>>', self._on_feeling_select)
        
        # Service selection
        ttk.Label(form_frame, text="Service to Recommend:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.service_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.service_combo.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Priority
        ttk.Label(form_frame, text="Priority (1 = highest, lower = recommended first):", font=("Arial", 9)).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.priority_entry = ttk.Entry(form_frame, width=30)
        self.priority_entry.insert(0, "1")
        self.priority_entry.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Active checkbox
        self.is_active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Active (include in recommendations)", variable=self.is_active_var).grid(row=6, column=0, sticky=tk.W, pady=(0, 15))
        
        # Action buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, pady=10)
        
        ttk.Button(button_frame, text="Add Mapping", command=self._add_mapping).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Mapping", command=self._update_mapping).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Mapping", command=self._delete_mapping).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self._clear_form).pack(side=tk.LEFT, padx=5)
        
        # Info label
        info_label = ttk.Label(
            form_frame,
            text="💡 Tip: Lower priority numbers are recommended first.\nMultiple services can be mapped to the same feeling.",
            font=("Arial", 8),
            foreground="gray",
            justify=tk.LEFT
        )
        info_label.grid(row=8, column=0, pady=10, sticky=tk.W)
        
        # Right panel - Mappings List
        list_frame = ttk.LabelFrame(main_frame, text="Current Mappings", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Filter by feeling
        filter_frame = ttk.Frame(list_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by Feeling:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_combo = ttk.Combobox(filter_frame, width=20, state="readonly")
        self.filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.filter_combo.bind('<<ComboboxSelected>>', self._filter_mappings)
        
        ttk.Button(filter_frame, text="Show All", command=self._load_mappings).pack(side=tk.LEFT, padx=5)
        
        # Treeview container
        tree_frame = ttk.Frame(list_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Mappings list
        columns = ('Feeling', 'Service', 'Priority', 'Active')
        self.mappings_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        self.mappings_tree.heading('Feeling', text='Feeling')
        self.mappings_tree.heading('Service', text='Service Name')
        self.mappings_tree.heading('Priority', text='Priority')
        self.mappings_tree.heading('Active', text='Active')
        
        self.mappings_tree.column('Feeling', width=120, anchor=tk.CENTER)
        self.mappings_tree.column('Service', width=250, anchor=tk.W)
        self.mappings_tree.column('Priority', width=80, anchor=tk.CENTER)
        self.mappings_tree.column('Active', width=80, anchor=tk.CENTER)
        
        self.mappings_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.mappings_tree.bind('<Double-1>', self._on_mapping_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.mappings_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.mappings_tree.configure(yscrollcommand=scrollbar.set)
        
        # Status label
        self.status_label = ttk.Label(list_frame, text="", font=("Arial", 9), foreground="green")
        self.status_label.grid(row=2, column=0, pady=5)
    
    def _load_feelings(self):
        """Load available feelings into combo boxes."""
        feelings = self.mood_service.get_available_feelings()
        self.feeling_combo['values'] = feelings
        self.filter_combo['values'] = ['All'] + feelings
    
    def _load_services(self):
        """Load available services into combo box."""
        services = self.db_manager.find(Service, is_available=True)
        service_list = [f"{s.id}: {s.name} (${s.price:.2f})" for s in services]
        self.service_combo['values'] = service_list
    
    def _load_mappings(self):
        """Load all mappings into treeview."""
        for item in self.mappings_tree.get_children():
            self.mappings_tree.delete(item)
        
        mappings = self.db_manager.get_all(FeelingServiceMapping)
        mappings.sort(key=lambda m: (m.feeling, m.priority))
        
        for mapping in mappings:
            service = self.db_manager.get_by_id(Service, mapping.service_id)
            service_name = service.name if service else f"ID:{mapping.service_id}"
            
            active_text = "Yes" if mapping.is_active else "No"
            tag = "active" if mapping.is_active else "inactive"
            
            self.mappings_tree.insert('', tk.END, values=(
                mapping.feeling,
                service_name,
                mapping.priority,
                active_text
            ), tags=(tag,))
        
        # Configure tags
        self.mappings_tree.tag_configure('active', foreground='green')
        self.mappings_tree.tag_configure('inactive', foreground='gray')
        
        self.status_label.config(text=f"Total mappings: {len(mappings)}")
    
    def _filter_mappings(self, event=None):
        """Filter mappings by feeling."""
        feeling = self.filter_combo.get()
        if feeling == 'All' or not feeling:
            self._load_mappings()
            return
        
        for item in self.mappings_tree.get_children():
            self.mappings_tree.delete(item)
        
        mappings = self.db_manager.find(FeelingServiceMapping, feeling=feeling)
        mappings.sort(key=lambda m: m.priority)
        
        for mapping in mappings:
            service = self.db_manager.get_by_id(Service, mapping.service_id)
            service_name = service.name if service else f"ID:{mapping.service_id}"
            
            active_text = "Yes" if mapping.is_active else "No"
            tag = "active" if mapping.is_active else "inactive"
            
            self.mappings_tree.insert('', tk.END, values=(
                mapping.feeling,
                service_name,
                mapping.priority,
                active_text
            ), tags=(tag,))
        
        self.status_label.config(text=f"Mappings for '{feeling}': {len(mappings)}")
    
    def _on_feeling_select(self, event=None):
        """Handle feeling selection."""
        self.current_feeling = self.feeling_combo.get()
        # Could load existing mappings for this feeling here
    
    def _on_mapping_select(self, event):
        """Handle mapping selection from list."""
        selection = self.mappings_tree.selection()
        if not selection:
            return
        
        item = self.mappings_tree.item(selection[0])
        feeling = item['values'][0]
        service_name = item['values'][1]
        
        # Find the mapping
        mappings = self.db_manager.find(FeelingServiceMapping, feeling=feeling)
        for mapping in mappings:
            service = self.db_manager.get_by_id(Service, mapping.service_id)
            if service and service.name == service_name:
                self.current_mapping = mapping
                self._load_mapping_to_form()
                break
    
    def _load_mapping_to_form(self):
        """Load selected mapping into form."""
        if not self.current_mapping:
            return
        
        self.feeling_combo.set(self.current_mapping.feeling)
        service = self.db_manager.get_by_id(Service, self.current_mapping.service_id)
        if service:
            service_str = f"{service.id}: {service.name} (${service.price:.2f})"
            self.service_combo.set(service_str)
        
        self.priority_entry.delete(0, tk.END)
        self.priority_entry.insert(0, str(self.current_mapping.priority))
        
        self.is_active_var.set(self.current_mapping.is_active)
    
    def _add_mapping(self):
        """Add a new feeling-service mapping."""
        try:
            feeling = self.feeling_combo.get()
            if not feeling:
                messagebox.showerror("Error", "Please select a feeling!")
                return
            
            if not self.service_combo.get():
                messagebox.showerror("Error", "Please select a service!")
                return
            
            service_id = int(self.service_combo.get().split(':')[0])
            priority = int(self.priority_entry.get())
            is_active = self.is_active_var.get()
            
            # Check if mapping already exists
            existing = self.db_manager.find_one(
                FeelingServiceMapping,
                feeling=feeling,
                service_id=service_id
            )
            
            if existing:
                messagebox.showwarning("Warning", "This mapping already exists! Use 'Update Mapping' to modify it.")
                return
            
            # Create new mapping
            mapping = FeelingServiceMapping(
                feeling=feeling,
                service_id=service_id,
                priority=priority,
                is_active=is_active
            )
            
            success = self.db_manager.save(mapping)
            if success:
                messagebox.showinfo("Success", f"Mapping added: {feeling} → Service")
                self._clear_form()
                self._load_mappings()
            else:
                messagebox.showerror("Error", "Failed to save mapping")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid priority value! Please enter a number.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add mapping: {e}")
    
    def _update_mapping(self):
        """Update existing mapping."""
        if not self.current_mapping:
            messagebox.showwarning("Warning", "Please select a mapping to update!")
            return
        
        try:
            feeling = self.feeling_combo.get()
            if not feeling:
                messagebox.showerror("Error", "Please select a feeling!")
                return
            
            if not self.service_combo.get():
                messagebox.showerror("Error", "Please select a service!")
                return
            
            service_id = int(self.service_combo.get().split(':')[0])
            priority = int(self.priority_entry.get())
            is_active = self.is_active_var.get()
            
            # Update mapping
            self.current_mapping.feeling = feeling
            self.current_mapping.service_id = service_id
            self.current_mapping.priority = priority
            self.current_mapping.is_active = is_active
            
            success = self.db_manager.save(self.current_mapping)
            if success:
                messagebox.showinfo("Success", "Mapping updated successfully!")
                self._clear_form()
                self._load_mappings()
            else:
                messagebox.showerror("Error", "Failed to update mapping")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid priority value! Please enter a number.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update mapping: {e}")
    
    def _delete_mapping(self):
        """Delete selected mapping."""
        if not self.current_mapping:
            messagebox.showwarning("Warning", "Please select a mapping to delete!")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this mapping?"):
            return
        
        try:
            self.db_manager.delete(self.current_mapping)
            messagebox.showinfo("Success", "Mapping deleted successfully!")
            self._clear_form()
            self._load_mappings()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete mapping: {e}")
    
    def _clear_form(self):
        """Clear the form."""
        self.feeling_combo.set('')
        self.service_combo.set('')
        self.priority_entry.delete(0, tk.END)
        self.priority_entry.insert(0, "1")
        self.is_active_var.set(True)
        self.current_mapping = None
        self.current_feeling = None


