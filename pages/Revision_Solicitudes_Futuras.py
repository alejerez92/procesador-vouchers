import streamlit as st
import pandas as pd
import io

# Configuración de la página
st.set_page_config(page_title="Revisión Solicitudes Futuras", layout="wide")

st.title("Revisión Solicitudes Futuras")
st.markdown("""
Sube el reporte de **Solicitudes** para aplicar las reglas de validación dinámica.
""")

# --- Funciones Auxiliares ---
def encontrar_columna_por_nombre(columnas, palabras_clave):
    columnas_lower = [c.lower() for c in columnas]
    for clave in palabras_clave:
        clave_lower = clave.lower()
        if clave_lower in columnas_lower:
            idx = columnas_lower.index(clave_lower)
            return columnas[idx]
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

def clean_numeric(x):
    if isinstance(x, str):
        x = x.replace('$', '').replace(',', '').strip()
    return pd.to_numeric(x, errors='coerce')

# --- Carga de Archivo ---
archivo_solicitudes = st.file_uploader("Cargar Reporte de Solicitudes (XLSX)", type=["xlsx"])

if archivo_solicitudes:
    try:
        df = pd.read_excel(archivo_solicitudes)
        df.columns = df.columns.str.strip()

        st.divider()
        st.subheader("1. Configuración de Columnas")
        
        # Auto-detección
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
            # Copia para no alterar original
            df_res = df.copy()
            
            # Normalización y Limpieza
            df_res['temp_cliente'] = df_res[c_cliente].astype(str).str.upper().str.strip()
            df_res['temp_estado'] = df_res[c_estado].astype(str).str.upper().str.strip()
            df_res['temp_ciudad'] = df_res[c_ciudad].astype(str).str.upper().str.strip()
            
            df_res['val_costo'] = df_res[c_costo].apply(clean_numeric).fillna(0)
            df_res['val_total_km'] = df_res[c_valor_km].apply(clean_numeric).fillna(0)
            df_res['val_km'] = df_res[c_km].apply(clean_numeric).fillna(0)
            df_res['val_tiempo'] = df_res[c_tiempo].apply(clean_numeric).fillna(0)

            # Clasificación Inicial
            # 1. Booking / I Need Tours -> PASAN DIRECTO
            mask_pasa_directo = df_res['temp_cliente'].isin(["BOOKING", "I NEED TOURS"])
            
            # 2. Canceladas o Ciudades fuera de Santiago/Valparaíso -> OMITIDAS (No se revisan)
            # Definimos lista con y sin tildes por seguridad
            ciudades_validas = ["SANTIAGO", "VALPARAISO", "VALPARAÍSO"]
            mask_omitida = (df_res['temp_estado'] == "CANCELADA") | (~df_res['temp_ciudad'].isin(ciudades_validas))
            
            # 3. El resto entra a AUDITORÍA
            mask_auditoria = (~mask_pasa_directo) & (~mask_omitida)
            
            df_res['Resultado'] = "Pendiente"
            df_res['Motivo_Revision'] = ""

            # Aplicar reglas solo a los de auditoría
            # Regla A: Costo proveedor > Valor Km estimado
            mask_costo_excesivo = mask_auditoria & (df_res['val_costo'] > df_res['val_total_km'])
            df_res.loc[mask_costo_excesivo, 'Motivo_Revision'] += "Costo Prov. supera Valor Km Est.; "

            # Regla B: Valor por Km < 1000
            # Evitar división por cero
            mask_km_ok = df_res['val_km'] > 0
            val_por_km = df_res['val_total_km'] / df_res['val_km']
            mask_km_bajo = mask_auditoria & mask_km_ok & (val_por_km < 1000)
            df_res.loc[mask_km_bajo, 'Motivo_Revision'] += "Valor por KM es menor a 1000; "
            
            # Regla C: Valor por Minuto <= 1000
            mask_tiempo_ok = df_res['val_tiempo'] > 0
            val_por_min = df_res['val_total_km'] / df_res['val_tiempo']
            mask_minuto_bajo = mask_auditoria & mask_tiempo_ok & (val_por_min <= 1000)
            df_res.loc[mask_minuto_bajo, 'Motivo_Revision'] += "Valor por minuto es menor o igual a 1000; "

            # Definir estados finales
            df_res.loc[mask_pasa_directo, 'Resultado'] = "Aprobado (Cliente Especial)"
            df_res.loc[mask_omitida, 'Resultado'] = "Omitido (Cancelada/Otra Ciudad)"
            
            # Para los de auditoría: si tienen motivo son Revisión, si no, son Aprobados
            mask_audit_con_error = mask_auditoria & (df_res['Motivo_Revision'] != "")
            mask_audit_ok = mask_auditoria & (df_res['Motivo_Revision'] == "")
            
            df_res.loc[mask_audit_con_error, 'Resultado'] = "REVISIÓN"
            df_res.loc[mask_audit_ok, 'Resultado'] = "Aprobado (OK)"

            # Limpiar columnas temporales
            df_final = df_res.drop(columns=['temp_cliente', 'temp_estado', 'temp_ciudad', 'val_costo', 'val_total_km', 'val_km', 'val_tiempo'])

            # Mostrar Resumen
            st.success("Procesamiento completado.")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total", len(df_final))
            c2.metric("Aprobados", len(df_final[df_final['Resultado'].str.contains("Aprobado")]))
            c3.metric("A Revisión", len(df_final[df_final['Resultado'] == "REVISIÓN"]))
            c4.metric("Omitidos", len(df_final[df_final['Resultado'].str.contains("Omitido")]))

            # Separar en pestañas para visualización
            tab1, tab2 = st.tabs(["⚠️ Solicitudes a Revisión", "✅ Todas las Solicitudes"])
            with tab1:
                df_solo_revision = df_final[df_final['Resultado'] == "REVISIÓN"]
                st.dataframe(df_solo_revision)
            with tab2:
                st.dataframe(df_final)

            # Descarga
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, sheet_name='Resultado_Completo', index=False)
                if not df_solo_revision.empty:
                    df_solo_revision.to_excel(writer, sheet_name='Solo_Revision', index=False)
            
            st.download_button(
                label="📥 Descargar Reporte de Revisión (XLSX)",
                data=buffer.getvalue(),
                file_name="Revision_Solicitudes_Futuras.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

    except Exception as e:
        st.error(f"Error en el procesamiento: {e}")
        st.exception(e)

else:
    st.info("Sube el archivo de solicitudes para aplicar las reglas.")