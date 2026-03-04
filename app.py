import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="SOCS Dashboard", page_icon="🌱", layout="wide")

# 2. Memuat Model
@st.cache_resource
def load_model():
    return joblib.load("XGBoost_baseline.pkl")

model = load_model()

# 3. Header Dashboard
st.title("🌱 Dashboard Prediksi Soil Organic Carbon Stock (SOCS)")
st.markdown("""
Aplikasi ini memprediksi nilai SOCS berdasarkan karakteristik fisik tanah, iklim, dan topografi. 
Silakan atur parameter di bawah ini dan klik tombol **Prediksi** untuk melihat hasilnya.
""")
st.markdown("---")

# 4. Tata Letak Input Menggunakan Tabs
tab1, tab2, tab3 = st.tabs(["🪨 Karakteristik Tanah", "📏 Kedalaman & Pengukuran", "🌤️ Iklim & Topografi"])

with tab1:
    st.subheader("Parameter Fisik & Kimia Tanah")
    col1, col2 = st.columns(2)
    # Menggunakan slider untuk persentase agar lebih interaktif
    Sand = col1.slider("Sand (%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0)
    Silt = col2.slider("Silt (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
    
    col3, col4, col5 = st.columns(3)
    SOC = col3.number_input("SOC (g/kg)", value=10.0)
    BD = col4.number_input("Bulk Density (BD g/cm3)", value=1.2)
    pH = col5.number_input("pH Tanah", value=6.5)

with tab2:
    st.subheader("Informasi Kedalaman & Metode")
    col1, col2, col3 = st.columns(3)
    upper_dept = col1.number_input("Upper Depth (cm)", value=0.0)
    lower_dept = col2.number_input("Lower Depth (cm)", value=20.0)
    SOCD_meth = col3.selectbox(
        "SOCD Measurement Method", 
        options=[0, 1], 
        help="Pilih metode pengukuran yang sesuai (0 atau 1)"
    )

with tab3:
    st.subheader("Kondisi Iklim & Lingkungan")
    col1, col2 = st.columns(2)
    MAT = col1.number_input("Mean Annual Temp (MAT °C)", value=15.0)
    PET = col2.number_input("Potential Evapotranspiration (PET)", value=1000.0)
    DEM = col1.number_input("DEM (Elevasi m)", value=100.0)
    AI = col2.number_input("Aridity Index (AI)", value=1.0)

# 5. Menyiapkan Data Sesuai Format Model
user_data = {
    'Silt': Silt,
    'SOC (g/kg)': SOC,
    'lower_dept': lower_dept,
    'SOCD__meth_Measurement': SOCD_meth,
    'BD (g/cm3)': BD,
    'upper_dept': upper_dept,
    'MAT': MAT,
    'PET': PET,
    'pH': pH,
    'Sand': Sand,
    'DEM': DEM,
    'AI': AI
}

expected_columns = [
    'Silt', 'SOC (g/kg)', 'lower_dept', 'SOCD__meth_Measurement', 
    'BD (g/cm3)', 'upper_dept', 'MAT', 'PET', 'pH', 'Sand', 'DEM', 'AI'
]
df_input = pd.DataFrame(user_data, index=[0])[expected_columns]

st.markdown("<br>", unsafe_allow_html=True)

# 6. Tombol Eksekusi Prediksi
if st.button("🚀 Jalankan Prediksi Prediksi SOCS", use_container_width=True):
    try:
        # Menjalankan model
        prediction = model.predict(df_input)[0]
        
        st.markdown("---")
        st.header("📊 Hasil Analisis")
        
        # Layout untuk visualisasi
        res_col1, res_col2 = st.columns([1, 1])
        
        with res_col1:
            # Menampilkan Metric dan Gauge Chart
            st.metric(label="Prediksi Nilai SOCS", value=f"{prediction:.2f}", delta="Estimasi Model")
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = prediction,
                title = {'text': "Indikator SOCS"},
                gauge = {
                    'axis': {'range': [None, max(50, prediction * 1.5)], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "#2E7D32"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, prediction*0.5], 'color': '#C8E6C9'},
                        {'range': [prediction*0.5, prediction], 'color': '#81C784'}],
                }
            ))
            fig_gauge.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with res_col2:
            # Visualisasi Komposisi Tanah (Asumsi Sand + Silt + Clay = 100%)
            clay_est = max(0, 100 - (Sand + Silt))
            soil_comp = pd.DataFrame({
                'Komponen': ['Sand', 'Silt', 'Clay (Estimasi)'],
                'Persentase': [Sand, Silt, clay_est]
            })
            
            fig_pie = px.pie(
                soil_comp, 
                values='Persentase', 
                names='Komponen', 
                title='Komposisi Tekstur Tanah',
                color_discrete_sequence=['#FFCA28', '#8D6E63', '#795548'],
                hole=0.4
            )
            fig_pie.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.balloons() # Animasi balon saat berhasil
            
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses data: {e}")