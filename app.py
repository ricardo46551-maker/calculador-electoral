import streamlit as st
import pandas as pd
import json
import urllib.parse 
import os
import io
from datetime import datetime
from modules.calculadora import CalculadoraElectoral
from modules.generador_pdf import crear_pdf_dispensa

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Asistente Electoral 2026", 
    page_icon="🇵🇪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. SISTEMA DE REGISTRO (LOGS CON EXCEL) ---
ARCHIVO_REGISTRO = "registro_consultas.csv"

def guardar_consulta(dni, distrito, categoria, tiene_deuda):
    """Guarda cada interacción incluyendo el DNI"""
    fecha = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M:%S")
    
    dni_guardar = dni if dni and len(dni) >= 8 else "Anónimo"
    
    nuevo_dato = {
        "fecha": fecha,
        "hora": hora,
        "dni": dni_guardar,
        "distrito": distrito,
        "categoria": categoria,
        "tiene_deuda": "SI" if tiene_deuda else "NO"
    }
    
    if not os.path.exists(ARCHIVO_REGISTRO):
        df = pd.DataFrame([nuevo_dato])
        df.to_csv(ARCHIVO_REGISTRO, index=False)
    else:
        df_existente = pd.read_csv(ARCHIVO_REGISTRO)
        # Verificamos si existe la columna DNI para evitar errores con archivos viejos
        if "dni" not in df_existente.columns:
            df_new = pd.DataFrame([nuevo_dato])
            df_final = pd.concat([df_existente, df_new], ignore_index=True)
            df_final.to_csv(ARCHIVO_REGISTRO, index=False)
        else:
            df_new = pd.DataFrame([nuevo_dato])
            df_new.to_csv(ARCHIVO_REGISTRO, mode='a', header=False, index=False)

def cargar_registros():
    if os.path.exists(ARCHIVO_REGISTRO):
        return pd.read_csv(ARCHIVO_REGISTRO)
    return pd.DataFrame()

