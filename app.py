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
    /* Fondo general (aseguramos que sea oscuro) */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Tarjetas Oscuras (Dark Cards) */
    .css-card {
        border-radius: 12px;
        padding: 20px;
        background-color: #1E212B; /* Gris azulado oscuro */
        border: 1px solid #30333F; /* Borde sutil */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    
    /* Textos con alto contraste */
    h1, h2, h3 {
        color: #ffffff !important; /* Blanco puro */
        font-family: 'Arial', sans-serif;
        text-shadow: 0px 0px 10px rgba(255, 255, 255, 0.1); /* Brillo sutil */
    }
    
    p, li, div {
        color: #e0e0e0; /* Blanco hueso para lectura cómoda */
    }

    /* Inputs (Cajas de texto) */
    .stTextInput input, .stSelectbox, .stTextArea textarea {
        color: #ffffff;
    }

    /* Botones Primarios (Rojo Neón para contraste) */
    div.stButton > button:first-child {
        background-color: #D91E18; /* Rojo Intenso */
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
        border: 1px solid #D91E18;
    }
    div.stButton > button:first-child:hover {
        background-color: #ff2b2b; /* Rojo más brillante al pasar el mouse */
        box-shadow: 0 0 15px rgba(217, 30, 24, 0.6); /* Efecto Glow/Resplandor */
        color: white;
    }

    /* Ocultar elementos de sistema */
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
            st.image("logo.png", use_column_width=True)
        except:
            st.markdown("<h1 style='text-align: center; font-size: 50px;'>🇵🇪</h1>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center;'>Asistente Electoral 2025</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a0a0a0;'>Modo Oscuro | Consulta oficial de multas</p>", unsafe_allow_html=True)

    # TABS
    tab1, tab2, tab3 = st.tabs(["📊 Calculadora", "📄 Trámite Dispensa", "ℹ️ Ayuda"])

    # --- TAB 1: CALCULADORA ---
    with tab1:
        df = cargar_datos()
        
        # Simulamos una tarjeta visual con st.container
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
                    # Etiqueta de color brillante
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

    # --- TAB 3: FAQ ---
    with tab3:
        st.markdown("### Preguntas Frecuentes")
        with st.expander("¿Hasta qué edad es obligatorio?"):
            st.write("Hasta los 70 años.")
        with st.expander("¿Cuánto es la multa 2025?"):
            st.write("Depende de tu distrito. Usa la calculadora para saber el monto exacto.")

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