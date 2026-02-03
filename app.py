"""
CDP Demo - Streamlit Dashboard
Ana uygulama dosyası
"""

import streamlit as st
import json
from pathlib import Path
import sys

# src klasörünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent / "src"))

st.set_page_config(
    page_title="CDP Demo - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


def load_data():
    """Veri dosyalarını yükle"""
    data_dir = Path("data")

    if not data_dir.exists() or not (data_dir / "customers.json").exists():
        return None, None, None

    with open(data_dir / "customers.json", "r", encoding="utf-8") as f:
        customers = json.load(f)

    with open(data_dir / "transactions.json", "r", encoding="utf-8") as f:
        transactions = json.load(f)

    with open(data_dir / "events.json", "r", encoding="utf-8") as f:
        events = json.load(f)

    return customers, transactions, events


def main():
    # Header
    st.markdown('<p class="main-header">📊 CDP Demo Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Customer Data Platform - Time & Growity</p>', unsafe_allow_html=True)

    # Veri yükle
    customers, transactions, events = load_data()

    if customers is None:
        st.warning("⚠️ Veri bulunamadı. Lütfen önce veri oluşturun:")
        st.code("python main.py generate", language="bash")

        if st.button("🔄 Veri Oluştur"):
            import subprocess
            with st.spinner("Veri oluşturuluyor..."):
                result = subprocess.run(["python", "main.py", "generate"], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ Veri oluşturuldu! Sayfayı yenileyin.")
                    st.rerun()
                else:
                    st.error(f"Hata: {result.stderr}")
        return

    # Ana KPI'lar
    st.markdown("### 📈 Genel Bakış")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Toplam Müşteri",
            value=f"{len(customers):,}",
            delta="+12% bu ay"
        )

    with col2:
        total_revenue = sum(tx["total_amount"] for tx in transactions)
        st.metric(
            label="Toplam Gelir",
            value=f"₺{total_revenue:,.0f}",
            delta="+8% bu ay"
        )

    with col3:
        premium_count = len([c for c in customers if c["segment"] == "premium"])
        st.metric(
            label="Premium Müşteri",
            value=f"{premium_count}",
            delta=f"%{premium_count/len(customers)*100:.1f}"
        )

    with col4:
        app_users = len([c for c in customers if c["has_app"]])
        st.metric(
            label="App Kullanıcısı",
            value=f"{app_users}",
            delta=f"%{app_users/len(customers)*100:.1f}"
        )

    st.divider()

    # İki sütunlu içerik
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 🎯 Segment Dağılımı")

        # Segment sayıları
        segments = {}
        for c in customers:
            seg = c["segment"]
            segments[seg] = segments.get(seg, 0) + 1

        # Plotly pie chart
        import plotly.express as px

        fig = px.pie(
            values=list(segments.values()),
            names=list(segments.keys()),
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4
        )
        fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            height=300,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### 🏙️ Şehir Dağılımı")

        # Şehir sayıları
        cities = {}
        for c in customers:
            city = c["city"]
            cities[city] = cities.get(city, 0) + 1

        # Bar chart
        fig = px.bar(
            x=list(cities.keys()),
            y=list(cities.values()),
            color=list(cities.values()),
            color_continuous_scale="Blues"
        )
        fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            height=300,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Müşteri Sayısı",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Günlük işlem trendi
    st.markdown("### 📅 Günlük İşlem Trendi")

    # Tarihe göre grupla
    daily_stats = {}
    for tx in transactions:
        date = tx["date"]
        if date not in daily_stats:
            daily_stats[date] = {"count": 0, "revenue": 0}
        daily_stats[date]["count"] += 1
        daily_stats[date]["revenue"] += tx["total_amount"]

    dates = sorted(daily_stats.keys())
    counts = [daily_stats[d]["count"] for d in dates]
    revenues = [daily_stats[d]["revenue"] for d in dates]

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=dates, y=counts, name="İşlem Sayısı", line=dict(color="#1f77b4")),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=dates, y=revenues, name="Gelir (₺)", line=dict(color="#ff7f0e")),
        secondary_y=True,
    )

    fig.update_layout(
        height=350,
        margin=dict(t=20, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(title_text="İşlem Sayısı", secondary_y=False)
    fig.update_yaxes(title_text="Gelir (₺)", secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Quick Actions
    st.markdown("### ⚡ Hızlı İşlemler")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.page_link("pages/1_Müşteri_Analizi.py", label="👥 Müşteri Analizi", icon="👥")

    with col2:
        st.page_link("pages/2_Segment_Builder.py", label="🎯 Segment Builder", icon="🎯")

    with col3:
        st.page_link("pages/3_Export.py", label="📤 Platform Export", icon="📤")

    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem;">
        CDP Demo v0.4 | Time & Growity | 2024
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
