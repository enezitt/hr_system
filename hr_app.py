import json
import tempfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os
import streamlit.components.v1 as components
import time

DATA_FILE = "employees.csv"

# تحميل البيانات
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "الاسم", "الرقم الوظيفي", "رقم الهوية", "رقم نسخة الهوية",
            "رقم الجوال", "تاريخ انتهاء الهوية", "تاريخ انتهاء رخصة العمل",
            "تاريخ انتهاء كرت السائق", "المسمى الوظيفي", "الراتب الأساسي",
            "الحوافز", "الاستقطاعات", "الراتب الصافي"
        ])

def upload_to_drive(local_file_path, drive_folder_id):
    try:
        print("🚀 بدأت عملية رفع الملف إلى Google Drive")
        st.success("🚀 بدأت عملية رفع الملف إلى Google Drive")

        credentials_info = json.loads(st.secrets["gdrive_credentials"])
        creds = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/drive"]
        )

        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': 'employees.csv',
            'parents': [drive_folder_id]
        }

        media = MediaFileUpload(local_file_path, mimetype='text/csv')

        query = f"name='employees.csv' and '{drive_folder_id}' in parents"
        results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
        files = results.get('files', [])

        if files:
            file_id = files[0]['id']
            service.files().update(fileId=file_id, media_body=media).execute()
        else:
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    except Exception as e:
        st.error(f"❌ فشل رفع الملف إلى Google Drive: {e}")
        print(f"❌ فشل رفع الملف إلى Google Drive: {e}")

def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

    folder_id = "1fCNL0oB95GB1wCDHLwqZDCFfEte8XxCg"
    upload_to_drive(DATA_FILE, folder_id)


def clear_form():
    st.session_state.clear()

# واجهة البرنامج
st.set_page_config(page_title="نظام شؤون الموظفين", layout="wide")

# تغيير لون خلفية الصفحة إلى لون فاتح
st.markdown("""
<style>
body, .stApp {
    background-color: #fff !important; /* أبيض للصفحة الرئيسية */
}
/* القائمة الجانبية */
section[data-testid="stSidebar"] {
    border: 2px solid #1565c0 !important; /* أزرق غامق */
    border-radius: 16px !important;
    background-color: #e3f0fc !important; /* أزرق فاتح للقائمة فقط */
    margin: 8px;
    width: 200px !important; /* عرض أصغر للقائمة */
}
/* أزرار القائمة الجانبية */
section[data-testid="stSidebar"] button {
    border: 2px solid #1565c0 !important;
    border-radius: 8px !important;
    background-color: #e3f0fc !important;
    color: #1565c0 !important;
    font-weight: bold;
    margin-bottom: 6px;
    font-size: 14px !important; /* حجم النص داخل الأزرار */
    padding: 8px 12px !important; /* تقليل الحشوة داخل الأزرار */
    display: flex;
    align-items: center;
    justify-content: flex-start;
}
section[data-testid="stSidebar"] button:focus, section[data-testid="stSidebar"] button:hover {
    background-color: #bbdefb !important;
    color: #0d47a1 !important;
    border-color: #0d47a1 !important;
}
section[data-testid="stSidebar"] button svg {
    width: 20px !important; /* توحيد عرض الأيقونات */
    height: 20px !important; /* توحيد ارتفاع الأيقونات */
    margin-right: 8px; /* مسافة بين الأيقونة والنص */
}
/* أزرار العمليات الرئيسية */
.stButton > button {
    border: 2px solid #1565c0 !important;
    border-radius: 8px !important;
    background-color: #e3f0fc !important;
    color: #1565c0 !important;
    font-size: 150% !important;
    padding: 0.75em 2.5em !important;
    font-weight: bold;
}
.stButton > button:focus, .stButton > button:hover {
    background-color: #bbdefb !important;
    color: #0d47a1 !important;
    border-color: #0d47a1 !important;
}
</style>
""", unsafe_allow_html=True)

data = load_data()

# إعادة تنظيم القائمة الجانبية
with st.sidebar:
    st.markdown("## القائمة")
    # الصفحة الرئيسية
    if st.button("الصفحة الرئيسية", key="sidebar_home"):
        st.session_state['menu'] = "الصفحة الرئيسية"
    # Dashboard
    if st.button("Dashboard", key="sidebar_Dashboard"):
        st.session_state['menu'] = "Dashboard"
    st.markdown("---")
    # شؤون الموظفين dropdown
    with st.expander("### شؤون الموظفين"):
        for option in ["إضافة موظف", "عرض الموظفين", "تعديل موظف", "حذف موظف", "تنبيهات المستندات"]:
            if st.button(option, key=f"sidebar_{option}"):
                st.session_state['menu'] = option
    if 'menu' not in st.session_state:
        st.session_state['menu'] = "الصفحة الرئيسية"
    menu = st.session_state['menu']

