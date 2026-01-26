import streamlit as st
import pandas as pd
import io
import re

# --- Configuración Global ---
st.set_page_config(page_title="Herramientas Procesamiento", layout="wide")

# --- Funciones de Utilidad Global ---
def encontrar_columna_por_nombre(columnas, palabras_clave):
    columnas_lower = [c.lower() for c in columnas]
    # Intento 1: Coincidencia exacta
    for clave in palabras_clave:
        clave_lower = clave.lower()
        if clave_lower in columnas_lower:
            idx = columnas_lower.index(clave_lower)
            return columnas[idx]
    # Intento 2: Coincidencia parcial
    for clave in palabras_clave:
        clave_lower = clave.lower()
        for i, col in enumerate(columnas_lower):
            if clave_lower in col:
                return columnas[i]
    return None

def encontrar_indice_columna(columnas, seleccion_default):
    if seleccion_default and seleccion_default in columnas:
        return list(columnas).index(seleccion_default)
    return 0

def clean_currency(x):
    if isinstance(x, str):
        x = x.replace('$', '').replace(',', '').strip()
    return pd.to_numeric(x, errors='coerce')

# ==============================================================================
# LÓGICA: PROCESADOR DE VOUCHERS (ORIGINAL)
# ==============================================================================
def run_procesador_vouchers():
    st.header("Procesador de Vouchers y Conductores")
    st.markdown("""
    Sube los archivos de **Reservas** y **Conductores**. 
    El sistema cruzará la información y buscará discrepancias según las reglas de negocio.
    """)

    # --- Configuración de Reglas ---
    EMPRESAS_RESTRICCION_CC = ["Godrej", "Unilever", "Pacific Hydro", "Parque Arauco", "Patio", "Rays", "Multi Export"]
    VALORES_CC_INVALIDOS = ["SIN", "SIN INFORMACION"]
    CIUDADES_SIN_MARGEN = ["Punta Cana", "Lima", "Santo domingo", "Buenos Aires", "Río de Janeiro", "Bogotá", "Mendoza", "Medellin"]
    CIUDADES_TC_ALTO = ["Punta Cana", "Santo domingo", "Rio de Janeiro", "Río de Janeiro", "Sao Paulo", "São Paulo"]
    CIUDADES_TC_BAJO = ["Mendoza", "Buenos Aires"]
    MOVILES_RESTRINGIDOS = ["000", "100", "200", "300"]
    CONVENIOS_ESPECIALES_VARIABLE = ["BOOKING", "I NEED TOURS"]
    CONTRATOS_ESPECIALES_VARIABLE = ["VARIABLE 23 A 30% ADMIN", "VARIABLE 25 A 31% ADMIN"]

    # --- Carga de Archivos ---
    col1, col2 = st.columns(2)
    with col1:
        archivo_reservas = st.file_uploader("Cargar Archivo de Reservas (XLSX)", type=["xlsx"], key="res")
    with col2:
        archivo_conductores = st.file_uploader("Cargar Archivo de Conductores (XLSX)", type=["xlsx"], key="cond")

    if archivo_reservas and archivo_conductores:
        try:
            # Cargar DataFrames
            df_res = pd.read_excel(archivo_reservas)
            df_cond = pd.read_excel(archivo_conductores, header=1) 
            
            df_res.columns = df_res.columns.str.strip()
            df_cond.columns = df_cond.columns.str.strip()

            st.divider()
            st.subheader("Configuración de Columnas")
            st.info("Por favor, confirma que las columnas seleccionadas son las correctas.")

            cols_config_1, cols_config_2 = st.columns(2)

            # --- Selección de Columnas: Reservas ---
            with cols_config_1:
                st.markdown("##### Archivo Reservas")
                auto_movil_res = encontrar_columna_por_nombre(df_res.columns, ["N° Móvil", "Movil", "Móvil"])
                auto_obs = encontrar_columna_por_nombre(df_res.columns, ["Obs. Conductor", "Observacion", "Obs"])
                auto_convenio = encontrar_columna_por_nombre(df_res.columns, ["Nombre convenio", "Convenio", "Nombre cliente"])
                auto_cc = encontrar_columna_por_nombre(df_res.columns, ["Código CC", "CC", "Centro Costo"])
                auto_total = encontrar_columna_por_nombre(df_res.columns, ["$ Total", "Total", "Monto"])
                auto_costo = encontrar_columna_por_nombre(df_res.columns, ["$ Costo proveedor", "Costo proveedor", "Costo"])
                auto_ciudad = encontrar_columna_por_nombre(df_res.columns, ["Ciudad", "City", "Nombre ciudad"])
                auto_naturaleza = encontrar_columna_por_nombre(df_res.columns, ["Naturaleza gasto", "Naturaleza", "Gasto"])
                auto_medio_pago = encontrar_columna_por_nombre(df_res.columns, ["Medio de pago", "Pago", "Metodo de Pago"])

                col_movil_res = st.selectbox("Columna Móvil (Reservas)", df_res.columns, index=encontrar_indice_columna(df_res.columns, auto_movil_res))
                col_obs_res = st.selectbox("Columna Obs. Conductor", df_res.columns, index=encontrar_indice_columna(df_res.columns, auto_obs))
                col_convenio_res = st.selectbox("Columna Nombre Convenio", df_res.columns, index=encontrar_indice_columna(df_res.columns, auto_convenio))
                col_cc_res = st.selectbox("Columna Código CC", df_res.columns, index=encontrar_indice_columna(df_res.columns, auto_cc))
                col_ciudad_res = st.selectbox("Columna Ciudad", df_res.columns, index=encontrar_indice_columna(df_res.columns, auto_ciudad))
                col_naturaleza_res = st.selectbox("Columna Naturaleza Gasto", df_res.columns, index=encontrar_indice_columna(df_res.columns, auto_naturaleza))
                col_total_res = st.selectbox("Columna $ Total", df_res.columns, index=encontrar_indice_columna(df_res.columns, auto_total))
                col_costo_res = st.selectbox("Columna $ Costo proveedor", df_res.columns, index=encontrar_indice_columna(df_res.columns, auto_costo))
                col_medio_pago_res = st.selectbox("Columna Medio de Pago", df_res.columns, index=encontrar_indice_columna(df_res.columns, auto_medio_pago))

            # --- Selección de Columnas: Conductores ---
            with cols_config_2:
                st.markdown("##### Archivo Conductores")
                auto_movil_cond = encontrar_columna_por_nombre(df_cond.columns, ["N° Móvil", "Movil", "Móvil"])
                auto_contrato = encontrar_columna_por_nombre(df_cond.columns, ["Contrato"])

                col_movil_cond = st.selectbox("Columna Móvil (Conductores)", df_cond.columns, index=encontrar_indice_columna(df_cond.columns, auto_movil_cond))
                col_contrato_cond = st.selectbox("Columna Contrato", df_cond.columns, index=encontrar_indice_columna(df_cond.columns, auto_contrato))

            st.divider()

            if st.button("Procesar Datos", type="primary"):
                log_proceso = []
                # Normalizar columnas de cruce
                df_res['temp_join_key'] = df_res[col_movil_res].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                df_cond['temp_join_key'] = df_cond[col_movil_cond].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                
                log_proceso.append(f"Cruce realizado por: '{col_movil_res}' y '{col_movil_cond}'")

                # Prevención duplicados
                df_cond_limpio = df_cond[['temp_join_key', col_contrato_cond]].drop_duplicates(subset=['temp_join_key'])
                n_duplicados = len(df_cond) - len(df_cond_limpio)
                if n_duplicados > 0:
                    log_proceso.append(f"⚠️ Se eliminaron {n_duplicados} móviles duplicados en Conductores.")

                # Merge
                df_merged = pd.merge(df_res, df_cond_limpio, on='temp_join_key', how='left')
                df_merged.drop(columns=['temp_join_key'], inplace=True)
                
                col_contrato_final = "Contrato_Conductor"
                df_merged.rename(columns={col_contrato_cond: col_contrato_final}, inplace=True)
                
                df_merged['Es_Discrepancia'] = False
                df_merged['Motivo_Discrepancia'] = ""

                # Preparación de datos
                df_merged['temp_total'] = df_merged[col_total_res].apply(clean_currency).fillna(0)
                df_merged['temp_costo'] = df_merged[col_costo_res].apply(clean_currency).fillna(0)
                df_merged['temp_naturaleza'] = df_merged[col_naturaleza_res].apply(clean_currency).fillna(0)
                
                df_merged['temp_contrato_upper'] = df_merged[col_contrato_final].astype(str).str.upper().str.strip()
                df_merged['temp_ciudad_norm'] = df_merged[col_ciudad_res].astype(str).str.strip()
                df_merged['temp_movil_check'] = df_merged[col_movil_res].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                df_merged['temp_medio_pago'] = df_merged[col_medio_pago_res].astype(str).str.upper().str.strip()

                # --- APLICACIÓN DE REGLAS ---
                
                # Regla 1: Obs
                mask_obs = df_merged[col_obs_res].notna() & (df_merged[col_obs_res].astype(str).str.strip() != "")
                mask_obs = mask_obs & (df_merged[col_obs_res].astype(str).str.lower() != "nan")
                df_merged.loc[mask_obs, 'Es_Discrepancia'] = True
                df_merged.loc[mask_obs, 'Motivo_Discrepancia'] += "Obs. Conductor no vacía; "

                # Regla 2: Convenio Restringido
                df_merged['temp_convenio'] = df_merged[col_convenio_res].astype(str).str.strip()
                df_merged['temp_cc'] = df_merged[col_cc_res].astype(str).str.strip()
                mask_convenio = df_merged['temp_convenio'].isin(EMPRESAS_RESTRICCION_CC)
                mask_cc_invalido = df_merged['temp_cc'].isin(VALORES_CC_INVALIDOS)
                mask_rule_2 = mask_convenio & mask_cc_invalido
                df_merged.loc[mask_rule_2, 'Es_Discrepancia'] = True
                df_merged.loc[mask_rule_2, 'Motivo_Discrepancia'] += "Falta Código CC en Convenio Restringido; "

                # Regla CC Pendiente
                mask_cc_pendiente = df_merged['temp_cc'].str.upper() == "PENDIENTE"
                if mask_cc_pendiente.any():
                    df_merged.loc[mask_cc_pendiente, 'Es_Discrepancia'] = True
                    df_merged.loc[mask_cc_pendiente, 'Motivo_Discrepancia'] += "Código CC es Pendiente; "

                # Regla 3: Margen Fijo
                ciudades_exentas_lower = [c.lower() for c in CIUDADES_SIN_MARGEN]
                mask_ciudad_exenta_margen = df_merged['temp_ciudad_norm'].str.lower().isin(ciudades_exentas_lower)
                mask_fijo = df_merged['temp_contrato_upper'] == "FIJO POR SERVICIO"
                mask_perdida = mask_fijo & (df_merged['temp_total'] <= df_merged['temp_costo'])
                if mask_perdida.any():
                    df_merged.loc[mask_perdida, 'Es_Discrepancia'] = True
                    df_merged.loc[mask_perdida, 'Motivo_Discrepancia'] += "Total menor o igual al Costo (Fijo por Servicio); "
                
                mask_costo_positivo = df_merged['temp_costo'] > 0
                margen = (df_merged['temp_total'] - df_merged['temp_costo']) / df_merged['temp_costo']
                mask_bajo_margen = mask_fijo & mask_costo_positivo & (margen <= 0.10) & (~mask_ciudad_exenta_margen)
                if mask_bajo_margen.any():
                    df_merged.loc[mask_bajo_margen, 'Es_Discrepancia'] = True
                    df_merged.loc[mask_bajo_margen, 'Motivo_Discrepancia'] += "Margen bajo 10% (Fijo por Servicio); "

                # Regla 4: TC
                mask_naturaleza_ok = df_merged['temp_naturaleza'] > 0
                tc_calculado = df_merged['temp_costo'] / df_merged['temp_naturaleza']
                ciudades_tc_alto_lower = [c.lower() for c in CIUDADES_TC_ALTO]
                mask_ciudad_tc_alto = df_merged['temp_ciudad_norm'].str.lower().isin(ciudades_tc_alto_lower)
                mask_tc_alto_bad = mask_naturaleza_ok & mask_ciudad_tc_alto & ((tc_calculado < 920) | (tc_calculado > 980))
                if mask_tc_alto_bad.any():
                    df_merged.loc[mask_tc_alto_bad, 'Es_Discrepancia'] = True
                    df_merged.loc[mask_tc_alto_bad, 'Motivo_Discrepancia'] += "TC fuera de rango (920-980); "

                ciudades_tc_bajo_lower = [c.lower() for c in CIUDADES_TC_BAJO]
                mask_ciudad_tc_bajo = df_merged['temp_ciudad_norm'].str.lower().isin(ciudades_tc_bajo_lower)
                mask_tc_bajo_bad = mask_naturaleza_ok & mask_ciudad_tc_bajo & ((tc_calculado < 0.5) | (tc_calculado > 0.9))
                if mask_tc_bajo_bad.any():
                    df_merged.loc[mask_tc_bajo_bad, 'Es_Discrepancia'] = True
                    df_merged.loc[mask_tc_bajo_bad, 'Motivo_Discrepancia'] += "TC fuera de rango (0.5-0.9); "

                # Regla 5: Móviles
                mask_movil_restringido = df_merged['temp_movil_check'].isin(MOVILES_RESTRINGIDOS)
                if mask_movil_restringido.any():
                    df_merged.loc[mask_movil_restringido, 'Es_Discrepancia'] = True
                    df_merged.loc[mask_movil_restringido, 'Motivo_Discrepancia'] += "Móvil restringido (000/100/200/300); "

                # Regla 6: Positivos
                mask_costo_cero = df_merged['temp_costo'] <= 0
                if mask_costo_cero.any():
                    df_merged.loc[mask_costo_cero, 'Es_Discrepancia'] = True
                    df_merged.loc[mask_costo_cero, 'Motivo_Discrepancia'] += "Costo proveedor debe ser > 0; "
                
                mask_total_cero = df_merged['temp_total'] <= 0
                if mask_total_cero.any():
                    df_merged.loc[mask_total_cero, 'Es_Discrepancia'] = True
                    df_merged.loc[mask_total_cero, 'Motivo_Discrepancia'] += "Total debe ser > 0; "

                # Regla 7: Variables
                mask_conv_var = df_merged['temp_convenio'].str.upper().isin(CONVENIOS_ESPECIALES_VARIABLE)
                mask_cont_var = df_merged['temp_contrato_upper'].isin(CONTRATOS_ESPECIALES_VARIABLE)
                mask_target_var = mask_conv_var & mask_cont_var
                diferencia_perdida = df_merged['temp_costo'] - df_merged['temp_total']
                mask_exceso_perdida = mask_target_var & (diferencia_perdida > 5000)
                if mask_exceso_perdida.any():
                    df_merged.loc[mask_exceso_perdida, 'Es_Discrepancia'] = True
                    df_merged.loc[mask_exceso_perdida, 'Motivo_Discrepancia'] += "Pérdida excede 5000 en contrato Variable; "

                # Regla 8: Travel Security
                mask_travel = df_merged['temp_convenio'].str.upper() == "TRAVEL SECURITY"
                valores_cc_malos_travel = VALORES_CC_INVALIDOS + ["PENDIENTE", ""]
                cc_series = df_merged['temp_cc'].fillna("").astype(str).str.upper().str.strip()
                mask_cc_malo_travel = cc_series.isin(valores_cc_malos_travel) | (cc_series == "NAN")
                naturaleza_as_num = pd.to_numeric(df_merged[col_naturaleza_res], errors='coerce')
                mask_naturaleza_no_numerica = naturaleza_as_num.isna()
                mask_travel_problem = mask_travel & mask_cc_malo_travel & mask_naturaleza_no_numerica
                if mask_travel_problem.any():
                    df_merged.loc[mask_travel_problem, 'Es_Discrepancia'] = True
                    df_merged.loc[mask_travel_problem, 'Motivo_Discrepancia'] += "Travel Security sin CC requiere Naturaleza Gasto Numérica; "

                # Regla Nueva: Particulares
                mask_particulares_convenio = df_merged['temp_convenio'].str.upper() == "PARTICULARES SIN CONVENIO"
                mask_medio_pago_efectivo = df_merged['temp_medio_pago'].str.upper() == "EFECTIVO"
                mask_rule_new = mask_particulares_convenio & mask_medio_pago_efectivo
                if mask_rule_new.any():
                    df_merged.loc[mask_rule_new, 'Es_Discrepancia'] = True
                    df_merged.loc[mask_rule_new, 'Motivo_Discrepancia'] += "PARTICULARES SIN CONVENIO con Medio de Pago Efectivo; "

                # Regla Nueva: Buenos Aires
                mask_ba = df_merged['temp_ciudad_norm'].str.upper() == "BUENOS AIRES"
                if mask_ba.any():
                    df_merged.loc[mask_ba, 'Es_Discrepancia'] = True
                    df_merged.loc[mask_ba, 'Motivo_Discrepancia'] += "Servicio en Buenos Aires (Restringido); "

                # Limpieza y Output
                df_merged.drop(columns=[
                    'temp_total', 'temp_costo', 'temp_naturaleza', 
                    'temp_contrato_upper', 'temp_ciudad_norm', 'temp_movil_check',
                    'temp_convenio', 'temp_cc', 'temp_medio_pago'
                ], inplace=True)

                df_discrepancias = df_merged[df_merged['Es_Discrepancia']].copy()
                df_procesables = df_merged[~df_merged['Es_Discrepancia']].copy()

                st.success("¡Procesamiento exitoso!")
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                metric_col1.metric("Total Reservas", len(df_merged))
                metric_col2.metric("Procesables", len(df_procesables))
                metric_col3.metric("Con Discrepancias", len(df_discrepancias))

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
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
            st.error(f"Error: {e}")

    else:
        st.info("Esperando archivos...")

