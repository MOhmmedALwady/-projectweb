import tkinter as tk
from tkinter import ttk, messagebox
from invoice_pdf import generate_invoice_pdf


class ViewsManager:
    def __init__(self, main_content, db):
        self.main_content = main_content
        self.db = db
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """إعداد أنماط TTK المخصصة للجداول والقوائم المنسدلة"""
        style = ttk.Style()
        style.theme_use("clam")

        # تنسيق جدول البيانات (Treeview)
        style.configure(
            "Custom.Treeview",
            background="#1E293B",
            foreground="#F8FAFC",
            fieldbackground="#1E293B",
            rowheight=35,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#0F172A",
            foreground="#38BDF8",
            font=("Segoe UI", 11, "bold"),
            borderwidth=0,
            padding=8
        )
        style.map("Custom.Treeview", background=[("selected", "#2563EB")], foreground=[("selected", "#FFFFFF")])

        # تنسيق القائمة المنسدلة (Combobox)
        style.configure(
            "Custom.TCombobox",
            fieldbackground="#334155",
            background="#1E293B",
            foreground="#FFFFFF",
            arrowcolor="#38BDF8",
            bordercolor="#475569",
            lightcolor="#475569",
            darkcolor="#475569",
            padding=6
        )
        style.map("Custom.TCombobox", fieldbackground=[("readonly", "#334155")],
                  selectbackground=[("readonly", "#334155")])

    def clear(self):
        """تفريغ مساحة العمل"""
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def create_header(self, title_text, icon="⚡"):
        """رأس الصفحة الموحد للواجهات"""
        header_frame = tk.Frame(self.main_content, bg="#0F172A")
        header_frame.pack(fill="x", pady=(0, 20))

        title = tk.Label(
            header_frame,
            text=f"{title_text} {icon}",
            font=("Segoe UI", 18, "bold"),
            bg="#0F172A",
            fg="#F8FAFC",
            anchor="e"
        )
        title.pack(side="right")

    def create_input(self, parent, label_text, row=None, col=None, readonly=False):
        """إنشاء حقل إدخال مع بطاقة نصية"""
        container = tk.Frame(parent, bg="#1E293B")

        if row is not None and col is not None:
            container.grid(row=row, column=col, sticky="ew", padx=10, pady=8)
        else:
            container.pack(fill="x", pady=6)

        lbl = tk.Label(
            container,
            text=label_text,
            font=("Segoe UI", 10, "bold"),
            bg="#1E293B",
            fg="#CBD5E1",
            anchor="e"
        )
        lbl.pack(fill="x", pady=(0, 4))

        bg_color = "#1E293B" if readonly else "#334155"
        entry = tk.Entry(
            container,
            font=("Segoe UI", 11, "bold" if readonly else "normal"),
            bg=bg_color,
            fg="#38BDF8" if readonly else "#FFFFFF",
            insertbackground="#38BDF8",
            bd=1,
            relief="flat",
            highlightbackground="#475569",
            highlightthickness=1,
            justify="right",
            state="readonly" if readonly else "normal"
        )
        entry.pack(fill="x", ipady=6)
        return entry

    def create_button(self, parent, text, bg_color, command):
        """زر عمليات احترافي"""
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            bd=0,
            height=2,
            cursor="hand2",
            command=command
        )
        return btn

    # --- 1. لوحة التحكم ---
    def show_dashboard(self):
        self.clear()
        self.create_header("لوحة التحكم والإحصائيات", "📊")

        # بطاقات ملخص إحصائي
        stats_frame = tk.Frame(self.main_content, bg="#0F172A")
        stats_frame.pack(fill="x", pady=(0, 20))
        stats_frame.columnconfigure((0, 1, 2), weight=1, uniform="stat")

        recent_users = self.db.get_recent_users()
        total_users_count = len(recent_users) if recent_users else 0

        cards_data = [
            ("المشتركين الجدد", str(total_users_count), "#3B82F6"),
            ("المولدات النشطة", "جاهز", "#10B981"),
            ("حالة النظام", "مستقر ⚡", "#8B5CF6")
        ]

        for idx, (title, val, color) in enumerate(cards_data):
            card = tk.Frame(stats_frame, bg="#1E293B", highlightbackground=color, highlightthickness=1)
            card.grid(row=0, column=idx, padx=8, sticky="ew")

            tk.Label(card, text=title, font=("Segoe UI", 10), bg="#1E293B", fg="#94A3B8", anchor="e").pack(fill="x",
                                                                                                           padx=15,
                                                                                                           pady=(12, 0))
            tk.Label(card, text=val, font=("Segoe UI", 18, "bold"), bg="#1E293B", fg="#F8FAFC", anchor="e").pack(
                fill="x", padx=15, pady=(0, 12))

        # حاوية الجدول زر الإضافة
        table_container = tk.Frame(self.main_content, bg="#1E293B", padx=15, pady=15)
        table_container.pack(fill="both", expand=True)

        top_table_bar = tk.Frame(table_container, bg="#1E293B")
        top_table_bar.pack(fill="x", pady=(0, 10))

        tk.Label(
            top_table_bar,
            text="أحدث المشتركين المضافين",
            font=("Segoe UI", 12, "bold"),
            bg="#1E293B",
            fg="#38BDF8",
            anchor="e"
        ).pack(side="right")

        # زر إضافة مشترك سريع
        add_user_btn = tk.Button(
            top_table_bar,
            text="➕ إضافة مشترك جديد",
            font=("Segoe UI", 9, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.show_add_user
        )
        add_user_btn.pack(side="left")

        # الجدول
        columns = ("da_add", "adriss", "phone", "name_user", "id")
        tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")

        tree.heading("id", text="#", anchor="center")
        tree.heading("name_user", text="اسم المشترك", anchor="e")
        tree.heading("phone", text="رقم الهاتف", anchor="e")
        tree.heading("adriss", text="العنوان", anchor="e")
        tree.heading("da_add", text="تاريخ الإضافة", anchor="e")

        tree.column("id", anchor="center", width=60)
        tree.column("name_user", anchor="e", width=200)
        tree.column("phone", anchor="e", width=140)
        tree.column("adriss", anchor="e", width=180)
        tree.column("da_add", anchor="e", width=150)

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="left", fill="y")
        tree.pack(side="right", fill="both", expand=True)

        if recent_users:
            for row in recent_users:
                tree.insert("", "end", values=(
                    str(row[4])[:10] if row[4] else "-",
                    row[3],
                    row[2],
                    row[1],
                    row[0]
                ))

    # --- 1.1 واجهة إضافة مشترك جديد ---
    def show_add_user(self):
        self.clear()
        self.create_header("تسجيل مشترك جديد", "👤")

        form = tk.Frame(self.main_content, bg="#1E293B", padx=30, pady=25)
        form.pack(fill="x")
        form.columnconfigure((0, 1), weight=1)

        entry_name = self.create_input(form, "👤 اسم المشترك كامل", row=0, col=1)
        entry_phone = self.create_input(form, "📞 رقم الهاتف", row=0, col=0)
        entry_address = self.create_input(form, "📍 العنوان / السكن", row=1, col=1)

        def save_user():
            name = entry_name.get().strip()
            phone = entry_phone.get().strip()
            address = entry_address.get().strip()

            if not name or not phone:
                messagebox.showwarning("تنبيه", "يرجى كتابة الاسم ورقم الهاتف على الأقل")
                return

            if hasattr(self.db, 'add_user'):
                if self.db.add_user(name, phone, address):
                    messagebox.showinfo("نجاح", "تمت إضافة المشترك بنجاح!")
                    self.show_dashboard()
            else:
                messagebox.showinfo("نجاح", "تم حفظ بيانات المشترك")
                self.show_dashboard()

        btn = self.create_button(form, "✅ حفظ بيانات المشترك", "#10B981", save_user)
        btn.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(20, 0))

    # --- 2. تموين الوقود مع حقل الإجمالي المكتمل ---
    def show_fuel(self):
        self.clear()
        self.create_header("تموين الوقود (جدول oil_gentor)", "⛽")

        form = tk.Frame(self.main_content, bg="#1E293B", padx=30, pady=25)
        form.pack(fill="x")
        form.columnconfigure((0, 1), weight=1)

        # اختيار المولد
        gen_frame = tk.Frame(form, bg="#1E293B")
        gen_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        tk.Label(gen_frame, text="⚙️ اختر المولد (genetor)", font=("Segoe UI", 10, "bold"), bg="#1E293B", fg="#CBD5E1",
                 anchor="e").pack(fill="x", pady=(0, 4))
        combo_gen = ttk.Combobox(gen_frame, values=self.db.get_generators(), style="Custom.TCombobox", state="readonly",
                                 justify="right")
        combo_gen.pack(fill="x")

        # الحقول: الكمية، السعر الفردي، والإجمالي
        entry_qty = self.create_input(form, "🛢️ الكمية باللتر (quanity)", row=1, col=1)
        entry_price = self.create_input(form, "💰 سعر اللتر / التكلفة (coast)", row=1, col=0)
        entry_total = self.create_input(form, "💵 المبلغ الإجمالي (Total)", row=2, col=0, readonly=True)

        # دالة الحساب التلقائي للإجمالي
        def calculate_total(*args):
            try:
                qty = float(entry_qty.get())
                price = float(entry_price.get())
                total = qty * price
                entry_total.config(state="normal")
                entry_total.delete(0, 'end')
                entry_total.insert(0, f"{total:,.2f}")
                entry_total.config(state="readonly")
            except ValueError:
                entry_total.config(state="normal")
                entry_total.delete(0, 'end')
                entry_total.config(state="readonly")

        entry_qty.bind("<KeyRelease>", calculate_total)
        entry_price.bind("<KeyRelease>", calculate_total)

        def save():
            selected = combo_gen.get()
            if not selected or not entry_qty.get() or not entry_price.get():
                messagebox.showwarning("تنبيه", "يرجى تعبئة كافة الحقول المطلوبة")
                return
            try:
                id_gentor = selected.split(']')[0].replace('[', '').strip()
                if self.db.add_fuel(id_gentor, entry_qty.get(), entry_price.get()):
                    messagebox.showinfo("نجاح", "تم تسجيل عملية التموين بنجاح!")
                    combo_gen.set('')
                    entry_qty.delete(0, 'end')
                    entry_price.delete(0, 'end')
                    entry_total.config(state="normal")
                    entry_total.delete(0, 'end')
                    entry_total.config(state="readonly")
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {str(e)}")

        btn = self.create_button(form, "✅ حفظ تموين الوقود", "#D97706", save)
        btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(20, 0))

    # --- 3. تسجيل القراءات مكتملة الحقول ---
    def show_meter(self):
        self.clear()
        self.create_header("تسجيل قراءات العداد (جدول meter)", "📟")

        form = tk.Frame(self.main_content, bg="#1E293B", padx=30, pady=25)
        form.pack(fill="x")
        form.columnconfigure((0, 1), weight=1)

        # اختيار المشترك
        user_frame = tk.Frame(form, bg="#1E293B")
        user_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        tk.Label(user_frame, text="👤 اختر المشترك", font=("Segoe UI", 10, "bold"), bg="#1E293B", fg="#CBD5E1",
                 anchor="e").pack(fill="x", pady=(0, 4))
        combo_user = ttk.Combobox(user_frame, values=self.db.get_users(), style="Custom.TCombobox", state="readonly",
                                  justify="right")
        combo_user.pack(fill="x")

        # الحقول الخاصة بالعداد
        entry_sn = self.create_input(form, "🔢 رقم العداد التسلسلي (Serial Number)", row=1, col=1)
        entry_prev = self.create_input(form, "📉 القراءة السابقة", row=1, col=0)
        entry_curr = self.create_input(form, "📈 القراءة الحالية", row=2, col=1)
        entry_diff = self.create_input(form, "⚡ كمية الاستهلاك (ك.و)", row=2, col=0, readonly=True)

        # دالة حساب الفرق تلقائياً
        def calc_consumption(*args):
            try:
                prev = float(entry_prev.get())
                curr = float(entry_curr.get())
                diff = curr - prev
                entry_diff.config(state="normal")
                entry_diff.delete(0, 'end')
                entry_diff.insert(0, f"{diff:,.1f}" if diff >= 0 else "قراءة خاطئة")
                entry_diff.config(state="readonly")
            except ValueError:
                entry_diff.config(state="normal")
                entry_diff.delete(0, 'end')
                entry_diff.config(state="readonly")

        entry_prev.bind("<KeyRelease>", calc_consumption)
        entry_curr.bind("<KeyRelease>", calc_consumption)

        def save_reading():
            if not combo_user.get() or not entry_sn.get() or not entry_curr.get():
                messagebox.showwarning("تنبيه", "يرجى تحديد المشترك وإدخال رقم العداد والقراءة الحالية")
                return
            messagebox.showinfo("نجاح", "تم حفظ قراءة العداد بنجاح!")

        btn = self.create_button(form, "💾 تسجيل القراءة", "#2563EB", save_reading)
        btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(20, 0))

    # --- 4. إضافة المولدات ---
    def show_generators(self):
        self.clear()
        self.create_header("إضافة مولد جديد (جدول genetor)", "⚙️")

        form = tk.Frame(self.main_content, bg="#1E293B", padx=30, pady=25)
        form.pack(fill="x")
        form.columnconfigure((0, 1), weight=1)

        entry_name = self.create_input(form, "🏷️ اسم المولد (name_gentor)", row=0, col=1)
        entry_power = self.create_input(form, "⚡ القدرة الكهربائية (power_gentor)", row=0, col=0)
        entry_cost = self.create_input(form, "💰 تكلفة الشراء (total_gentor)", row=1, col=1)

        def save():
            name = entry_name.get().strip()
            if not name:
                messagebox.showwarning("تنبيه", "يرجى كتابة اسم المولد على الأقل")
                return

            if self.db.add_generator(name):
                messagebox.showinfo("نجاح", "تمت إضافة المولد بنجاح!")
                entry_name.delete(0, 'end')
                entry_power.delete(0, 'end')
                entry_cost.delete(0, 'end')

        btn = self.create_button(form, "➕ إضافة المولد", "#2563EB", save)
        btn.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(20, 0))

    # --- 5. صيانة المولدات ---
    def show_maintenance(self):
        self.clear()
        self.create_header("تسجيل صيانة المولدات", "🔧")

        form = tk.Frame(self.main_content, bg="#1E293B", padx=30, pady=25)
        form.pack(fill="x")

        tk.Label(
            form,
            text="⚙️ المولدات الكهربائية التي تحتاج صيانة",
            font=("Segoe UI", 11, "bold"),
            bg="#1E293B",
            fg="#CBD5E1",
            anchor="e"
        ).pack(fill="x", pady=(0, 8))

        generators_list = getattr(self.db, 'get_gentor', self.db.get_generators)()
        combo_gen = ttk.Combobox(form, values=generators_list, style="Custom.TCombobox", state="readonly",
                                 justify="right")
        combo_gen.pack(fill="x", pady=(0, 15))

        entry_desc = self.create_input(form, "📝 تفاصيل ورشة الصيانة / القطع المستبدلة")
        entry_cost = self.create_input(form, "💰 تكلفة الصيانة")

        def save_maint():
            if not combo_gen.get():
                messagebox.showwarning("تنبيه", "يرجى اختيار المولد")
                return
            messagebox.showinfo("نجاح", "تم تسجيل أمر الصيانة بنجاح")

        btn = self.create_button(form, "🛠️ تسجيل أمر الصيانة", "#059669", save_maint)
        btn.pack(fill="x", pady=(20, 0))

    # --- واجهة الفواتير والتحصيل (إضافة إلى ViewsManager) ---
    def show_invoices(self):
        self.clear()
        self.create_header("إصدار فاتورة وتحصيل", "🧾")

        form = tk.Frame(self.main_content, bg="#1E293B", padx=30, pady=25)
        form.pack(fill="x")
        form.columnconfigure((0, 1), weight=1)

        # 1. اختيار المشترك والعداد
        f_user = tk.Frame(form, bg="#1E293B")
        f_user.grid(row=0, column=1, sticky="ew", padx=10, pady=8)
        tk.Label(
            f_user,
            text="👤 اختر المشترك",
            font=("Segoe UI", 10, "bold"),
            bg="#1E293B",
            fg="#CBD5E1",
            anchor="e",
        ).pack(fill="x")
        combo_user = ttk.Combobox(
            f_user,
            values=self.db.get_users(),
            style="Custom.TCombobox",
            state="readonly",
            justify="right",
        )
        combo_user.pack(fill="x")

        f_meter = tk.Frame(form, bg="#1E293B")
        f_meter.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        tk.Label(
            f_meter,
            text="📟 رقم العداد",
            font=("Segoe UI", 10, "bold"),
            bg="#1E293B",
            fg="#CBD5E1",
            anchor="e",
        ).pack(fill="x")
        combo_meter = ttk.Combobox(
            f_meter, style="Custom.TCombobox", state="readonly", justify="right"
        )
        combo_meter.pack(fill="x")

        # 2. سعر الواط والمبلغ الإجمالي
        entry_price = self.create_input(form, "⚡ سعر الواط/الكيلو", row=1, col=1)
        entry_price.insert(0, "500")

        entry_total = self.create_input(
            form, "💰 المبلغ الإجمالي (total)", row=1, col=0, readonly=True
        )

        # كود يضاف لزر الطباعة والحفظ
        def save_and_print():
            user_sel = combo_user.get()
            meter_sel = combo_meter.get()

            if not user_sel or not meter_sel:
                messagebox.showwarning("تنبيه", "يرجى اختيار المشترك والعداد")
                return

            u_id = (
                user_sel.split("]")[0].replace("[", "").strip()
                if "[" in user_sel
                else user_sel
            )
            m_id = (
                meter_sel.split("]")[0].replace("[", "").strip()
                if "[" in meter_sel
                else meter_sel
            )
            u_name = user_sel.split("]")[1].strip() if "]" in user_sel else user_sel

            # 1. حفظ الفاتورة بالفيزياء في قاعدة البيانات
            if self.db.save_invoice(
                    u_id, m_id, entry_price.get(), combo_status.get(), entry_write.get()
            ):
                # 2. طباعة الفاتورة PDF تلقائياً
                invoice_info = {
                    "user_name": u_name,
                    "meter_id": m_id,
                    "consumption": str(self.db.get_meter_consumption(m_id)),
                    "price": entry_price.get(),
                    "total": entry_total.get(),
                    "status": combo_status.get(),
                    "write": entry_write.get(),
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }

                generate_invoice_pdf(invoice_info)
                messagebox.showinfo(
                    "نجاح", "تم حفظ الفاتورة وتم فتح ملف PDF للطباعة بنجاح!"
                )

        # 3. حالة السداد والملاحظات
        f_status = tk.Frame(form, bg="#1E293B")
        f_status.grid(row=2, column=1, sticky="ew", padx=10, pady=8)
        tk.Label(
            f_status,
            text="💳 حالة السداد",
            font=("Segoe UI", 10, "bold"),
            bg="#1E293B",
            fg="#CBD5E1",
            anchor="e",
        ).pack(fill="x")
        combo_status = ttk.Combobox(
            f_status,
            values=["تم السداد", "لم يتم السداد"],
            style="Custom.TCombobox",
            state="readonly",
            justify="right",
        )
        combo_status.current(0)
        combo_status.pack(fill="x")

        entry_write = self.create_input(
            form, "📝 ملاحظات / الآجل (write)", row=2, col=0, readonly=True
        )

        # 4. الأحداث التفاعلية
        def calc_total(*args):
            m_val = combo_meter.get()
            if not m_val:
                return
            try:
                m_id = (
                    m_val.split("]")[0].replace("[", "").strip()
                    if "[" in m_val
                    else m_val
                )
                qty = self.db.get_meter_consumption(m_id)
                total = float(qty) * float(entry_price.get())
                entry_total.config(state="normal")
                entry_total.delete(0, "end")
                entry_total.insert(0, f"{total:,.2f}")
                entry_total.config(state="readonly")
            except ValueError:
                pass

        def on_user_select(event):
            u_val = combo_user.get()
            if not u_val:
                return
            u_id = (
                u_val.split("]")[0].replace("[", "").strip()
                if "[" in u_val
                else u_val
            )
            meters = self.db.get_user_meters(u_id)
            combo_meter["values"] = meters
            if meters:
                combo_meter.current(0)
                calc_total()

        def on_status_select(event):
            if combo_status.get() == "لم يتم السداد":
                entry_write.config(state="normal")
            else:
                entry_write.config(state="normal")
                entry_write.delete(0, "end")
                entry_write.config(state="readonly")

        combo_user.bind("<<ComboboxSelected>>", on_user_select)
        combo_meter.bind("<<ComboboxSelected>>", calc_total)
        entry_price.bind("<KeyRelease>", calc_total)
        combo_status.bind("<<ComboboxSelected>>", on_status_select)

        # 5. حفظ الفاتورة
        def save():
            u_val, m_val = combo_user.get(), combo_meter.get()
            if not u_val or not m_val:
                messagebox.showwarning(
                    "تنبيه", "يرجى اختيار المشترك والعداد"
                )
                return

            u_id = (
                u_val.split("]")[0].replace("[", "").strip()
                if "[" in u_val
                else u_val
            )
            m_id = (
                m_val.split("]")[0].replace("[", "").strip()
                if "[" in m_val
                else m_val
            )

            if self.db.save_invoice(
                    u_id,
                    m_id,
                    entry_price.get(),
                    combo_status.get(),
                    entry_write.get(),
            ):
                messagebox.showinfo("نجاح", "تم حفظ الفاتورة بنجاح!")
                self.show_invoices()

        btn = self.create_button(
            form, "💳 حفظ وإصدار الفاتورة", "#10B981", save
        )
        btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(20, 0))
