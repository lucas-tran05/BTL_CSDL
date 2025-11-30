import sqlite3
from datetime import datetime
try:
    import mysql.connector
    from mysql.connector import errors as mysql_errors
except ImportError:
    mysql = None

class ReportModel:
    def __init__(self, db_path="database.db", backend="sqlite", mysql_config=None):
        self.db_path = db_path
        self.backend = "mysql" if (backend == "mysql" and mysql and mysql_config) else "sqlite"
        self.mysql_config = mysql_config or {}
        self._invoice_id_col = None
        self._invoice_date_col = None

    def _get_conn(self):
        if self.backend == "mysql":
            try:
                return mysql.connector.connect(**self.mysql_config)
            except mysql_errors.ProgrammingError as e:
                raise RuntimeError(
                    f"Lỗi đăng nhập MySQL (1045): {e}. Kiểm tra user/password, hoặc tạo user riêng:\n"
                    "Ví dụ:\nCREATE USER 'dms_user'@'localhost' IDENTIFIED BY 'StrongPass!';\n"
                    "GRANT SELECT ON NHA_THUOC123.* TO 'dms_user'@'localhost'; FLUSH PRIVILEGES;"
                )
            except mysql_errors.InterfaceError as e:
                raise RuntimeError(f"Lỗi kết nối MySQL: {e}")
            except mysql_errors.Error as e:
                raise RuntimeError(f"Lỗi MySQL: {e}")
        return sqlite3.connect(self.db_path)

    def _detect_invoice_schema(self, conn):
        if self._invoice_id_col and self._invoice_date_col:
            return
        try:
            if self.backend == "mysql":
                cur = conn.cursor()
                cur.execute("DESCRIBE HOA_DON")
                cols = [r[0] for r in cur.fetchall()]
            else:
                cur = conn.execute("PRAGMA table_info(HOA_DON)")
                cols = [r[1] for r in cur.fetchall()]
        except Exception:
            cols = []
        # ID column
        self._invoice_id_col = "ma_hd" if "ma_hd" in cols else ("ma_hoa_don" if "ma_hoa_don" in cols else None)
        self._invoice_date_col = "ngay_lap" if "ngay_lap" in cols else ("ngay_gio" if "ngay_gio" in cols else None)
        if not self._invoice_id_col or not self._invoice_date_col:
            raise RuntimeError("Không xác định được schema bảng HOA_DON (cột mã hoặc ngày).")

    def _detect_detail_schema(self, conn):
        if hasattr(self, "_detail_invoice_fk"):
            return
        try:
            if self.backend == "mysql":
                cur = conn.cursor()
                cur.execute("DESCRIBE HOA_DON_THUOC")
                cols = [r[0] for r in cur.fetchall()]
            else:
                cur = conn.execute("PRAGMA table_info(HOA_DON_THUOC)")
                cols = [r[1] for r in cur.fetchall()]
        except Exception:
            cols = []
        self._detail_invoice_fk = "ma_hd" if "ma_hd" in cols else ("ma_hoa_don" if "ma_hoa_don" in cols else None)
        if not self._detail_invoice_fk:
            raise RuntimeError("Không xác định được khóa ngoại hóa đơn trong HOA_DON_THUOC.")

    def get_positions(self):
        q = "SELECT DISTINCT chuc_vu FROM NHAN_VIEN WHERE chuc_vu IS NOT NULL AND chuc_vu<>'' ORDER BY chuc_vu"
        if self.backend == "mysql":
            conn = self._get_conn()
            try:
                cur = conn.cursor()
                cur.execute(q)
                return [r[0] for r in cur.fetchall()]
            except Exception:
                return []
            finally:
                conn.close()
        else:
            with self._get_conn() as conn:
                try:
                    return [r[0] for r in conn.execute(q).fetchall()]
                except Exception:
                    return []

    def get_seniority(self, position=None):
        if self.backend == "mysql":
            conn = self._get_conn()
            try:
                cur = conn.cursor(dictionary=True)
                sql = """
                    SELECT
                        nv.ma_nv,
                        nv.ho_va_ten,
                        nv.chuc_vu,
                        nv.ngay_vao_lam,
                        CONCAT(
                            TIMESTAMPDIFF(YEAR, nv.ngay_vao_lam, CURDATE()), ' năm ',
                            MOD(TIMESTAMPDIFF(MONTH, nv.ngay_vao_lam, CURDATE()),12), ' tháng'
                        ) AS tham_nien,
                        CASE
                            WHEN TIMESTAMPDIFF(YEAR, nv.ngay_vao_lam, CURDATE()) < 1 THEN 'Dưới 1 năm'
                            WHEN TIMESTAMPDIFF(YEAR, nv.ngay_vao_lam, CURDATE()) BETWEEN 1 AND 3 THEN '1-3 năm'
                            WHEN TIMESTAMPDIFF(YEAR, nv.ngay_vao_lam, CURDATE()) BETWEEN 4 AND 6 THEN '4-6 năm'
                            ELSE 'Trên 6 năm'
                        END AS nhom_tham_nien
                    FROM NHAN_VIEN nv
                """
                params = []
                if position:
                    sql += " WHERE nv.chuc_vu = %s"
                    params.append(position)
                sql += " ORDER BY nv.ngay_vao_lam"
                cur.execute(sql, tuple(params))
                rows = cur.fetchall() or []
                for r in rows:
                    dt = str(r.get("ngay_vao_lam", ""))
                    try:
                        d = datetime.strptime(dt, "%Y-%m-%d")
                        r["ngay_vao_lam"] = d.strftime("%d/%m/%Y")
                    except ValueError:
                        pass
                return rows
            except Exception:
                return []
            finally:
                conn.close()
        # SQLite path
        base = "SELECT ma_nv, ho_va_ten, chuc_vu, ngay_vao_lam FROM NHAN_VIEN"
        params = []
        if position:
            base += " WHERE chuc_vu = ?"
            params.append(position)
        base += " ORDER BY ngay_vao_lam"
        rows = []
        with self._get_conn() as conn:
            try:
                for ma_nv, ho_va_ten, chuc_vu, ngay_vao_lam in conn.execute(base, params):
                    tenure_years, tenure_months = self._calc_tenure(ngay_vao_lam)
                    group = self._tenure_group(tenure_years, tenure_months)
                    rows.append({
                        "ma_nv": ma_nv,
                        "ho_va_ten": ho_va_ten,
                        "chuc_vu": chuc_vu,
                        "ngay_vao_lam": self._format_date(ngay_vao_lam),
                        "tham_nien": f"{tenure_years} năm {tenure_months} tháng",
                        "nhom_tham_nien": group
                    })
            except Exception:
                return []
        return rows

    def _calc_tenure(self, date_str):
        try:
            start = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                start = datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                return 0, 0
        now = datetime.now()
        diff_months = (now.year - start.year) * 12 + (now.month - start.month)
        years = diff_months // 12
        months = diff_months % 12
        return max(years, 0), max(months, 0)

    def _tenure_group(self, years, months):
        total_months = years * 12 + months
        if total_months < 12:
            return "Mới"
        if total_months < 36:
            return "Trung bình"
        return "Lâu năm"

    def _format_date(self, date_str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                d = datetime.strptime(date_str, fmt)
                return d.strftime("%d/%m/%Y")
            except ValueError:
                continue
        return date_str

    def get_revenue_by_month(self, month, year):
        m = f"{int(month):02d}"
        y = str(year)
        data = []
        with self._get_conn() as conn:
            self._detect_invoice_schema(conn)
            self._detect_detail_schema(conn)
            id_col = self._invoice_id_col
            detail_fk = self._detail_invoice_fk
            date_col = self._invoice_date_col
            if self.backend == "mysql":
                q = f"""
                SELECT hdt.ma_thuoc,
                       t.ten_thuoc,
                       SUM(hdt.so_luong) AS so_luong_ban,
                       AVG(hdt.gia_ban) AS don_gia_tb,
                       SUM((hdt.so_luong * hdt.gia_ban) - COALESCE(hdt.giam_gia,0)) AS tong_doanh_thu
                FROM HOA_DON hd
                JOIN HOA_DON_THUOC hdt ON hd.{id_col} = hdt.{detail_fk}
                JOIN THUOC t ON t.ma_thuoc = hdt.ma_thuoc
                WHERE MONTH(hd.{date_col}) = %s AND YEAR(hd.{date_col}) = %s
                GROUP BY hdt.ma_thuoc, t.ten_thuoc
                ORDER BY tong_doanh_thu DESC
                """
                try:
                    cur = conn.cursor()
                    cur.execute(q, (int(month), int(year)))
                    for ma_thuoc, ten_thuoc, so_luong, don_gia_tb, tong_doanh_thu in cur.fetchall():
                        data.append({
                            "ma_thuoc": ma_thuoc,
                            "ten_thuoc": ten_thuoc,
                            "so_luong_ban": so_luong,
                            "don_gia": round(don_gia_tb or 0, 2),
                            "tong_doanh_thu": round(tong_doanh_thu or 0, 2)
                        })
                except Exception as e:
                    raise RuntimeError(f"Lỗi truy vấn doanh thu: {e}")
                return data
            # SQLite path
            try:
                q = f"""
                SELECT hdt.ma_thuoc,
                       t.ten_thuoc,
                       SUM(hdt.so_luong) AS so_luong_ban,
                       AVG(hdt.gia_ban) AS don_gia_tb,
                       SUM((hdt.so_luong * hdt.gia_ban) - COALESCE(hdt.giam_gia,0)) AS tong_doanh_thu
                FROM HOA_DON hd
                JOIN HOA_DON_THUOC hdt ON hd.{id_col} = hdt.{detail_fk}
                JOIN THUOC t ON t.ma_thuoc = hdt.ma_thuoc
                WHERE strftime('%m', hd.{date_col}) = ? AND strftime('%Y', hd.{date_col}) = ?
                GROUP BY hdt.ma_thuoc, t.ten_thuoc
                ORDER BY tong_doanh_thu DESC
                """
                for ma_thuoc, ten_thuoc, so_luong, don_gia_tb, tong_doanh_thu in conn.execute(q, (m, y)):
                    data.append({
                        "ma_thuoc": ma_thuoc,
                        "ten_thuoc": ten_thuoc,
                        "so_luong_ban": so_luong,
                        "don_gia": round(don_gia_tb or 0, 2),
                        "tong_doanh_thu": round(tong_doanh_thu or 0, 2)
                    })
            except Exception as e:
                raise RuntimeError(f"Lỗi truy vấn doanh thu (SQLite): {e}")
            return data

    def revenue_exists(self, month, year):
        with self._get_conn() as conn:
            self._detect_invoice_schema(conn)
            self._detect_detail_schema(conn)
            id_col = self._invoice_id_col
            detail_fk = self._detail_invoice_fk
            date_col = self._invoice_date_col
            if self.backend == "mysql":
                q = f"SELECT COUNT(*) FROM HOA_DON hd JOIN HOA_DON_THUOC hdt ON hd.{id_col}=hdt.{detail_fk} WHERE MONTH(hd.{date_col})=%s AND YEAR(hd.{date_col})=%s"
                cur = conn.cursor()
                cur.execute(q, (int(month), int(year)))
                return cur.fetchone()[0]
            else:
                q = f"SELECT COUNT(*) FROM HOA_DON hd JOIN HOA_DON_THUOC hdt ON hd.{id_col}=hdt.{detail_fk} WHERE strftime('%m', hd.{date_col})=? AND strftime('%Y', hd.{date_col})=?"
                cur = conn.execute(q, (f"{int(month):02d}", str(year)))
                return cur.fetchone()[0]

    def sum_revenue(self, rows):
        return sum(r.get("tong_doanh_thu", 0) for r in rows)