# --- 3. ESTILOS CSS (MODO OSCURO) ---
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
    
    st.markdown("<h1 style='text-align: center;'>Asistente Electoral 2026</h1>", unsafe_allow_html=True)
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
                st.markdown("**1. Identificación**")
                dni_consulta = st.text_input("Ingresa tu DNI (Opcional para registro)", max_chars=8, help="Se usará para generar tu reporte")
                
                st.divider() 
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**2. Ubicación**")
                    nombres = df['nombre'].tolist()
                    distrito = st.selectbox("Distrito de Votación", nombres, label_visibility="collapsed")
                    
                    categoria = df[df['nombre'] == distrito]['categoria'].values[0]
                    color_tag = "#00c853" if categoria == "No Pobre" else "#ffab00"
                    st.markdown(f"<span style='color:{color_tag}; font-weight:bold;'>• Clasificación: {categoria}</span>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    url_mapa = f"https://www.google.com/maps/search/ODPE+{distrito.replace(' ', '+')}"
                    st.link_button("📍 Ver Oficina en Mapa", url_mapa)

                with col2:
                    st.markdown("**3. Participación**")
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

            # REGISTRO
            guardar_consulta(dni_consulta, distrito, categoria, total > 0)

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

    # --- TAB 3: FAQ (PREGUNTAS AMPLIADAS) ---
    with tab3:
        st.markdown("### 📚 Centro de Ayuda al Elector")
        st.markdown("Resolvemos tus dudas sobre el proceso electoral 2025.")
        
        preguntas_frecuentes = [
            ("📆 ¿Hasta qué edad es obligatorio votar?", 
             "El voto es obligatorio desde los **18 hasta los 70 años**. Para los mayores de 70 años, el voto es facultativo (opcional), por lo que no generan multa si deciden no asistir."),
            
            ("💰 ¿Cuánto es la multa en 2025?", 
             "Depende de la clasificación socioeconómica de tu distrito (No Pobre, Pobre, Pobre Extremo) y de la UIT vigente (S/ 5,350). Puede variar entre **S/ 26.75** y **S/ 107.00** por omisión al voto."),
            
            ("🆔 ¿Puedo votar con mi DNI vencido?", 
             "**SÍ.** El RENIEC suele emitir una resolución que prorroga la vigencia de los DNI caducos exclusivamente para el día de las elecciones. No obstante, se recomienda renovarlo para otros trámites."),
            
            ("⚠️ Me robaron el DNI, ¿Qué hago?", 
             "Si no tienes DNI físico el día de la votación, no podrás votar y se generará multa. Debes tramitar una **Dispensa** al día siguiente adjuntando la denuncia policial por robo o pérdida (la denuncia debe tener fecha anterior a la elección)."),

            ("🤔 ¿Cuál es la diferencia entre Justificación y Dispensa?", 
             "**Justificación:** Se solicita cuando fuiste elegido miembro de mesa y no pudiste asistir (multa de S/ 267.50). \n\n**Dispensa:** Se solicita cuando no fuiste a votar (multa de S/ 26.75 a S/ 107.00)."),

            ("✈️ ¿Si estoy en el extranjero tengo multa?", 
             "Si tu DNI tiene dirección en el extranjero, no tienes multa. Si tu DNI dice que vives en Perú pero estabas de viaje, **SÍ** tienes multa, a menos que tramites una dispensa probando estudios o salud."),

            ("💳 ¿Dónde pago mis multas acumuladas?", 
             "Puedes pagarlas en la plataforma **Págalo.pe** (del Banco de la Nación) o presencialmente en cualquier agencia del banco. Conserva siempre tu voucher de pago.")
        ]
        
        for pregunta, respuesta in preguntas_frecuentes:
            with st.expander(pregunta):
                st.markdown(respuesta)

    # --- FOOTER ---
    st.divider()
    col_ft1, col_ft2 = st.columns([1,3])
    with col_ft1:
        link_wa = f"https://wa.me/?text={urllib.parse.quote('Calcula tus multas aquí: https://calculador-electoral.onrender.com')}"
        st.link_button("📲 Compartir", link_wa)
    
    # --- CRÉDITOS DEL EQUIPO (AQUÍ ESTÁN) ---
    with col_ft2:
        st.markdown("**Equipo de Desarrollo:**")
        st.caption("👨‍💻 Ricardo Condori | Manuel Serra | Pablo Huasasquiche | Cristhian Arotoma | Arnold Cocha")
        st.caption("© 2025 Herramienta Ciudadana Independiente")

    # ==========================================
    # 🔐 ZONA ADMIN
    # ==========================================
    st.sidebar.markdown("---")
    with st.sidebar.expander("🔐 Acceso Admin"):
        if not st.session_state['admin_logged_in']:
            contra = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if contra == "admin123": 
                    st.session_state['admin_logged_in'] = True
                    st.rerun()
                else:
                    st.error("Acceso denegado")
        
        else:
            st.success("✅ Sesión Activa")
            if st.button("Cerrar Sesión"):
                st.session_state['admin_logged_in'] = False
                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📊 Dashboard de Control")
            
            df_logs = cargar_registros()
            
            if not df_logs.empty:
                # KPIs
                total_consultas = len(df_logs)
                if 'dni' in df_logs.columns:
                    dnis_capturados = df_logs[df_logs['dni'] != 'Anónimo']['dni'].nunique()
                else:
                    dnis_capturados = 0
                
                kpi1, kpi2 = st.columns(2)
                kpi1.metric("Total Consultas", total_consultas)
                kpi2.metric("DNIs Capturados", dnis_capturados)
                
                # Gráficos
                st.markdown("#### 🏆 Distritos Top")
                st.bar_chart(df_logs['distrito'].value_counts().head(5))
                
                # Tabla
                st.markdown("#### 📋 Vista Previa")
                st.dataframe(df_logs.tail(5))
                
                # Descarga Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_logs.to_excel(writer, index=False, sheet_name='Reporte')
                
                st.download_button(
                    label="📥 Descargar Excel (.xlsx)",
                    data=buffer,
                    file_name="reporte_visitas_2025.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("Aún no hay registros de visitas.")

if __name__ == '__main__':
    main()