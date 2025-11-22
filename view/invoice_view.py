import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class InvoiceView:
    """View layer for Invoice Management GUI"""
    
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
                return False, f"{field_name} phải lớn hơn {min_val - 1}"
            if max_val is not None and num > max_val:
                return False, f"{field_name} không hợp lý (quá {max_val:,})"
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
                return False, f"{field_name} không được âm"
            if max_val is not None and num > max_val:
                return False, f"{field_name} không hợp lý (quá {max_val:,})"
            return True, ""
        except ValueError:
            return False, f"{field_name} phải là số"
    
    @staticmethod
    def validate_percentage(value, field_name, required=False):
        """Validate percentage value (0-100)"""
        if not value:
            if required:
                return False, f"Vui lòng nhập {field_name}"
            return True, ""
        try:
            num = float(value)
            if num < 0 or num > 100:
                return False, f"{field_name} phải từ 0 đến 100%"
            return True, ""
        except ValueError:
            return False, f"{field_name} phải là số"
    
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Current invoice items
        self.invoice_items = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=2)
        
        # Top-left panel - Invoice creation form
        self.setup_form_panel(main_container)
        
        # Top-right panel - Invoice items
        self.setup_items_panel(main_container)
        
        # Bottom panel - Invoice list
        self.setup_list_panel(main_container)
    
    def setup_form_panel(self, parent):
        """Setup the left panel with invoice creation form"""
        form_frame = ttk.LabelFrame(parent, text="Tạo Hóa đơn", padding="10")
        form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Invoice info fields
        ttk.Label(form_frame, text="Mã hóa đơn:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_ma_hoa_don = ttk.Entry(form_frame, width=30)
        self.entry_ma_hoa_don.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(form_frame, text="Tên khách hàng:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_ten_khach_hang = ttk.Entry(form_frame, width=30)
        self.entry_ten_khach_hang.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(form_frame, text="Mã Nhân Viên:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_ma_nv = ttk.Entry(form_frame, width=30)
        self.entry_ma_nv.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(form_frame, text="Giảm giá (%):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_giam_gia = ttk.Entry(form_frame, width=30)
        self.entry_giam_gia.insert(0, "0")
        self.entry_giam_gia.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.entry_giam_gia.bind('<KeyRelease>', lambda e: self.update_total())
        
        # Medicine selection section
        medicine_frame = ttk.LabelFrame(form_frame, text="Thêm thuốc vào hóa đơn", padding="10")
        medicine_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        medicine_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(medicine_frame, text="Thuốc:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.combo_medicine = ttk.Combobox(medicine_frame, state='readonly', width=40)
        self.combo_medicine.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.combo_medicine.bind('<<ComboboxSelected>>', self.on_medicine_selected)
        
        ttk.Label(medicine_frame, text="Số lượng:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_so_luong = ttk.Entry(medicine_frame, width=20)
        self.entry_so_luong.insert(0, "1")
        self.entry_so_luong.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(medicine_frame, text="Đơn giá:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_don_gia = ttk.Entry(medicine_frame, width=20, state='readonly')
        self.entry_don_gia.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(medicine_frame, text="Đơn vị tính:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_don_vi_tinh = ttk.Entry(medicine_frame, width=20, state='readonly')
        self.entry_don_vi_tinh.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        btn_add_medicine = ttk.Button(medicine_frame, text="Thêm thuốc", command=self.on_add_medicine_click)
        btn_add_medicine.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Total and buttons
        total_frame = ttk.Frame(form_frame)
        total_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(total_frame, text="Tổng tiền:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
        self.label_total = ttk.Label(total_frame, text="0 VNĐ", font=('Arial', 14, 'bold'), foreground='red')
        self.label_total.pack(anchor=tk.W, pady=5)
        
        btn_frame = ttk.Frame(total_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Xóa thuốc", command=self.on_remove_medicine_click).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Tạo hóa đơn", command=self.on_create_invoice_click).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Hủy", command=self.on_clear_click).pack(side=tk.LEFT, padx=5)
    
    def setup_items_panel(self, parent):
        """Setup the right panel with invoice items"""
        # Invoice items treeview
        item_frame = ttk.LabelFrame(parent, text="Danh sách thuốc trong hóa đơn", padding="10")
        item_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        item_frame.grid_rowconfigure(0, weight=1)
        item_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview for invoice items
        tree_scroll_y = ttk.Scrollbar(item_frame, orient=tk.VERTICAL)
        self.tree_items = ttk.Treeview(item_frame,
                                        columns=("Mã thuốc", "Tên thuốc", "Số lượng", "Đơn vị", "Đơn giá", "Thành tiền"),
                                        show="headings",
                                        height=5,
                                        yscrollcommand=tree_scroll_y.set)
        tree_scroll_y.config(command=self.tree_items.yview)
        
        self.tree_items.heading("Mã thuốc", text="Mã thuốc")
        self.tree_items.heading("Tên thuốc", text="Tên thuốc")
        self.tree_items.heading("Số lượng", text="Số lượng")
        self.tree_items.heading("Đơn vị", text="Đơn vị")
        self.tree_items.heading("Đơn giá", text="Đơn giá")
        self.tree_items.heading("Thành tiền", text="Thành tiền")
        
        self.tree_items.column("Mã thuốc", width=100, anchor=tk.CENTER)
        self.tree_items.column("Tên thuốc", width=200, anchor=tk.W)
        self.tree_items.column("Số lượng", width=80, anchor=tk.CENTER)
        self.tree_items.column("Đơn vị", width=80, anchor=tk.CENTER)
        self.tree_items.column("Đơn giá", width=100, anchor=tk.E)
        self.tree_items.column("Thành tiền", width=100, anchor=tk.E)
        
        self.tree_items.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def setup_list_panel(self, parent):
        """Setup the bottom panel with invoice list"""
        list_frame = ttk.LabelFrame(parent, text="Danh sách Hóa đơn", padding="10")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        
        self.tree = ttk.Treeview(list_frame,
                                 columns=("Mã HĐ", "Tên KH", "Ngày giờ", "Tổng tiền", "Giảm giá", "Thành tiền"),
                                 show="headings",
                                 yscrollcommand=tree_scroll_y.set,
                                 xscrollcommand=tree_scroll_x.set)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Define columns
        self.tree.heading("Mã HĐ", text="Mã hóa đơn")
        self.tree.heading("Tên KH", text="Tên khách hàng")
        self.tree.heading("Ngày giờ", text="Ngày giờ")
        self.tree.heading("Tổng tiền", text="Tổng tiền")
        self.tree.heading("Giảm giá", text="Giảm giá")
        self.tree.heading("Thành tiền", text="Thành tiền")
        
        # Column widths
        self.tree.column("Mã HĐ", width=100, anchor=tk.CENTER)
        self.tree.column("Tên KH", width=200, anchor=tk.W)
        self.tree.column("Ngày giờ", width=150, anchor=tk.CENTER)
        self.tree.column("Tổng tiền", width=120, anchor=tk.E)
        self.tree.column("Giảm giá", width=100, anchor=tk.CENTER)
        self.tree.column("Thành tiền", width=120, anchor=tk.E)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def populate_medicine_combobox(self):
        """Populate medicine combobox from database"""
        if not hasattr(self, 'controller') or not self.controller:
            return
            
        try:
            medicines = self.controller.get_all_medicines()
            if medicines:
                display_values = []
                self.medicine_dict = {}
                for med in medicines:
                    display = f"{med['ma_thuoc']} - {med['ten_thuoc']}"
                    display_values.append(display)
                    self.medicine_dict[display] = med
                
                self.combo_medicine['values'] = display_values
            else:
                self.combo_medicine['values'] = []
                self.medicine_dict = {}
        except Exception as e:
            print(f"Error populating medicine combobox: {str(e)}")
            self.combo_medicine['values'] = []
            self.medicine_dict = {}
    
    def on_medicine_selected(self, event):
        """Handle medicine selection from combobox"""
        selected = self.combo_medicine.get()
        if selected and selected in self.medicine_dict:
            med = self.medicine_dict[selected]
            # Lấy giá và đơn vị từ HOA_DON_THUOC (nếu có), nếu không có thì để trống
            gia_ban = med.get('gia_ban', '')
            don_vi_tinh = med.get('don_vi_tinh', '')
            
            self.entry_don_gia.config(state='normal')
            self.entry_don_gia.delete(0, tk.END)
            if gia_ban is not None and gia_ban != '':
                self.entry_don_gia.insert(0, str(gia_ban))
            self.entry_don_gia.config(state='readonly')
            
            self.entry_don_vi_tinh.config(state='normal')
            self.entry_don_vi_tinh.delete(0, tk.END)
            if don_vi_tinh is not None and don_vi_tinh != '':
                self.entry_don_vi_tinh.insert(0, str(don_vi_tinh))
            self.entry_don_vi_tinh.config(state='readonly')
    
    def on_add_medicine_click(self):
        """Add selected medicine to invoice items"""
        selected = self.combo_medicine.get()
        if not selected:
            messagebox.showerror("Lỗi", "Vui lòng chọn thuốc")
            return
        
        so_luong_str = self.entry_so_luong.get().strip()
        don_gia_str = self.entry_don_gia.get().strip()
        don_vi_tinh = self.entry_don_vi_tinh.get().strip()
        
        # Validate so_luong
        valid, msg = self.validate_integer(so_luong_str, "Số lượng", min_val=1, max_val=100000, required=True)
        if not valid:
            messagebox.showerror("Lỗi", msg)
            return
        
        # Validate don_gia
        valid, msg = self.validate_float(don_gia_str, "Đơn giá", min_val=0, max_val=1000000000, required=True)
        if not valid:
            messagebox.showerror("Lỗi", msg)
            return
        
        # Validate don_vi_tinh
        valid, msg = self.validate_string_length(don_vi_tinh, "Đơn vị tính", 20, required=True)
        if not valid:
            messagebox.showerror("Lỗi", msg)
            return
        
        so_luong = int(so_luong_str)
        don_gia = float(don_gia_str)
        
        medicine = self.medicine_dict[selected]
        thanh_tien = so_luong * don_gia
        
        # Add to invoice items list
        item = {
            'ma_thuoc': medicine['ma_thuoc'],
            'ten_thuoc': medicine['ten_thuoc'],
            'so_luong': so_luong,
            'don_vi_tinh': don_vi_tinh,
            'don_gia': don_gia,
            'thanh_tien': thanh_tien
        }
        self.invoice_items.append(item)
        
        # Add to treeview
        self.tree_items.insert('', tk.END, values=(
            item['ma_thuoc'],
            item['ten_thuoc'],
            item['so_luong'],
            item['don_vi_tinh'],
            f"{item['don_gia']:,.0f}",
            f"{item['thanh_tien']:,.0f}"
        ))
        
        # Update total
        self.update_total()
        
        # Clear inputs
        self.combo_medicine.set('')
        self.entry_so_luong.delete(0, tk.END)
        self.entry_so_luong.insert(0, "1")
        self.entry_don_gia.config(state='normal')
        self.entry_don_gia.delete(0, tk.END)
        self.entry_don_gia.config(state='readonly')
        self.entry_don_vi_tinh.config(state='normal')
        self.entry_don_vi_tinh.delete(0, tk.END)
        self.entry_don_vi_tinh.config(state='readonly')
    
    def on_remove_medicine_click(self):
        """Remove selected medicine from invoice items"""
        selected = self.tree_items.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn thuốc để xóa")
            return
        
        # Get index
        index = self.tree_items.index(selected[0])
        
        # Remove from list and treeview
        del self.invoice_items[index]
        self.tree_items.delete(selected[0])
        
        # Update total
        self.update_total()
    
    def update_total(self):
        """Calculate and update total amount"""
        total = sum(item['thanh_tien'] for item in self.invoice_items)
        try:
            giam_gia = float(self.entry_giam_gia.get().strip() or 0)
        except ValueError:
            giam_gia = 0
        
        final_total = total * (1 - giam_gia / 100)
        self.label_total.config(text=f"{final_total:,.0f} VNĐ")
    
    def on_create_invoice_click(self):
        """Create new invoice"""
        ma_hoa_don = self.entry_ma_hoa_don.get().strip()
        ten_khach_hang = self.entry_ten_khach_hang.get().strip()
        ma_nv = self.entry_ma_nv.get().strip()
        giam_gia_str = self.entry_giam_gia.get().strip()
        
        # Validate ma_hoa_don
        valid, msg = self.validate_string_length(ma_hoa_don, "Mã hóa đơn", 20, required=True)
        if not valid:
            messagebox.showerror("Lỗi", msg)
            return
        
        # Validate ten_khach_hang
        valid, msg = self.validate_string_length(ten_khach_hang, "Tên khách hàng", 100, required=True)
        if not valid:
            messagebox.showerror("Lỗi", msg)
            return
        
        # Validate ma_nv
        valid, msg = self.validate_string_length(ma_nv, "Mã nhân viên", 20, required=True)
        if not valid:
            messagebox.showerror("Lỗi", msg)
            return
        
        # Validate invoice items
        if not self.invoice_items:
            messagebox.showerror("Lỗi", "Vui lòng thêm ít nhất một thuốc")
            return
        
        # Validate discount
        valid, msg = self.validate_percentage(giam_gia_str or "0", "Giảm giá")
        if not valid:
            messagebox.showerror("Lỗi", msg)
            return
        
        giam_gia = float(giam_gia_str or 0)
        
        success, message = self.controller.create_invoice(
            ma_hoa_don, ten_khach_hang, ma_nv, giam_gia, self.invoice_items
        )
        
        if success:
            messagebox.showinfo("Thành công", message)
            self.on_clear_click()
            self.loadData()
        else:
            messagebox.showerror("Lỗi", message)
    
    def on_clear_click(self):
        """Clear form"""
        self.entry_ma_hoa_don.delete(0, tk.END)
        self.entry_ten_khach_hang.delete(0, tk.END)
        self.entry_ma_nv.delete(0, tk.END)
        self.entry_giam_gia.delete(0, tk.END)
        self.entry_giam_gia.insert(0, "0")
        self.combo_medicine.set('')
        self.entry_so_luong.delete(0, tk.END)
        self.entry_so_luong.insert(0, "1")
        self.entry_don_gia.config(state='normal')
        self.entry_don_gia.delete(0, tk.END)
        self.entry_don_gia.config(state='readonly')
        self.entry_don_vi_tinh.config(state='normal')
        self.entry_don_vi_tinh.delete(0, tk.END)
        self.entry_don_vi_tinh.config(state='readonly')
        
        # Clear items
        self.invoice_items.clear()
        for item in self.tree_items.get_children():
            self.tree_items.delete(item)
        
        self.update_total()
    
    def display_invoices(self, invoices):
        """Display invoices in treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert new items
        for inv in invoices:
            self.tree.insert('', tk.END, values=(
                inv.get('ma_hoa_don', ''),
                inv.get('ten_khach_hang', ''),
                inv.get('ngay_gio', ''),
                f"{inv.get('tong_tien_hang', 0):,.0f}",
                f"{inv.get('tong_giam_gia', 0):,.0f}",
                f"{inv.get('thanh_tien', 0):,.0f}"
            ))
    
    def show_message(self, title, message, msg_type="info"):
        """Show message box"""
        if msg_type == "info":
            messagebox.showinfo(title, message)
        elif msg_type == "error":
            messagebox.showerror(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
    
    def loadData(self):
        """Load data into the invoice list"""
        self.controller.load_all_invoices()
