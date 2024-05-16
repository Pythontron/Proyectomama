import sqlite3

def init_db():
    conn = sqlite3.connect("clientes.db")
    cursor = conn.cursor()
    
    # Crear tabla de vendedores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    ''')

    # Crear tabla de empresas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            razon_social TEXT NOT NULL,
            numero_cliente TEXT NOT NULL,
            RUT TEXT NOT NULL,
            direccion TEXT NOT NULL,
            telefono TEXT NOT NULL,
            FOREIGN KEY (vendedor_id) REFERENCES vendedores (id)
        )
    ''')

    # Crear tabla de facturas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            numero_factura TEXT NOT NULL,
            deuda REAL NOT NULL,
            pagado REAL NOT NULL DEFAULT 0,
            fecha TEXT NOT NULL,
            fecha_pago TEXT,
            FOREIGN KEY (empresa_id) REFERENCES empresas (id)
        )
    ''')

    # Crear tabla de pagos para registrar los cambios en los pagos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            factura_id INTEGER NOT NULL,
            numero_factura TEXT NOT NULL,
            cantidad REAL NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY (factura_id) REFERENCES facturas (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect("clientes.db")
