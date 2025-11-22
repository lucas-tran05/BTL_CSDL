import tkinter as tk
from tkinter import ttk, messagebox

class ReportView:
    def __init__(self, parent, controller=None):
        self.parent = parent
        self.controller = controller
        self._seniority_rows = []
        self._revenue_rows = []

        self._build_ui()

    def _build_ui(self):
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Thâm niên
        self.seniority_frame = SeniorityReportFrame(notebook, self)
        notebook.add(self.seniority_frame.root, text="Báo cáo Thâm niên")

        # Doanh thu
        self.revenue_frame = RevenueReportFrame(notebook, self)
        notebook.add(self.revenue_frame.root, text="Báo cáo Doanh thu")

    # Message helper
    def show_message(self, title, msg, level="info"):
        fn = {
            "info": messagebox.showinfo,
            "error": messagebox.showerror,
            "warning": messagebox.showwarning
        }.get(level, messagebox.showinfo)
        fn(title, msg)

    # Controller callbacks
    def set_positions(self, positions):
        self.seniority_frame.position_cb["values"] = ["(Tất cả)"] + positions
        self.seniority_frame.position_cb.current(0)

    def render_seniority(self, rows):
        self._seniority_rows = rows
        tv = self.seniority_frame.tree
        tv.delete(*tv.get_children())
        for r in rows:
            tv.insert("", tk.END, values=(
                r["ma_nv"],
                r["ho_va_ten"],
                r["chuc_vu"],
                r["ngay_vao_lam"],
                r["tham_nien"],
                r["nhom_tham_nien"]
            ))

    def render_revenue(self, rows, total):
        self._revenue_rows = rows
        tv = self.revenue_frame.tree
        tv.delete(*tv.get_children())
        for r in rows:
            tv.insert("", tk.END, values=(
                r["ma_thuoc"],
                r["ten_thuoc"],
                r["so_luong_ban"],
                r["don_gia"],
                r["tong_doanh_thu"]
            ))
        # Footer total row (disable selection style)
        tv.insert("", tk.END, values=("", "", "", "Tổng cộng", total))

    # Export triggers
    def export_seniority(self):
        self.controller.export_seniority(self._seniority_rows)

    def export_revenue(self):
        # Exclude footer
        data = [r for r in self._revenue_rows]
        self.controller.export_revenue(data)


class SeniorityReportFrame:
    def __init__(self, parent, main_view):
        self.main_view = main_view
        self.root = ttk.Frame(parent)
        self._build()

    def _build(self):
        # Header (Masthead + Title + Numbering)
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=4, pady=(4,2))

        # Pharmacy info (masthead)
        masthead = ttk.Label(
            header_frame,
            text=(
                "Nhà thuốc The Blue\n"
                "Mã số thuế: 012345\n"
                "Địa chỉ: Số 10, Trần Phú, Hà Đông, Hà Nội\n"
                "Điện thoại: 0987654321\n"
                "Tài khoản Ngân hàng: 0382117403 - MBBank"
            ),
            justify=tk.LEFT
        )
        masthead.grid(row=0, column=0, sticky="w", padx=(2,20))

        # Report title
        title_lbl = ttk.Label(
            header_frame,
            text="BÁO CÁO THÂM NIÊN NHÂN VIÊN",
            font=("TkDefaultFont", 12, "bold")
        )
        title_lbl.grid(row=0, column=1, sticky="e")

        # Numbering line
        numbering_frame = ttk.Frame(self.root)
        numbering_frame.pack(fill=tk.X, padx=4, pady=(0,4))
        numbering_lbl = ttk.Label(
            numbering_frame,
            text="Mẫu số: TTTTT0101    Số: 0000",
            anchor="e"
        )
        numbering_lbl.pack(fill=tk.X)

        filter_frame = ttk.LabelFrame(self.root, text="Bộ lọc")
        filter_frame.pack(fill=tk.X, padx=4, pady=4)

        ttk.Label(filter_frame, text="Lọc theo Chức vụ:").pack(side=tk.LEFT, padx=(8,4), pady=4)
        self.position_cb = ttk.Combobox(filter_frame, width=30, state="readonly")
        self.position_cb.pack(side=tk.LEFT, padx=4, pady=4)
        self.position_cb.bind("<<ComboboxSelected>>", self._on_filter)

        export_btn = ttk.Button(filter_frame, text="Xuất sang Trang tính", command=self.main_view.export_seniority)
        export_btn.pack(side=tk.RIGHT, padx=8, pady=4)

        columns = ("Mã nhân viên", "Họ và tên", "Chức vụ", "Ngày vào làm", "Thâm niên", "Nhóm thâm niên")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140 if col != "Họ và tên" else 220)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0,4))

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_filter(self, _):
        val = self.position_cb.get()
        if val == "(Tất cả)":
            val = None
        self.main_view.controller.load_seniority(val)


