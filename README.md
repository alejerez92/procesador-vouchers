# Procesador de Vouchers y Conductores

Aplicación web desarrollada en Python con Streamlit para automatizar la conciliación, validación y detección de discrepancias entre registros de Reservas y Conductores.

## 📋 Reglas de Negocio Implementadas

El sistema cruza la información usando el **N° de Móvil** y aplica las siguientes validaciones automáticas:

### 1. Validaciones Generales
*   **Detección Dinámica de Columnas:** El sistema busca automáticamente los encabezados, soportando formatos antiguos y nuevos (ej: "Ciudad" o "Nombre ciudad", "Convenio" o "Nombre cliente").
*   **Móviles Restringidos:** Se marcan como discrepancia los servicios realizados por los móviles: `000`, `100`, `200` y `300`.
*   **Información Faltante:**
    *   **Obs. Conductor:** No debe tener texto (debe estar vacía).
    *   **Centros de Costo (CC):**
        *   Si el convenio es *Godrej, Unilever, Pacific Hydro, Parque Arauco, Patio, Rays* o **Multi Export**, el CC no puede ser "SIN" ni "SIN INFORMACION".
        *   El CC nunca puede ser "PENDIENTE" (para ningún convenio).
*   **Validación de Montos:**
    *   `$ Costo proveedor` debe ser mayor a 0.
    *   `$ Total` debe ser mayor a 0 (el sistema prioriza la coincidencia exacta de esta columna para evitar confusiones con totales de conductores).
*   **Restricción por Ciudad:**
    *   Todos los servicios cuya `Ciudad` sea "Buenos Aires" serán marcados como discrepancia.

### 2. Reglas Financieras (Márgenes y Pérdidas)
... (resto de reglas se mantienen igual) ...

## 🛠 Mejoras Recientes (Enero 2026)
*   **Soporte Multiformato:** Adaptación al nuevo reporte de la App que incluye más columnas.
*   **Prevención de Duplicados:** Limpieza automática de la base de conductores para evitar que una misma reserva se duplique en el resultado final si un móvil está repetido.
*   **Priorización de Columnas:** Búsqueda inteligente que prefiere nombres exactos antes que parciales para asegurar el cálculo correcto del Margen.

### 3. Validaciones de Tipo de Cambio (TC)
Se calcula como: `TC = Costo Proveedor / Naturaleza Gasto`.

*   **Ciudades Grupo 1** (*Punta Cana, Santo Domingo, Rio de Janeiro, Sao Paulo*):
    *   El TC debe estar entre **920 y 980**.
*   **Ciudades Grupo 2** (*Mendoza, Buenos Aires*):
    *   El TC debe estar entre **0.5 y 0.9**.

### 4. Regla Travel Security
*   Si el convenio es "TRAVEL SECURITY" y el Código CC no es válido (está vacío, es "SIN", "SIN INFORMACION" o "PENDIENTE"):
    *   Es obligatorio que la columna **Naturaleza Gasto** contenga información.

## 🛠 Ejecución Local (Desarrollo)

Si necesitas correr la aplicación en tu propio computador para hacer cambios:

1.  Clonar el repositorio y entrar en la carpeta.
2.  Activar entorno virtual:
    ```bash
    source venv/bin/activate
    ```
3.  Ejecutar:
    ```bash
    streamlit run app.py
    ```