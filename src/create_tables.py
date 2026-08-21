import os
from sqlalchemy import text
from db_connection import get_engine

def deploy_schema():
    print("Iniciando despliegue de arquitectura...")
    engine = get_engine(include_db=True)
    
    # Ruta del archivo SQL
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(current_dir, '..', 'sql', '01_schema_ddl.sql')
    
    try:
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
            
        # Ejecutar las sentencias DDL
        with engine.connect() as conn:
            for statement in sql_script.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
            conn.commit()
            
        print("Tablas creadas exitosamente en MySQL.")
    except Exception as e:
        print(f"Error durante el despliegue: {e}")

if __name__ == "__main__":
    deploy_schema()