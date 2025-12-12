# 🇵🇪 Calculadora Electoral de Bolsillo

Aplicación web desarrollada en Python para ayudar a los ciudadanos peruanos a calcular multas electorales y generar solicitudes de dispensa automáticamente.

🔗 **Demo en vivo:** [https://calculador-electoral.onrender.com](https://calculador-electoral.onrender.com)

## 🌟 Características

* **Calculadora de Multas:** Estima la deuda electoral basándose en la UIT vigente (2025) y la clasificación socioeconómica del distrito (Pobre / No Pobre / Extremo).
* **Base de Datos Local:** Incluye los 43 distritos de Lima Metropolitana.
* **Generador de Documentos:** Crea automáticamente una carta de solicitud de dispensa en formato PDF lista para imprimir y firmar.
* **Memoria de Sesión:** Mantiene los datos del usuario mientras navega entre las herramientas.

## 🛠️ Tecnologías Usadas

* **Python 3.11+**
* **Streamlit:** Para la interfaz de usuario web.
* **ReportLab:** Para la generación dinámica de PDFs.
* **Pandas:** Para el manejo de la base de datos de distritos (JSON).
* **Render:** Para el despliegue en la nube (CI/CD).

## 🚀 Cómo ejecutar localmente

1.  Clonar el repositorio:
    ```bash
    git clone [https://github.com/TU_USUARIO/calculador-electoral.git](https://github.com/TU_USUARIO/calculador-electoral.git)
    ```
2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ejecutar la app:
    ```bash
    streamlit run app.py
    ```

## 👥 Equipo de Desarrollo

* Ricardo Condori
* Manuel Serra
* Pablo Huasasquiche
* Cristhian Arotoma

---
*Este proyecto es una herramienta ciudadana no oficial.*