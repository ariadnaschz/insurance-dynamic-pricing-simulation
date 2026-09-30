/*
===============================================================================
Objetivo de negocio: Análisis Exploratorio de Datos (EDA) en SQL para auditar la integridad de la base simulada de Seguros.
Decisiones técnicas: Se validan registros huérfanos, consistencia categórica y se comprueba matemáticamente la fuga de capital por riesgo demográfico.

INSTRUCCIONES DE DESPLIEGUE:
Ejecutar directamente en MySQL Workbench o mediante el conector de Python.
===============================================================================
*/

USE insurance_pricing_dw;

-- 1. Auditoría de Integridad Referencial (¿Hay pólizas fantasma sin cliente o vehículo?)
SELECT 
    COUNT(*) as total_polizas,
    SUM(CASE WHEN id_cliente IS NULL THEN 1 ELSE 0 END) as clientes_nulos,
    SUM(CASE WHEN id_vehiculo IS NULL THEN 1 ELSE 0 END) as vehiculos_nulos
FROM fact_polizas;

-- 2. Auditoría de Consistencia Categórica (Distribución de la cartera)
-- Verificamos si la generación de datos respetó los porcentajes de edad que programamos
SELECT 
    rango_edad, 
    COUNT(id_cliente) as volumen_clientes,
    ROUND((COUNT(id_cliente) / (SELECT COUNT(*) FROM dim_clientes)) * 100, 2) as porcentaje_cartera
FROM dim_clientes
GROUP BY rango_edad
ORDER BY volumen_clientes DESC;

-- 3. AUDITORÍA FINANCIERA (La Prueba de Fuego del Negocio)
-- Aislamos el margen operativo cruzando la demografía con el tipo de vehículo
SELECT 
    c.rango_edad,
    v.tipo_vehiculo,
    COUNT(f.id_poliza) as volumen_polizas,
    ROUND(SUM(f.prima_anual_cobrada), 2) as ingresos_totales,
    ROUND(SUM(f.costo_siniestro_pagado), 2) as perdidas_siniestros,
    ROUND(SUM(f.margen_operativo), 2) as margen_neto_real
FROM fact_polizas f
JOIN dim_clientes c ON f.id_cliente = c.id_cliente
JOIN dim_vehiculos v ON f.id_vehiculo = v.id_vehiculo
GROUP BY c.rango_edad, v.tipo_vehiculo
ORDER BY margen_neto_real ASC; -- Los peores márgenes (pérdidas) aparecerán arriba