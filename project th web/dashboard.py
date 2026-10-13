import tkinter as tk
from datetime import datetime
from ttkbootstrap import Style  # اختياري للثيمات
from conn import DatabaseManager
from style import ViewsManager


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("⚡ نظام إلكترو - لوحة التحكم وإدارة المحطة")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(bg="#0F172A")

        # ربط قاعدة البيانات
        self.db = DatabaseManager()
        self.active_button = None

        # شبكة التطبيق الرئيسية
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # شريط الحالة السفلي
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # ------------ 1. الشريط الجانبي (Sidebar) ------------
        self.sidebar = tk.Frame(self, bg="#1E293B", width=260)
        self.sidebar.grid(row=0, column=1, sticky="nsew")
        self.sidebar.pack_propagate(False)

        # الهيدر الخاص بالشريط الجانبي
        branding_frame = tk.Frame(self.sidebar, bg="#1E293B")
        branding_frame.pack(fill="x", pady=(25, 15), padx=20)

        tk.Label(
            branding_frame,
            text="ELECTRO ⚡",
            font=("Segoe UI", 20, "bold"),
            bg="#1E293B",
            fg="#38BDF8",
            anchor="e"
        ).pack(fill="x")

        tk.Label(
            branding_frame,
            text="نظام إدارة المحطات والمولدات",
            font=("Segoe UI", 8),
            bg="#1E293B",
            fg="#64748B",
            anchor="e"
        ).pack(fill="x", pady=(2, 0))

        # خط فاصل
        tk.Frame(self.sidebar, bg="#334155", height=1).pack(fill="x", padx=20, pady=(0, 15))

        # حاوية أزرار التنقل
        self.nav_frame = tk.Frame(self.sidebar, bg="#1E293B")
        self.nav_frame.pack(fill="both", expand=True)

        # مؤشر الاتصال بالقاعدة في أسفل القائمة الجانبية
        db_status_frame = tk.Frame(self.sidebar, bg="#0F172A", height=45)
        db_status_frame.pack(fill="x", side="bottom", padx=15, pady=15)

        # نقطة ضوئية خضراء تعبر عن اتصال القاعدة
        self.status_dot = tk.Label(db_status_frame, text="●", font=("Segoe UI", 12), bg="#0F172A", fg="#22C55E")
        self.status_dot.pack(side="right", padx=(0, 10), pady=8)

        tk.Label(
            db_status_frame,
            text="قاعدة البيانات متصلة",
            font=("Segoe UI", 9),
            bg="#0F172A",
            fg="#94A3B8"
        ).pack(side="right", pady=8)

        # ------------ 2. منطقة المحتوى (Main Content Area) ------------
        self.content_container = tk.Frame(self, bg="#0F172A")
        self.content_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))

        self.content_container.grid_rowconfigure(1, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # الشريط العلوي التفاعلي (Top Bar)
        self.top_bar = tk.Frame(self.content_container, bg="#1E293B", height=60)
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.top_bar.pack_propagate(False)

        # عنوان الواجهة
        self.page_title = tk.Label(
            self.top_bar,
            text="لوحة التحكم الرئيسية",
            font=("Segoe UI", 13, "bold"),
            bg="#1E293B",
            fg="#F8FAFC"
        )
        self.page_title.pack(side="right", padx=20, pady=15)

        # معلومات المستخدم والصلاحيات
        user_info = tk.Frame(self.top_bar, bg="#1E293B")
        user_info.pack(side="left", padx=20, pady=10)

        tk.Label(
            user_info,
            text="👤 المسؤول",
            font=("Segoe UI", 10, "bold"),
            bg="#1E293B",
            fg="#38BDF8"
        ).pack(side="left")

        # حاوية المشاهد
        self.main_content = tk.Frame(self.content_container, bg="#0F172A")
        self.main_content.grid(row=1, column=0, sticky="nsew")

        # مدير الواجهات
        self.views = ViewsManager(self.main_content, self.db)

        # ------------ 3. شريط الحالة السفلي (Status Bar) ------------
        self.status_bar = tk.Frame(self, bg="#1E293B", height=30)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.time_label = tk.Label(self.status_bar, font=("Segoe UI", 9), bg="#1E293B", fg="#64748B")
        self.time_label.pack(side="left", padx=15)

        self.system_status = tk.Label(self.status_bar, text="الجهاز يعمل بشكل طبيعي", font=("Segoe UI", 9),
                                      bg="#1E293B", fg="#64748B")
        self.system_status.pack(side="right", padx=15)

        # تحديث الساعة تلقائياً
        self._update_clock()

        # ------------ 4. إنشاء الأزرار مع ربط الأحداث ------------
        self.btn_dashboard = self.btn("📊 لوحة التحكم",
                                      lambda: self.navigate(self.views.show_dashboard, "لوحة التحكم الرئيسية",
                                                            self.btn_dashboard))

        # زر الفواتير والتحصيل الجديد
        self.btn_invoices = self.btn("🧾 الفواتير والتحصيل",
                                     lambda: self.navigate(self.views.show_invoices, "إصدار وتتبع الفواتير",
                                                           self.btn_invoices))

        self.btn_generators = self.btn("⚙️ إدارة المولدات",
                                       lambda: self.navigate(self.views.show_generators, "إدارة  المولدات",
                                                             self.btn_generators))
        self.btn_maintenance = self.btn("🔧 صيانة المولدات",
                                        lambda: self.navigate(self.views.show_maintenance, "جدول وأوامر الصيانة",
                                                              self.btn_maintenance))
        self.btn_meter = self.btn("📟 تسجيل القراءات",
                                  lambda: self.navigate(self.views.show_meter, "تسجيل قراءات العدادات", self.btn_meter))
        self.btn_fuel = self.btn("⛽ تموين الوقود",
                                 lambda: self.navigate(self.views.show_fuel, "إدارة وخزانات الوقود", self.btn_fuel))

        # التوجيه والتحديد الأولي
        self.navigate(self.views.show_dashboard, "لوحة التحكم الرئيسية", self.btn_dashboard)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def btn(self, text, command):
        """تنسيق وتجهيز أزرار القائمة الجانبية"""
        btn_container = tk.Frame(self.nav_frame, bg="#1E293B")
        btn_container.pack(fill="x", padx=12, pady=3)

        b = tk.Button(
            btn_container,
            text=f"  {text}  ",
            font=("Segoe UI", 10, "bold"),
            bg="#1E293B",
            fg="#94A3B8",
            activebackground="#0F172A",
            activeforeground="#38BDF8",
            bd=0,
            height=2,
            cursor="hand2",
            anchor="e",
            justify="right",
            command=command
        )
        b.pack(fill="x", expand=True)

        b.bind("<Enter>", lambda e, button=b: self._on_hover(button))
        b.bind("<Leave>", lambda e, button=b: self._on_leave(button))

        return b

    def navigate(self, view_callback, title_text, target_button):
        """إدارة التنقل وتغيير حالات الأزرار والعناوين"""
        view_callback()
        self.page_title.config(text=title_text)
        self._set_active_button(target_button)

    def _on_hover(self, button):
        if button != self.active_button:
            button.config(bg="#334155", fg="#F8FAFC")

    def _on_leave(self, button):
        if button != self.active_button:
            button.config(bg="#1E293B", fg="#94A3B8")

    def _set_active_button(self, button):
        if self.active_button and self.active_button.winfo_exists():
            self.active_button.config(bg="#1E293B", fg="#94A3B8")
        self.active_button = button
        self.active_button.config(bg="#2563EB", fg="#FFFFFF")

    def _update_clock(self):
        """تحديث الوقت في شريط الحالة السفلي"""
        now = datetime.now().strftime("%Y-%m-%d  %I:%M:%S %p")
        self.time_label.config(text=now)
        self.after(1000, self._update_clock)

    def on_close(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