# صفحة رئيسية
if menu == "الصفحة الرئيسية":
    st.markdown("""
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh;'>
            <h1 style='color: #1565c0; font-size: 3.5em; font-weight: bold; margin-bottom: 0.2em;'>أبراج الميناء للخدمات اللوجستية</h1>
            <hr style='width: 60%; border: 2px solid #1565c0; margin: 1em 0;'>
            <p style='font-size: 1.5em; color: #333;'>نظام شؤون الموظفين</p>
        </div>
    """, unsafe_allow_html=True)

# 0️⃣ الداش بورد
if menu == "Dashboard":
    st.subheader("📊 Dashboard")
    today = date.today()  # تعريف today هنا
    # عدد الموظفين
    total_employees = len(data)
    # عدد المستندات التي ستنتهي خلال أقل من 50 يوم
    def count_soon_expiry(col):
        dates = pd.to_datetime(data[col], errors='coerce')
        mask = dates.notna()
        soon = (dates - pd.Timestamp(today)).dt.days <= 50
        return (mask & soon).sum()
    soon_expiry_count = (
        count_soon_expiry("تاريخ انتهاء الهوية") +
        count_soon_expiry("تاريخ انتهاء رخصة العمل") +
        count_soon_expiry("تاريخ انتهاء كرت السائق")
    )
    # عدد المستندات التي ستنتهي خلال أقل من 50 يوم لكل نوع
    soon_id_expiry = count_soon_expiry("تاريخ انتهاء الهوية")
    soon_work_permit_expiry = count_soon_expiry("تاريخ انتهاء رخصة العمل")
    soon_driver_card_expiry = count_soon_expiry("تاريخ انتهاء كرت السائق")
    # إجمالي الرواتب
    total_salary = data["الراتب الأساسي"].sum() if not data.empty else 0
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد الموظفين", total_employees)
    col2.metric("عدد المستندات ستنتهي خلال 50 يوم", soon_expiry_count)
    col3.metric("إجمالي الرواتب", f"{total_salary:,.2f}")
    st.markdown("---")
    st.markdown("#### تفاصيل المستندات التي ستنتهي خلال 50 يوم")
    doc_col1, doc_col2, doc_col3 = st.columns(3)
    doc_col1.metric("هويات ستنتهي", soon_id_expiry)
    doc_col2.metric("رخص عمل ستنتهي", soon_work_permit_expiry)
    doc_col3.metric("كروت سائق ستنتهي", soon_driver_card_expiry)
    # إجمالي الرواتب حسب المسمى الوظيفي
    st.markdown("---")
    st.markdown("#### إجمالي الرواتب حسب المسمى الوظيفي")
    if not data.empty:
        grouped = data.groupby("المسمى الوظيفي")["الراتب الأساسي"].sum().reset_index()
        grouped = grouped.rename(columns={"المسمى الوظيفي": "المسمى الوظيفي", "الراتب الأساسي": "إجمالي الرواتب"})
        grouped["إجمالي الرواتب"] = grouped["إجمالي الرواتب"].apply(lambda x: f"{x:,.2f}")
        st.dataframe(grouped, use_container_width=True)
    else:
        st.info("لا توجد بيانات لعرض إجمالي الرواتب حسب المسمى الوظيفي.")

