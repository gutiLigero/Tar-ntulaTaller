import streamlit as st
import database
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Safelight / Tarántula", page_icon="🎞️", layout="centered")

# --- 1. CSS ESTILO SAFELIGHT BERLIN (Blanco, limpio, tipografía Arimo) ---
st.markdown('''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Arimo:ital,wght@0,400;0,700;1,400;1,700&display=swap');

    /* Fondo blanco, texto negro */
    .stApp { 
        background-color: #ffffff; 
        color: #000000; 
        font-family: 'Arimo', sans-serif;
    }
    
    /* Títulos en cursiva, mayúsculas y negrita */
    h1, h2, h3, h4, .st-emotion-cache-10trnc { 
        font-family: 'Arimo', sans-serif !important;
        font-weight: 700 !important; 
        font-style: italic !important;
        text-transform: uppercase !important;
        letter-spacing: -0.025em;
        color: #000000 !important;
    }
    
    /* Botones negros, rectos y minimalistas */
    .stButton>button { 
        background-color: #000000 !important; 
        color: #ffffff !important; 
        border-radius: 0px !important; 
        border: 1px solid #000000 !important; 
        font-family: 'Arimo', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        padding: 10px 20px;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Separadores de productos limpios */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] {
        background-color: transparent;
        border-bottom: 1px solid #eeeeee;
        padding: 15px 0px;
        align-items: center;
    }
    
    /* Textos secundarios */
    p { color: #555555; margin-bottom: 0rem; font-family: 'Arimo', sans-serif; }
    
    /* Inputs y formularios */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: #f9f9f9 !important;
        color: #000 !important;
        border: 1px solid #ddd !important;
        border-radius: 0px !important;
        font-family: 'Arimo', sans-serif;
    }
    
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #ddd; }
    .stTabs [data-baseweb="tab"] { color: #888; font-family: 'Arimo', sans-serif; text-transform: uppercase; font-weight: 700; font-style: italic; }
    .stTabs [aria-selected="true"] { color: #000; border-bottom: 3px solid #000 !important; }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
''', unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN Y FUNCIONES DEL CARRITO ---
database.init_db()

# Memoria de sesión para usuarios y carrito
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
    st.session_state['nombre'] = None
    st.session_state['rol'] = None

# Memoria REAL para el carrito de compras {id_producto: cantidad}
if 'carrito' not in st.session_state:
    st.session_state['carrito'] = {}

def agregar_al_carrito(producto_id, nombre):
    if producto_id in st.session_state['carrito']:
        st.session_state['carrito'][producto_id]['cantidad'] += 1
    else:
        st.session_state['carrito'][producto_id] = {'nombre': nombre, 'cantidad': 1}
    st.toast(f"Añadido: {nombre}", icon="✅")

def vaciar_carrito():
    st.session_state['carrito'] = {}

def logout():
    st.session_state['user_id'] = None
    st.session_state['nombre'] = None
    st.session_state['rol'] = None
    st.rerun()

# --- 3. PANTALLA DE LOGIN ---
if not st.session_state['user_id']:
    st.title("Tarántula Taller")
    st.write("Laboratorio de fotografía analógica. Revelado, digitalización y venta.")
    
    pestanas_auth = st.tabs(["Iniciar Sesión", "Crear Cuenta"])
    
    with pestanas_auth[0]:
        with st.form("login_form"):
            email = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Entrar"):
                user = database.verificar_login(email, password)
                if user:
                    st.session_state['user_id'] = user[0]
                    st.session_state['nombre'] = user[1]
                    st.session_state['rol'] = user[2]
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
                    
    with pestanas_auth[1]:
        with st.form("registro_form"):
            reg_nombre = st.text_input("Nombre completo")
            reg_email = st.text_input("Correo electrónico")
            reg_telefono = st.text_input("Teléfono / WhatsApp")
            reg_password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Registrarse"):
                if reg_nombre and reg_email and reg_password:
                    if database.registrar_usuario(reg_nombre, reg_email, reg_password, reg_telefono):
                        st.success("¡Cuenta creada! Ya puedes iniciar sesión.")
                    else:
                        st.error("Ese correo ya está registrado.")
                else:
                    st.warning("Completa todos los campos.")

# --- 4. APLICACIÓN PRINCIPAL ---
else:
    # Encabezado principal
    col_logo, col_espacio, col_salir = st.columns([3, 1, 1])
    with col_logo:
        st.title("Tarántula Shop")
    with col_salir:
        st.write("")
        if st.button("Salir"):
            logout()

    # ---- VISTA DE ADMINISTRADOR ----
    if st.session_state['rol'] == 'admin':
        st.subheader("Panel de Control (Admin)")
        pedidos_df = database.obtener_todos_pedidos()
        st.dataframe(pedidos_df, use_container_width=True)

    # ---- VISTA DE CLIENTE ----
    else:
        # Calcular total de items en el carrito para mostrar en la pestaña
        total_items = sum(item['cantidad'] for item in st.session_state['carrito'].values())
        
        tab1, tab2, tab3, tab4 = st.tabs(["Tienda", "Revelado", f"Mi Carrito ({total_items})", "Bóveda"])
        
        # PESTAÑA 1: CATÁLOGO DE ROLLOS
        with tab1:
            st.markdown('<img src="https://images.unsplash.com/photo-1549264875-e854ba0d10b7?w=800&q=80" style="width: 100%; margin-bottom: 20px;" alt="Banner">', unsafe_allow_html=True)
            st.markdown("### Films")
            st.markdown("<p style='font-style: italic;'>Our most popular</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            cat_df = database.obtener_catalogo()
            
            for index, row in cat_df.iterrows():
                c1, c2, c3 = st.columns([1, 3, 1])
                with c1:
                    # Imagen simulada con fondo gris claro
                    st.markdown('''
                        <div style="background-color:#f4f4f4; height:70px; width:70px; display:flex; align-items:center; justify-content:center;">
                            <span style="color:#000; font-size:24px;">🎞️</span>
                        </div>
                    ''', unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<span style='color:#000; font-weight:bold; font-size:16px;'>{row['nombre_producto']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:#666; font-size:14px;'>€ {row['precio']:,.0f}</span>", unsafe_allow_html=True)
                with c3:
                    st.write("")
                    # Al hacer clic, se llama a la función agregar_al_carrito
                    if st.button("Add", key=f"btn_add_{row['id']}"):
                        agregar_al_carrito(row['id'], row['nombre_producto'])
                        st.rerun() # Recarga para actualizar el contador de pestañas
        
        # PESTAÑA 2: SERVICIO DE REVELADO
        with tab2:
            st.markdown("### Develop Your Film")
            with st.form("form_revelado"):
                st.write("Completa los datos para traer tus rollos al laboratorio.")
                tipo = st.selectbox("Proceso", ["Color C-41", "Blanco y Negro", "E-6"])
                qty = st.number_input("Cantidad de rollos", min_value=1)
                obs = st.text_area("Notas / Forzado")
                
                if st.form_submit_button("Agendar Revelado"):
                    database.guardar_pedido(st.session_state['user_id'], tipo, qty, "Revelado en Lab", obs)
                    st.success("¡Tu solicitud de revelado fue enviada!")
        
        # PESTAÑA 3: EL CARRITO DE COMPRAS (FUNCIONAL)
        with tab3:
            st.markdown("### Tu Orden")
            if not st.session_state['carrito']:
                st.info("Tu carrito está vacío. Ve a la Tienda para añadir rollos.")
            else:
                total_pagar = 0
                cat_df = database.obtener_catalogo()
                
                for prod_id, datos in st.session_state['carrito'].items():
                    # Buscar el precio en la base de datos
                    precio_unitario = cat_df.loc[cat_df['id'] == prod_id, 'precio'].values[0]
                    subtotal = precio_unitario * datos['cantidad']
                    total_pagar += subtotal
                    
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.write(f"**{datos['nombre']}**")
                    with c2:
                        st.write(f"x{datos['cantidad']}")
                    with c3:
                        st.write(f"€ {subtotal:,.0f}")
                
                st.markdown("---")
                st.markdown(f"<h3 style='text-align: right;'>Total: € {total_pagar:,.0f}</h3>", unsafe_allow_html=True)
                
                if st.button("Proceder al Pago / Checkout"):
                    # Aquí generarías el pedido en la BD con los items del carrito
                    st.success("¡Pedido procesado con éxito!")
                    vaciar_carrito()
                    st.rerun()

        # PESTAÑA 4: LA BÓVEDA DIGITAL
        with tab4:
            st.markdown("### Negativos Digitales")
            mis_pedidos = database.obtener_pedidos_usuario(st.session_state['user_id'])
            if mis_pedidos.empty:
                st.info("Aún no tienes archivos en la bóveda.")
            else:
                for _, row in mis_pedidos.iterrows():
                    with st.expander(f"Orden #{row['id']} - {row['item_solicitado']}"):
                        st.write(f"**Estado:** {row['estado']}")
                        if row['link_descarga']:
                            st.markdown(f"[📥 Descargar Archivos (Alta Resolución)]({row['link_descarga']})")
                        else:
                            st.warning("Archivos en proceso.")
