import streamlit as st
import pandas as pd
import io
import re

# Configuración de la página
st.set_page_config(page_title="Procesador de Vouchers", layout="wide")

st.title("Procesador de Vouchers y Conductores")
st.markdown("""
Sube los archivos de **Reservas** y **Conductores**. 
El sistema intentará detectar las columnas automáticamente, pero puedes ajustarlas si es necesario.
""")

# --- Sidebar para Configuración ---
st.sidebar.header("Configuración de Reglas")

EMPRESAS_RESTRICCION_CC = [
    "Godrej", 
    "Unilever", 
    "Pacific Hydro", 
    "Parque Arauco", 
    "Patio"
]

VALORES_CC_INVALIDOS = [
    "SIN", 
    "SIN INFORMACION"
]

CIUDADES_SIN_MARGEN = [
    "Punta Cana", 
    "Lima", 
    "Santo domingo", 
    "Buenos Aires", 
    "Río de Janeiro", 
    "Bogotá", 
    "Mendoza", 
    "Medellin"
]

CIUDADES_TC_ALTO = [
    "Punta Cana", 
    "Santo domingo", 
    "Rio de Janeiro", 
    "Río de Janeiro", # Por si acaso con tilde
    "Sao Paulo",
    "São Paulo" # Por si acaso con tilde
]

CIUDADES_TC_BAJO = [
    "Mendoza", 
    "Buenos Aires"
]

MOVILES_RESTRINGIDOS = ["000", "100", "200", "300"]

CONVENIOS_ESPECIALES_VARIABLE = ["BOOKING", "I NEED TOURS"]
CONTRATOS_ESPECIALES_VARIABLE = ["VARIABLE 23 A 30% ADMIN", "VARIABLE 25 A 31% ADMIN"]

# --- Funciones Auxiliares ---
def encontrar_columna_por_nombre(columnas, palabras_clave):
    """Busca la primera columna que contenga alguna de las palabras clave (case insensitive)."""
    columnas_lower = [c.lower() for c in columnas]
    for clave in palabras_clave:
        clave_lower = clave.lower()
        for i, col in enumerate(columnas_lower):
            if clave_lower in col:
                return columnas[i]
    return None

def encontrar_indice_columna(columnas, seleccion_default):
    """Devuelve el índice de la selección por defecto en la lista de columnas."""
    if seleccion_default and seleccion_default in columnas:
        return list(columnas).index(seleccion_default)
    return 0

# --- Carga de Archivos ---
col1, col2 = st.columns(2)
with col1:
    archivo_reservas = st.file_uploader("Cargar Archivo de Reservas (XLSX)", type=["xlsx"])
with col2:
    archivo_conductores = st.file_uploader("Cargar Archivo de Conductores (XLSX)", type=["xlsx"])