# 1️⃣ إضافة موظف
if menu == "إضافة موظف":
    st.subheader("➕ إضافة موظف جديد")

    with st.form("add_employee"):
        name = st.text_input("الاسم الكامل", key="add_name")
        job_id = st.text_input("الرقم الوظيفي", key="add_job_id")
        id_number = st.text_input("رقم الهوية", key="add_id_number")
        id_copy_number = st.text_input("رقم نسخة الهوية (اختياري)", key="add_id_copy_number")
        phone = st.text_input("رقم الجوال", key="add_phone")
        id_expiry = st.date_input("تاريخ انتهاء الهوية", value=None, key="add_id_expiry")
        work_permit_expiry = st.date_input("تاريخ انتهاء رخصة العمل", value=None, key="add_work_permit_expiry")
        driver_card_expiry = st.date_input("تاريخ انتهاء كرت السائق (اختياري)", value=None, key="add_driver_card_expiry")
        st.caption(":orange[يرجى اختيار التاريخ من التقويم]")
        job_title = st.text_input("المسمى الوظيفي", key="add_job_title")
        base_salary = st.number_input("الراتب الأساسي", min_value=0.0, key="add_base_salary")
        # زر إضافة كبير مع تكبير الخط
        add_btn_style = """
        <style>
        .stButton > button {
            font-size: 150% !important;
            padding: 0.75em 2.5em !important;
        }
        </style>
        """
        st.markdown(add_btn_style, unsafe_allow_html=True)
        confirm = st.form_submit_button("إضافة")

    if confirm:
        # التحقق من الرقم الوظيفي كرقم فريد مع تجاهل الحقول الفارغة
        if not job_id:
            st.error("⚠️ يجب إدخال الرقم الوظيفي")
        elif job_id in data["الرقم الوظيفي"].dropna().astype(str).values:
            st.error("❌ الرقم الوظيفي مكرر")
        elif name in data["الاسم"].values:
            st.error("❌ الاسم مكرر")
        elif id_number in data["رقم الهوية"].values:
            st.error("❌ رقم الهوية مكرر")
        elif id_expiry is None or work_permit_expiry is None:
            st.warning("⚠️ يجب تعبئة تواريخ الهوية ورخصة العمل بشكل صحيح")
        else:
            if 'add_confirm' not in st.session_state or not st.session_state['add_confirm']:
                st.session_state['add_confirm'] = True
                st.warning("هل أنت متأكد من إضافة هذا الموظف؟ أعد الضغط على إضافة للتأكيد.")
                st.stop()
            else:
                st.session_state['add_confirm'] = False
                net_salary = base_salary
                new_row = pd.DataFrame({
                    "الاسم": [name],
                    "الرقم الوظيفي": [job_id],
                    "رقم الهوية": [id_number],
                    "رقم نسخة الهوية": [id_copy_number],
                    "رقم الجوال": [phone],
                    "تاريخ انتهاء الهوية": [id_expiry],
                    "تاريخ انتهاء رخصة العمل": [work_permit_expiry],
                    "تاريخ انتهاء كرت السائق": [driver_card_expiry if driver_card_expiry else ""],
                    "المسمى الوظيفي": [job_title],
                    "الراتب الأساسي": [base_salary],
                    "الراتب الصافي": [net_salary]
                })
                data = pd.concat([data, new_row], ignore_index=True)
                save_data(data)
                st.success("✅ تم حفظ الموظف بنجاح، سيتم تحديث الصفحة...")
                # تأخير بسيط حتى يرى المستخدم الرسالة
                time.sleep(1)
                # تفريغ session_state قبل التحديث
                for key in list(st.session_state.keys()):
                    if key.startswith("add_") or key == "add_confirm":
                        del st.session_state[key]
                st.rerun()

# 2️⃣ عرض الموظفين
elif menu == "عرض الموظفين":
    st.subheader("👥 قائمة الموظفين")
    df_display = data.copy()
    df_display.index = df_display.index + 1
    df_display.index.name = "#"
    st.dataframe(df_display)

# 3️⃣ تعديل موظف
elif menu == "تعديل موظف":
    st.subheader("✏️ تعديل بيانات موظف")
    names = data["الاسم"].tolist()
    selected_name = st.selectbox("اختر موظفًا للتعديل", names)

    if selected_name:
        emp = data[data["الاسم"] == selected_name].iloc[0]
        placeholder_date = date(2000, 1, 1)

        with st.form("edit_form"):
            name = st.text_input("الاسم الكامل", emp["الاسم"])
            job_id = st.text_input("الرقم الوظيفي", emp["الرقم الوظيفي"])
            id_number = st.text_input("رقم الهوية", emp["رقم الهوية"])
            id_copy_number = st.text_input("رقم نسخة الهوية", emp["رقم نسخة الهوية"])
            phone = st.text_input("رقم الجوال", emp["رقم الجوال"])
            id_expiry = st.date_input("تاريخ انتهاء الهوية", value=pd.to_datetime(emp["تاريخ انتهاء الهوية"]) if pd.notna(emp["تاريخ انتهاء الهوية"]) and emp["تاريخ انتهاء الهوية"] != '' else None, key="edit_id_expiry")
            work_permit_expiry = st.date_input("تاريخ انتهاء رخصة العمل", value=pd.to_datetime(emp["تاريخ انتهاء رخصة العمل"]) if pd.notna(emp["تاريخ انتهاء رخصة العمل"]) and emp["تاريخ انتهاء رخصة العمل"] != '' else None, key="edit_work_permit_expiry")
            driver_card_expiry = st.date_input("تاريخ انتهاء كرت السائق (اختياري)", value=pd.to_datetime(emp["تاريخ انتهاء كرت السائق"]) if pd.notna(emp["تاريخ انتهاء كرت السائق"]) and emp["تاريخ انتهاء كرت السائق"] != '' else None, key="edit_driver_card_expiry")
            st.caption(":orange[يرجى اختيار التاريخ من التقويم]")
            job_title = st.text_input("المسمى الوظيفي", emp["المسمى الوظيفي"])
            base_salary = st.number_input("الراتب الأساسي", value=float(emp["الراتب الأساسي"]))
            bonus = st.number_input("الحوافز", value=float(emp["الحوافز"]))
            deductions = st.number_input("الاستقطاعات", value=float(emp["الاستقطاعات"]))
            # في التعديل
            submit_edit = st.form_submit_button("تعديل")
            if submit_edit:
                if 'edit_confirm' not in st.session_state or not st.session_state['edit_confirm']:
                    st.session_state['edit_confirm'] = True
                    st.warning("هل أنت متأكد من تعديل بيانات هذا الموظف؟ أعد الضغط على تعديل للتأكيد.")
                    st.stop()
                else:
                    st.session_state['edit_confirm'] = False
                    index = data[data["الاسم"] == selected_name].index[0]
                    data.loc[index, [
                        "الاسم", "الرقم الوظيفي", "رقم الهوية", "رقم نسخة الهوية", "رقم الجوال",
                        "تاريخ انتهاء الهوية", "تاريخ انتهاء رخصة العمل", "تاريخ انتهاء كرت السائق",
                        "المسمى الوظيفي", "الراتب الأساسي", "الراتب الصافي"
                    ]] = [
                        name, job_id, id_number, id_copy_number, phone,
                        id_expiry, work_permit_expiry, driver_card_expiry if driver_card_expiry != placeholder_date else "",
                        job_title, base_salary, base_salary
                    ]
                    save_data(data)
                    st.success("✅ تم تعديل بيانات الموظف")
                    st.rerun()

