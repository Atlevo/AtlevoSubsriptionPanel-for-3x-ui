import streamlit as st
import sqlite3
import json
import uuid
import time
import bcrypt

DB_PATH = '/etc/x-ui/x-ui.db'

# --- СЛОВАРЬ ПЕРЕВОДОВ ---
LANG = {
    "ru": {
        "title": "Atlevo Subscription Manager",
        "tab1": "Подключения",
        "tab2": "Создать пользователя",
        "name": "Примечание",
        "uuid": "UUID",
        "subid": "Subscription ID",
        "limit": "Лимит трафика (ГБ)",
        "bind": "Настройка доступа к инбаундам",
        "create_btn": "Создать пакет",
        "active": "Включить пользователя",
        "save": "Сохранить изменения",
        "del": "Удалить пользователя",
        "restart_msg": "Готово! Не забудьте Restart Xray.",
        "login_btn": "Войти",
        "auth_title": "🔐 Авторизация Atlevo"
    },
    "en": {
        "title": "Atlevo Subscription Manager",
        "tab1": "Connections",
        "tab2": "Create User",
        "name": "Remark",
        "uuid": "UUID",
        "subid": "Subscription ID",
        "limit": "Traffic Limit (GB)",
        "bind": "Inbound Access Management",
        "create_btn": "Create Package",
        "active": "Enable User",
        "save": "Save Changes",
        "del": "Delete User",
        "restart_msg": "Done! Please Restart Xray.",
        "login_btn": "Login",
        "auth_title": "🔐 Atlevo Auth"
    }
}

