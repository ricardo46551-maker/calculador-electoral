import streamlit as st
# Importamos tu lógica desde la carpeta modules
from modules.calculadora import CalculadoraElectoral 

def main():
    st.title("🇵🇪 Calculador Electoral de Bolsillo")
    
    # Inputs
    opcion = st.selectbox("Selecciona tu distrito", ["VMT", "Miraflores", "SJM"])
    
    # Lógica
    calc = CalculadoraElectoral()
    if st.button("Calcular Multa"):
        # Aquí llamas a tu lógica
        st.success("Cálculo realizado (simulación)")

if __name__ == '__main__':
    main()