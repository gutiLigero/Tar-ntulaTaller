import streamlit as st
import database
import pandas as pd

# Configuración de página - Estética Tarántula Taller (Basado en Safelight Berlin)
st.set_page_config(page_title="Tarántula Taller", page_icon="🕷️", layout="centered")

st.markdown('''
    <style>
    /* 1. Importar la fuente exacta que usa Safelight Berlin (Arimo) */
    @import url('https://fonts.googleapis.com/css2?family=Arimo:ital,wght@0,400;0,700;1,700&display=swap');

    /* 2. Fondo con el gradiente oscuro exacto de su código y fuente base */
    .stApp { 
        background-image: linear-gradient(100deg, #000000 40%, #212121 63%, #000000 79%);
        color: #ffffff; 
        font-family: 'Arimo', sans-serif;
        font-size: 20px;
    }
    
    /* 3. Títulos en cursiva, mayúsculas y negrita (Igual a Safelight) */
    h1, h2, h3, .st-emotion-cache-10trnc { 
        font-family: 'Arimo', sans-serif !important;
        font-weight: 700 !important; 
        font-style: italic !important;
        text-transform: uppercase !important;
        letter-spacing: -0.025em;
        color: #ffffff !important;
    }
    
    /* Ocultar elementos por defecto de Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 4. Botones completamente CUADRADOS, en blanco y negro, estilo industrial */
    .stButton>button { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        border-radius: 0px !important; /* Bordes rectos */
        border: none; 
        font-family: 'Arimo', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em;
        padding: 12px 24px;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #cccccc !important;
        transform: scale(1.01);
    }
    
    /* Tarjetas de catálogo más crudas */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] {
        background-color: transparent;
        border: 1px solid #333333;
        padding: 15px;
        border-radius: 0px;
        margin-bottom: 10px;
        align-items: center;
    }
    
    /* Textos secundarios */
    p { color: #d0d0d0; margin-bottom: 0rem; font-family: 'Arimo', sans-serif; }
    
    /* Inputs y formularios cuadrados */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: transparent !important;
        color: white !important;
        border: 1px solid #555 !important;
        border-radius: 0px !important;
        font-family: 'Arimo', sans-serif;
    }
    
    /* Estilos para los expanders (Bóveda) */
    [data-testid="stExpander"] {
        background-color: transparent;
        border: 1px solid #555;
        border-radius: 0px;
    }
    [data-testid="stExpander"] summary { color: #ffffff; font-weight: 700; font-style: italic; text-transform: uppercase; }
    
    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #888888; font-family: 'Arimo', sans-serif; text-transform: uppercase; font-weight: 700; font-style: italic; }
    .stTabs [aria-selected="true"] { color: #ffffff; border-bottom: 3px solid #ffffff !important; }
    
    </style>
''', unsafe_allow_html=True)

database.init_db()

if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'nombre' not in st.session_state:
    st.session_state['nombre'] = None
if 'rol' not in st.session_state:
    st.session_state['rol'] = None

def logout():
    st.session_state['user_id'] = None
    st.session_state['nombre'] = None
    st.session_state['rol'] = None
    st.rerun()

# ----------------- PANTALLA DE LOGIN / REGISTRO -----------------
if not st.session_state['user_id']:
    st.title("Tarántula Taller")
    st.write("Laboratorio de fotografía analógica. Revelado, digitalización y venta de rollos.")
    
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

