import tkinter as tk
from tkinter import ttk, messagebox


class StaffView:
    """View layer for Staff Management GUI"""
    
    @staticmethod
    def validate_phone_number(sdt):
        """Validate phone number format"""
        if not sdt:
            return True, ""
        if not sdt.isdigit():
            return False, "Số điện thoại chỉ được chứa số"
        if len(sdt) < 10 or len(sdt) > 11:
            return False, "Số điện thoại phải có 10-11 số"
        return True, ""
    
    @staticmethod
    def validate_date_format(date_str):
        """Validate date format DD/MM/YYYY"""
        if not date_str:
            return False, "Vui lòng nhập ngày"
        
        import re
        date_pattern = r'^\d{2}/\d{2}/\d{4}$'
        if not re.match(date_pattern, date_str):
            return False, "Ngày phải theo định dạng DD/MM/YYYY"
        
        try:
            from datetime import datetime
            day, month, year = map(int, date_str.split('/'))
            datetime(year, month, day)
            return True, ""
        except ValueError:
            return False, "Ngày không hợp lệ"
    
    @staticmethod
    def validate_string_length(value, field_name, max_length, required=True):
        """Validate string length"""
        if not value:
            if required:
                return False, f"Vui lòng nhập {field_name}"
            return True, ""
        if len(value) > max_length:
            return False, f"{field_name} không được quá {max_length} ký tự"
        return True, ""
    
    @staticmethod
    def validate_integer(value, field_name, min_val=None, max_val=None, required=False):
        """Validate integer value"""
        if not value:
            if required:
                return False, f"Vui lòng nhập {field_name}"
            return True, ""
        try:
            num = int(value)
            if min_val is not None and num < min_val:
                return False, f"{field_name} không được nhỏ hơn {min_val}"
            if max_val is not None and num > max_val:
                return False, f"{field_name} không được lớn hơn {max_val}"
            return True, ""
        except ValueError:
            return False, f"{field_name} phải là số nguyên"
    
    @staticmethod
    def validate_float(value, field_name, min_val=None, max_val=None, required=False):
        """Validate float value"""
        if not value:
            if required:
                return False, f"Vui lòng nhập {field_name}"
            return True, ""
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                return False, f"{field_name} không được nhỏ hơn {min_val}"
            if max_val is not None and num > max_val:
                return False, f"{field_name} không được lớn hơn {max_val}"
            return True, ""
        except ValueError:
            return False, f"{field_name} phải là số"
    
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Initialize positions as empty, will load after controller is set
        self.positions = ()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=2)
        
        # Left panel - Form
        self.setup_form_panel(main_container)
        
        # Right panel - Staff List
        self.setup_list_panel(main_container)
    
    def setup_form_panel(self, parent):
        """Setup the left panel with form"""
        form_frame = ttk.LabelFrame(parent, text="Thông tin Nhân viên", padding="10")
        form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Form fields
        fields = [
            ("Mã nhân viên:", "ma_nv"),
            ("Họ và tên:", "ho_va_ten"),
            ("Số điện thoại:", "sdt"),
            ("Chức vụ:", "chuc_vu"),
            ("Ngày vào làm:", "ngay_vao_lam"),
            ("Mã quản lý:", "ma_quan_ly")
        ]
        
        self.entries = {}
        
        for idx, (label_text, field_name) in enumerate(fields):
            label = ttk.Label(form_frame, text=label_text)
            label.grid(row=idx, column=0, sticky=tk.W, pady=5)
            
            # Use Combobox for chuc_vu field
            if field_name == "chuc_vu":
                entry = ttk.Combobox(form_frame, width=28, state='readonly')
                # Will be populated later via update_positions method
                entry['values'] = self.positions
                entry.grid(row=idx, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
            else:
                entry = ttk.Entry(form_frame, width=30)
                entry.grid(row=idx, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
            
            # Add placeholder text for date field
            if field_name == "ngay_vao_lam":
                entry.insert(0, "DD/MM/YYYY")
                entry.config(foreground='gray')
                
                def on_focus_in(event, e=entry):
                    if e.get() == "DD/MM/YYYY":
                        e.delete(0, tk.END)
                        e.config(foreground='black')
                
                def on_focus_out(event, e=entry):
                    if not e.get():
                        e.insert(0, "DD/MM/YYYY")
                        e.config(foreground='gray')
                
                entry.bind('<FocusIn>', on_focus_in)
                entry.bind('<FocusOut>', on_focus_out)
            
            self.entries[field_name] = entry
        
        # Configure column weights for form_frame
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)
        
        # Buttons
        self.btn_create = ttk.Button(button_frame, text="Tạo mới", 
                                      command=self.on_create_click)
        self.btn_create.grid(row=0, column=0, padx=5)
        
        self.btn_update = ttk.Button(button_frame, text="Cập nhật", 
                                      command=self.on_update_click, state='disabled')
        self.btn_update.grid(row=0, column=1, padx=5)
        
        self.btn_delete = ttk.Button(button_frame, text="Xóa", 
                                      command=self.on_delete_click, state='disabled')
        self.btn_delete.grid(row=0, column=2, padx=5)
        
        # Search frame
        search_frame = ttk.LabelFrame(form_frame, text="Tìm kiếm", padding="10")
        search_frame.grid(row=len(fields)+1, column=0, columnspan=2, 
                         sticky=(tk.W, tk.E), pady=10)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        search_btn = ttk.Button(search_frame, text="Tìm kiếm", 
                               command=self.on_search_click)
        search_btn.grid(row=0, column=1, padx=5)
        
        search_frame.grid_columnconfigure(0, weight=1)
    
    def setup_list_panel(self, parent):
        """Setup the right panel with staff list"""
        list_frame = ttk.LabelFrame(parent, text="Danh sách Nhân viên", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        
        self.tree = ttk.Treeview(list_frame, 
                                 columns=("Mã NV", "Họ tên", "Chức vụ", "SĐT", "Ngày vào làm", "Quản lý"),
                                 show="headings",
                                 yscrollcommand=tree_scroll_y.set,
                                 xscrollcommand=tree_scroll_x.set)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Define columns
        self.tree.heading("Mã NV", text="Mã nhân viên")
        self.tree.heading("Họ tên", text="Họ và tên")
        self.tree.heading("Chức vụ", text="Chức vụ")
        self.tree.heading("SĐT", text="Số điện thoại")
        self.tree.heading("Ngày vào làm", text="Ngày vào làm")
        self.tree.heading("Quản lý", text="Mã quản lý")
        
        # Column widths
        self.tree.column("Mã NV", width=120, anchor=tk.CENTER)
        self.tree.column("Họ tên", width=200, anchor=tk.W)
        self.tree.column("Chức vụ", width=150, anchor=tk.W)
        self.tree.column("SĐT", width=120, anchor=tk.CENTER)
        self.tree.column("Ngày vào làm", width=120, anchor=tk.CENTER)
        self.tree.column("Quản lý", width=120, anchor=tk.CENTER)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def on_create_click(self):
        """Handle create button click"""
        data = self.get_form_data()
        if self.validate_form_data(data):
            self.controller.create_staff(data)
    
    def on_update_click(self):
        """Handle update button click"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên để cập nhật")
            return
        
        staff_id = self.tree.item(selected[0])['values'][0]
        data = self.get_form_data()
        if self.validate_form_data(data):
            self.controller.update_staff(staff_id, data)
    
    def on_delete_click(self):
        """Handle delete button click"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên để xóa")
            return
        
        staff_id = self.tree.item(selected[0])['values'][0]
        staff_name = self.tree.item(selected[0])['values'][1]
        
        result = messagebox.askyesno("Xác nhận", 
                                    f"Bạn có chắc muốn xóa nhân viên '{staff_name}'?")
        if result:
            self.controller.delete_staff(staff_id)
    
    def on_search_click(self):
        """Handle search button click"""
        search_term = self.search_var.get().strip()
        self.controller.search_staff(search_term)
    
    def on_search_change(self, *args):
        """Handle search field change (for live search)"""
        # Uncomment for live search
        # search_term = self.search_var.get().strip()
        # if search_term:
        #     self.controller.search_staff(search_term)
        # else:
        #     self.loadData()
        pass
    
    def on_tree_select(self, event):
        """Handle tree item selection"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            
            # Fill form with selected staff data
            self.entries['ma_nv'].delete(0, tk.END)
            self.entries['ma_nv'].insert(0, values[0])
            
            self.entries['ho_va_ten'].delete(0, tk.END)
            self.entries['ho_va_ten'].insert(0, values[1])
            
            self.entries['sdt'].delete(0, tk.END)
            self.entries['sdt'].insert(0, values[3])
            
            self.entries['chuc_vu'].set(values[2])
            
            self.entries['ngay_vao_lam'].delete(0, tk.END)
            self.entries['ngay_vao_lam'].insert(0, values[4])
            
            self.entries['ma_quan_ly'].delete(0, tk.END)
            self.entries['ma_quan_ly'].insert(0, values[5])
            
            # Enable update and delete buttons
            self.btn_update.config(state='normal')
            self.btn_delete.config(state='normal')
    
    def get_form_data(self):
        """Get data from form fields"""
        ngay_vao_lam = self.entries['ngay_vao_lam'].get().strip()
        # Don't return placeholder text
        if ngay_vao_lam == "DD/MM/YYYY":
            ngay_vao_lam = ""
        
        return {
            'ma_nv': self.entries['ma_nv'].get().strip(),
            'ho_va_ten': self.entries['ho_va_ten'].get().strip(),
            'sdt': self.entries['sdt'].get().strip(),
            'chuc_vu': self.entries['chuc_vu'].get().strip(),
            'ngay_vao_lam': ngay_vao_lam,
            'ma_quan_ly': self.entries['ma_quan_ly'].get().strip()
        }
    
    def validate_form_data(self, data):
        """Validate form data"""
        # Validate ma_nv
        valid, msg = self.validate_string_length(data['ma_nv'], "Mã nhân viên", 20, required=True)
        if not valid:
            messagebox.showerror("Lỗi", msg)
            return False
        
        # Validate ho_va_ten
        valid, msg = self.validate_string_length(data['ho_va_ten'], "Họ và tên", 100, required=True)
        if not valid:
            messagebox.showerror("Lỗi", msg)
            return False
        
        # Validate sdt
        valid, msg = self.validate_phone_number(data['sdt'])
        if not valid:
            messagebox.showerror("Lỗi", msg)
            return False
        
        # Validate chuc_vu
        if not data['chuc_vu']:
            messagebox.showerror("Lỗi", "Vui lòng chọn chức vụ")
            return False
        
        # Validate ngay_vao_lam
        valid, msg = self.validate_date_format(data['ngay_vao_lam'])
        if not valid:
            messagebox.showerror("Lỗi", msg)
            return False
        
        # Validate ma_quan_ly
        valid, msg = self.validate_string_length(data['ma_quan_ly'], "Mã quản lý", 20, required=False)
        if not valid:
            messagebox.showerror("Lỗi", msg)
            return False
        
        return True
    
    def load_positions(self):
        """Load positions from database"""
        try:
            if self.controller is None:
                return ('Nhân viên bán hàng', 'Nhân viên kho', 'Quản lí của hàng', 'Quản lí')
            positions_data = self.controller.get_all_positions()
            return tuple(pos['chuc_vu'] for pos in positions_data)
        except Exception as e:
            print(f"Error loading positions: {e}")
            return ('Nhân viên bán hàng', 'Nhân viên kho', 'Quản lí của hàng', 'Quản lí')
    
    def update_positions(self):
        """Update positions in combobox after controller is set"""
        self.positions = self.load_positions()
        if 'chuc_vu' in self.entries:
            self.entries['chuc_vu']['values'] = self.positions
    
    def loadData(self):
        """Load data into the staff list based on queries"""
        self.controller.load_all_staff()
    
    def display_staff(self, staff_list):
        """Display staff in the treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert new items
        for emp in staff_list:
            self.tree.insert('', tk.END, values=(
                emp.get('ma_nv', ''),
                emp.get('ho_va_ten', ''),
                emp.get('chuc_vu', ''),
                emp.get('sdt', ''),
                emp.get('ngay_vao_lam', ''),
                emp.get('ma_quan_ly', '')
            ))
    
    def show_message(self, title, message, msg_type="info"):
        """Show message box"""
        if msg_type == "info":
            messagebox.showinfo(title, message)
        elif msg_type == "error":
            messagebox.showerror(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
    
    def clear_form(self):
        """Clear all form fields"""
        for field_name, entry in self.entries.items():
            if field_name == "chuc_vu":
                # For Combobox, use set method
                entry.set('')
            elif field_name == "ngay_vao_lam":
                # Reset date field to placeholder
                entry.delete(0, tk.END)
                entry.insert(0, "DD/MM/YYYY")
                entry.config(foreground='gray')
            else:
                # For Entry widgets
                entry.delete(0, tk.END)
        
        # Disable update and delete buttons
        self.btn_update.config(state='disabled')
        self.btn_delete.config(state='disabled')