# 4️⃣ حذف موظف
elif menu == "حذف موظف":
    st.subheader("🗑️ حذف موظف")
    names = data["الاسم"].tolist()
    if not names:
        st.info("لا يوجد موظفين للحذف.")
    else:
        selected_name = st.selectbox("اختر موظفًا للحذف", names)
        confirm = st.checkbox("أؤكد أنني أريد حذف هذا الموظف نهائيًا")
        # في الحذف (خارج الفورم)
        delete_btn_style = """
        <style>
        .stButton > button {
            font-size: 150% !important;
            padding: 0.75em 2.5em !important;
        }
        </style>
        """
        st.markdown(delete_btn_style, unsafe_allow_html=True)
        if st.button("حذف"):
            if 'delete_confirm' not in st.session_state or not st.session_state['delete_confirm']:
                st.session_state['delete_confirm'] = True
                st.warning("هل أنت متأكد أنك تريد حذف هذا الموظف نهائيًا؟ أعد الضغط على حذف للتأكيد.")
                st.stop()
            else:
                st.session_state['delete_confirm'] = False
                data = data[data["الاسم"] != selected_name]
                save_data(data)
                st.success(f"✅ تم حذف {selected_name}")
                st.rerun()

# 5️⃣ تنبيهات المستندات
elif menu == "تنبيهات المستندات":
    st.subheader("🚨 تنبيهات قرب انتهاء المستندات")

    today = date.today()
    alert_days = 30

    def check_expiry(col):
        # تجاهل القيم الفارغة وتحويل اليوم إلى Timestamp
        dates = pd.to_datetime(data[col], errors='coerce')
        mask = dates.notna()
        compare_date = pd.Timestamp(today + timedelta(days=alert_days))
        return mask & (dates <= compare_date)

    alerts = data[
        check_expiry("تاريخ انتهاء الهوية") |
        check_expiry("تاريخ انتهاء رخصة العمل") |
        check_expiry("تاريخ انتهاء كرت السائق")
    ]

    if alerts.empty:
        st.success("✅ لا توجد مستندات ستنتهي قريبًا.")
    else:
        st.error("⚠️ يوجد مستندات أو وثائق على وشك الانتهاء:")
        # تجهيز نسخة للعرض مع اندكس يبدأ من 1
        alerts_display = alerts.copy()
        alerts_display.index = alerts_display.index + 1
        alerts_display.index.name = "#"
        # تلوين الأعمدة حسب المدة المتبقية
        def color_expiry(val):
            if pd.isna(val) or val == '':
                return ''
            try:
                days_left = (pd.to_datetime(val) - pd.Timestamp(today)).days
                if days_left > 100:
                    return 'background-color: #d4edda; color: #155724;'  # أخضر فاتح
                elif 50 < days_left <= 100:
                    return 'background-color: #fff3cd; color: #856404;'  # أصفر فاتح
                elif days_left <= 50:
                    return 'background-color: #f8d7da; color: #721c24;'  # أحمر فاتح
            except:
                return ''
            return ''
        styled_alerts = alerts_display[["الاسم", "تاريخ انتهاء الهوية", "تاريخ انتهاء رخصة العمل", "تاريخ انتهاء كرت السائق"]].style\
            .applymap(color_expiry, subset=["تاريخ انتهاء الهوية", "تاريخ انتهاء رخصة العمل", "تاريخ انتهاء كرت السائق"])
        st.dataframe(styled_alerts, use_container_width=True)
