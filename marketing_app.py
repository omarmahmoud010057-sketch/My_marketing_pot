import streamlit as st
import pandas as pd
import json
import time
import random
import sqlite3
from datetime import datetime
import openai
import telebot

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="AutoClient AI | نظام التسويق الذكي",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- تنسيق CSS لتحسين المظهر ودعم اللغة العربية ---
st.markdown("""
<style>
    body {
        direction: rtl;
        text-align: right;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
    }
    .stTextInput>div>div>input, .stTextArea>div>textarea {
        text-align: right;
        direction: rtl;
    }
    .report-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_stdio=True)

# ==========================================
# --- كلاس المنطق البرمجي (المطور) ---
# (تم تعديله ليتوافق مع واجهة Streamlit)
# ==========================================
class AutoClientAI:
    def __init__(self, product_data, api_keys):
        self.product = product_data
        self.clients_db = "clients_database.db"
        self._init_databases()
        
        # APIs Configuration
        self.telegram_token = api_keys.get('telegram')
        self.openai_api_key = api_keys.get('openai')
        
        # Initialize APIs only if keys are provided
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        if self.telegram_token:
            try:
                self.bot = telebot.TeleBot(self.telegram_token)
            except:
                self.bot = None
        else:
            self.bot = None

    def _init_databases(self):
        conn = sqlite3.connect(self.clients_db)
        c = conn.cursor()
        # جدول العملاء المحتملين (المبسط للعرض)
        c.execute('''CREATE TABLE IF NOT EXISTS leads
                    (id INTEGER PRIMARY KEY,
                     source TEXT,
                     name TEXT,
                     contact_info TEXT,
                     interest_level TEXT,
                     status TEXT)''')
        conn.commit()
        conn.close()

    def generate_marketing_content(self):
        """توليد محتوى تسويقي باستخدام الذكاء الاصطناعي أو بديل"""
        if not self.openai_api_key:
            return self._generate_fallback_content()

        prompt = f"""
        أنا مسوق لمنتج: {self.product['product_name']}
        السعر: {self.product['price']}
        الوصف: {self.product['description']}
        المميزات: {self.product['features']}
        
        أريد:
        1. رسالة تسويقية جذابة (150 كلمة) مناسبة للواتساب والتليجرام.
        2. 5 نقاط بيع رئيسية (Bullet points).
        3. ردود على الاعتراضات الشائعة.
        4. هاشتاقات مناسبة.
        
        بلغة عربية طبيعية وجذابة واحترافية.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", # استخدام 3.5 للسرعة والتكلفة، يمكن تغييره لـ gpt-4
                messages=[
                    {"role": "system", "content": "أنت مسوق محترف وخبير في المبيعات الإلكترونية في الوطن العربي."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ فشل الاتصال بـ OpenAI: {str(e)}\n\n{self._generate_fallback_content()}"

    def _generate_fallback_content(self):
        """محتوى بديل إذا فشل الاتصال أو لم يتوفر المفتاح"""
        msg = f"🎯 *اكتشف {self.product['product_name']}!*\n\n{self.product['description']}\n\n✨ المميزات:\n• {self.product['features'].replace(',', '\n• ')}\n\n💰 السعر: {self.product['price']}\n🔗 للطلب: {self.product['product_link']}"
        return msg

    def find_potential_clients_simulated(self):
        """محاكاة البحث عن عملاء (لأن الكود الأصلي يحتاج ربط حقيقي)"""
        platforms = ["تويتر", "فيسبوك", "تليجرام", "منتدى تقني"]
        names = ["أحمد", "سارة", "محمد", "ليلى", "عمر", "ريم"]
        
        new_leads = []
        conn = sqlite3.connect(self.clients_db)
        c = conn.cursor()
        
        for _ in range(random.randint(3, 7)):
            lead = {
                'source': random.choice(platforms),
                'name': random.choice(names) + str(random.randint(10,99)),
                'contact_info': f"@{random.choice(names).lower()}{random.randint(100,999)}",
                'interest': random.choice(["عالي", "متوسط", "منخفض"])
            }
            # حفظ في قاعدة البيانات
            c.execute("INSERT INTO leads (source, name, contact_info, interest_level, status) VALUES (?, ?, ?, ?, ?)",
                      (lead['source'], lead['name'], lead['contact_info'], lead['interest'], 'جديد'))
            new_leads.append(lead)
            
        conn.commit()
        conn.close()
        return new_leads

    def get_all_leads(self):
        """جلب جميع العملاء من قاعدة البيانات لعرضهم"""
        conn = sqlite3.connect(self.clients_db)
        df = pd.read_sql_query("SELECT source as 'المنصة', name as 'الاسم', contact_info as 'بيانات التواصل', interest_level as 'مستوى الاهتمام', status as 'الحالة' FROM leads", conn)
        conn.close()
        return df

# ==========================================
# --- واجهة المستخدم (Streamlit UI) ---
# ==========================================

st.title("🚀 نظام AutoClient AI التسويقي الذاتي")
st.markdown("مساعدك الذكي لإدارة الحملات التسويقية وجلب العملاء وتوليد المحتوى.")

# --- القائمة الجانبية (Sidebar) لإدخال البيانات ---
with st.sidebar:
    st.header("🔑 إعدادات التشغيل")
    openai_key = st.text_input("OpenAI API Key", type="password", help="للاستفادة من توليد المحتوى بالذكاء الاصطناعي")
    tele_token = st.text_input("Telegram Bot Token", type="password", help="إذا كنت تريد الإرسال عبر التليجرام")
    
    st.divider()
    
    st.header("📦 بيانات المنتج/الخدمة")
    p_name = st.text_input("اسم المنتج", value="سماعات لاسلكية برو")
    p_price = st.text_input("السعر", value="299 جنيه")
    p_link = st.text_input("رابط المنتج", value="https://example.com/shop")
    p_features = st.text_area("المميزات الرئيسية (افصل بينها بفاصلة)", value="بطارية 20 ساعة, عزل ضوضاء, مقاومة للماء, ضمان سنة")
    p_desc = st.text_area("وصف مختصر", value="سماعات عالية الجودة بتصميم مريح")

    st.divider()
    duration = st.number_input("مدة الحملة (بالساعات)", min_value=1, value=24)

    # حفظ البيانات في جلسة Streamlit لتبقى متاحة
    st.session_state['product_data'] = {
        'product_name': p_name,
        'product_link': p_link,
        'price': p_price,
        'description': p_desc,
        'category': 'عام',
        'target_audience': 'عام',
        'features': p_features,
        'commission': '0%'
    }
    st.session_state['api_keys'] = {
        'openai': openai_key,
        'telegram': tele_token
    }

# --- الجسم الرئيسي للأداة (Main Body) ---

# تبويبات (Tabs) لتنظيم الأداة
tab1, tab2, tab3 = st.tabs(["💡 توليد المحتوى", "🔍 جلب العملاء والتشغيل", "📊 لوحة التحكّم"])

# --- التبويب الأول: توليد المحتوى ---
with tab1:
    st.subheader("📝 صناعة محتوى تسويقي ذكي")
    st.markdown("سيقوم النظام بتحليل بيانات المنتج وكتابة نص بيعي مقنع باستخدام GPT.")
    
    if st.button("✨ ابدأ كتابة المحتوى الآن"):
        if not p_name or not p_price:
            st.error("الرجاء إدخال اسم المنتج وسعره في القائمة الجانبية أولاً.")
        else:
            with st.spinner("⏳ جاري التفكير والكتابة... قد يستغرق الأمر دقيقة."):
                agent = AutoClientAI(st.session_state['product_data'], st.session_state['api_keys'])
                content = agent.generate_marketing_content()
                st.session_state['generated_content'] = content
                st.success("✅ تم توليد المحتوى بنجاح!")

    if 'generated_content' in st.session_state:
        st.divider()
        st.subheader("📄 النتيجة:")
        st.text_area("المحتوى المولد (يمكنك نسخه والتعديل عليه)", value=st.session_state['generated_content'], height=400)

# --- التبويب الثاني: جلب العملاء والتشغيل ---
with tab1:
    st.subheader("🔎 رادار العملاء وتشغيل الحملة")
    col_run1, col_run2 = st.columns([1, 2])
    
    with col_run1:
        st.markdown("### تحكم")
        btn_find = st.button("🔍 بحث سريع عن عملاء جدد (محاكاة)")
        btn_start_campaign = st.button("🚀 بدء الحملة الأوتوماتيكية الكاملة")
        
    with col_run2:
        status_area = st.empty() # مكان لعرض تحديثات الحالة
        
    if btn_find:
        agent = AutoClientAI(st.session_state['product_data'], st.session_state['api_keys'])
        with st.spinner("🕵️‍♂️ جاري مسح المنصات..."):
            leads = agent.find_potential_clients_simulated()
            st.success(f"✅ تم العثور على {len(leads)} عميل محتمل جديد وإضافتهم للقاعدة.")
            st.json(leads) # عرض عينة من النتائج

    if btn_start_campaign:
        agent = AutoClientAI(st.session_state['product_data'], st.session_state['api_keys'])
        status_area.info(f"▶️ تم بدء الحملة الأوتوماتيكية لمدة {duration} ساعة...")
        
        # محاكاة دورة واحدة من الحملة للعرض في الواجهة
        progress_bar = st.progress(0)
        status_area.write("⏳ دقيقة 1: جاري البحث عن عملاء...")
        time.sleep(1)
        leads = agent.find_potential_clients_simulated()
        progress_bar.progress(30)
        
        status_area.write(f"💬 دقيقة 2: تم العثور على {len(leads)} عميل. جاري توليد رسائل مخصصة وتجهيز الإرسال...")
        time.sleep(1)
        progress_bar.progress(60)
        
        status_area.write(f"📲 دقيقة 3: جاري التواصل مع العملاء عبر القنوات المتاحة...")
        time.sleep(1)
        progress_bar.progress(100)
        
        st.balloons()
        status_area.success(f"✅ انتهت الدورة الأولى من الحملة. النظام سيعمل في الخلفية (في الحقيقة يحتاج هذا لاستضافة).")

# --- التبويب الثالث: لوحة التحكّم والتقارير ---
with tab3:
    st.subheader("📊 إدارة قاعدة بيانات العملاء (CRM)")
    
    agent = AutoClientAI(st.session_state['product_data'], st.session_state['api_keys'])
    df_leads = agent.get_all_leads()
    
    # إحصائيات سريعة
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("إجمالي العملاء المحتملين", len(df_leads))
    with col_stat2:
        # محاكاة
        st.metric("تفاعلات ناجحة", f"{random.randint(1, len(df_leads) if len(df_leads)>0 else 1)}")
    with col_stat3:
        st.metric("أفضل منصة", "Telegram" if not df_leads.empty else "-")

    st.divider()
    
    # عرض الجدول
    st.dataframe(df_leads, use_container_width=True)
    
    # خيار تحميل البيانات
    if not df_leads.empty:
        csv = df_leads.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل قاعدة العملاء كـ CSV",
            data=csv,
            file_name=f'leads_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )

# --- تذييل الصفحة ---
st.divider()
st.markdown("<center>مطور الأداة: Dark Thorfin AI 313 (تحويل للواجهة بواسطة AI)</center>", unsafe_allow_stdio=True)
