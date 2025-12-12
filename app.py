import streamlit as st
import pandas as pd
import json
import urllib.parse 
from modules.calculadora import CalculadoraElectoral
from modules.generador_pdf import crear_pdf_dispensa

# --- 1. CONFIGURACIÓN DE PÁGINA PROFESIONAL ---
st.set_page_config(
    page_title="Asistente Electoral 2025", 
    page_icon="🇵🇪",
    layout="centered", # 'centered' se ve más elegante para formularios que 'wide'
    initial_sidebar_state="collapsed"
)

# --- 2. ESTILOS CSS PERSONALIZADOS (EL SECRETO DEL DISEÑO) ---
st.markdown("""
<style>
    /* Estilo para el fondo y contenedores */
    .stApp {
        background-color: #f4f6f9;
    }
    
    /* Estilo para las 'Tarjetas' (Contenedores blancos con sombra) */
    .css-card {
        border-radius: 10px;
        padding: 20px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* Títulos más elegantes */
    h1 {
        color: #2c3e50;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        margin-bottom: 0px;
    }
    h2, h3 {
        color: #34495e;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Botones primarios más llamativos */
    div.stButton > button:first-child {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }

    /* Ocultar elementos molestos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. INICIALIZACIÓN DE MEMORIA ---
if 'deuda_actual' not in st.session_state:
    st.session_state['deuda_actual'] = 0.0
if 'desglose_actual' not in st.session_state:
    st.session_state['desglose_actual'] = []

# --- 4. FUNCIÓN DE CARGA ---
def cargar_datos():
    try:
        with open('data/distritos.json', 'r', encoding='utf-8') as f:
            return pd.DataFrame(json.load(f))
    except FileNotFoundError:
        st.error("⚠️ Error crítico: Base de datos no encontrada.")
        return pd.DataFrame()

# --- 5. INTERFAZ PRINCIPAL ---
def main():
    # --- ENCABEZADO TIPO HERO ---
    col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])
    with col_logo2:
        try:
            st.image("logo.png", use_column_width=True)
        except:
            st.markdown("<h1 style='font-size: 60px;'>🇵🇪</h1>", unsafe_allow_html=True)
    
    st.markdown("<h1>Asistente Electoral 2025</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d; margin-bottom: 30px;'>Consulta de multas, ubicación de oficinas y gestión de dispensas.</p>", unsafe_allow_html=True)

    # --- NAVEGACIÓN ESTILIZADA ---
    tab1, tab2, tab3 = st.tabs(["📊 Calculadora & Pagos", "📄 Generar Trámite", "ℹ️ Ayuda & Dudas"])

    # ==========================
    # PESTAÑA 1: CALCULADORA
    # ==========================
    with tab1:
        df = cargar_datos()
        
        # Usamos st.container para agrupar visualmente (efecto tarjeta)
        with st.container():
            st.markdown("### 🔍 Tu Información Electoral")
            st.info("Selecciona los datos para simular tu situación actual.")
            
            if not df.empty:
                col_input1, col_input2 = st.columns(2)
                
                with col_input1:
                    st.markdown("**¿Dónde votas?**")
                    nombres_distritos = df['nombre'].tolist()
                    distrito = st.selectbox("Seleccione distrito", nombres_distritos, label_visibility="collapsed")
                    
                    # Logic para categoria
                    categoria = df[df['nombre'] == distrito]['categoria'].values[0]
                    
                    # Badge de categoría
                    color_badge = "blue" if categoria == "No Pobre" else "orange"
                    st.markdown(f"<span style='background-color:{color_badge}; color:white; padding: 4px 8px; border-radius: 4px; font-size: 12px;'>{categoria}</span>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    url_mapa = f"https://www.google.com/maps/search/ODPE+{distrito.replace(' ', '+')}"
                    st.link_button("📍 Ver Oficina en Mapa", url_mapa)

                with col_input2:
                    st.markdown("**Tu participación**")
                    es_miembro = st.toggle("Fui Miembro de Mesa")
                    
                    asistio_mesa = False
                    if es_miembro:
                        asistio_mesa = st.checkbox("✅ Asistí a instalar")
                    
                    voto = st.checkbox("✅ Fui a votar")

        st.markdown("---")

        # Botón de Acción Principal
        col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
        with col_btn2:
            calcular = st.button("CALCULAR MI ESTADO", type="primary")

        if calcular:
            paga_mesa = es_miembro and not asistio_mesa
            calc = CalculadoraElectoral()
            total, desglose = calc.calcular_deuda(paga_mesa, voto, categoria)
            
            st.session_state['deuda_actual'] = total
            st.session_state['desglose_actual'] = desglose

            if total > 0:
                # Diseño de Alerta de Deuda
                st.error("⚠️ Se han detectado multas pendientes")
                
                # Tarjeta de Resultado
                with st.container():
                    col_res1, col_res2 = st.columns([2,1])
                    with col_res1:
                        st.markdown("#### Detalle:")
                        for item in desglose:
                            st.write(f"• {item}")
                    with col_res2:
                        st.metric(label="Total a Pagar", value=f"S/ {total:.2f}")
                
                # Call to Action: Pagar
                st.markdown("<br>", unsafe_allow_html=True)
                st.link_button("💳 PAGAR AHORA (Págalo.pe)", "https://www.pagalo.pe/", use_container_width=True)
                
            else:
                st.success("🎉 ¡Excelente! No tienes deudas estimadas.")
                st.balloons()
                st.session_state['deuda_actual'] = 0.0

    # ==========================
    # PESTAÑA 2: DOCUMENTOS
    # ==========================
    with tab2:
        st.markdown("### 📝 Generador de Solicitudes")
        st.markdown("Si tienes una justificación válida, genera tu documento oficial aquí.")
        
        # Panel lateral de estado
        monto = st.session_state['deuda_actual']
        if monto > 0:
            st.warning(f"💡 Estás gestionando una dispensa por: **S/ {monto:.2f}**")
        
        with st.container():
            with st.form("form_carta"):
                col_form1, col_form2 = st.columns(2)
                with col_form1:
                    nombre_usuario = st.text_input("Nombres y Apellidos")
                with col_form2:
                    dni_usuario = st.text_input("DNI / CE")
                
                motivo_usuario = st.text_area("Detalle de la justificación (Sé claro y breve)")
                
                st.caption("Al generar este documento, declaras que la información es verdadera.")
                generar = st.form_submit_button("📄 GENERAR DOCUMENTO PDF")

        if generar:
            if nombre_usuario and dni_usuario and motivo_usuario:
                distrito_actual = "Mi Distrito" 
                pdf_buffer = crear_pdf_dispensa(nombre_usuario, dni_usuario, motivo_usuario, distrito_actual)
                
                st.success("¡Documento listo!")
                
                col_d1, col_d2, col_d3 = st.columns([1,2,1])
                with col_d2:
                    st.download_button(
                        label="⬇️ DESCARGAR PDF OFICIAL",
                        data=pdf_buffer,
                        file_name="Solicitud_Dispensa_2025.pdf",
                        mime="application/pdf",
                        type="primary"
                    )
            else:
                st.warning("⚠️ Por favor completa todos los campos requeridos.")

    # ==========================
    # PESTAÑA 3: FAQ
    # ==========================
    with tab3:
        st.markdown("### 📚 Centro de Ayuda")
        
        preguntas = [
            ("¿Hasta qué edad es obligatorio votar?", "Desde los 18 hasta los 70 años. Mayores de 70 es facultativo."),
            ("¿Qué pasa si no pago?", "No podrás realizar trámites notariales, ser funcionario público ni inscribir actos en SUNARP."),
            ("¿Cómo tramito una dispensa?", "Es 100% virtual a través de la página del JNE, adjuntando tu PDF generado aquí y las pruebas."),
            ("¿La UIT cambia?", "Sí, en 2025 la UIT es de S/ 5,350. Los montos de esta app están actualizados.")
        ]
        
        for preg, resp in preguntas:
            with st.expander(f"❓ {preg}"):
                st.write(resp)

    # --- FOOTER ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.divider()
    
    # Share Section
    texto_whatsapp = "Consulta tus multas electorales 2025 aquí: https://calculador-electoral.onrender.com"
    link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_whatsapp)}"
    
    col_f1, col_f2 = st.columns([1, 4])
    with col_f1:
        st.link_button("📲 Compartir", link_wa)
    with col_f2:
        st.caption("Desarrollado por: **Ricardo Condori, Manuel Serra, Pablo Huasasquiche, Cristhian Arotoma**")
        st.caption("© 2025 Herramienta Ciudadana Independiente v2.0 Pro")

if __name__ == '__main__':
    main()