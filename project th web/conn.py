import pyodbc
from datetime import datetime


class DatabaseManager:

    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        """الاتصال بقاعدة البيانات SQL Server"""
        try:
            connection_string = (
                "DRIVER={SQL Server};"
                r"SERVER=PC1\SQLEXPRESS;"
                "DATABASE=eloctro;"
                "Trusted_Connection=yes;"
            )
            self.conn = pyodbc.connect(connection_string)
        except Exception as e:
            print(f"خطأ الاتصال بقاعدة البيانات: {e}")

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except:
                pass

    # --- 1. استعلامات المولدات والوقود ---
    def get_generators(self):
        """جلب id_gentor و name_gentor لجدول المولدات"""
        if not self.conn:
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id_gentor, name_gentor FROM genetor")
            return [f"[{row[0]}] {row[1]}" for row in cursor.fetchall()]
        except Exception as e:
            print(f"خطأ في جلب المولدات: {e}")
            return []

    def get_gentor(self):
        """دالة بديلة لجلب قائمة المولدات للصيانة"""
        return self.get_generators()

    def add_generator(self, name, power="", total_cost=""):
        """إضافة مولد جديد لجدول genetor"""
        if not self.conn:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO genetor (name_gentor, power_gentor, total_gentor) VALUES (?, ?, ?)",
                (name, power, total_cost),
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"خطأ في إضافة المولد: {e}")
            return False

    def add_fuel(self, id_gentor, qty, cost):
        """تسجيل تموين وقود في جدول oil_gentor"""
        if not self.conn:
            return False
        try:
            cursor = self.conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "INSERT INTO oil_gentor (id_gentor, quanity, coast, date_oil) VALUES (?, ?, ?, ?)"
            cursor.execute(sql, (id_gentor, float(qty), float(cost), now))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"خطأ في إضافة الوقود: {e}")
            return False

    # --- 2. استعلامات المشتركين والعدادات ---
    def get_users(self):
        """جلب Id_user و name_user من جدول [user] للكومبوبوكس"""
        if not self.conn:
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT Id_user, name_user FROM [user]")
            return [f"[{row[0]}] {row[1]}" for row in cursor.fetchall()]
        except Exception as e:
            print(f"خطأ في جلب المشتركين: {e}")
            return []

    def get_user_meters(self, id_user):
        """جلب العدادات التابعة للمشترك المحدد من جدول meter"""
        if not self.conn:
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id_meter FROM meter WHERE Id_user = ?", (id_user,)
            )
            return [f"[{row[0]}]" for row in cursor.fetchall()]
        except Exception as e:
            print(f"خطأ في جلب العدادات: {e}")
            return []

    def get_meter_consumption(self, id_meter):
        """جلب كمية الاستهلاك للعداد من جدول meter"""
        if not self.conn:
            return 0.0
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT TOP 1 current_new FROM meter WHERE id_meter = ? ORDER BY id_meter DESC",
                (id_meter,),
            )
            row = cursor.fetchone()
            return float(row[0]) if row and row[0] else 0.0
        except Exception as e:
            print(f"خطأ في جلب كمية الاستهلاك: {e}")
            return 0.0

    def add_user(self, name, phone, address):
        """إضافة مشترك جديد لجدول [user]"""
        if not self.conn:
            return False
        try:
            cursor = self.conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO [user] (name_user, phone, adriss, da_add) VALUES (?, ?, ?, ?)",
                (name, phone, address, now),
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"خطأ في إضافة المشترك: {e}")
            return False

    def get_recent_users(self):
        """جلب أحدث 10 مشتركين للوحة التحكم"""
        if not self.conn:
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT TOP 10 Id_user, name_user, phone, adriss, da_add FROM [user] ORDER BY Id_user DESC"
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"خطأ في جلب أحدث المشتركين: {e}")
            return []

    # --- 3. استعلام حفظ الفاتورة (جدول invoice) ---
    def save_invoice(
            self, id_user, id_meter, price_per_watt, status_payment, note=""
    ):
        """
        إصدار فاتورة وحفظها في جدول invoice:
        - حساب Total = الاستهلاك * سعر الواط
        - إذا تم السداد: stuts = 'تم السداد', write = ''
        - إذا لم يتم السداد: stuts = 'غير مدفوع', write = النص المكتوب في الملاحظات
        """
        if not self.conn:
            return False
        try:
            consumption = self.get_meter_consumption(id_meter)
            total = float(consumption) * float(price_per_watt)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if status_payment == "تم السداد":
                stuts_val = "تم السداد"
                write_val = ""
            else:
                stuts_val = "غير مدفوع"
                write_val = note.strip() if note and note.strip() else "آجل"

            cursor = self.conn.cursor()
            sql = """
                INSERT INTO invoice (id_user, id_meter, total, date_invoice, stuts, write)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(
                sql, (id_user, id_meter, total, now, stuts_val, write_val)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"خطأ في حفظ الفاتورة: {e}")
            return False
