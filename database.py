import sqlite3
import pandas as pd
import hashlib
from datetime import datetime

def init_db():
    conn = sqlite3.connect("pedidos.db")
    cursor = conn.cursor()
    
    # Tabla de Usuarios
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        email TEXT UNIQUE,
        password TEXT,
        telefono TEXT,
        rol TEXT
    )''')
    
    # Insertar admin
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol='admin'")
    if cursor.fetchone()[0] == 0:
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("INSERT INTO usuarios (nombre, email, password, telefono, rol) VALUES (?, ?, ?, ?, ?)",
                       ("Admin Tarantula", "admin@taller.com", admin_pass, "0000000000", "admin"))

    # Tabla de Catálogo
    cursor.execute('''CREATE TABLE IF NOT EXISTS catalogo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_producto TEXT,
        categoria TEXT,
        precio REAL,
        stock INTEGER
    )''')
    
    # Insertar los 16 rollos exactos de las imágenes
    cursor.execute("SELECT COUNT(*) FROM catalogo")
    if cursor.fetchone()[0] == 0:
        productos = [
            ("Kodak Double X 250 (Rebobinado)", "Película cinematográfica blanco y negro", 40000, 15),
            ("Kodak Gold 200", "Película color con saturación cálida", 60000, 20),
            ("Kodak Portra 400", "Película profesional color con tonos", 100000, 10),
            ("Kentmere 400 (Rebobinado)", "Película blanco y negro económica", 45000, 12),
            ("Kodak Colorplus 200", "Película color de ISO medio", 60000, 25),
            ("Kodak Tri-X 400 120", "Película formato medio blanco y negro", 65000, 8),
            ("Kodak Portra 800 120", "Película formato medio de alta sensi...", 120000, 5),
            ("Kodak Portra 400 120", "Versión formato medio de la películ...", 100000, 5),
            ("Kodak Ultramax 400", "Película color de alta sensibilidad", 65000, 18),
            ("Fujifilm 200", "Película color de ISO medio", 50000, 14),
            ("Kodak Tri-X 400 (Rebobinado)", "Película blanco y negro icónica", 60000, 10),
            ("Kodak Proimage 100", "Película color de bajo ISO", 65000, 10),
            ("Kodak Vision 250D (Rebobinado)", "Película de cine balanceada para luz", 65000, 12),
            ("Ilford FP4+ 125", "Película blanco y negro de grano fin...", 55000, 10),
            ("Kodak Portra 800", "Película color de alta sensibilidad", 120000, 10),
            ("Fujifilm 400", "Película color versátil con tonos", 65000, 15)
        ]
        cursor.executemany("INSERT INTO catalogo (nombre_producto, categoria, precio, stock) VALUES (?, ?, ?, ?)", productos)

    # Tabla de Pedidos / Servicios
    cursor.execute('''CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        fecha TEXT,
        item_solicitado TEXT,
        cantidad INTEGER,
        tipo_servicio TEXT,
        observaciones TEXT,
        estado TEXT,
        link_descarga TEXT,
        FOREIGN KEY(user_id) REFERENCES usuarios(id)
    )''')

    conn.commit()
    conn.close()

def registrar_usuario(nombre, email, password, telefono):
    conn = sqlite3.connect("pedidos.db")
    cursor = conn.cursor()
    try:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO usuarios (nombre, email, password, telefono, rol) VALUES (?, ?, ?, ?, ?)",
                       (nombre, email, hashed, telefono, "cliente"))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verificar_login(email, password):
    conn = sqlite3.connect("pedidos.db")
    cursor = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT id, nombre, rol FROM usuarios WHERE email=? AND password=?", (email, hashed))
    user = cursor.fetchone()
    conn.close()
    return user

def obtener_catalogo():
    conn = sqlite3.connect("pedidos.db")
    df = pd.read_sql_query("SELECT * FROM catalogo", conn)
    conn.close()
    return df

def guardar_pedido(user_id, item_solicitado, cantidad, tipo_servicio, observaciones):
    conn = sqlite3.connect("pedidos.db")
    cursor = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''INSERT INTO pedidos (user_id, fecha, item_solicitado, cantidad, tipo_servicio, observaciones, estado, link_descarga)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (user_id, fecha, item_solicitado, cantidad, tipo_servicio, observaciones, "Recibido en taller", ""))
    conn.commit()
    conn.close()

def obtener_pedidos_usuario(user_id):
    conn = sqlite3.connect("pedidos.db")
    df = pd.read_sql_query(f"SELECT id, fecha, item_solicitado, cantidad, tipo_servicio, estado, link_descarga FROM pedidos WHERE user_id={user_id} ORDER BY id DESC", conn)
    conn.close()
    return df

def obtener_todos_pedidos():
    conn = sqlite3.connect("pedidos.db")
    df = pd.read_sql_query('''SELECT p.id, u.nombre, u.email, u.telefono, p.fecha, p.item_solicitado, p.cantidad, p.tipo_servicio, p.estado, p.link_descarga 
                              FROM pedidos p JOIN usuarios u ON p.user_id = u.id ORDER BY p.id DESC''', conn)
    conn.close()
    return df

def actualizar_pedido(pedido_id, nuevo_estado, link_descarga):
    conn = sqlite3.connect("pedidos.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET estado=?, link_descarga=? WHERE id=?", (nuevo_estado, link_descarga, pedido_id))
    conn.commit()
    conn.close()
