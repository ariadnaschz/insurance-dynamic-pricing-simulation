import pandas as pd
import numpy as np
from sqlalchemy import text
from db_connection import get_engine

def generate_dimensions(engine):
    """Genera e inserta los catálogos dimensionales en MySQL."""
    print("Generando Dimensiones...")
    
    # 1. Dimensión Clientes
    clientes_data = {
        'rango_edad': np.random.choice(['18-25', '26-39', '40-55', '56+'], 1000, p=[0.2, 0.4, 0.3, 0.1]),
        'genero': np.random.choice(['M', 'F'], 1000),
        'zona_geografica': np.random.choice(['Urbana', 'Suburbana', 'Rural'], 1000, p=[0.6, 0.3, 0.1])
    }
    df_clientes = pd.DataFrame(clientes_data)
    df_clientes.to_sql('dim_clientes', con=engine, if_exists='append', index=False)

    # 2. Dimensión Vehículos
    vehiculos_data = {
        'tipo_vehiculo': np.random.choice(['Sedán', 'SUV', 'Deportivo', 'Motocicleta'], 1000, p=[0.4, 0.3, 0.15, 0.15])
    }
    df_vehiculos = pd.DataFrame(vehiculos_data)
    # Asignar clasificación de riesgo basada en el tipo
    riesgo_map = {'Deportivo': 'Alto', 'Motocicleta': 'Alto', 'Sedán': 'Medio', 'SUV': 'Bajo'}
    df_vehiculos['clasificacion_riesgo'] = df_vehiculos['tipo_vehiculo'].map(riesgo_map)
    df_vehiculos.to_sql('dim_vehiculos', con=engine, if_exists='append', index=False)

    # 3. Dimensión Seguros
    seguros_data = [
        {'categoria': 'Básico', 'cobertura_maxima': 100000.00},
        {'categoria': 'Limitada', 'cobertura_maxima': 300000.00},
        {'categoria': 'Amplia', 'cobertura_maxima': 1000000.00}
    ]
    df_seguros = pd.DataFrame(seguros_data)
    df_seguros.to_sql('dim_tipos_seguro', con=engine, if_exists='append', index=False)

def generate_facts(engine):
    """Extrae los IDs generados e inyecta reglas actuariales para los hechos."""
    print("Extrayendo IDs de dimensiones...")
    
    # Extraer IDs reales generados por MySQL
    df_c = pd.read_sql("SELECT id_cliente, rango_edad, zona_geografica FROM dim_clientes", con=engine)
    df_v = pd.read_sql("SELECT id_vehiculo, tipo_vehiculo FROM dim_vehiculos", con=engine)
    df_s = pd.read_sql("SELECT id_seguro, categoria FROM dim_tipos_seguro", con=engine)

    n_polizas = 5000
    print(f"Generando {n_polizas} pólizas con sesgos de negocio...")
    
    # Asignación aleatoria base
    polizas = pd.DataFrame({
        'id_cliente': np.random.choice(df_c['id_cliente'], n_polizas),
        'id_vehiculo': np.random.choice(df_v['id_vehiculo'], n_polizas),
        'id_seguro': np.random.choice(df_s['id_seguro'], n_polizas)
    })

    # Cruzar con características para inyectar reglas matemáticas
    polizas = polizas.merge(df_c, on='id_cliente').merge(df_v, on='id_vehiculo').merge(df_s, on='id_seguro')

    # Regla 1: Primas Base
    prima_base = {'Básico': 3000, 'Limitada': 5500, 'Amplia': 9000}
    polizas['prima_anual_cobrada'] = polizas['categoria'].map(prima_base) * np.random.uniform(0.9, 1.1, n_polizas)

    # Regla 2: Probabilidad de Siniestro (La trampa de rentabilidad)
    # Base aleatoria pequeña (10% de chocar)
    prob_siniestro = np.full(n_polizas, 0.10)
    
    # EL NICHO TÓXICO: Jóvenes + Deportivos + Urbana -> 80% de probabilidad de choque
    mask_toxico = (polizas['rango_edad'] == '18-25') & (polizas['tipo_vehiculo'] == 'Deportivo') & (polizas['zona_geografica'] == 'Urbana')
    prob_siniestro[mask_toxico] = 0.80
    
    # LA VACA LECHERA: Adultos + SUVs + Suburbana -> 2% de probabilidad
    mask_rentable = (polizas['rango_edad'] == '40-55') & (polizas['tipo_vehiculo'] == 'SUV') & (polizas['zona_geografica'] == 'Suburbana')
    prob_siniestro[mask_rentable] = 0.02

    # Generar si chocaron o no (1 o 0) basado en las probabilidades inyectadas
    chocaron = np.random.binomial(1, prob_siniestro)

    # Regla 3: Costos de Siniestro
    # Si chocaron, el costo del choque depende del tipo de auto. Los deportivos cuestan una fortuna.
    costos_base = np.random.uniform(5000, 25000, n_polizas)
    costos_base[polizas['tipo_vehiculo'] == 'Deportivo'] *= 3.5  # Siniestros inflados para deportivos
    
    polizas['costo_siniestro_pagado'] = chocaron * costos_base

    # Filtrar solo las columnas de la tabla de hechos
    fact_df = polizas[['id_cliente', 'id_vehiculo', 'id_seguro', 'prima_anual_cobrada', 'costo_siniestro_pagado']]
    
    print("Inyectando hechos en MySQL...")
    fact_df.to_sql('fact_polizas', con=engine, if_exists='append', index=False)

if __name__ == "__main__":
    engine = get_engine(include_db=True)
    try:
        with engine.connect() as conn:
            # Limpiar tablas por si corres el script varias veces (respeta las FKs)
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            conn.execute(text("TRUNCATE TABLE fact_polizas;"))
            conn.execute(text("TRUNCATE TABLE dim_clientes;"))
            conn.execute(text("TRUNCATE TABLE dim_vehiculos;"))
            conn.execute(text("TRUNCATE TABLE dim_tipos_seguro;"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            
        generate_dimensions(engine)
        generate_facts(engine)
        print("✅ Simulación y carga completada exitosamente.")
    except Exception as e:
        print(f"❌ Error durante la simulación: {e}")