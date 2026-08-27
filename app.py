import streamlit as st
import database

# Configuración de página - Estética TTT / Analógica
st.set_page_config(page_title="Tres Tristes Tigres | Lab", page_icon="🎞️", layout="wide")

st.markdown('''
    <style>
    .main { background-color: #0d0d0d; color: #f5f5f5; }
    .stButton>button { border: 1px solid #4CAF50; border-radius: 5px; }
    h1, h2, h3 { color: #e0e0e0; font-family: monospace; }
    </style>
''', unsafe_allow_html=True)

# Inicializar DB
database.init_db()

# Variables de sesión para Login
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
    st.title("🎞️ Tres Tristes Tigres | Film Lab")
    st.write("Bóveda digital de negativos y laboratorio de revelado.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔑 Iniciar Sesión")
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
                    
    with col2:
        st.subheader("📝 Crear Cuenta")
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
    st.sidebar.title(f"Hola, {st.session_state['nombre']}")
    st.sidebar.caption(f"Cuenta: {st.session_state['rol'].capitalize()}")
    if st.sidebar.button("Cerrar Sesión"):
        logout()

    # ---- VISTA DE ADMINISTRADOR (EL LABORATORIO) ----
    if st.session_state['rol'] == 'admin':
        st.title("🛠️ Panel de Control del Laboratorio")
        st.write("Administración de órdenes, stock y subida de archivos a la bóveda de clientes.")
        
        tab_admin1, tab_admin2 = st.tabs(["📦 Gestión de Pedidos y Escaneos", "🛒 Inventario de Rollos"])
        
        with tab_admin1:
            pedidos_df = database.obtener_todos_pedidos()
            st.dataframe(pedidos_df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("Actualizar Estado y Subir Archivos")
            st.info("Pega aquí el enlace de Google Drive, AWS o Supabase Storage donde subiste los 1GB de escaneos.")
            
            with st.form("update_form"):
                col_id, col_est, col_link = st.columns([1, 2, 3])
                with col_id:
                    p_id = st.number_input("ID Pedido", min_value=1, step=1)
                with col_est:
                    p_est = st.selectbox("Estado", ["Recibido en taller", "En Proceso Químico", "Escaneándose", "Listo (Archivos Subidos)"])
                with col_link:
                    p_link = st.text_input("Enlace de Descarga de Escaneos (TIFF/JPG)")
                    
                if st.form_submit_button("Actualizar y Notificar al Cliente"):
                    database.actualizar_pedido(p_id, p_est, p_link)
                    st.success(f"Pedido #{p_id} actualizado. El cliente ya puede ver su enlace.")
                    st.rerun()

        with tab_admin2:
            st.write("Aquí iría el módulo para actualizar precios y cantidad de rollos en stock (Próxima actualización).")
            cat_df = database.obtener_catalogo()
            st.dataframe(cat_df, use_container_width=True)

    # ---- VISTA DE CLIENTE ----
    else:
        st.title("🎞️ Tres Tristes Tigres | Bóveda & Lab")
        tab_cliente1, tab_cliente2, tab_cliente3 = st.tabs(["📁 Mis Rollos (Bóveda)", "📦 Enviar a Revelar", "🛒 Catálogo de Películas"])
        
        with tab_cliente1:
            st.subheader("Bóveda Digital Permanente")
            st.write("Tus negativos escaneados en alta resolución se almacenarán aquí.")
            
            mis_pedidos = database.obtener_pedidos_usuario(st.session_state['user_id'])
            if mis_pedidos.empty:
                st.info("Aún no tienes pedidos de revelado con nosotros.")
            else:
                for _, row in mis_pedidos.iterrows():
                    with st.expander(f"Orden #{row['id']} - {row['item_solicitado']} ({row['fecha']})"):
                        st.write(f"**Estado:** {row['estado']}")
                        st.write(f"**Servicio:** {row['tipo_servicio']}")
                        
                        if row['link_descarga'] and row['link_descarga'].strip() != "":
                            st.success("🎉 ¡Tus fotos están listas para descargar!")
                            st.markdown(f"[📥 Descargar Archivos (Alta Resolución)]({row['link_descarga']})")
                        else:
                            st.warning("Archivos aún no disponibles. Tus rollos están en el laboratorio.")
                            
        with tab_cliente2:
            st.subheader("Solicitar Revelado")
            with st.form("solicitar_revelado"):
                cat = database.obtener_catalogo()
                opciones_rollos = cat['nombre_producto'].tolist()
                
                item_seleccionado = st.selectbox("¿Qué rollo nos envías?", opciones_rollos)
                cantidad = st.number_input("Cantidad de rollos iguales", min_value=1, value=1)
                
                tipo_servicio = st.selectbox("Proceso", [
                    "Revelado C-41 + Escaneo Alta Res (Bóveda Nube)",
                    "Revelado B/N + Escaneo Alta Res (Bóveda Nube)",
                    "Revelado E-6 + Escaneo",
                    "Solo Revelado Químico"
                ])
                
                obs = st.text_area("Instrucciones (Ej. Forzar a ASA 800, Devolver negativos por mensajería)")
                
                if st.form_submit_button("Agendar Revelado"):
                    database.guardar_pedido(st.session_state['user_id'], item_seleccionado, cantidad, tipo_servicio, obs)
                    st.success("¡Solicitud enviada al laboratorio! Tráenos tus rollos o envíalos.")
                    
        with tab_cliente3:
            st.subheader("Stock Disponible")
            cat_df = database.obtener_catalogo()
            
            # Mostrar como catálogo visual
            for index, row in cat_df.iterrows():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**{row['nombre_producto']}** | {row['categoria']}")
                with c2:
                    st.write(f"${row['precio']:,.0f} COP")
                st.divider()
