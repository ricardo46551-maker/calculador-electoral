import streamlit as st
import pandas as pd
import json
import urllib.parse 
from modules.calculadora import CalculadoraElectoral
from modules.generador_pdf import crear_pdf_dispensa

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Asistente Electoral 2025", 
    page_icon="🇵🇪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. ESTILOS CSS (MODO OSCURO / DARK MODE) ---
st.markdown("""
<style>
    /* Fondo general */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Tarjetas Oscuras */
    .css-card {
        border-radius: 12px;
        padding: 20px;
        background-color: #1E212B;
        border: 1px solid #30333F;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    
    /* Textos */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Arial', sans-serif;
        text-shadow: 0px 0px 10px rgba(255, 255, 255, 0.1);
    }
    
    p, li, div {
        color: #e0e0e0;
    }

    /* Inputs */
    .stTextInput input, .stSelectbox, .stTextArea textarea {
        color: #ffffff;
    }

    /* Botones */
    div.stButton > button:first-child {
        background-color: #D91E18;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
        border: 1px solid #D91E18;
    }
    div.stButton > button:first-child:hover {
        background-color: #ff2b2b;
        box-shadow: 0 0 15px rgba(217, 30, 24, 0.6);
        color: white;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. MEMORIA ---
if 'deuda_actual' not in st.session_state:
    st.session_state['deuda_actual'] = 0.0
if 'desglose_actual' not in st.session_state:
    st.session_state['desglose_actual'] = []

# --- 4. CARGA DE DATOS ---
def cargar_datos():
    try:
        with open('data/distritos.json', 'r', encoding='utf-8') as f:
            return pd.DataFrame(json.load(f))
    except FileNotFoundError:
        st.error("⚠️ Error: Base de datos no encontrada.")
        return pd.DataFrame()

# --- 5. INTERFAZ PRINCIPAL ---
def main():
    # ENCABEZADO
    col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])
    with col_logo2:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.markdown("<h1 style='text-align: center; font-size: 50px;'>🇵🇪</h1>", unsafe_allow_html=True)
    
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
                st.write("**Opciones de Pago:**")
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

    # --- TAB 3: FAQ (AMPLIADO) ---
    with tab3:
        st.markdown("### 📚 Centro de Ayuda al Elector")
        st.markdown("Respuestas a las dudas más comunes sobre el proceso 2025.")
        
        # Lista ampliada de preguntas
        preguntas_frecuentes = [
            ("📆 ¿Hasta qué edad es obligatorio votar?", 
             "El voto es obligatorio desde los 18 hasta los 70 años. Para los mayores de 70 años es facultativo (opcional), por lo que no generan multa si no asisten."),
            
            ("💰 ¿Cuánto es la multa en 2025?", 
             "Depende de la clasificación de tu distrito (Pobre, No Pobre, Extremo) y de la UIT vigente (S/ 5,350). Usa la **Calculadora** en la primera pestaña para ver tu monto exacto."),
            
            ("🆔 ¿Puedo votar con mi DNI vencido?", 
             "**SÍ.** El RENIEC suele prorrogar la vigencia de los DNI caducos o por caducar exclusivamente para el día de las elecciones, permitiendo que todos ejerzan su derecho al voto."),
            
            ("🚫 Si tengo multas antiguas, ¿puedo votar?", 
             "**SÍ.** Nadie puede impedirte votar, incluso si tienes multas pendientes de años anteriores. Sin embargo, la deuda seguirá acumulándose y podría llegar a cobranza coactiva."),
            
            ("🤰 ¿Si estoy embarazada o lactando tengo multa?", 
             "Sí, si no asistes se genera la multa, **PERO** puedes pedir una **Dispensa** (trámite gratuito) ante el JNE presentando tu certificado médico o partida de nacimiento del bebé."),
            
            ("💳 ¿Dónde pago mis multas?", 
             "Puedes pagarlas en la plataforma **Págalo.pe** del Banco de la Nación, o presencialmente en las agencias del banco. Conserva tu voucher."),
             
            ("📉 ¿Cuándo prescriben las multas?", 
             "Las multas electorales pueden prescribir a los 4 años, pero debes solicitar la prescripción formalmente ante el JNE. No es automático.")
        ]
        
        for pregunta, respuesta in preguntas_frecuentes:
            with st.expander(pregunta):
                st.markdown(respuesta)

    # FOOTER
    st.divider()
    col_ft1, col_ft2 = st.columns([1,3])
    with col_ft1:
        link_wa = f"https://wa.me/?text={urllib.parse.quote('Consulta tus multas aquí: https://calculador-electoral.onrender.com')}"
        st.link_button("📲 Compartir", link_wa)
    with col_ft2:
        st.caption("Desarrollado por: Ricardo Condori, Manuel Serra, Pablo Huasasquiche, Cristhian Arotoma")

if __name__ == '__main__':
    main()