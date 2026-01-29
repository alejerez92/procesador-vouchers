# Herramientas de Procesamiento de Vouchers y Solicitudes

Aplicación web unificada desarrollada en Python con Streamlit para la automatización de auditoría y conciliación de servicios de transporte.

## 🛠 Herramientas Disponibles

### 1. Procesador de Vouchers y Conductores
Automatiza la conciliación y detección de discrepancias entre registros de Reservas y Conductores.

**Reglas de Negocio:**
*   **Cruce de Datos:** Mediante N° de Móvil (detección dinámica de columnas).
*   **Móviles Restringidos:** Servicios realizados por móviles `000`, `100`, `200` y `300` son marcados como discrepancia.
*   **Márgenes (Cálculo Dinámico):** 
    *   Margen mínimo requerido: **10%**.
    *   **Contratos Fijos:** Margen calculado sobre el costo bruto.
    *   **Contratos Variables:** Se descuenta la comisión administrativa antes de validar el margen:
        *   *Variable 23-30%:* Descuento del 23% si costo < 100k, 30% si >= 100k.
        *   *Variable 25-31%:* Descuento del 25% si costo < 100k, 31% si >= 100k.
    *   **Ciudades Exentas:** Punta Cana, Lima, Santo Domingo, Buenos Aires, etc. (Excepto si hay pérdida en contratos Fijos).
*   **Tipo de Cambio (TC):** 
    *   **Grupo 1 (Alto):** Rango **870 - 940** (Punta Cana, Santo Domingo, Río, São Paulo).
    *   **Grupo 2 (Bajo):** Rango **0.5 - 0.9** (Mendoza, Buenos Aires).
    *   *Nota:* Se incluye columna `TC_Calculado_Sistema` en el Excel para auditoría.
*   **Formato Numérico:** Soporte nativo para formato chileno (punto para miles, coma para decimales).
*   **Travel Security:** Si falta CC, es obligatorio que la columna *Naturaleza Gasto* contenga un valor numérico.
*   **Particulares:** Bloqueo de servicios de "PARTICULARES SIN CONVENIO" pagados en "EFECTIVO".
*   **Buenos Aires:** Todo servicio en esta ciudad se marca para revisión.

### 2. Revisión Solicitudes Futuras
Auditoría dinámica de reportes de solicitudes para validar rentabilidad y estados.

**Filtros de Clasificación:**
*   **Paso Directo (Aprobado):** Clientes *Booking* e *I Need Tours*.
*   **Omitidos (No se revisan):** Servicios con estado *Cancelada* o ciudades distintas a *Santiago* y *Valparaíso*.

**Reglas de Auditoría (Para el resto de solicitudes):**
*   **Costo vs Valor:** El *Costo Proveedor* no puede ser mayor al *Valor Km Estimado*.
*   **Rentabilidad por KM:** El valor por kilómetro debe ser **mayor o igual a 1000**.
*   **Rentabilidad por Tiempo:** El valor por minuto debe ser **mayor a 1000**.

## 🚀 Ejecución

### Local
1.  Activar entorno virtual: `source venv/bin/activate`
2.  Ejecutar: `streamlit run app.py`

### Producción (Web)
La aplicación se despliega automáticamente mediante cada commit a la rama `main` en GitHub y está disponible en Streamlit Cloud.

---
*Última actualización: Enero 2026*