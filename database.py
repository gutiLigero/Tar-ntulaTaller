import streamlit as st
import pandas as pd
import bcrypt
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Obtener la conexión a Google Sheets
def get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

def init_db():
    # En Google Sheets, las tablas ya están creadas.
    pass

def registrar_usuario(nombre, email, password, telefono):
    conn = get_conn()
    usuarios_df = conn.read(worksheet="usuarios")
    
    # Verificar si el correo ya existe (ignorando valores nulos si la hoja está vacía)
    if not usuarios_df.empty and email in usuarios_df['email'].values:
        return False

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    nuevo_id = int(usuarios_df['id'].max() + 1) if not usuarios_df.empty and pd.notna(usuarios_df['id'].max()) else 1
    
    nuevo_usuario = pd.DataFrame([{
        "id": nuevo_id,
        "nombre": nombre,
        "email": email,
        "password": hashed,
        "telefono": telefono,
        "rol": "cliente"
    }])
    
    updated_df = pd.concat([usuarios_df, nuevo_usuario], ignore_index=True)
    conn.update(worksheet="usuarios", data=updated_df)
    
    # Limpiar caché para asegurar que la app lea los datos actualizados
    st.cache_data.clear()
    return True

def verificar_login(email, password):
    conn = get_conn()
    usuarios_df = conn.read(worksheet="usuarios")
    
    if usuarios_df.empty:
        return None
        
    # Filtrar el usuario por email
    user_row = usuarios_df[usuarios_df['email'] == email]
    
    if not user_row.empty:
        db_hash = str(user_row.iloc[0]['password'])
        if bcrypt.checkpw(password.encode('utf-8'), db_hash.encode('utf-8')):
            return (int(user_row.iloc[0]['id']), str(user_row.iloc[0]['nombre']), str(user_row.iloc[0]['rol']))
            
    return None

def obtener_catalogo():
    conn = get_conn()
    return conn.read(worksheet="catalogo").dropna(how="all")

def guardar_pedido(user_id, item_solicitado, cantidad, tipo_servicio, observaciones):
    conn = get_conn()
    pedidos_df = conn.read(worksheet="pedidos")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    nuevo_id = int(pedidos_df['id'].max() + 1) if not pedidos_df.empty and pd.notna(pedidos_df['id'].max()) else 1
    
    nuevo_pedido = pd.DataFrame([{
        "id": nuevo_id,
        "user_id": user_id,
        "fecha": fecha,
        "item_solicitado": item_solicitado,
        "cantidad": cantidad,
        "tipo_servicio": tipo_servicio,
        "observaciones": observaciones,
        "estado": "Recibido en taller",
        "link_descarga": ""
    }])
    
    updated_df = pd.concat([pedidos_df, nuevo_pedido], ignore_index=True)
    conn.update(worksheet="pedidos", data=updated_df)
    st.cache_data.clear()

def obtener_pedidos_usuario(user_id):
    conn = get_conn()
    pedidos_df = conn.read(worksheet="pedidos")
    if pedidos_df.empty:
        return pd.DataFrame()
    return pedidos_df[pedidos_df['user_id'] == user_id].sort_values(by='id', ascending=False)

def obtener_todos_pedidos():
    conn = get_conn()
    pedidos_df = conn.read(worksheet="pedidos")
    usuarios_df = conn.read(worksheet="usuarios")
    
    if pedidos_df.empty or usuarios_df.empty:
        return pd.DataFrame()
        
    # Hacer un JOIN entre pedidos y usuarios
    merged_df = pd.merge(pedidos_df, usuarios_df[['id', 'nombre', 'email', 'telefono']], left_on='user_id', right_on='id', suffixes=('', '_user'))
    return merged_df[['id', 'nombre', 'email', 'telefono', 'fecha', 'item_solicitado', 'cantidad', 'tipo_servicio', 'estado', 'link_descarga']].sort_values(by='id', ascending=False)

def actualizar_pedido(pedido_id, nuevo_estado, link_descarga):
    conn = get_conn()
    pedidos_df = conn.read(worksheet="pedidos")
    
    if not pedidos_df.empty:
        # Encontrar la fila del pedido y actualizar
        mask = pedidos_df['id'] == pedido_id
        pedidos_df.loc[mask, 'estado'] = nuevo_estado
        pedidos_df.loc[mask, 'link_descarga'] = link_descarga
        
        conn.update(worksheet="pedidos", data=pedidos_df)
        st.cache_data.clear()
