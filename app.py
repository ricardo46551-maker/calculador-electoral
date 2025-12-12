import streamlit as st
import pandas as pd
import json
import urllib.parse 
import os
from datetime import datetime
from modules.calculadora import CalculadoraElectoral
from modules.generador_pdf import crear_pdf_dispensa

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Asistente Electoral 2025", 
    page_icon="🇵🇪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. SISTEMA DE REGISTRO (LOGS) ---
ARCHIVO_REGISTRO = "registro_consultas.csv"

def guardar_consulta(distrito, categoria, tiene_deuda):
    """Guarda cada interacción en un archivo CSV local"""
    fecha = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M:%S")
    
    nuevo_dato = {
        "fecha": fecha,
        "hora": hora,
        "distrito": distrito,
        "categoria": categoria,
        "tiene_deuda": "SI" if tiene_deuda else "NO"
    }
    
    # Si el archivo no existe, crearlo con cabeceras
    if not os.path.exists(ARCHIVO_REGISTRO):
        df = pd.DataFrame([nuevo_dato])
        df.to_csv(ARCHIVO_REGISTRO, index=False)
    else:
        # Si existe, agregar la nueva fila
        df_new = pd.DataFrame([nuevo_dato])
        df_new.to_csv(ARCHIVO_REGISTRO, mode='a', header=False, index=False)

def cargar_registros():
    """Lee el archivo de registros para el dashboard"""
    if os.path.exists(ARCHIVO_REGISTRO):
        return pd.read_csv(ARCHIVO_REGISTRO)
    return pd.DataFrame()