class RevenueReportFrame:
    def __init__(self, parent, main_view):
        self.main_view = main_view
        self.root = ttk.Frame(parent)
        self._build()

    def _build(self):
        # Header (Masthead + Title + Numbering)
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=4, pady=(4,2))

        masthead = ttk.Label(
            header_frame,
            text=(
                "THE BLUE\n"
                "Mã số thuế: 012345\n"
                "Địa chỉ: Số 10, Trần Phú, Hà Đông, Hà Nội\n"
                "Điện thoại: 0987654321\n"
                "Tài khoản Ngân hàng: 0382117403 - MBBank"
            ),
            justify=tk.LEFT
        )
        masthead.grid(row=0, column=0, sticky="w", padx=(2,20))

        title_lbl = ttk.Label(
            header_frame,
            text="BÁO CÁO DOANH THU THEO THÁNG",
            font=("TkDefaultFont", 12, "bold")
        )
        title_lbl.grid(row=0, column=1, sticky="e")

        numbering_frame = ttk.Frame(self.root)
        numbering_frame.pack(fill=tk.X, padx=4, pady=(0,4))
        numbering_lbl = ttk.Label(
            numbering_frame,
            text="Mẫu số: TTTTT0101    Số: 0000",
            anchor="e"
        )
        numbering_lbl.pack(fill=tk.X)

        filter_frame = ttk.LabelFrame(self.root, text="Bộ lọc")
        filter_frame.pack(fill=tk.X, padx=4, pady=4)

        ttk.Label(filter_frame, text="Chọn Tháng/Năm (MM/yyyy):").pack(side=tk.LEFT, padx=(8,4), pady=4)
        self.month_year_cb = ttk.Combobox(filter_frame, width=12, state="readonly")
        self.month_year_cb.pack(side=tk.LEFT, padx=4, pady=4)
        self._populate_months()
        self.month_year_cb.bind("<<ComboboxSelected>>", self._on_change)

        view_btn = ttk.Button(filter_frame, text="Xem Báo cáo", command=self._view_report)
        view_btn.pack(side=tk.LEFT, padx=6)

        export_btn = ttk.Button(filter_frame, text="Xuất sang Trang tính", command=self.main_view.export_revenue)
        export_btn.pack(side=tk.RIGHT, padx=8, pady=4)

        columns = ("Mã thuốc", "Tên thuốc", "Số lượng bán", "Đơn giá", "Tổng doanh thu")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140 if col != "Tên thuốc" else 220)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0,4))

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _populate_months(self):
        import datetime
        now = datetime.datetime.now()
        vals = []
        for i in range(12):
            dt = now - datetime.timedelta(days=30*i)
            vals.append(dt.strftime("%m/%Y"))
        # Unique preserve order
        seen = set()
        unique = []
        for v in vals:
            if v not in seen:
                seen.add(v)
                unique.append(v)
        self.month_year_cb["values"] = unique
        self.month_year_cb.current(0)

    def _on_change(self, _):
        self._view_report()

    def _view_report(self):
        val = self.month_year_cb.get()
        if val:
            self.main_view.controller.load_revenue(val)
