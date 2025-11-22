from model.database import Database
from model.invoice import Invoice


class InvoiceController:
    """Controller layer to connect View and Model for Invoices"""
    
    def __init__(self, view):
        self.view = view
        self.db = Database()
        self.invoice_model = Invoice(self.db)
        
        # Connect to database
        if not self.db.connect():
            self.view.show_message("Lỗi kết nối", 
                                  "Không thể kết nối đến cơ sở dữ liệu. Vui lòng kiểm tra cấu hình.",
                                  "error")
    
    def create_invoice(self, ma_hoa_don, ten_khach_hang, ma_nv, giam_gia, items):
        """Create a new invoice"""
        try:
            return self.invoice_model.create_invoice(
                ma_hoa_don,
                ten_khach_hang,
                ma_nv,
                giam_gia,
                items
            )
        except Exception as e:
            return False, f"Không thể tạo hóa đơn: {str(e)}"
    
    def load_all_invoices(self):
        """Load all invoices"""
        try:
            invoices = self.invoice_model.get_all_invoices()
            self.view.display_invoices(invoices)
        except Exception as e:
            self.view.show_message("Lỗi", f"Không thể tải danh sách hóa đơn: {str(e)}", "error")
    
    def search_invoices(self, search_term):
        """Search invoices"""
        try:
            invoices = self.invoice_model.search_invoices(search_term)
            self.view.display_invoices(invoices)
            if not invoices:
                self.view.show_message("Thông báo", "Không tìm thấy hóa đơn nào", "info")
        except Exception as e:
            self.view.show_message("Lỗi", f"Không thể tìm kiếm hóa đơn: {str(e)}", "error")
    
    def get_all_medicines(self):
        """Get all medicines for invoice creation"""
        try:
            return self.invoice_model.get_all_medicines()
        except Exception as e:
            print(f"Error getting medicines: {str(e)}")
            return []
    
    def close(self):
        """Close database connection"""
        self.db.disconnect()
