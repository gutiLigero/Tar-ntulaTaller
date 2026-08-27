import streamlit as st
import database
import pandas as pd

# Configuración de página - Estética Tarántula Taller / Safelight (Oscura y minimalista)
st.set_page_config(page_title="Tarántula Taller", page_icon="🕷️", layout="centered")

st.markdown('''
    <style>
    /* Fondo completamente negro como la app de referencia */
    .stApp { background-color: #0b0b0b; color: #ffffff; }
    
    /* Tipografía más limpia */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Ocultar elementos por defecto de Streamlit para más limpieza */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Estilizar los botones primarios (como el botón verde brillante de "Message") */
    .stButton>button { 
        background-color: #1ed760; /* Verde brillante tipo Spotify/Safelight */
        color: #000000; 
        border-radius: 30px; 
        border: none; 
        font-weight: 700;
        padding: 10px 24px;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1abc54;
        color: #000000;
        transform: scale(1.02);
    }
    
    /* Tarjetas de catálogo */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] {
        background-color: #161616;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        align-items: center;
    }
    
    /* Textos secundarios en gris */
    p { color: #a0a0a0; margin-bottom: 0rem; }
    h1, h2, h3 { color: #ffffff; font-weight: 600; }
    
    /* Inputs y formularios oscuros */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #1f1f1f;
        color: white;
        border: 1px solid #333;
        border-radius: 10px;
    }
    
    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { background-color: #0b0b0b; }
    .stTabs [data-baseweb="tab"] { color: #a0a0a0; }
    .stTabs [aria-selected="true"] { color: #ffffff; border-bottom: 2px solid #1ed760; }
    
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
    st.title("🕷️ Tarántula Taller")
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
        st.subheader("🛠️ Panel de Control - Tarántula Taller")
        
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
        tab_cliente1, tab_cliente2, tab_cliente3 = st.tabs(["🛒 Catálogo", "📦 Revelado", "📁 Bóveda"])
        
        with tab_cliente1:
            st.image("https://images.unsplash.com/photo-1549264875-e854ba0d10b7?w=800&q=80", use_column_width=True) # Imagen de banner tipo Safelight
            st.write("Laboratorio de fotografía analógica. Revelado, digitalización y venta de rollos.")
            st.markdown("<br>", unsafe_allow_html=True)
            
            cat_df = database.obtener_catalogo()
            
            for index, row in cat_df.iterrows():
                # Replicando el layout de la captura (Imagen/Círculo gris, texto, botón +)
                c1, c2, c3 = st.columns([1, 4, 1])
                with c1:
                    # Simulación del fondo gris curvo del rollo
                    st.markdown('''
                        <div style="background-color:#d9d9d9; height:60px; width:60px; border-radius:15px; display:flex; align-items:center; justify-content:center;">
                            <span style="color:#000; font-size:24px;">🎞️</span>
                        </div>
                    ''', unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<span style='color:white; font-weight:bold; font-size:16px;'>{row['nombre_producto']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:#a0a0a0; font-size:13px;'>{row['categoria']}<br>$ {row['precio']:,.0f}</span>", unsafe_allow_html=True)
                with c3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("＋", key=f"btn_{row['id']}"):
                        st.success("Añadido")
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center;'>Looking for something else?<br>Message</p>", unsafe_allow_html=True)
            st.button("Message") # Botón verde estilo Spotify/Safelight
                                
        with tab_cliente2:
            st.subheader("Solicitar Revelado")
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
            st.subheader("Tus Negativos Digitales")
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