# ==============================================================================
# LÓGICA: REVISIÓN SOLICITUDES FUTURAS (NUEVO)
# ==============================================================================
def run_revision_solicitudes():
    st.header("Revisión Solicitudes Futuras")
    st.markdown("Sube el reporte de **Solicitudes** para aplicar las reglas de validación.")

    archivo_solicitudes = st.file_uploader("Cargar Reporte de Solicitudes (XLSX)", type=["xlsx"], key="soli")

    if archivo_solicitudes:
        try:
            df = pd.read_excel(archivo_solicitudes)
            df.columns = df.columns.str.strip()

            st.divider()
            st.subheader("Configuración de Columnas")
            
            auto_cliente = encontrar_columna_por_nombre(df.columns, ["Nombre Cliente", "Cliente", "Convenio"])
            auto_estado = encontrar_columna_por_nombre(df.columns, ["Estado solicitud", "Estado", "Status"])
            auto_ciudad = encontrar_columna_por_nombre(df.columns, ["Ciudad", "City"])
            auto_costo = encontrar_columna_por_nombre(df.columns, ["Costo proveedor", "Costo", "Costo Prov"])
            auto_valor_km = encontrar_columna_por_nombre(df.columns, ["Valor Km estimado", "Valor Km", "Monto Estimado"])
            auto_km = encontrar_columna_por_nombre(df.columns, ["Km estimado", "Kilometros", "Distancia"])
            auto_tiempo = encontrar_columna_por_nombre(df.columns, ["Tiempo estimado", "Tiempo", "Duracion"])

            col1, col2, col3 = st.columns(3)
            with col1:
                c_cliente = st.selectbox("Columna Cliente", df.columns, index=encontrar_indice_columna(df.columns, auto_cliente))
                c_estado = st.selectbox("Columna Estado", df.columns, index=encontrar_indice_columna(df.columns, auto_estado))
            with col2:
                c_ciudad = st.selectbox("Columna Ciudad", df.columns, index=encontrar_indice_columna(df.columns, auto_ciudad))
                c_costo = st.selectbox("Columna Costo Prov.", df.columns, index=encontrar_indice_columna(df.columns, auto_costo))
                c_valor_km = st.selectbox("Columna Valor Km Est.", df.columns, index=encontrar_indice_columna(df.columns, auto_valor_km))
            with col3:
                c_km = st.selectbox("Columna Km Est.", df.columns, index=encontrar_indice_columna(df.columns, auto_km))
                c_tiempo = st.selectbox("Columna Tiempo Est.", df.columns, index=encontrar_indice_columna(df.columns, auto_tiempo))

            if st.button("Procesar Revisión", type="primary"):
                df_res = df.copy()
                
                df_res['temp_cliente'] = df_res[c_cliente].astype(str).str.upper().str.strip()
                df_res['temp_estado'] = df_res[c_estado].astype(str).str.upper().str.strip()
                df_res['temp_ciudad'] = df_res[c_ciudad].astype(str).str.upper().str.strip()
                
                df_res['val_costo'] = df_res[c_costo].apply(clean_currency).fillna(0)
                df_res['val_total_km'] = df_res[c_valor_km].apply(clean_currency).fillna(0)
                df_res['val_km'] = df_res[c_km].apply(clean_currency).fillna(0)
                df_res['val_tiempo'] = df_res[c_tiempo].apply(clean_currency).fillna(0)

                mask_pasa_directo = df_res['temp_cliente'].isin(["BOOKING", "I NEED TOURS"])
                ciudades_validas = ["SANTIAGO", "VALPARAISO", "VALPARAÍSO"]
                mask_omitida = (df_res['temp_estado'] == "CANCELADA") | (~df_res['temp_ciudad'].isin(ciudades_validas))
                
                mask_auditoria = (~mask_pasa_directo) & (~mask_omitida)
                
                df_res['Resultado'] = "Pendiente"
                df_res['Motivo_Revision'] = ""

                # Reglas
                mask_costo_excesivo = mask_auditoria & (df_res['val_costo'] > df_res['val_total_km'])
                df_res.loc[mask_costo_excesivo, 'Motivo_Revision'] += "Costo Prov. supera Valor Km Est.; "

                mask_km_ok = df_res['val_km'] > 0
                val_por_km = df_res['val_total_km'] / df_res['val_km']
                mask_km_bajo = mask_auditoria & mask_km_ok & (val_por_km < 1000)
                df_res.loc[mask_km_bajo, 'Motivo_Revision'] += "Valor por KM es menor a 1000; "
                
                mask_tiempo_ok = df_res['val_tiempo'] > 0
                val_por_min = df_res['val_total_km'] / df_res['val_tiempo']
                mask_minuto_bajo = mask_auditoria & mask_tiempo_ok & (val_por_min <= 1000)
                df_res.loc[mask_minuto_bajo, 'Motivo_Revision'] += "Valor por minuto es menor o igual a 1000; "

                # Resultado Final
                df_res.loc[mask_pasa_directo, 'Resultado'] = "Aprobado (Cliente Especial)"
                df_res.loc[mask_omitida, 'Resultado'] = "Omitido (Cancelada/Otra Ciudad)"
                
                mask_audit_con_error = mask_auditoria & (df_res['Motivo_Revision'] != "")
                mask_audit_ok = mask_auditoria & (df_res['Motivo_Revision'] == "")
                
                df_res.loc[mask_audit_con_error, 'Resultado'] = "REVISIÓN"
                df_res.loc[mask_audit_ok, 'Resultado'] = "Aprobado (OK)"

                df_final = df_res.drop(columns=['temp_cliente', 'temp_estado', 'temp_ciudad', 'val_costo', 'val_total_km', 'val_km', 'val_tiempo'])

                st.success("Procesamiento completado.")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total", len(df_final))
                c2.metric("Aprobados", len(df_final[df_final['Resultado'].str.contains("Aprobado")]))
                c3.metric("A Revisión", len(df_final[df_final['Resultado'] == "REVISIÓN"]))
                c4.metric("Omitidos", len(df_final[df_final['Resultado'].str.contains("Omitido")]))

                tab1, tab2 = st.tabs(["⚠️ Solicitudes a Revisión", "✅ Todas las Solicitudes"])
                with tab1:
                    df_solo_revision = df_final[df_final['Resultado'] == "REVISIÓN"]
                    st.dataframe(df_solo_revision)
                with tab2:
                    st.dataframe(df_final)

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, sheet_name='Resultado_Completo', index=False)
                    if not df_solo_revision.empty:
                        df_solo_revision.to_excel(writer, sheet_name='Solo_Revision', index=False)
                
                st.download_button(
                    label="📥 Descargar Reporte (XLSX)",
                    data=buffer.getvalue(),
                    file_name="Revision_Solicitudes_Futuras.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

        except Exception as e:
            st.error(f"Error: {e}")

    else:
        st.info("Sube el archivo de solicitudes.")

# ==============================================================================
# MENU PRINCIPAL (SIDEBAR)
# ==============================================================================
st.sidebar.title("Menú")
opcion = st.sidebar.radio(
    "Selecciona una herramienta:",
    ["Procesar Vouchers", "Revisión Solicitudes"]
)

if opcion == "Procesar Vouchers":
    run_procesador_vouchers()
elif opcion == "Revisión Solicitudes":
    run_revision_solicitudes()
