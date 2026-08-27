import streamlit as st
import database
import urllib.parse
import pandas as pd

st.set_page_config(page_title="Tarántula Taller", layout="centered")

# --- CSS MINIMALISTA, BRUTALISTA (Safelight Real) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Arimo:ital,wght@0,400;0,700;1,400;1,700&display=swap');

    /* Fondo blanco puro, texto negro absoluto */
    .stApp { 
        background-color: #ffffff; 
        color: #000000; 
        font-family: 'Arimo', sans-serif;
    }
    
    /* Headers en cursiva, bold y mayúsculas */
    h1, h2, h3, h4, .st-emotion-cache-10trnc { 
        font-family: 'Arimo', sans-serif !important;
        font-weight: 700 !important; 
        font-style: italic !important;
        text-transform: uppercase !important;
        letter-spacing: -0.02em;
        color: #000000 !important;
    }
    
    /* Botones negros 100% cuadrados */
    .stButton>button { 
        background-color: #000000 !important; 
        color: #ffffff !important; 
        border-radius: 0px !important; 
        border: 1px solid #000000 !important; 
        font-family: 'Arimo', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        padding: 12px 20px;
        width: 100%;
        transition: opacity 0.2s ease;
    }
    .stButton>button:hover {
        opacity: 0.8;
    }
    
    /* Separadores de productos limpios */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] {
        background-color: transparent;
        border-top: 1px solid #000000;
        padding: 15px 0px;
        align-items: center;
    }
    
    /* Textos secundarios */
    p { color: #333333; margin-bottom: 0rem; font-family: 'Arimo', sans-serif; font-size: 15px; }
    
    /* Inputs y formularios cuadrados y sin fondos raros */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        border-radius: 0px !important;
        font-family: 'Arimo', sans-serif;
    }
    
    /* Pestañas (Tabs) estilo menú */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 2px solid #000000; }
    .stTabs [data-baseweb="tab"] { color: #888888; font-family: 'Arimo', sans-serif; text-transform: uppercase; font-weight: 700; font-style: italic; font-size: 16px;}
    .stTabs [aria-selected="true"] { color: #000000; border-bottom: 4px solid #000000 !important; }
    
    /* Link de WPP negro y crudo */
    .wpp-btn {
        display: block; width: 100%; text-align: center;
        background-color: #000000; color: #ffffff !important;
        padding: 12px; text-decoration: none; font-family: 'Arimo', sans-serif;
        font-weight: 700; font-style: italic; text-transform: uppercase;
        border: 1px solid #000000; margin-top: 10px;
    }
    .wpp-btn:hover { opacity: 0.8; }

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
  st.toast(f"Añadido: {nombre}", icon="✅")

def vaciar_carrito():
  st.session_state["carrito"] = {}

def logout():
  st.session_state["user_id"] = None
  st.session_state["nombre"] = None
  st.session_state["rol"] = None
  st.rerun()

# --- LOGIN / REGISTRO ---
if not st.session_state["user_id"]:
  st.title("Tarántula Taller")
  st.write("Film Lab & Camera Shop")

  pestanas_auth = st.tabs(["Login", "Register"])

  with pestanas_auth[0]:
    with st.form("login_form"):
      email = st.text_input("Email")
      password = st.text_input("Password", type="password")
      if st.form_submit_button("Sign In"):
        user = database.verificar_login(email, password)
        if user:
          st.session_state["user_id"] = user[0]
          st.session_state["nombre"] = user[1]
          st.session_state["rol"] = user[2]
          st.rerun()
        else:
          st.error("Credenciales incorrectas")

  with pestanas_auth[1]:
    with st.form("registro_form"):
      reg_nombre = st.text_input("Full Name")
      reg_email = st.text_input("Email")
      reg_telefono = st.text_input("Phone / WhatsApp")
      reg_password = st.text_input("Password", type="password")
      if st.form_submit_button("Create Account"):
        if reg_nombre and reg_email and reg_password:
          if database.registrar_usuario(reg_nombre, reg_email, reg_password, reg_telefono):
            st.success("Account created. Please log in.")
          else:
            st.error("Email is already registered.")
        else:
          st.warning("Please fill all fields.")

# --- APP PRINCIPAL ---
else:
  col_logo, col_espacio, col_salir = st.columns([3, 1, 1])
  with col_logo:
    st.title("TARÁNTULA")
  with col_salir:
    st.write("")
    if st.button("Logout"):
      logout()

  # ADMIN
  if st.session_state["rol"] == "admin":
    st.subheader("Lab Control Panel")
    tab_admin1, tab_admin2 = st.tabs(["Orders", "Inventory"])

    with tab_admin1:
      pedidos_df = database.obtener_todos_pedidos()
      if not pedidos_df.empty:
        st.dataframe(pedidos_df, use_container_width=True)
        st.write("### Update Order & Upload Files")
        with st.form("update_form"):
          p_id = st.number_input("Order ID", min_value=1, step=1)
          p_est = st.selectbox("Status", ["Recibido", "En Proceso Químico", "Escaneándose", "Listo (Archivos Subidos)"])
          p_link = st.text_input("Download Link (Drive/Wetransfer)")
          if st.form_submit_button("Update Status"):
            database.actualizar_pedido(p_id, p_est, p_link)
            st.success("Order updated.")
            st.rerun()
      else:
        st.info("No active orders.")

    with tab_admin2:
      cat_df = database.obtener_catalogo()
      st.dataframe(cat_df, use_container_width=True)

  # CLIENTE
  else:
    total_items = sum(item["cantidad"] for item in st.session_state["carrito"].values())

    tab1, tab2, tab3, tab4 = st.tabs(["Shop", "Lab", f"Cart ({total_items})", "Vault"])

    # 1. TIENDA
    with tab1:
      st.markdown("### Films")
      st.markdown("<br>", unsafe_allow_html=True)
      cat_df = database.obtener_catalogo()

      for index, row in cat_df.iterrows():
        c1, c2 = st.columns([3, 1])
        with c1:
          st.markdown(f"<span style='color:#000; font-weight:700; font-size:18px; text-transform:uppercase;'>{row['nombre_producto']}</span>", unsafe_allow_html=True)
          st.markdown(f"<span style='color:#333; font-size:14px;'>$ {row['precio']:,.0f} COP</span>", unsafe_allow_html=True)
        with c2:
          if st.button("Add to cart", key=f"btn_add_{row['id']}"):
            agregar_al_carrito(row["id"], row["nombre_producto"])
            st.rerun()

    # 2. REVELADO
    with tab2:
      st.markdown("### Develop Your Film")
      with st.form("form_revelado"):
        tipo = st.selectbox("Process", ["A color", "Blanco y Negro"])
        qty = st.number_input("Quantity", min_value=1, value=1)
        obs = st.text_area("Notes (Push/Pull, etc.)")

        if st.form_submit_button("Submit Lab Order"):
          database.guardar_pedido(st.session_state["user_id"], f"Revelado ({tipo})", qty, "Lab Service", obs)
          st.success("Order submitted. Check your Vault.")

    # 3. CARRITO
    with tab3:
      st.markdown("### Checkout")
      if not st.session_state["carrito"]:
        st.info("Your cart is empty.")
      else:
        total_pagar = 0
        cat_df = database.obtener_catalogo()

        for prod_id, datos in st.session_state["carrito"].items():
          precio_unitario = cat_df.loc[cat_df["id"] == prod_id, "precio"].values[0]
          subtotal = precio_unitario * datos["cantidad"]
          total_pagar += subtotal

          st.write(f"**{datos['cantidad']}x {datos['nombre']}** — $ {subtotal:,.0f} COP")

        st.markdown("<hr style='border-top: 2px solid #000;'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: right;'>TOTAL: $ {total_pagar:,.0f} COP</h3>", unsafe_allow_html=True)

        mensaje_wpp = "¡Hola Tarántula Taller! 🕷️\nConfirmación de pedido:\n\n"
        for prod_id, datos in st.session_state["carrito"].items():
          mensaje_wpp += f"▪️ {datos['cantidad']}x {datos['nombre']}\n"
        mensaje_wpp += f"\n*Total:* $ {total_pagar:,.0f} COP\n\n¿A qué cuenta transfiero?"
        mensaje_codificado = urllib.parse.quote(mensaje_wpp)

        # REEMPLAZA EL NÚMERO AQUÍ:
        numero_taller = "573000000000"
        link_wpp = f"https://wa.me/{numero_taller}?text={mensaje_codificado}"

        if st.button("Complete Order"):
          for prod_id, datos in st.session_state["carrito"].items():
            database.guardar_pedido(st.session_state["user_id"], datos["nombre"], datos["cantidad"], "Store Purchase", "WhatsApp Order")
          vaciar_carrito()
          st.markdown(f'<meta http-equiv="refresh" content="0; url={link_wpp}">', unsafe_allow_html=True)
          st.success("Order generated!")
          st.markdown(f'<a href="{link_wpp}" target="_blank" class="wpp-btn">Proceed to WhatsApp</a>', unsafe_allow_html=True)

    # 4. BÓVEDA
    with tab4:
      st.markdown("### Digital Vault")
      mis_pedidos = database.obtener_pedidos_usuario(st.session_state["user_id"])
      if mis_pedidos.empty:
        st.info("No files in vault yet.")
      else:
        for _, row in mis_pedidos.iterrows():
          with st.expander(f"Order #{row['id']} - {row['item_solicitado']}"):
            st.write(f"**Status:** {row['estado']}")
            if row["link_descarga"]:
              st.markdown(f"**[DOWNLOAD SCANS]({row['link_descarga']})**")
            else:
              st.write("Processing...")
