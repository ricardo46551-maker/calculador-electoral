import streamlit as st
import pandas as pd
import json
from modules.calculadora import CalculadoraElectoral
from modules.generador_pdf import crear_pdf_dispensa

st.set_page_config(page_title="Calculadora Electoral", page_icon="🇵🇪")

# --- 0. CONFIGURACIÓN DE MEMORIA (SESSION STATE) ---
# Inicializamos la variable 'deuda_actual' si no existe
if 'deuda_actual' not in st.session_state:
    st.session_state['deuda_actual'] = 0.0
if 'desglose_actual' not in st.session_state:
    st.session_state['desglose_actual'] = []

def cargar_datos():
    with open('data/distritos.json', 'r', encoding='utf-8') as f:
        return pd.DataFrame(json.load(f))

def main():
    st.title("🇵🇪 Asistente Electoral 2025")
    
    tab1, tab2 = st.tabs(["💰 Calculadora de Multas", "📄 Generar Excusa (PDF)"])

    # --- PESTAÑA 1: CALCULADORA ---
    with tab1:
        st.write("Consulta rápida de deudas electorales.")
        try:
            df = cargar_datos()
            nombres_distritos = df['nombre'].tolist()

            col1, col2 = st.columns(2)
            with col1:
                distrito = st.selectbox("📍 Distrito de votación", nombres_distritos)
                categoria = df[df['nombre'] == distrito]['categoria'].values[0]
                st.info(f"Clasificación: **{categoria}**")
            
            with col2:
                es_miembro = st.checkbox("¿Fui Miembro de Mesa?")
                asistio_mesa = False
                if es_miembro:
                    asistio_mesa = st.checkbox("¿Asistí a instalar?")
                voto = st.checkbox("¿Fui a votar?")

            if st.button("Calcular Deuda", type="primary"):
                paga_mesa = es_miembro and not asistio_mesa
                calc = CalculadoraElectoral()
                total, desglose = calc.calcular_deuda(paga_mesa, voto, categoria)
                
                # GUARDAMOS EL RESULTADO EN LA MEMORIA
                st.session_state['deuda_actual'] = total
                st.session_state['desglose_actual'] = desglose

                if total > 0:
                    st.error(f"Deuda Total: S/ {total:.2f}")
                    for item in desglose:
                        st.write(f"- {item}")
                else:
                    st.success("¡Sin multas estimadas!")
                    # Si no hay deuda, reseteamos la memoria
                    st.session_state['deuda_actual'] = 0.0
                    
        except Exception as e:
            st.error(f"Error: {e}")

    # --- PESTAÑA 2: GENERADOR DE CARTAS ---
    with tab2:
        st.header("Generador de Solicitud de Dispensa")
        
        # --- AQUÍ MOSTRAMOS EL DINERO ---
        monto = st.session_state['deuda_actual']
        if monto > 0:
            # Usamos un componente visual llamativo (Metric)
            st.metric(label="Monto que estás justificando:", value=f"S/ {monto:.2f}", delta="- Deuda Pendiente", delta_color="inverse")
            st.warning("⚠️ Recuerda adjuntar tus pruebas (certificado médico, denuncia, etc.) a esta solicitud.")
        else:
            st.info("💡 Consejo: Primero calcula tu multa en la otra pestaña para ver el monto aquí.")

        st.divider()

        with st.form("form_carta"):
            nombre_usuario = st.text_input("Nombre Completo")
            dni_usuario = st.text_input("DNI")
            motivo_usuario = st.text_area("Explica el motivo (Ej: Salud, Robo, Viaje)")
            
            generar = st.form_submit_button("Generar Documento PDF")

        if generar:
            if nombre_usuario and dni_usuario and motivo_usuario:
                # Usamos el distrito seleccionado en la memoria si es posible, o uno genérico
                distrito_actual = "Mi Distrito" 
                
                pdf_buffer = crear_pdf_dispensa(nombre_usuario, dni_usuario, motivo_usuario, distrito_actual)
                
                st.success("¡Documento generado!")
                
                st.download_button(
                    label="⬇️ Descargar Solicitud PDF",
                    data=pdf_buffer,
                    file_name="solicitud_dispensa.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("⚠️ Completa todos los campos.")

if __name__ == '__main__':
    main()