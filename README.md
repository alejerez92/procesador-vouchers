# Procesador de Vouchers y Conductores

Aplicación desarrollada en Python con Streamlit para automatizar la conciliación y validación de reservas y conductores, aplicando reglas de negocio complejas.

## 🚀 Cómo ejecutar la aplicación

1.  Asegúrate de estar en el directorio del proyecto:
    ```bash
    cd "/Volumes/SSD Externo/SSD Gemini/Procesar Vouchers"
    ```
2.  Activa el entorno virtual (si no lo está):
    ```bash
    source venv/bin/activate
    # O usa el path directo:
    ```
3.  Ejecuta la aplicación:
    ```bash
    ./venv/bin/streamlit run app.py
    ```
4.  La aplicación se abrirá automáticamente en tu navegador (usualmente en `http://localhost:8501`).

## 📋 Resumen de Reglas y Parámetros Implementados

La aplicación procesa dos archivos Excel: **Reservas** y **Conductores**. Los cruza utilizando el **N° de Móvil** y aplica las siguientes validaciones en orden:

### 1. Cruce de Información
*   Se une la información de Reservas con la de Conductores usando la columna `N° Móvil` como llave.
*   Se obtiene el tipo de contrato del conductor desde el archivo de Conductores (Columna `Contrato`).

### 2. Reglas de Validación (Discrepancias)

Un registro se marca como **"Discrepancia"** si cumple cualquiera de las siguientes condiciones:

*   **Obs. Conductor con datos:** Si la columna `Obs. Conductor` (Reservas) tiene cualquier texto.
*   **Convenios Restringidos sin CC:**
    *   Si el `Nombre convenio` es: *Godrej, Unilever, Pacific Hydro, Parque Arauco* o *Patio*.
    *   Y el `Código CC` es: *"SIN"* o *"SIN INFORMACION"*.
*   **Código CC Pendiente:** Si el `Código CC` dice explícitamente *"Pendiente"*.
*   **Móviles Restringidos:** Si el `N° Móvil` es *000, 100, 200* o *300*.
*   **Valores Inválidos:**
    *   Si `$ Costo proveedor` es menor o igual a 0.
    *   Si `$ Total` es menor o igual a 0.

### 3. Reglas Financieras Avanzadas

*   **Contrato "FIJO POR SERVICIO":**
    *   **Pérdida:** Error si `$ Total` <= `$ Costo proveedor` (siempre).
    *   **Margen Mínimo:** Error si el margen `(Total - Costo) / Costo` es **<= 10%**.
        *   *Excepción:* Esta regla de margen **NO** aplica si la `Ciudad` es: *Punta Cana, Lima, Santo Domingo, Buenos Aires, Río de Janeiro, Bogotá, Mendoza* o *Medellin*.

*   **Excepción Variable (Booking / I Need Tours):**
    *   Para convenios *"BOOKING"* o *"I NEED TOURS"* con contratos variables (*"VARIABLE 23 A 30% ADMIN"* o *"VARIABLE 25 A 31% ADMIN"*).
    *   Se permite que el Costo sea mayor al Total (pérdida), **siempre que la diferencia no supere los 5.000**. Si pierde más de 5.000, es discrepancia.

*   **Validación Tipo de Cambio (TC):**
    *   Se calcula `TC = $ Costo proveedor / Naturaleza gasto`.
    *   **Ciudades Grupo 1** (*Punta Cana, Santo Domingo, Rio, Sao Paulo*): El TC debe estar entre **920 y 980**.
    *   **Ciudades Grupo 2** (*Mendoza, Buenos Aires*): El TC debe estar entre **0.5 y 0.9**.

*   **Regla Travel Security:**
    *   Si el convenio es *"TRAVEL SECURITY"* y el `Código CC` no es válido (Vacío, SIN, SIN INFORMACION, Pendiente).
    *   **Entonces:** La columna `Naturaleza gasto` **DEBE** tener información. Si está vacía, es discrepancia.

## 🛠 Estructura del Proyecto

*   `app.py`: Código fuente principal de la aplicación.
*   `requirements.txt`: Lista de dependencias (streamlit, pandas, openpyxl, xlsxwriter).
*   `venv/`: Entorno virtual de Python.
