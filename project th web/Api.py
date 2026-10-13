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
