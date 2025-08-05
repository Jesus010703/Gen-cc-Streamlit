import streamlit as st
import requests
import json
import random
from datetime import datetime
import webbrowser
import base64

# Configuración de la página
st.set_page_config(
    page_title="Generador de BIN RS",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para diseño responsive y moderno
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .title {
        text-align: center;
        color: #2c3e50;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .result-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
    }
    
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(45deg, #3498db, #2980b9);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    
    @media (max-width: 768px) {
        .title {
            font-size: 2rem;
        }
        .card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

def generar_luhn(bin_prefix):
    """Genera un número de tarjeta válido usando el algoritmo de Luhn"""
    numero_sin_verificar = ''
    for digito in bin_prefix:
        if digito.lower() == 'x':
            numero_sin_verificar += str(random.randint(0, 9))
        else:
            numero_sin_verificar += digito
    
    if not numero_sin_verificar.isdigit():
        raise ValueError("El BIN debe contener solo dígitos o 'x'")
    
    if len(numero_sin_verificar) > 15:
        numero_sin_verificar = numero_sin_verificar[:15]
    
    suma = 0
    for i, digito in enumerate(reversed(numero_sin_verificar)):
        n = int(digito)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        suma += n
    
    digito_verificacion = (10 - (suma % 10)) % 10
    return numero_sin_verificar + str(digito_verificacion)

def verificar_luhn(numero):
    """Verifica si un número de tarjeta cumple con el algoritmo de Luhn"""
    if not numero.isdigit():
        return False
        
    suma = 0
    for i, digito in enumerate(reversed(numero)):
        n = int(digito)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        suma += n
            
    return suma % 10 == 0

def obtener_info_bin(bin_number):
    """Obtiene información del BIN usando la API de binlist.net"""
    try:
        headers = {'Accept-Version': '3'}
        response = requests.get(f'https://lookup.binlist.net/{bin_number}', headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error al consultar BIN: {str(e)}")
        return None

def guardar_tarjetas(tarjetas):
    """Guarda las tarjetas generadas en el estado de la sesión"""
    if 'tarjetas_guardadas' not in st.session_state:
        st.session_state.tarjetas_guardadas = []
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for tarjeta in tarjetas:
        st.session_state.tarjetas_guardadas.append({
            'tarjeta': tarjeta,
            'fecha': timestamp
        })

# Título principal
st.markdown('<div class="title">💳 Generador de CC Friends School</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Generador profesional de números de tarjeta con validación Luhn</div>', unsafe_allow_html=True)

# Sidebar para controles principales
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Campo BIN
    bin_input = st.text_input(
        "BIN (usa 'x' para dígitos aleatorios):",
        value="453900xxxxxxxx",
        help="Ingresa el BIN base. Usa 'x' para generar dígitos aleatorios"
    )
    
    # Controles de fecha
    st.subheader("📅 Fecha de Expiración")
    col1, col2 = st.columns(2)
    
    with col1:
        mes = st.selectbox("Mes", [f"{i:02d}" for i in range(1, 13)], index=0)
    
    with col2:
        año = st.selectbox("Año", [f"{i:02d}" for i in range(23, 31)], index=1)
    
    if st.button("🎲 Fecha Aleatoria", use_container_width=True):
        mes = f"{random.randint(1, 12):02d}"
        año = f"{random.randint(23, 30):02d}"
        st.rerun()
    
    # Cantidad de tarjetas
    cantidad = st.selectbox(
        "Cantidad de tarjetas:",
        [10, 15, 50, 100],
        index=0
    )

# Contenido principal
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Generador", "🔍 BIN Checker", "💾 Guardadas", "ℹ️ Info"])

with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button("🚀 Generar Tarjetas", type="primary", use_container_width=True):
            if not bin_input.strip():
                st.error("⚠️ Por favor ingrese un BIN")
            else:
                # Procesar BIN
                bin_base = bin_input.strip()
                if len(bin_base) < 15:
                    bin_base = bin_base + 'x' * (15 - len(bin_base))
                elif len(bin_base) > 15:
                    bin_base = bin_base[:15]
                
                # Generar tarjetas
                with st.spinner("Generando tarjetas válidas..."):
                    resultados = []
                    tarjetas_generadas = 0
                    intentos_maximos = cantidad * 10
                    intentos = 0
                    
                    progress_bar = st.progress(0)
                    
                    while tarjetas_generadas < cantidad and intentos < intentos_maximos:
                        intentos += 1
                        try:
                            tarjeta = generar_luhn(bin_base)
                            if verificar_luhn(tarjeta):
                                cvv = str(random.randint(100, 999))
                                resultado = f"{tarjeta}|{mes}|{año}|{cvv}"
                                resultados.append(resultado)
                                tarjetas_generadas += 1
                                progress_bar.progress(tarjetas_generadas / cantidad)
                        except:
                            pass
                    
                    progress_bar.empty()
                
                if resultados:
                    st.success(f"✅ {len(resultados)} tarjetas válidas generadas!")
                    
                    # Mostrar métricas
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Tarjetas Generadas", len(resultados))
                    with col2:
                        st.metric("Intentos Realizados", intentos)
                    with col3:
                        st.metric("Tasa de Éxito", f"{(len(resultados)/intentos)*100:.1f}%")
                    with col4:
                        st.metric("CVV Range", "100-999")
                    
                    # Mostrar resultados
                    st.markdown("### 📋 Tarjetas Generadas:")
                    resultado_texto = "\n".join(resultados)
                    st.code(resultado_texto, language="text")
                    
                    # Botones de acción
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("📋 Copiar al Portapapeles", use_container_width=True):
                            st.write("```")
                            st.write(resultado_texto)
                            st.write("```")
                            st.info("💡 Selecciona el texto de arriba y cópialo manualmente")
                    
                    with col2:
                        if st.button("💾 Guardar Tarjetas", use_container_width=True):
                            guardar_tarjetas(resultados)
                            st.success("Tarjetas guardadas exitosamente!")
                    
                    with col3:
                        # Botón de descarga
                        st.download_button(
                            label="⬇️ Descargar TXT",
                            data=resultado_texto,
                            file_name=f"tarjetas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                
                else:
                    st.warning("⚠️ No se pudo generar ninguna tarjeta válida")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔍 Verificador de BIN")
    
    bin_check = st.text_input("Ingresa el BIN a verificar (mínimo 6 dígitos):", value=bin_input[:8])
    
    if st.button("🔎 Verificar BIN", use_container_width=True):
        if len(bin_check) >= 6:
            with st.spinner("Consultando información del BIN..."):
                data = obtener_info_bin(bin_check)
                
                if data:
                    st.success("✅ Información del BIN encontrada!")
                    
                    # Mostrar información en tarjetas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 💳 Información de la Tarjeta")
                        st.info(f"**Esquema:** {data.get('scheme', 'N/A')}")
                        st.info(f"**Tipo:** {data.get('type', 'N/A')}")
                        st.info(f"**Marca:** {data.get('brand', 'N/A')}")
                    
                    with col2:
                        if 'country' in data:
                            st.markdown("#### 🌍 Información del País")
                            country = data['country']
                            st.info(f"**País:** {country.get('name', 'N/A')} {country.get('emoji', '')}")
                            st.info(f"**Moneda:** {country.get('currency', 'N/A')}")
                            st.info(f"**Código:** {country.get('alpha2', 'N/A')}")
                    
                    if 'bank' in data:
                        st.markdown("#### 🏦 Información del Banco")
                        bank = data['bank']
                        bank_info = f"""
                        **Banco:** {bank.get('name', 'N/A')}
                        **URL:** {bank.get('url', 'N/A')}
                        **Teléfono:** {bank.get('phone', 'N/A')}
                        **Ciudad:** {bank.get('city', 'N/A')}
                        """
                        st.info(bank_info)
                else:
                    st.error("❌ No se pudo obtener información del BIN")
        else:
            st.warning("⚠️ Por favor ingrese un BIN válido (mínimo 6 dígitos)")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💾 Tarjetas Guardadas")
    
    if 'tarjetas_guardadas' in st.session_state and st.session_state.tarjetas_guardadas:
        st.info(f"📊 Total de tarjetas guardadas: {len(st.session_state.tarjetas_guardadas)}")
        
        # Mostrar tarjetas guardadas
        for i, item in enumerate(st.session_state.tarjetas_guardadas):
            with st.expander(f"Tarjeta {i+1} - {item['fecha']}"):
                st.code(item['tarjeta'], language="text")
        
        # Opciones de gestión
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpiar Todas", use_container_width=True):
                st.session_state.tarjetas_guardadas = []
                st.success("Todas las tarjetas han sido eliminadas")
                st.rerun()
        
        with col2:
            # Descargar todas las tarjetas guardadas
            todas_las_tarjetas = "\n".join([item['tarjeta'] for item in st.session_state.tarjetas_guardadas])
            st.download_button(
                label="⬇️ Descargar Todas",
                data=todas_las_tarjetas,
                file_name=f"tarjetas_guardadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.info("📝 No hay tarjetas guardadas todavía")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Información de la aplicación
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ℹ️ Información de la Aplicación")
        st.info("""
        **Generador de BIN RS v2.0**
        
        Esta aplicación genera números de tarjeta de crédito válidos usando el algoritmo de Luhn para propósitos educativos y de testing.
        
        **Características:**
        - ✅ Validación con algoritmo de Luhn
        - 🔍 Verificador de BIN integrado
        - 💾 Sistema de guardado de tarjetas
        - 📱 Interfaz responsive
        - 🎲 Generación aleatoria de fechas y CVV
        """)
    
    with col2:
        st.subheader("👥 Créditos")
        st.success("""
        **Desarrollado por:**
        - Curso Python Friends School
        - Version: streamlit-pro-v2.0
        
        **Tecnologías utilizadas:**
        - Python 3.x
        - Streamlit
        - Requests
        - API binlist.net
        
        **Enlaces útiles:**
        - 📧 [Correo Temporal](https://temp-mail.org/es/)
        - 🔗 [BIN Database](https://binlist.net/)
        """)
    
    # Botón para correo temporal
    if st.button("📧 Abrir Correo Temporal", use_container_width=True):
        st.markdown("[Haz clic aquí para abrir el correo temporal](https://temp-mail.org/es/)")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7f8c8d;'>💳 Generador de BIN RS - Friends School © 2024</div>",
    unsafe_allow_html=True
)