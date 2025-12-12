import streamlit as st
import pandas as pd
import json
import urllib.parse 
from modules.calculadora import CalculadoraElectoral
from modules.generador_pdf import crear_pdf_dispensa

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Calculadora Electoral", page_icon="🇵🇪")

# 2. INICIALIZACIÓN DE MEMORIA
if 'deuda_actual' not in st.session_state:
    st.session_state['deuda_actual'] = 0.0
if 'desglose_actual' not in st.session_state:
    st.session_state['desglose_actual'] = []

# 3. FUNCIÓN DE CARGA DE DATOS
def cargar_datos():
    try:
        with open('data/distritos.json', 'r', encoding='utf-8') as f:
            return pd.DataFrame(json.load(f))
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo data/distritos.json")
        return pd.DataFrame()

# 4. LÓGICA PRINCIPAL
def main():
    st.title("🇵🇪 Asistente Electoral 2025")
    
    # Logo (si existe)
    try:
        st.image("logo.png", width=100)
    except:
        pass 
    
    # PESTAÑAS
    tab1, tab2 = st.tabs(["💰 Calculadora de Multas", "📄 Generar Excusa (PDF)"])

    # --- PESTAÑA 1: CALCULADORA ---
    with tab1:
        st.write("Consulta rápida de deudas electorales según tu distrito.")
        
        df = cargar_datos()
        
        if not df.empty:
            nombres_distritos = df['nombre'].tolist()

            col1, col2 = st.columns(2)
            with col1:
                distrito = st.selectbox("📍 Distrito de votación", nombres_distritos)
                # Categoría
                categoria = df[df['nombre'] == distrito]['categoria'].values[0]
                st.info(f"Clasificación: **{categoria}**")
                
                # Botón Mapa ONPE
                url_mapa = f"https://www.google.com/maps/search/ODPE+{distrito.replace(' ', '+')}"
                st.link_button("🗺️ Ubicar Oficina ONPE", url_mapa, help="Ver oficina en Google Maps")
            
            with col2:
                es_miembro = st.checkbox("¿Fui Miembro de Mesa?")
                asistio_mesa = False
                if es_miembro:
                    asistio_mesa = st.checkbox("¿Asistí a instalar?")
                voto = st.checkbox("¿Fui a votar?")

            st.divider()

            # Botón Calcular
            if st.button("Calcular Deuda", type="primary"):
                paga_mesa = es_miembro and not asistio_mesa
                
                calc = CalculadoraElectoral()
                total, desglose = calc.calcular_deuda(paga_mesa, voto, categoria)
                
                st.session_state['deuda_actual'] = total
                st.session_state['desglose_actual'] = desglose

                if total > 0:
                    st.error(f"Deuda Total Estimada: S/ {total:.2f}")
                    for item in desglose:
                        st.write(f"- {item}")
                    
                    # --- AQUÍ ESTÁ EL CÓDIGO NUEVO DE PÁGALO.PE ---
                    st.markdown("---")
                    st.write("👇 **¿Quieres pagar ahora?**")
                    st.link_button(
                        "💳 Ir a Págalo.pe (Banco de la Nación)", 
                        "https://www.pagalo.pe/", 
                        help="Plataforma oficial para pagar multas al JNE"
                    )
                    # ---------------------------------------------

                else:
                    st.success("¡Sin multas estimadas!")
                    st.balloons()
                    st.session_state['deuda_actual'] = 0.0

    # --- PESTAÑA 2: GENERADOR PDF ---
    with tab2:
        st.header("Generador de Solicitud de Dispensa")
        
        monto = st.session_state['deuda_actual']
        if monto > 0:
            st.metric(label="Monto a justificar:", value=f"S/ {monto:.2f}", delta="Deuda pendiente", delta_color="inverse")
            st.warning("Recuerda adjuntar tus pruebas a esta solicitud.")
        else:
            st.info("💡 Consejo: Calcula tu multa en la primera pestaña para ver el monto aquí.")

        st.divider()

        with st.form("form_carta"):
            nombre_usuario = st.text_input("Nombre Completo")
            dni_usuario = st.text_input("DNI")
            motivo_usuario = st.text_area("Explica el motivo (Ej: Salud, Robo, Viaje)")
            
            generar = st.form_submit_button("Generar Documento PDF")

        if generar:
            if nombre_usuario and dni_usuario and motivo_usuario:
                distrito_actual = "Mi Distrito" 
                pdf_buffer = crear_pdf_dispensa(nombre_usuario, dni_usuario, motivo_usuario, distrito_actual)
                
                st.success("¡Documento generado con éxito!")
                st.download_button(
                    label="⬇️ Descargar Solicitud PDF",
                    data=pdf_buffer,
                    file_name="solicitud_dispensa.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("⚠️ Por favor completa todos los campos.")

    # --- PIE DE PÁGINA (WHATSAPP + CRÉDITOS) ---
    st.divider()
    
    # Link de WhatsApp
    texto_whatsapp = "¡Hola! Mira esta app para calcular multas electorales y dispensas: https://calculador-electoral.onrender.com"
    texto_encoded = urllib.parse.quote(texto_whatsapp)
    link_wa = f"https://wa.me/?text={texto_encoded}"
    
    col_footer1, col_footer2 = st.columns([1, 3])
    with col_footer1:
        st.link_button("📲 Compartir App", link_wa, help="Enviar por WhatsApp")
    
    with col_footer2:
        st.caption("🗳️ **Sobre la App:** Herramienta ciudadana no oficial.")
        st.caption("**Equipo:** Ricardo Condori, Manuel Serra, Pablo Huasasquiche, Cristhian Arotoma")

if __name__ == '__main__':
    main()