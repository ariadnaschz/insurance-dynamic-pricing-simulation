import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno desde el archivo .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "insurance_pricing_dw")

def get_engine(include_db=True):
    """Crea un motor de conexión SQLAlchemy para MySQL."""
    base_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    url = f"{base_url}/{DB_NAME}" if include_db else base_url
    return create_engine(url)

def initialize_database():
    """Verifica la conexión al servidor y crea la base de datos si no existe."""
    try:
        # 1. Conexión al servidor sin especificar BD
        server_engine = get_engine(include_db=False)
        with server_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};"))
            print(f" Base de datos '{DB_NAME}' verificada/creada exitosamente.")

        # 2. Conexión directa a la BD del proyecto
        db_engine = get_engine(include_db=True)
        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION();")).fetchone()
            print(f" Conexión establecida con MySQL Server. Versión: {result[0]}")
            
        return db_engine

    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

if __name__ == "__main__":
    print("Probando conexión con el servidor MySQL...")
    initialize_database()