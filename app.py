import streamlit as st
import pandas as pd
import json
from modules.calculadora import CalculadoraElectoral

# Configuración visual
st.set_page_config(page_title="Calculadora Electoral", page_icon="🇵🇪")

def cargar_datos():
    with open('data/distritos.json', 'r', encoding='utf-8') as f:
        return pd.DataFrame(json.load(f))

def main():
    st.title("🇵🇪 Calculadora de Multas 2025")
    st.write("Consulta rápida de deudas electorales según tu distrito.")

    try:
        # 1. Cargamos la base de datos
        df = cargar_datos()
        nombres_distritos = df['nombre'].tolist()

        # 2. Formulario de usuario
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                distrito = st.selectbox("📍 Distrito de votación", nombres_distritos)
                # Buscamos la categoría automáticamente
                categoria = df[df['nombre'] == distrito]['categoria'].values[0]
                st.info(f"Clasificación: **{categoria}**")
            
            with col2:
                es_miembro = st.checkbox("¿Fui Miembro de Mesa sorteado?")
                # Si fue miembro, preguntamos si cumplió
                asistio_mesa = False
                if es_miembro:
                    asistio_mesa = st.checkbox("¿Asistí a instalar la mesa?")
                
                voto = st.checkbox("¿Fui a votar?")

        st.divider()

        # 3. Botón de Cálculo
        if st.button("💰 Calcular Deuda", type="primary"):
            # Lógica:
            # - Si fue miembro y NO asistió a la mesa = Paga multa de mesa
            # - Si NO votó = Paga multa de voto
            
            paga_mesa = es_miembro and not asistio_mesa
            
            calc = CalculadoraElectoral()
            total, desglose = calc.calcular_deuda(
                es_miembro_mesa=paga_mesa,
                voto=voto,
                categoria_distrito=categoria
            )

            if total > 0:
                st.error(f"Deuda Total Estimada: S/ {total:.2f}")
                for item in desglose:
                    st.write(f"- {item}")
            else:
                st.balloons()
                st.success("¡No tienes multas pendientes! (Estimación)")

    except Exception as e:
        st.error(f"Error cargando datos: {e}")

if __name__ == '__main__':
    main()