# ----------------- APLICACIÓN PRINCIPAL -----------------
else:
    col_header1, col_header2 = st.columns([4, 1])
    with col_header1:
        st.title("Catalog")
    with col_header2:
        if st.button("Salir"):
            logout()

    # ---- VISTA DE ADMINISTRADOR ----
    if st.session_state['rol'] == 'admin':
        st.subheader("Panel de Control - Tarántula Taller")
        
        tab_admin1, tab_admin2 = st.tabs(["Órdenes y Bóveda", "Inventario"])
        
        with tab_admin1:
            pedidos_df = database.obtener_todos_pedidos()
            st.dataframe(pedidos_df, use_container_width=True)
            
            st.markdown("---")
            st.write("Actualizar Estado y Link de Descarga")
            with st.form("update_form"):
                p_id = st.number_input("ID Pedido", min_value=1, step=1)
                p_est = st.selectbox("Estado", ["Recibido en taller", "En Proceso Químico", "Escaneándose", "Listo (Archivos Subidos)"])
                p_link = st.text_input("Enlace de Descarga (Drive/S3)")
                if st.form_submit_button("Actualizar y Notificar"):
                    database.actualizar_pedido(p_id, p_est, p_link)
                    st.success(f"Pedido #{p_id} actualizado.")
                    st.rerun()

        with tab_admin2:
            cat_df = database.obtener_catalogo()
            st.dataframe(cat_df, use_container_width=True)

    # ---- VISTA DE CLIENTE ----
    else:
        tab_cliente1, tab_cliente2, tab_cliente3 = st.tabs(["Catálogo", "Revelado", "Bóveda"])
        
        with tab_cliente1:
            # Solución al error TypeError usando HTML directo y eliminando bordes redondeados
            st.markdown('<img src="https://images.unsplash.com/photo-1549264875-e854ba0d10b7?w=800&q=80" style="width: 100%; margin-bottom: 15px; border-radius: 0px;" alt="Banner">', unsafe_allow_html=True)
            st.write("Laboratorio de fotografía analógica. Revelado, digitalización y venta de rollos.")
            st.markdown("<br>", unsafe_allow_html=True)
            
            cat_df = database.obtener_catalogo()
            
            for index, row in cat_df.iterrows():
                c1, c2, c3 = st.columns([1, 4, 1])
                with c1:
                    # Cuadro crudo en lugar de burbuja redondeada
                    st.markdown('''
                        <div style="background-color:#222; height:60px; width:60px; border-radius:0px; border: 1px solid #444; display:flex; align-items:center; justify-content:center;">
                            <span style="color:#000; font-size:24px;">🎞️</span>
                        </div>
                    ''', unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<span style='color:white; font-family: Arimo, sans-serif; font-weight:bold; font-size:16px; text-transform:uppercase;'>{row['nombre_producto']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:#a0a0a0; font-family: Arimo, sans-serif; font-size:14px;'>{row['categoria']}<br>$ {row['precio']:,.0f}</span>", unsafe_allow_html=True)
                with c3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("＋", key=f"btn_{row['id']}"):
                        st.success("Añadido")
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center;'>Looking for something else?<br>Message</p>", unsafe_allow_html=True)
            st.button("Message")
                                
        with tab_cliente2:
            st.markdown("### Solicitar Revelado")
            with st.form("solicitar_revelado"):
                cat = database.obtener_catalogo()
                opciones_rollos = cat['nombre_producto'].tolist()
                
                item_seleccionado = st.selectbox("¿Qué rollo nos envías?", opciones_rollos)
                cantidad = st.number_input("Cantidad", min_value=1, value=1)
                
                tipo_servicio = st.selectbox("Proceso", [
                    "Revelado C-41 + Escaneo",
                    "Revelado B/N + Escaneo",
                    "Solo Revelado Químico"
                ])
                obs = st.text_area("Instrucciones")
                
                if st.form_submit_button("Agendar Revelado"):
                    database.guardar_pedido(st.session_state['user_id'], item_seleccionado, cantidad, tipo_servicio, obs)
                    st.success("¡Solicitud enviada a Tarántula Taller!")
                    
        with tab_cliente3:
            st.markdown("### Tus Negativos Digitales")
            mis_pedidos = database.obtener_pedidos_usuario(st.session_state['user_id'])
            if mis_pedidos.empty:
                st.info("Aún no tienes rollos en la bóveda.")
            else:
                for _, row in mis_pedidos.iterrows():
                    with st.expander(f"Orden #{row['id']} - {row['item_solicitado']}"):
                        st.write(f"**Estado:** {row['estado']}")
                        if row['link_descarga']:
                            st.markdown(f"[📥 Descargar Archivos (Alta Resolución)]({row['link_descarga']})")
                        else:
                            st.warning("Archivos aún no disponibles.")