# --- 3. ESTILOS CSS (DARK MODE) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .css-card {
        border-radius: 12px; padding: 20px; background-color: #1E212B;
        border: 1px solid #30333F; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 20px;
    }
    h1, h2, h3 { color: #ffffff !important; font-family: 'Arial', sans-serif; }
    p, li, div { color: #e0e0e0; }
    .stTextInput input, .stSelectbox, .stTextArea textarea { color: #ffffff; }
    div.stButton > button:first-child {
        background-color: #D91E18; color: white; border-radius: 8px; font-weight: bold; border: 1px solid #D91E18;
    }
    div.stButton > button:first-child:hover {
        background-color: #ff2b2b; box-shadow: 0 0 15px rgba(217, 30, 24, 0.6); color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. MEMORIA DE SESIÓN ---
if 'deuda_actual' not in st.session_state:
    st.session_state['deuda_actual'] = 0.0
if 'desglose_actual' not in st.session_state:
    st.session_state['desglose_actual'] = []
# Estado para el login de admin
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

# --- 5. CARGA DE DATOS ---
def cargar_datos():
    try:
        with open('data/distritos.json', 'r', encoding='utf-8') as f:
            return pd.DataFrame(json.load(f))
    except FileNotFoundError:
        st.error("⚠️ Error: Base de datos no encontrada.")
        return pd.DataFrame()

# --- 6. INTERFAZ PRINCIPAL ---
def main():
    # ENCABEZADO
    col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])
    with col_logo2:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.markdown("<h1 style='text-align: center;'>🇵🇪</h1>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center;'>Asistente Electoral 2025</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a0a0a0;'>Modo Oscuro | Consulta oficial de multas</p>", unsafe_allow_html=True)

    # TABS
    tab1, tab2, tab3 = st.tabs(["📊 Calculadora", "📄 Trámite Dispensa", "ℹ️ Ayuda & FAQ"])

    # --- TAB 1: CALCULADORA ---
    with tab1:
        df = cargar_datos()
        
        with st.container():
            st.markdown("### 🔍 Consulta Ciudadana")
            st.info("Ingresa tus datos para verificar tu estado.")
            
            if not df.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Distrito de Votación**")
                    nombres = df['nombre'].tolist()
                    distrito = st.selectbox("Seleccione distrito", nombres, label_visibility="collapsed")
                    
                    categoria = df[df['nombre'] == distrito]['categoria'].values[0]
                    color_tag = "#00c853" if categoria == "No Pobre" else "#ffab00"
                    st.markdown(f"<span style='color:{color_tag}; font-weight:bold;'>• Clasificación: {categoria}</span>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    url_mapa = f"https://www.google.com/maps/search/ODPE+{distrito.replace(' ', '+')}"
                    st.link_button("📍 Ver Oficina en Mapa", url_mapa)

                with col2:
                    st.markdown("**Participación**")
                    es_miembro = st.toggle("Fui Miembro de Mesa")
                    asistio_mesa = False
                    if es_miembro:
                        asistio_mesa = st.checkbox("✅ Asistí a instalar")
                    voto = st.checkbox("✅ Fui a votar")

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("CONSULTAR MULTAS", type="primary"):
            paga_mesa = es_miembro and not asistio_mesa
            calc = CalculadoraElectoral()
            total, desglose = calc.calcular_deuda(paga_mesa, voto, categoria)
            
            st.session_state['deuda_actual'] = total
            st.session_state['desglose_actual'] = desglose

            # --- REGISTRAR LA CONSULTA (NUEVO) ---
            # Guardamos cada vez que alguien usa la app
            guardar_consulta(distrito, categoria, total > 0)
            # -------------------------------------

            if total > 0:
                st.error("⚠️ DEUDA DETECTADA")
                with st.container():
                    col_res1, col_res2 = st.columns([2,1])
                    with col_res1:
                        for item in desglose:
                            st.write(f"• {item}")
                    with col_res2:
                        st.metric(label="Total a Pagar", value=f"S/ {total:.2f}")
                st.markdown("---")
                st.link_button("💳 PAGAR EN PÁGALO.PE", "https://www.pagalo.pe/", use_container_width=True)
            else:
                st.success("🎉 ¡LIMPIO! No tienes multas pendientes.")
                st.balloons()
                st.session_state['deuda_actual'] = 0.0

    # --- TAB 2: PDF ---
    with tab2:
        st.markdown("### 📝 Solicitud de Dispensa")
        monto = st.session_state['deuda_actual']
        if monto > 0:
            st.warning(f"Generando solicitud por deuda de: S/ {monto:.2f}")
        
        with st.form("form_carta"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                nombre = st.text_input("Nombres Completos")
            with col_f2:
                dni = st.text_input("DNI")
            motivo = st.text_area("Motivo de la dispensa")
            generar = st.form_submit_button("GENERAR PDF")

        if generar:
            if nombre and dni and motivo:
                pdf = crear_pdf_dispensa(nombre, dni, motivo, "Mi Distrito")
                st.success("Documento generado correctamente.")
                st.download_button("⬇️ DESCARGAR PDF", pdf, "solicitud.pdf", "application/pdf")
            else:
                st.warning("Completa todos los campos.")

    # --- TAB 3: FAQ ---
    with tab3:
        st.markdown("### 📚 Centro de Ayuda")
        preguntas_frecuentes = [
            ("📆 ¿Hasta qué edad es obligatorio votar?", "Hasta los 70 años. Mayores de 70 es opcional."),
            ("💰 ¿Cuánto es la multa 2025?", "Varía entre S/ 26.75 y S/ 107.00 según tu distrito."),
            ("🆔 ¿Puedo votar con DNI vencido?", "SÍ. RENIEC suele autorizarlo para el día de la elección."),
            ("💳 ¿Dónde pago?", "En Págalo.pe o Banco de la Nación.")
        ]
        for p, r in preguntas_frecuentes:
            with st.expander(p):
                st.write(r)

    # --- FOOTER ---
    st.divider()
    col_ft1, col_ft2 = st.columns([1,3])
    with col_ft1:
        link_wa = f"https://wa.me/?text={urllib.parse.quote('Calcula tus multas: https://calculador-electoral.onrender.com')}"
        st.link_button("📲 Compartir", link_wa)
    with col_ft2:
        st.caption("Desarrollado por: Equipo de Desarrollo 2025")

    # ==========================================
    # 🔐 ZONA ADMIN (PANEL OCULTO)
    # ==========================================
    st.sidebar.markdown("---")
    with st.sidebar.expander("🔐 Acceso Admin"):
        if not st.session_state['admin_logged_in']:
            contra = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if contra == "admin123": # <--- CAMBIA TU CONTRASEÑA AQUÍ
                    st.session_state['admin_logged_in'] = True
                    st.rerun()
                else:
                    st.error("Acceso denegado")
        
        else:
            # SI YA ESTÁ LOGUEADO, MOSTRAR EL DASHBOARD
            st.success("✅ Sesión Activa")
            if st.button("Cerrar Sesión"):
                st.session_state['admin_logged_in'] = False
                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📊 Métricas de Uso")
            
            df_logs = cargar_registros()
            
            if not df_logs.empty:
                # 1. KPIs
                total_consultas = len(df_logs)
                deudores = len(df_logs[df_logs['tiene_deuda'] == "SI"])
                
                kpi1, kpi2 = st.columns(2)
                kpi1.metric("Total Consultas", total_consultas)
                kpi2.metric("Con Multas", f"{deudores} ({int(deudores/total_consultas*100)}%)")
                
                # 2. Gráfico: Top Distritos
                st.markdown("#### 🏆 Distritos con más consultas")
                conteo_distritos = df_logs['distrito'].value_counts().head(5)
                st.bar_chart(conteo_distritos)
                
                # 3. Gráfico: Cronología
                st.markdown("#### 📈 Actividad por Fecha")
                actividad_fecha = df_logs['fecha'].value_counts().sort_index()
                st.line_chart(actividad_fecha)
                
                # 4. Descargar Data
                st.markdown("#### 📥 Descargar Datos")
                csv = df_logs.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Descargar Reporte Completo (CSV)",
                    csv,
                    "reporte_visitas.csv",
                    "text/csv"
                )
                
                # 5. Tabla de últimos registros
                with st.expander("Ver últimos 10 registros"):
                    st.dataframe(df_logs.tail(10))
                    
            else:
                st.info("Aún no hay registros de visitas.")

if __name__ == '__main__':
    main()