# --- СТИЛИЗАЦИЯ (ПО СКРИНШОТАМ) ---
def local_css():
    st.markdown("""
        <style>
        /* Общий фон страницы */
        .stApp { background-color: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; }
        
        /* Контейнер вкладок (Tabs) */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #161e2e;
            border-radius: 12px;
            padding: 8px;
            gap: 8px;
            border-bottom: none;
        }

        /* Сами кнопки вкладок */
        .stTabs [data-baseweb="tab"] {
            height: 44px;
            border-radius: 10px;
            color: #94a3b8;
            border: none;
            background-color: transparent;
            transition: all 0.3s ease;
            padding: 0 20px;
            font-weight: 500;
        }

        /* Активная вкладка (как на скрине 3) */
        .stTabs [aria-selected="true"] {
            background-color: #00a594 !important;
            color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(0, 165, 148, 0.2);
        }

        /* Ховер на вкладках */
        .stTabs [data-baseweb="tab"]:hover {
            color: #ffffff;
            background-color: rgba(0, 165, 148, 0.1);
        }

        /* Карточки (Expander) */
        div[data-testid="stExpander"] {
            background-color: #111827;
            border: 1px solid #1e293b;
            border-radius: 12px;
            margin-bottom: 12px;
        }

        /* Кнопки действий (Сохранить/Создать) */
        .stButton>button {
            border: 1px solid #00a594;
            background-color: #00a594;
            color: white;
            border-radius: 10px;
            font-weight: 600;
            height: 45px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #00897b;
            border-color: #00897b;
            box-shadow: 0 0 15px rgba(0, 165, 148, 0.3);
        }

        /* Поля ввода */
        input {
            background-color: #1e293b !important;
            color: #f8fafc !important;
            border: 1px solid #334155 !important;
            border-radius: 10px !important;
            padding: 12px !important;
        }
        
        /* Переключатели */
        .stToggle div[aria-checked="true"] {
            background-color: #00a594 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- ИНИЦИАЛИЗАЦИЯ СЕССИИ ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- ФУНКЦИИ АВТОРИЗАЦИИ ---
def check_login(user, pwd):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = ?", (user,))
        res = cur.fetchone()
        conn.close()
        if res:
            stored_hash = res[0]
            return bcrypt.checkpw(pwd.encode('utf-8'), stored_hash.encode('utf-8'))
        return False
    except Exception:
        return False

# --- ЛОГИКА БД ---
def get_db_connection(): return sqlite3.connect(DB_PATH)

def get_inbounds():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT id, remark, protocol, port FROM inbounds")
    data = cur.fetchall(); conn.close()
    return data

def get_all_users():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT email, inbound_id, total, enable FROM client_traffics")
    rows = cur.fetchall(); conn.close()
    users = {}
    for r in rows:
        if '_' in r[0]:
            name = r[0].rsplit('_', 1)[0]
            if name not in users: users[name] = {"name": name, "inbounds": {}, "total": r[2], "enable": r[3]}
            users[name]["inbounds"][r[1]] = r[3]
    return users

def delete_user(name):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT email, inbound_id FROM client_traffics WHERE email LIKE ?", (f"{name}_%",))
    for email, ib_id in cur.fetchall():
        cur.execute("SELECT settings FROM inbounds WHERE id = ?", (ib_id,))
        res = cur.fetchone()
        if res:
            setts = json.loads(res[0])
            setts['clients'] = [c for c in setts.get('clients', []) if c.get('email') != email]
            cur.execute("UPDATE inbounds SET settings = ? WHERE id = ?", (json.dumps(setts), ib_id))
        cur.execute("DELETE FROM client_traffics WHERE email = ? AND inbound_id = ?", (email, ib_id))
    conn.commit(); conn.close()

def save_user(name, uid, ib_dict, limit_gb, sid, master):
    delete_user(name)
    conn = get_db_connection(); cur = conn.cursor()
    bytes_val = int(limit_gb * 1024**3) if limit_gb > 0 else 0
    for ib_id, active in ib_dict.items():
        email = f"{name}_{ib_id}"
        cur.execute("SELECT settings FROM inbounds WHERE id = ?", (ib_id,))
        res = cur.fetchone()
        if res:
            setts = json.loads(res[0]); final = 1 if (master and active) else 0
            if 'clients' not in setts: setts['clients'] = []
            setts['clients'].append({"id": uid, "email": email, "totalGB": bytes_val, "enable": bool(final), "subId": sid})
            cur.execute("UPDATE inbounds SET settings = ? WHERE id = ?", (json.dumps(setts), ib_id))
            cur.execute("INSERT INTO client_traffics (inbound_id, enable, email, up, down, total) VALUES (?,?,?,0,0,?)", (ib_id, final, email, bytes_val))
    conn.commit(); conn.close()

# --- ПРИМЕНЕНИЕ СТИЛЕЙ ---
local_css()

# --- САЙДБАР ---
with st.sidebar:
    lang_choice = st.selectbox("🌐 Language", ["RU", "EN"])
    L = LANG["ru"] if lang_choice == "RU" else LANG["en"]
    st.divider()
    if st.session_state.auth:
        if st.button("Выход / Logout", type="primary"):
            st.session_state.auth = False
            st.rerun()

# --- ЭКРАН ЛОГИНА ---
if not st.session_state.auth:
    st.markdown(f"<h2 style='text-align: center;'>{L['auth_title']}</h2>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button(L["login_btn"]):
                if check_login(u, p):
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Ошибка входа")
    st.stop()

# --- ОСНОВНОЙ ЭКРАН ---
st.title(f"🛡️ {L['title']}")
tab1, tab2 = st.tabs([L["tab1"], L["tab2"]])
all_ib = get_inbounds()

with tab2:
    with st.container():
        c1, c2 = st.columns(2)
        n_name = c1.text_input(L["name"])
        n_uid = c2.text_input(L["uuid"], value=str(uuid.uuid4()))
        n_sid = c1.text_input(L["subid"], value=str(uuid.uuid4())[:8])
        n_lim = c2.number_input(L["limit"], min_value=0)
        st.write(f"**{L['bind']}**")
        sel_new = {}
        cols = st.columns(3)
        for i, ib in enumerate(all_ib):
            if cols[i%3].checkbox(f"{ib[1]}", key=f"n_{ib[0]}"): sel_new[ib[0]] = True
        if st.button(L["create_btn"]):
            if n_name and sel_new:
                save_user(n_name, n_uid, sel_new, n_lim, n_sid, True)
                st.success(L["restart_msg"]); st.rerun()

with tab1:
    users = get_all_users()
    for name, data in users.items():
        is_active = any(data['inbounds'].values())
        with st.expander(f"{'🟢' if is_active else '🔴'} {name}"):
            first_id = list(data['inbounds'].keys())[0]
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("SELECT settings FROM inbounds WHERE id = ?", (first_id,))
            udata = next((c for c in json.loads(cur.fetchone()[0])['clients'] if c['email'].startswith(name)), {})
            conn.close()

            with st.form(f"e_{name}"):
                m_on = st.toggle(L["active"], value=is_active)
                c1, c2 = st.columns(2)
                e_uuid = c1.text_input(L["uuid"], value=udata.get('id',''))
                e_sid = c2.text_input(L["subid"], value=udata.get('subId',''))
                e_lim = st.number_input(L["limit"], value=int(data['total']/(1024**3)))
                st.write("---")
                upd_ib = {}
                for ib in all_ib:
                    col_c, col_t = st.columns([3, 1])
                    is_s = col_c.checkbox(f"{ib[1]}", value=(ib[0] in data['inbounds']), key=f"c_{name}_{ib[0]}")
                    is_t = col_t.toggle("On", value=data['inbounds'].get(ib[0],0)==1, key=f"t_{name}_{ib[0]}", disabled=not is_s)
                    if is_s: upd_ib[ib[0]] = is_t
                
                b_save, b_del = st.columns(2)
                if b_save.form_submit_button(L["save"]):
                    save_user(name, e_uuid, upd_ib, e_lim, e_sid, m_on); st.rerun()
                if b_del.form_submit_button(L["del"], type="primary"):
                    delete_user(name); st.rerun()
