import streamlit as st
import pandas as pd
import json
from modules.calculadora import CalculadoraElectoral
from modules.generador_pdf import crear_pdf_dispensa

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Calculadora Electoral", page_icon="🇵🇪")

# --- BARRA LATERAL (TU MARCA) ---
with st.sidebar:
    st.header("🗳️ Sobre la App")
    st.write("Herramienta ciudadana para cálculo de multas y generación de dispensas.")
    
    st.divider()
    st.write("**Desarrollado por:**")
    st.markdown("👨‍💻 **Ricardo Condori, Manuel Serra, Pablo Huasasquiche, Cristhian Arotoma**") # ¡Puedes cambiar esto por tu nombre completo!
    
    st.info("⚠️ **Aviso:** Esta es una herramienta no oficial. Los montos son estimados basados en la UIT vigente.")
    st.caption("Versión 1.0.0 | Datos 2025")

# 2. INICIALIZACIÓN DE MEMORIA (SESSION STATE)
# Esto permite que la app "recuerde" la deuda cuando cambias de pestaña
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
    
    # PESTAÑAS
    tab1, tab2 = st.tabs(["💰 Calculadora de Multas", "📄 Generar Excusa (PDF)"])

    # --- PESTAÑA 1: CALCULADORA ---
    with tab1:
        st.write("Consulta rápida de deudas electorales según tu distrito.")
        
        df = cargar_datos()
        
        if not df.empty:
            nombres_distritos = df['nombre'].tolist()

            # Formulario de entrada
            col1, col2 = st.columns(2)
            with col1:
                distrito = st.selectbox("📍 Distrito de votación", nombres_distritos)
                # Buscamos la categoría del distrito
                categoria = df[df['nombre'] == distrito]['categoria'].values[0]
                st.info(f"Clasificación: **{categoria}**")
            
            with col2:
                es_miembro = st.checkbox("¿Fui Miembro de Mesa?")
                asistio_mesa = False
                if es_miembro:
                    asistio_mesa = st.checkbox("¿Asistí a instalar?")
                voto = st.checkbox("¿Fui a votar?")

            # Botón de cálculo
            if st.button("Calcular Deuda", type="primary"):
                paga_mesa = es_miembro and not asistio_mesa
                
                # Llamamos a tu lógica matemática
                calc = CalculadoraElectoral()
                total, desglose = calc.calcular_deuda(paga_mesa, voto, categoria)
                
                # GUARDAMOS EN MEMORIA
                st.session_state['deuda_actual'] = total
                st.session_state['desglose_actual'] = desglose

                if total > 0:
                    st.error(f"Deuda Total Estimada: S/ {total:.2f}")
                    for item in desglose:
                        st.write(f"- {item}")
                else:
                    st.success("¡Sin multas estimadas!")
                    st.balloons()
                    # Reset si no hay deuda
                    st.session_state['deuda_actual'] = 0.0

    # --- PESTAÑA 2: GENERADOR DE CARTAS ---
    with tab2:
        st.header("Generador de Solicitud de Dispensa")
        
        # MOSTRAR LA DEUDA DE LA MEMORIA
        monto = st.session_state['deuda_actual']
        if monto > 0:
            st.metric(label="Monto a justificar:", value=f"S/ {monto:.2f}", delta="Deuda pendiente", delta_color="inverse")
            st.warning("Recuerda adjuntar tus pruebas a esta solicitud.")
        else:
            st.info("💡 Consejo: Calcula tu multa en la primera pestaña para ver el monto aquí.")

        st.divider()

        # FORMULARIO
        with st.form("form_carta"):
            nombre_usuario = st.text_input("Nombre Completo")
            dni_usuario = st.text_input("DNI")
            motivo_usuario = st.text_area("Explica el motivo (Ej: Salud, Robo, Viaje)")
            
            # Botón dentro del form (solo envía datos)
            generar = st.form_submit_button("Generar Documento PDF")

        # LÓGICA FUERA DEL FORM (Para que funcione la descarga)
        if generar:
            if nombre_usuario and dni_usuario and motivo_usuario:
                # Usamos el distrito que esté seleccionado actualmente
                # (Si no cargó data, usamos un genérico)
                distrito_actual = "Mi Distrito" 
                
                # Generar el PDF en memoria
                pdf_buffer = crear_pdf_dispensa(nombre_usuario, dni_usuario, motivo_usuario, distrito_actual)
                
                st.success("¡Documento generado con éxito!")