from model.database import Database
from datetime import datetime


class Invoice:
    def __init__(self, db: Database):
        self.db = db
    
    def create_invoice(self, ma_hoa_don, ten_khach_hang, ma_nv, giam_gia, items):
        """
        Create a new invoice with items
        """
        try:
            ngay_gio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Insert into HOA_DON table
            query_hoa_don = """
            INSERT INTO HOA_DON (ma_hoa_don, ten_khach_hang, ngay_gio, ma_nv)
            VALUES (%s, %s, %s, %s)
            """
            params_hoa_don = (ma_hoa_don, ten_khach_hang, ngay_gio, ma_nv)
            cursor_hoa_don = self.db.execute_query(query_hoa_don, params_hoa_don)
            
            if not cursor_hoa_don:
                return False, "Không thể tạo hóa đơn"
            
            # Insert invoice items (giam_gia applies to whole invoice)
            query_chi_tiet = """
            INSERT INTO HOA_DON_THUOC (ma_hoa_don, ma_thuoc, don_vi_tinh, so_luong, giam_gia, gia_ban)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            for item in items:
                params_chi_tiet = (
                    ma_hoa_don,
                    item['ma_thuoc'],
                    item['don_vi_tinh'],
                    item['so_luong'],
                    giam_gia,  # Apply invoice-level discount to all items
                    item['don_gia']
                )
                cursor_chi_tiet = self.db.execute_query(query_chi_tiet, params_chi_tiet)
                if not cursor_chi_tiet:
                    return False, f"Không thể thêm thuốc {item['ten_thuoc']} vào hóa đơn"
            
            return True, "Tạo hóa đơn thành công"
        except Exception as e:
            return False, f"Lỗi khi tạo hóa đơn: {str(e)}"
    
    def get_all_invoices(self):
        """
        Get all invoices with calculated totals
        """
        query = """
        SELECT 
            h.ma_hoa_don,
            h.ten_khach_hang,
            h.ngay_gio,
            h.ma_nv,
            COALESCE(SUM(ht.so_luong * ht.gia_ban), 0) as tong_tien_hang,
            COALESCE(SUM(ht.so_luong * ht.gia_ban * ht.giam_gia / 100), 0) as tong_giam_gia,
            COALESCE(SUM(ht.so_luong * ht.gia_ban * (1 - ht.giam_gia / 100)), 0) as thanh_tien
        FROM HOA_DON h
        LEFT JOIN HOA_DON_THUOC ht 
            ON h.ma_hoa_don = ht.ma_hoa_don
        GROUP BY 
            h.ma_hoa_don,
            h.ten_khach_hang,
            h.ngay_gio,
            h.ma_nv
        ORDER BY h.ngay_gio DESC;
        """
        return self.db.fetch_query(query)
    
    def get_invoice_by_id(self, ma_hoa_don):
        """
        Get invoice by ID with details
        """
        query = """
        SELECT h.ma_hoa_don, h.ten_khach_hang, h.ngay_gio, h.ma_nv,
               ht.ma_thuoc, t.ten_thuoc, ht.don_vi_tinh, ht.so_luong, ht.gia_ban as don_gia, ht.giam_gia,
               (ht.so_luong * ht.gia_ban - ht.giam_gia) as item_thanh_tien
        FROM HOA_DON h
        LEFT JOIN HOA_DON_THUOC ht ON h.ma_hoa_don = ht.ma_hoa_don
        LEFT JOIN THUOC t ON ht.ma_thuoc = t.ma_thuoc
        WHERE h.ma_hoa_don = %s
        """
        params = (ma_hoa_don,)
        return self.db.fetch_query(query, params)
    
    def delete_invoice(self, ma_hoa_don):
        """
        Delete invoice
        """
        try:
            # Delete invoice details first (foreign key constraint)
            query_chi_tiet = "DELETE FROM HOA_DON_THUOC WHERE ma_hoa_don = %s"
            self.db.execute_query(query_chi_tiet, (ma_hoa_don,))
            
            # Delete invoice
            query_hoa_don = "DELETE FROM HOA_DON WHERE ma_hoa_don = %s"
            cursor = self.db.execute_query(query_hoa_don, (ma_hoa_don,))
            
            return cursor is not None, "Xóa hóa đơn thành công" if cursor else "Không thể xóa hóa đơn"
        except Exception as e:
            return False, f"Lỗi khi xóa hóa đơn: {str(e)}"
    
    def get_all_medicines(self):
        """
        Get all medicines for invoice creation, including don_vi_tinh and gia_ban
        """
        query = """
        SELECT t.ma_thuoc, t.ten_thuoc, t.hang_sx, t.so_luong_ton_kho,
        ht.gia_ban, ht.don_vi_tinh
        FROM THUOC t
        LEFT JOIN HOA_DON_THUOC ht ON t.ma_thuoc = ht.ma_thuoc
        ORDER BY t.ten_thuoc
        """
        return self.db.fetch_query(query)
