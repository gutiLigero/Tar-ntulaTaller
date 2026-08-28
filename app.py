import streamlit as st
import database
import urllib.parse
import pandas as pd

st.set_page_config(page_title="Tarántula - Optics & Design", layout="centered")

# --- CSS SEVERANCE / LUMON INDUSTRIES AESTHETIC ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@400;700&display=swap');

    /* Fondo blanco estéril, texto verde corporativo/negro */
    .stApp { 
        background-color: #F4F5F5; 
        color: #0F171A; 
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers estilo terminal retro */
    h1, h2, h3, h4, .st-emotion-cache-10trnc { 
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important; 
        text-transform: uppercase !important;
        letter-spacing: 0.05em;
        color: #074D39 !important; /* Lumon Green */
        border-bottom: 1px solid #074D39;
        padding-bottom: 5px;
        margin-bottom: 15px;
    }
    
    /* Botones corporativos estrictos */
    .stButton>button { 
        background-color: #074D39 !important; /* Lumon Green */
        color: #ffffff !important; 
        border-radius: 0px !important; 
        border: 2px solid #074D39 !important; 
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em;
        padding: 10px 20px;
        width: 100%;
        transition: all 0.1s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #F4F5F5 !important;
        color: #074D39 !important;
        box-shadow: 4px 4px 0px #074D39;
    }
    
    /* Separadores de productos limpios */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] {
        background-color: #ffffff;
        border: 1px solid #D1D5D8;
        padding: 15px;
        margin-bottom: 10px;
        align-items: center;
        box-shadow: 2px 2px 0px #D1D5D8;
    }
    
    /* Textos secundarios */
    p { color: #2E3B42; margin-bottom: 0rem; font-family: 'Inter', sans-serif; font-size: 15px; }
    
    /* Inputs y formularios estilo terminal */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: #ffffff !important;
        color: #0F171A !important;
        border: 1px solid #074D39 !important;
        border-radius: 0px !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    /* Pestañas (Tabs) estilo departamento */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 2px solid #074D39; }
    .stTabs [data-baseweb="tab"] { 
        color: #7A8B94; 
        font-family: 'IBM Plex Mono', monospace; 
        text-transform: uppercase; 
        font-weight: 600; 
        font-size: 14px;
        letter-spacing: 0.02em;
    }
    .stTabs [aria-selected="true"] { color: #074D39; border-bottom: 4px solid #074D39 !important; background-color: #E8ECEB; }
    
    /* Link de WPP estilo directiva */
    .wpp-btn {
        display: block; width: 100%; text-align: center;
        background-color: #074D39; color: #ffffff !important;
        padding: 12px; text-decoration: none; font-family: 'IBM Plex Mono', monospace;
        font-weight: 600; text-transform: uppercase;
        border: 2px solid #074D39; margin-top: 10px;
        transition: all 0.1s ease-in-out;
    }
    .wpp-btn:hover { background-color: #F4F5F5; color: #074D39 !important; box-shadow: 4px 4px 0px #074D39; }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

database.init_db()

# Memoria de la sesión
if "user_id" not in st.session_state:
  st.session_state["user_id"] = None
  st.session_state["nombre"] = None
  st.session_state["rol"] = None

if "carrito" not in st.session_state:
  st.session_state["carrito"] = {}

def agregar_al_carrito(producto_id, nombre):
  if producto_id in st.session_state["carrito"]:
    st.session_state["carrito"][producto_id]["cantidad"] += 1
  else:
    st.session_state["carrito"][producto_id] = {"nombre": nombre, "cantidad": 1}
  st.toast(f"Item secured: {nombre}", icon="📎")

def vaciar_carrito():
  st.session_state["carrito"] = {}

def logout():
  st.session_state["user_id"] = None
  st.session_state["nombre"] = None
  st.session_state["rol"] = None
  st.rerun()

# --- LOGIN / REGISTRO ---
if not st.session_state["user_id"]:
  st.title("TARÁNTULA CORP.")
  st.write("Optics & Design Division")

  pestanas_auth = st.tabs(["Employee Login", "Onboarding"])

  with pestanas_auth[0]:
    with st.form("login_form"):
      email = st.text_input("Employee Email")
      password = st.text_input("Passcode", type="password")
      if st.form_submit_button("Authenticate"):
        user = database.verificar_login(email, password)
        if user:
          st.session_state["user_id"] = user[0]
          st.session_state["nombre"] = user[1]
          st.session_state["rol"] = user[2]
          st.rerun()
        else:
          st.error("Authentication failed. Please check your credentials.")

  with pestanas_auth[1]:
    with st.form("registro_form"):
      reg_nombre = st.text_input("Full Designation (Name)")
      reg_email = st.text_input("Assigned Email")
      reg_telefono = st.text_input("Contact Ext. (WhatsApp)")
      reg_password = st.text_input("Passcode", type="password")
      if st.form_submit_button("Submit Orientation Form"):
        if reg_nombre and reg_email and reg_password:
          if database.registrar_usuario(reg_nombre, reg_email, reg_password, reg_telefono):
            st.success("Orientation complete. Please log in to begin your shift.")
          else:
            st.error("This designation is already registered.")
        else:
          st.warning("All data fields are mandatory.")

# --- APP PRINCIPAL ---
else:
  col_logo, col_espacio, col_salir = st.columns([3, 1, 1])
  with col_logo:
    st.title("TARÁNTULA CORP.")
  with col_salir:
    st.write("")
    if st.button("Sever Session"):
      logout()

  # ADMIN
  if st.session_state["rol"] == "admin":
    st.subheader("Macrodata Refinement (Admin)")
    tab_admin1, tab_admin2 = st.tabs(["Active Directives", "Asset Inventory"])

    with tab_admin1:
      pedidos_df = database.obtener_todos_pedidos()
      if not pedidos_df.empty:
        st.dataframe(pedidos_df, use_container_width=True)
        st.write("### Update Protocol")
        with st.form("update_form"):
          p_id = st.number_input("Directive ID (Order)", min_value=1, step=1)
          p_est = st.selectbox("Current State", ["Recibido", "En Proceso Químico", "Escaneándose", "Listo (Archivos Subidos)"])
          p_link = st.text_input("Archive Node (Link)")
          if st.form_submit_button("Commit Update"):
            database.actualizar_pedido(p_id, p_est, p_link)
            st.success("Protocol updated successfully.")
            st.rerun()
      else:
        st.info("No active directives at this time.")

    with tab_admin2:
      cat_df = database.obtener_catalogo()
      st.dataframe(cat_df, use_container_width=True)

  # CLIENTE
  else:
    total_items = sum(item["cantidad"] for item in st.session_state["carrito"].values())

    # Renamed Tabs for corporate aesthetic
    tab1, tab2, tab3, tab4 = st.tabs(["Procurement", "Processing", f"Receptacle ({total_items})", "The Archive"])

    # 1. TIENDA (Procurement)
    with tab1:
      st.markdown("### Approved Materials")
      cat_df = database.obtener_catalogo()

      for index, row in cat_df.iterrows():
        c1, c2 = st.columns([3, 1])
        with c1:
          st.markdown(f"<span style='color:#074D39; font-weight:700; font-size:16px; text-transform:uppercase; font-family:\"IBM Plex Mono\", monospace;'>{row['nombre_producto']}</span>", unsafe_allow_html=True)
          st.markdown(f"<span style='color:#7A8B94; font-size:14px; font-family:\"IBM Plex Mono\", monospace;'>$ {row['precio']:,.0f} COP</span>", unsafe_allow_html=True)
        with c2:
          if st.button("Requisition", key=f"btn_add_{row['id']}"):
            agregar_al_carrito(row["id"], row["nombre_producto"])
            st.rerun()

    # 2. REVELADO (Processing)
    with tab2:
      st.markdown("### Chemical Refinement")
      with st.form("form_revelado"):
        tipo = st.selectbox("Refinement Method", ["A color", "Blanco y Negro"])
        qty = st.number_input("Unit Count", min_value=1, value=1)
        obs = st.text_area("Deviations / Notes (Push/Pull)")

        if st.form_submit_button("Submit to Lab"):
          database.guardar_pedido(st.session_state["user_id"], f"Revelado ({tipo})", qty, "Lab Service", obs)
          st.success("Request submitted. Please enjoy all processes equally.")

    # 3. CARRITO (Receptacle)
    with tab3:
      st.markdown("### Order Receptacle")
      if not st.session_state["carrito"]:
        st.info("Your receptacle is currently empty.")
      else:
        total_pagar = 0
        cat_df = database.obtener_catalogo()

        for prod_id, datos in st.session_state["carrito"].items():
          precio_unitario = cat_df.loc[cat_df["id"] == prod_id, "precio"].values[0]
          subtotal = precio_unitario * datos["cantidad"]
          total_pagar += subtotal

          st.write(f"**{datos['cantidad']}x {datos['nombre']}** — $ {subtotal:,.0f} COP")

        st.markdown("<hr style='border-top: 2px solid #074D39;'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: right; color: #074D39;'>TOTAL: $ {total_pagar:,.0f} COP</h3>", unsafe_allow_html=True)

        mensaje_wpp = "Tarántula - Optics & Design Division\nApproved Requisition:\n\n"
        for prod_id, datos in st.session_state["carrito"].items():
          mensaje_wpp += f"▪️ {datos['cantidad']}x {datos['nombre']}\n"
        mensaje_wpp += f"\n*Total Allocation:* $ {total_pagar:,.0f} COP\n\nPlease provide transfer coordinates."
        mensaje_codificado = urllib.parse.quote(mensaje_wpp)

        # REEMPLAZA EL NÚMERO AQUÍ:
        numero_taller = "573000000000"
        link_wpp = f"https://wa.me/{numero_taller}?text={mensaje_codificado}"

        if st.button("Authorize Requisition"):
          for prod_id, datos in st.session_state["carrito"].items():
            database.guardar_pedido(st.session_state["user_id"], datos["nombre"], datos["cantidad"], "Store Purchase", "WhatsApp Order")
          vaciar_carrito()
          st.markdown(f'<meta http-equiv="refresh" content="0; url={link_wpp}">', unsafe_allow_html=True)
          st.success("Requisition authorized. Awaiting fulfillment.")
          st.markdown(f'<a href="{link_wpp}" target="_blank" class="wpp-btn">Open Communication Channel</a>', unsafe_allow_html=True)

    # 4. BÓVEDA (Archive)
    with tab4:
      st.markdown("### The Archive")
      mis_pedidos = database.obtener_pedidos_usuario(st.session_state["user_id"])
      if mis_pedidos.empty:
        st.info("No data nodes available in your archive.")
      else:
        for _, row in mis_pedidos.iterrows():
          with st.expander(f"Directive #{row['id']} - {row['item_solicitado']}"):
            st.write(f"**Current State:** {row['estado']}")
            if row["link_descarga"]:
              st.markdown(f"**[EXTRACT DATA NODE]({row['link_descarga']})**")
            else:
              st.write("Refinement in progress...")
