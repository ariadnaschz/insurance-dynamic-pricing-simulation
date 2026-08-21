USE insurance_pricing_dw;

CREATE TABLE IF NOT EXISTS dim_clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    rango_edad VARCHAR(20),
    genero VARCHAR(20),
    zona_geografica VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS dim_vehiculos (
    id_vehiculo INT AUTO_INCREMENT PRIMARY KEY,
    tipo_vehiculo VARCHAR(50),  -- Deportivo, Familiar, Sedán
    clasificacion_riesgo VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS dim_tipos_seguro (
    id_seguro INT AUTO_INCREMENT PRIMARY KEY,
    categoria VARCHAR(50), -- Básico, Amplio, Premium
    cobertura_maxima DECIMAL(15,2)
);

CREATE TABLE IF NOT EXISTS fact_polizas (
    id_poliza INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT,
    id_vehiculo INT,
    id_seguro INT,
    prima_anual_cobrada DECIMAL(10,2),
    costo_siniestro_pagado DECIMAL(10,2) DEFAULT 0.00,
    margen_operativo DECIMAL(10,2) GENERATED ALWAYS AS (prima_anual_cobrada - costo_siniestro_pagado) STORED,
    FOREIGN KEY (id_cliente) REFERENCES dim_clientes(id_cliente),
    FOREIGN KEY (id_vehiculo) REFERENCES dim_vehiculos(id_vehiculo),
    FOREIGN KEY (id_seguro) REFERENCES dim_tipos_seguro(id_seguro)
);