if archivo_reservas and archivo_conductores:
    try:
        # Cargar DataFrames
        df_res = pd.read_excel(archivo_reservas)
        df_cond = pd.read_excel(archivo_conductores, header=1) 
        
        # Limpiar espacios en nombres de columnas para facilitar lectura
        df_res.columns = df_res.columns.str.strip()
        df_cond.columns = df_cond.columns.str.strip()

        st.divider()
        st.subheader("Configuración de Columnas")
        st.info("Por favor, confirma que las columnas seleccionadas son las correctas.")

        cols_config_1, cols_config_2 = st.columns(2)

        # --- Selección de Columnas: Reservas ---
        with cols_config_1:
            st.markdown("##### Archivo Reservas")
            # Auto-detección
            auto_movil_res = encontrar_columna_por_nombre(df_res.columns, ["N° Móvil", "Movil", "Móvil"])
            auto_obs = encontrar_columna_por_nombre(df_res.columns, ["Obs. Conductor", "Observacion", "Obs"])
            auto_convenio = encontrar_columna_por_nombre(df_res.columns, ["Nombre convenio", "Convenio"])
            auto_cc = encontrar_columna_por_nombre(df_res.columns, ["Código CC", "CC", "Centro Costo"])
            
            # Nuevas columnas para validación de margen
            auto_total = encontrar_columna_por_nombre(df_res.columns, ["$ Total", "Total", "Monto"])
            auto_costo = encontrar_columna_por_nombre(df_res.columns, ["$ Costo proveedor", "Costo proveedor", "Costo"])
            
            # Auto-detección Ciudad (aprox BA - indice 52 o nombre)
            auto_ciudad = encontrar_columna_por_nombre(df_res.columns, ["Ciudad", "City"])
            if not auto_ciudad and len(df_res.columns) > 52:
                 auto_ciudad = df_res.columns[52]
            
            # Nueva columna para Naturaleza gasto (aprox X - indice 23)
            auto_naturaleza = encontrar_columna_por_nombre(df_res.columns, ["Naturaleza gasto", "Naturaleza", "Gasto"])
            if not auto_naturaleza and len(df_res.columns) > 23:
                auto_naturaleza = df_res.columns[23]

            # Nueva columna para Medio de Pago (columna N - indice 13)
            auto_medio_pago = encontrar_columna_por_nombre(df_res.columns, ["Medio de pago", "Pago", "Metodo de Pago"])
            if not auto_medio_pago and len(df_res.columns) > 13:
                auto_medio_pago = df_res.columns[13]

            col_movil_res = st.selectbox(
                "Columna Móvil (Reservas)", 
                options=df_res.columns, 
                index=encontrar_indice_columna(df_res.columns, auto_movil_res)
            )
            col_obs_res = st.selectbox(
                "Columna Obs. Conductor", 
                options=df_res.columns, 
                index=encontrar_indice_columna(df_res.columns, auto_obs)
            )
            col_convenio_res = st.selectbox(
                "Columna Nombre Convenio", 
                options=df_res.columns, 
                index=encontrar_indice_columna(df_res.columns, auto_convenio)
            )
            col_cc_res = st.selectbox(
                "Columna Código CC", 
                options=df_res.columns, 
                index=encontrar_indice_columna(df_res.columns, auto_cc)
            )
            col_ciudad_res = st.selectbox(
                "Columna Ciudad", 
                options=df_res.columns, 
                index=encontrar_indice_columna(df_res.columns, auto_ciudad)
            )
            col_naturaleza_res = st.selectbox(
                "Columna Naturaleza Gasto", 
                options=df_res.columns, 
                index=encontrar_indice_columna(df_res.columns, auto_naturaleza)
            )
            col_total_res = st.selectbox(
                "Columna $ Total", 
                options=df_res.columns, 
                index=encontrar_indice_columna(df_res.columns, auto_total)
            )
            col_costo_res = st.selectbox(
                "Columna $ Costo proveedor", 
                options=df_res.columns, 
                index=encontrar_indice_columna(df_res.columns, auto_costo)
            )
            col_medio_pago_res = st.selectbox(
                "Columna Medio de Pago", 
                options=df_res.columns, 
                index=encontrar_indice_columna(df_res.columns, auto_medio_pago)
            )

        # --- Selección de Columnas: Conductores ---
        with cols_config_2:
            st.markdown("##### Archivo Conductores")
            # Auto-detección
            auto_movil_cond = encontrar_columna_por_nombre(df_cond.columns, ["N° Móvil", "Movil", "Móvil"])
            # Auto-detección contrato: busca "Contrato" o usa la columna AY (índice 50) si existe
            auto_contrato = encontrar_columna_por_nombre(df_cond.columns, ["Contrato"])
            if not auto_contrato and len(df_cond.columns) > 50:
                auto_contrato = df_cond.columns[50] # Columna AY

            col_movil_cond = st.selectbox(
                "Columna Móvil (Conductores)", 
                options=df_cond.columns, 
                index=encontrar_indice_columna(df_cond.columns, auto_movil_cond)
            )
            col_contrato_cond = st.selectbox(
                "Columna Contrato", 
                options=df_cond.columns, 
                index=encontrar_indice_columna(df_cond.columns, auto_contrato)
            )

        st.divider()

        if st.button("Procesar Datos", type="primary"):
            log_proceso = []
            
            # --- Lógica de Procesamiento ---
            # Normalizar columnas de cruce (Móvil) para asegurar match
            # Convertimos a string y quitamos decimales (.0) que Excel a veces añade a números
            df_res['temp_join_key'] = df_res[col_movil_res].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df_cond['temp_join_key'] = df_cond[col_movil_cond].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            
            log_proceso.append(f"Cruce realizado por: '{col_movil_res}' (Reservas) y '{col_movil_cond}' (Conductores)")

            # Merge
            df_merged = pd.merge(
                df_res,
                df_cond[['temp_join_key', col_contrato_cond]],
                on='temp_join_key',
                how='left'
            )
            
            # Limpiar llave temporal
            df_merged.drop(columns=['temp_join_key'], inplace=True)
            
            # Renombrar columna contrato traída
            col_contrato_final = "Contrato_Conductor"
            df_merged.rename(columns={col_contrato_cond: col_contrato_final}, inplace=True)
            
            # Inicializar flags
            df_merged['Es_Discrepancia'] = False
            df_merged['Motivo_Discrepancia'] = ""

            # --- Preparación de datos numéricos comunes ---
            def clean_currency(x):
                if isinstance(x, str):
                    x = x.replace('$', '').replace(',', '').strip()
                return pd.to_numeric(x, errors='coerce')

            df_merged['temp_total'] = df_merged[col_total_res].apply(clean_currency).fillna(0)
            df_merged['temp_costo'] = df_merged[col_costo_res].apply(clean_currency).fillna(0)
            df_merged['temp_naturaleza'] = df_merged[col_naturaleza_res].apply(clean_currency).fillna(0)
            
            # Normalizaciones string
            df_merged['temp_contrato_upper'] = df_merged[col_contrato_final].astype(str).str.upper().str.strip()
            df_merged['temp_ciudad_norm'] = df_merged[col_ciudad_res].astype(str).str.strip()
            # Usamos la columna original de movil reservas normalizada para comparar
            df_merged['temp_movil_check'] = df_merged[col_movil_res].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df_merged['temp_medio_pago'] = df_merged[col_medio_pago_res].astype(str).str.upper().str.strip()


            # --- REGLA 1: Obs. Conductor no vacía ---
            # Verifica nulos y strings vacíos
            mask_obs = df_merged[col_obs_res].notna() & (df_merged[col_obs_res].astype(str).str.strip() != "")
            # Algunos Excels tienen espacios en blanco o strings "nan" literales
            mask_obs = mask_obs & (df_merged[col_obs_res].astype(str).str.lower() != "nan")
            
            df_merged.loc[mask_obs, 'Es_Discrepancia'] = True
            df_merged.loc[mask_obs, 'Motivo_Discrepancia'] += "Obs. Conductor no vacía; "

            # --- REGLA 2: Convenio Restringido sin CC ---
            df_merged['temp_convenio'] = df_merged[col_convenio_res].astype(str).str.strip()
            df_merged['temp_cc'] = df_merged[col_cc_res].astype(str).str.strip()

            mask_convenio = df_merged['temp_convenio'].isin(EMPRESAS_RESTRICCION_CC)
            mask_cc_invalido = df_merged['temp_cc'].isin(VALORES_CC_INVALIDOS)
            
            mask_rule_2 = mask_convenio & mask_cc_invalido
            
            df_merged.loc[mask_rule_2, 'Es_Discrepancia'] = True
            df_merged.loc[mask_rule_2, 'Motivo_Discrepancia'] += "Falta Código CC en Convenio Restringido; "

            # --- NUEVA REGLA (Adicional a la 2): Código CC 'Pendiente' ---
            # Si dice 'Pendiente' (exacto o aproximado), a discrepancia.
            mask_cc_pendiente = df_merged['temp_cc'].str.upper() == "PENDIENTE"
            if mask_cc_pendiente.any():
                df_merged.loc[mask_cc_pendiente, 'Es_Discrepancia'] = True
                df_merged.loc[mask_cc_pendiente, 'Motivo_Discrepancia'] += "Código CC es Pendiente; "
            
            
            # --- REGLA 3: Margen en Contrato FIJO POR SERVICIO ---
            # Verificar si ciudad está en lista de exentas de margen (case insensitive)
            ciudades_exentas_lower = [c.lower() for c in CIUDADES_SIN_MARGEN]
            mask_ciudad_exenta_margen = df_merged['temp_ciudad_norm'].str.lower().isin(ciudades_exentas_lower)

            mask_fijo = df_merged['temp_contrato_upper'] == "FIJO POR SERVICIO"
            
            # Sub-regla 3.1: Total > Costo (Aplica SIEMPRE para Fijo por Servicio)
            mask_perdida = mask_fijo & (df_merged['temp_total'] <= df_merged['temp_costo'])
            if mask_perdida.any():
                df_merged.loc[mask_perdida, 'Es_Discrepancia'] = True
                df_merged.loc[mask_perdida, 'Motivo_Discrepancia'] += "Total menor o igual al Costo (Fijo por Servicio); "

            # Sub-regla 3.2: Margen > 10% (Aplica SOLO si NO es ciudad exenta)
            mask_costo_positivo = df_merged['temp_costo'] > 0
            # Cálculo vectorizado del margen
            margen = (df_merged['temp_total'] - df_merged['temp_costo']) / df_merged['temp_costo']
            
            mask_bajo_margen = mask_fijo & mask_costo_positivo & (margen <= 0.10) & (~mask_ciudad_exenta_margen)
            
            if mask_bajo_margen.any():
                df_merged.loc[mask_bajo_margen, 'Es_Discrepancia'] = True
                df_merged.loc[mask_bajo_margen, 'Motivo_Discrepancia'] += "Margen bajo 10% (Fijo por Servicio); "

            # --- REGLA 4: Validación Tipo de Cambio por Ciudad ---
            mask_naturaleza_ok = df_merged['temp_naturaleza'] > 0
            tc_calculado = df_merged['temp_costo'] / df_merged['temp_naturaleza']
            
            # Ciudades TC Alto (920 - 980)
            ciudades_tc_alto_lower = [c.lower() for c in CIUDADES_TC_ALTO]
            mask_ciudad_tc_alto = df_merged['temp_ciudad_norm'].str.lower().isin(ciudades_tc_alto_lower)
            
            mask_tc_alto_bad = mask_naturaleza_ok & mask_ciudad_tc_alto & ((tc_calculado < 920) | (tc_calculado > 980))
            if mask_tc_alto_bad.any():
                df_merged.loc[mask_tc_alto_bad, 'Es_Discrepancia'] = True
                df_merged.loc[mask_tc_alto_bad, 'Motivo_Discrepancia'] += "TC fuera de rango (920-980); "
                
            # Ciudades TC Bajo (0.5 - 0.9)
            ciudades_tc_bajo_lower = [c.lower() for c in CIUDADES_TC_BAJO]
            mask_ciudad_tc_bajo = df_merged['temp_ciudad_norm'].str.lower().isin(ciudades_tc_bajo_lower)
            
            mask_tc_bajo_bad = mask_naturaleza_ok & mask_ciudad_tc_bajo & ((tc_calculado < 0.5) | (tc_calculado > 0.9))
            if mask_tc_bajo_bad.any():
                df_merged.loc[mask_tc_bajo_bad, 'Es_Discrepancia'] = True
                df_merged.loc[mask_tc_bajo_bad, 'Motivo_Discrepancia'] += "TC fuera de rango (0.5-0.9); "

            # --- REGLA 5: Móviles Restringidos (000, 100, 200, 300) ---
            mask_movil_restringido = df_merged['temp_movil_check'].isin(MOVILES_RESTRINGIDOS)
            if mask_movil_restringido.any():
                df_merged.loc[mask_movil_restringido, 'Es_Discrepancia'] = True
                df_merged.loc[mask_movil_restringido, 'Motivo_Discrepancia'] += "Móvil restringido (000/100/200/300); "

            # --- REGLA 6: Costo > 0 y Total > 0 ---
            # Costo debe ser > 0
            mask_costo_cero = df_merged['temp_costo'] <= 0
            if mask_costo_cero.any():
                df_merged.loc[mask_costo_cero, 'Es_Discrepancia'] = True
                df_merged.loc[mask_costo_cero, 'Motivo_Discrepancia'] += "Costo proveedor debe ser > 0; "

            # Total debe ser > 0
            mask_total_cero = df_merged['temp_total'] <= 0
            if mask_total_cero.any():
                 df_merged.loc[mask_total_cero, 'Es_Discrepancia'] = True
                 df_merged.loc[mask_total_cero, 'Motivo_Discrepancia'] += "Total debe ser > 0; "

            # --- REGLA 7: Excepción Variable Booking/I Need Tours (Permite pérdida hasta 5000) ---
            # Identificar Convenios Booking/I Need Tours
            mask_conv_var = df_merged['temp_convenio'].str.upper().isin(CONVENIOS_ESPECIALES_VARIABLE)
            # Identificar Contratos Variables Específicos
            mask_cont_var = df_merged['temp_contrato_upper'].isin(CONTRATOS_ESPECIALES_VARIABLE)
            
            mask_target_var = mask_conv_var & mask_cont_var
            
            # Calcular pérdida: Costo - Total (Si es positivo, hay pérdida)
            diferencia_perdida = df_merged['temp_costo'] - df_merged['temp_total']
            
            # Flag: Si aplica la regla Y la pérdida es mayor a 5000
            mask_exceso_perdida = mask_target_var & (diferencia_perdida > 5000)
            
            if mask_exceso_perdida.any():
                df_merged.loc[mask_exceso_perdida, 'Es_Discrepancia'] = True
                df_merged.loc[mask_exceso_perdida, 'Motivo_Discrepancia'] += "Pérdida excede 5000 en contrato Variable; "

            # --- REGLA 8: Travel Security y Naturaleza Gasto ---
            # Si Convenio es TRAVEL SECURITY y CC es (Vacío, SIN, SIN INF, PENDIENTE) -> Naturaleza debe tener dato
            mask_travel = df_merged['temp_convenio'].str.upper() == "TRAVEL SECURITY"
            
            # Definir qué consideramos CC "Malo" para Travel Security
            # Incluye los nulos, vacíos, y las palabras prohibidas
            valores_cc_malos_travel = VALORES_CC_INVALIDOS + ["PENDIENTE", ""]
            
            # Normalizamos CC a string y mayusculas para checkear, reemplazando nan por ""
            cc_series = df_merged['temp_cc'].fillna("").astype(str).str.upper().str.strip()
            mask_cc_malo_travel = cc_series.isin(valores_cc_malos_travel) | (cc_series == "NAN")
            
            # Verificar si Naturaleza tiene dato. Usamos la columna ORIGINAL para ver si hay texto o numero
            # Si temp_naturaleza > 0 significa que había numero. Pero a veces es texto.
            # Mejor chequeamos si la columna original no es nula y no es vacía
            mask_naturaleza_vacia = df_merged[col_naturaleza_res].isna() | (df_merged[col_naturaleza_res].astype(str).str.strip() == "")
            
            mask_travel_problem = mask_travel & mask_cc_malo_travel & mask_naturaleza_vacia
            
            if mask_travel_problem.any():
                df_merged.loc[mask_travel_problem, 'Es_Discrepancia'] = True
                df_merged.loc[mask_travel_problem, 'Motivo_Discrepancia'] += "Travel Security sin CC requiere Naturaleza Gasto; "

            # --- NUEVA REGLA: PARTICULARES SIN CONVENIO y Medio de Pago EFECTIVO ---
            mask_particulares_convenio = df_merged['temp_convenio'].str.upper() == "PARTICULARES SIN CONVENIO"
            mask_medio_pago_efectivo = df_merged['temp_medio_pago'].str.upper() == "EFECTIVO"

            mask_rule_new = mask_particulares_convenio & mask_medio_pago_efectivo
            if mask_rule_new.any():
                df_merged.loc[mask_rule_new, 'Es_Discrepancia'] = True
                df_merged.loc[mask_rule_new, 'Motivo_Discrepancia'] += "PARTICULARES SIN CONVENIO con Medio de Pago Efectivo; "

            # Limpieza temporales final
            df_merged.drop(columns=[
                'temp_total', 'temp_costo', 'temp_naturaleza', 
                'temp_contrato_upper', 'temp_ciudad_norm', 'temp_movil_check',
                'temp_convenio', 'temp_cc', 'temp_medio_pago'
            ], inplace=True)

            # --- Resultados ---
            df_discrepancias = df_merged[df_merged['Es_Discrepancia']].copy()
            df_procesables = df_merged[~df_merged['Es_Discrepancia']].copy()

            st.success("¡Procesamiento exitoso!")
            
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric("Total Reservas", len(df_merged))
            metric_col2.metric("Procesables", len(df_procesables))
            metric_col3.metric("Con Discrepancias", len(df_discrepancias))

            # Crear Excel descargable
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Ajustar ancho de columnas básico
                df_discrepancias.to_excel(writer, sheet_name='Discrepancias', index=False)
                df_procesables.to_excel(writer, sheet_name='Procesables', index=False)
                
            st.download_button(
                label="📥 Descargar Resultado (XLSX)",
                data=buffer.getvalue(),
                file_name="Resultado_Procesamiento_Vouchers.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
            
            with st.expander("Ver Logs del Sistema"):
                for l in log_proceso:
                    st.text(l)

    except Exception as e:
        st.error(f"Error al leer los archivos: {e}")
        st.info("Consejo: Verifica que los archivos no estén abiertos en Excel y que sean formato .xlsx válido.")

else:
    st.info("Esperando archivos...")