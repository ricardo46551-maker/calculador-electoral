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

# --- 2. ESTILOS CSS (AZUL Y BLANCO) ---
st.markdown("""
<style>
    /* Forzar fondo blanco por si acaso */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Tarjetas con borde azul suave */
    .css-card {
        border-radius: 10px;
        padding: 20px;
        background-color: white;
        box-shadow: 0 4px 12px rgba(0, 51, 160, 0.1); /* Sombra azulada */
        border: 1px solid #e1e8f0;
        margin-bottom: 20px;
    }
    
    /* Títulos en Azul ONPE */
    h1, h2, h3 {
        color: #0033A0 !important;
        font-family: 'Arial', sans-serif;
    }
    
    /* Botones Azules */
    div.stButton > button:first-child {
        background-color: #0033A0;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #00227a; /* Azul más oscuro al pasar el mouse */
        color: white;
    }

    /* Ocultar menú de Streamlit */
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
            st.header("🇵🇪 ONPE")
    
    st.markdown("<h1 style='text-align: center;'>Asistente Electoral 2025</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Consulta oficial de multas y dispensas</p>", unsafe_allow_html=True)

    # TABS
    tab1, tab2, tab3 = st.tabs(["📊 Calculadora", "📄 Trámite Dispensa", "ℹ️ Ayuda"])

    # --- TAB 1: CALCULADORA ---
    with tab1:
        df = cargar_datos()
        
        # Contenedor visual
        with st.container():
            st.markdown("### 🔍 Consulta Ciudadana")
            st.info("Ingresa tus datos para verificar tu estado.")
            
            if not df.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Distrito de Votación**")
                    nombres = df['nombre'].tolist()
                    distrito = st.selectbox("Seleccione distrito", nombres, label_visibility="collapsed")
                    
                    # Datos del distrito
                    categoria = df[df['nombre'] == distrito]['categoria'].values[0]
                    st.caption(f"Clasificación: {categoria}")
                    
                    url_mapa = f"https://www.google.com/maps/search/ODPE+{distrito.replace(' ', '+')}"
                    st.markdown(f"[📍 Ver Oficina ODPE en Mapa]({url_mapa})")

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
                st.error("⚠️ Se han encontrado multas pendientes")
                
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
                st.success("🎉 ¡No registras multas estimadas!")
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