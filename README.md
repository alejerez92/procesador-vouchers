# Herramientas de Procesamiento de Vouchers y Solicitudes

Aplicación web unificada desarrollada en Python con Streamlit para la automatización de auditoría y conciliación de servicios de transporte.

## 🛠 Herramientas Disponibles

### 1. Procesador de Vouchers y Conductores
Automatiza la conciliación y detección de discrepancias entre registros de Reservas y Conductores.

**Reglas de Negocio:**
*   **Cruce de Datos:** Mediante N° de Móvil (detección dinámica de columnas).
*   **Móviles Restringidos:** Servicios realizados por móviles `000`, `100`, `200` y `300` son marcados como discrepancia.
*   **Centros de Costo (CC):** 
    *   Obligatorio para convenios: *Godrej, Unilever, Pacific Hydro, Parque Arauco, Patio, Rays, Multi Export*.
    *   No puede ser "SIN", "SIN INFORMACION" o "PENDIENTE".
*   **Márgenes (Contrato Fijo):** Margen mínimo del 10% (excepto en ciudades exentas como Punta Cana, Lima, etc.).
*   **Tipo de Cambio (TC):** Validaciones específicas por grupos de ciudades (920-980 para Grupo 1, 0.5-0.9 para Grupo 2).
*   **Travel Security:** Si falta CC, es obligatorio que la columna *Naturaleza Gasto* contenga un valor numérico.
*   **Particulares:** Bloqueo de servicios de "PARTICULARES SIN CONVENIO" pagados en "EFECTIVO".
*   **Buenos Aires:** Todo servicio en esta ciudad se marca para revisión.

### 2. Revisión Solicitudes Futuras
Auditoría dinámica de reportes de solicitudes para validar rentabilidad y estados.

**Filtros de Clasificación:**
*   **Paso Directo (Aprobado):** Clientes *Booking* e *I Need Tours*.
*   **Omitidos (No se revisan):** Servicios con estado *Cancelada* o ciudades distintas a *Santiago* y *Valparaíso* (con/sin tilde).

**Reglas de Auditoría (Para el resto de solicitudes):**
*   **Costo vs Valor:** El *Costo Proveedor* no puede ser mayor al *Valor Km Estimado*.
*   **Rentabilidad por KM:** El valor por kilómetro (*Valor Km Estimado / Km Estimado*) debe ser **mayor o igual a 1000**.
*   **Rentabilidad por Tiempo:** El valor por minuto (*Valor Km Estimado / Tiempo Estimado*) debe ser **mayor a 1000**.

## 🚀 Ejecución

### Local
1.  Activar entorno virtual: `source venv/bin/activate`
2.  Ejecutar: `streamlit run app.py`

### Producción (Web)
La aplicación se despliega automáticamente mediante cada commit a la rama `main` en GitHub y está disponible en Streamlit Cloud.

---
*Última actualización: Enero 2026*
