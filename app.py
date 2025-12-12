import streamlit as st
import pandas as pd
import json
from modules.calculadora import CalculadoraElectoral
from modules.generador_pdf import crear_pdf_dispensa # <--- NUEVO IMPORT

st.set_page_config(page_title="Calculadora Electoral", page_icon="🇵🇪")

def cargar_datos():
    with open('data/distritos.json', 'r', encoding='utf-8') as f:
        return pd.DataFrame(json.load(f))

def main():
    st.title("🇵🇪 Asistente Electoral 2025")
    
    # CREAMOS PESTAÑAS PARA ORGANIZAR LA APP
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

                if total > 0:
                    st.error(f"Deuda Total: S/ {total:.2f}")
                    for item in desglose:
                        st.write(f"- {item}")
                else:
                    st.success("¡Sin multas estimadas!")
        except Exception as e:
            st.error(f"Error: {e}")

    # --- PESTAÑA 2: GENERADOR DE CARTAS (NUEVO) ---
    with tab2:
        st.header("Generador de Solicitud de Dispensa")
        st.write("Si tienes una justificación válida (salud, robo, viaje), genera tu carta aquí.")

        with st.form("form_carta"):
            nombre_usuario = st.text_input("Nombre Completo")
            dni_usuario = st.text_input("DNI")
            motivo_usuario = st.text_area("Explica el motivo (Ej: Salud, Viaje de estudios, Robo de DNI)")
            
            # Botón de envío del formulario
            generar = st.form_submit_button("Generar Documento PDF")
            
            if generar:
                if nombre_usuario and dni_usuario and motivo_usuario:
                    # Llamamos a la función del PDF
                    pdf_buffer = crear_pdf_dispensa(nombre_usuario, dni_usuario, motivo_usuario, distrito)
                    
                    st.success("¡Documento generado con éxito!")
                    
                    # Botón de descarga real
                    st.download_button(
                        label="⬇️ Descargar Solicitud lista para imprimir",
                        data=pdf_buffer,
                        file_name="solicitud_dispensa.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.warning("Por favor completa todos los campos para generar la carta.")

if __name__ == '__main__':
    main()