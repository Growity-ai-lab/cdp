"""
CDP Demo - Müşteri Analizi Sayfası
Demografik ve davranışsal müşteri analizi
"""

import streamlit as st
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Müşteri Analizi - CDP Demo",
    page_icon="👥",
    layout="wide"
)


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
    st.title("👥 Müşteri Analizi")
    st.markdown("Müşteri tabanınızın demografik ve davranışsal analizi")

    # Veri yükle
    customers, transactions, events = load_data()

    if customers is None:
        st.warning("⚠️ Veri bulunamadı. Ana sayfadan veri oluşturun.")
        return

    # DataFrame'e çevir
    df_customers = pd.DataFrame(customers)
    df_transactions = pd.DataFrame(transactions)

    # Sidebar filtreler
    st.sidebar.header("🔍 Filtreler")

    selected_cities = st.sidebar.multiselect(
        "Şehir",
        options=df_customers["city"].unique(),
        default=df_customers["city"].unique()
    )

    selected_segments = st.sidebar.multiselect(
        "Segment",
        options=df_customers["segment"].unique(),
        default=df_customers["segment"].unique()
    )

    age_range = st.sidebar.slider(
        "Yaş Aralığı",
        min_value=int(df_customers["age"].min()),
        max_value=int(df_customers["age"].max()),
        value=(int(df_customers["age"].min()), int(df_customers["age"].max()))
    )

    # Filtreleme
    df_filtered = df_customers[
        (df_customers["city"].isin(selected_cities)) &
        (df_customers["segment"].isin(selected_segments)) &
        (df_customers["age"] >= age_range[0]) &
        (df_customers["age"] <= age_range[1])
    ]

    # Özet metrikler
    st.markdown("### 📊 Özet Metrikler")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Toplam Müşteri", f"{len(df_filtered):,}")

    with col2:
        avg_age = df_filtered["age"].mean()
        st.metric("Ortalama Yaş", f"{avg_age:.1f}")

    with col3:
        app_pct = df_filtered["has_app"].mean() * 100
        st.metric("App Oranı", f"%{app_pct:.1f}")

    with col4:
        email_pct = df_filtered["email_opted_in"].mean() * 100
        st.metric("Email Opt-in", f"%{email_pct:.1f}")

    with col5:
        loyalty_pct = df_filtered["loyalty_card"].mean() * 100
        st.metric("Sadakat Kartı", f"%{loyalty_pct:.1f}")

    st.divider()

    # Grafikler - 2 sütun
    col_left, col_right = st.columns(2)

    with col_left:
        # Yaş dağılımı
        st.markdown("### 📈 Yaş Dağılımı")
        fig = px.histogram(
            df_filtered,
            x="age",
            nbins=20,
            color="segment",
            barmode="overlay",
            opacity=0.7,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            height=350,
            margin=dict(t=20, b=0, l=0, r=0),
            xaxis_title="Yaş",
            yaxis_title="Müşteri Sayısı",
            legend_title="Segment"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # Cinsiyet dağılımı
        st.markdown("### 👤 Cinsiyet Dağılımı")
        gender_counts = df_filtered["gender"].value_counts()
        gender_labels = {"M": "Erkek", "F": "Kadın"}

        fig = px.pie(
            values=gender_counts.values,
            names=[gender_labels.get(g, g) for g in gender_counts.index],
            color_discrete_sequence=["#1f77b4", "#ff7f0e"],
            hole=0.4
        )
        fig.update_layout(
            height=350,
            margin=dict(t=20, b=0, l=0, r=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    col_left2, col_right2 = st.columns(2)

    with col_left2:
        # Şehir bazlı segment dağılımı
        st.markdown("### 🏙️ Şehir Bazlı Segment Dağılımı")

        city_segment = df_filtered.groupby(["city", "segment"]).size().reset_index(name="count")

        fig = px.bar(
            city_segment,
            x="city",
            y="count",
            color="segment",
            barmode="group",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            height=350,
            margin=dict(t=20, b=0, l=0, r=0),
            xaxis_title="",
            yaxis_title="Müşteri Sayısı",
            legend_title="Segment"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right2:
        # App vs Non-App
        st.markdown("### 📱 Dijital Adoption")

        app_data = df_filtered.groupby(["segment", "has_app"]).size().reset_index(name="count")
        app_data["has_app"] = app_data["has_app"].map({True: "App Var", False: "App Yok"})

        fig = px.bar(
            app_data,
            x="segment",
            y="count",
            color="has_app",
            barmode="stack",
            color_discrete_sequence=["#2ecc71", "#e74c3c"]
        )
        fig.update_layout(
            height=350,
            margin=dict(t=20, b=0, l=0, r=0),
            xaxis_title="Segment",
            yaxis_title="Müşteri Sayısı",
            legend_title=""
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # RFM Analizi
    st.markdown("### 💎 RFM Benzeri Analiz")
    st.markdown("Müşterilerin ziyaret sıklığı ve segment dağılımı")

    # Müşteri başına işlem sayısı
    customer_tx_counts = df_transactions.groupby("customer_id").size().reset_index(name="tx_count")
    customer_revenue = df_transactions.groupby("customer_id")["total_amount"].sum().reset_index(name="total_revenue")

    df_rfm = df_filtered.merge(customer_tx_counts, on="customer_id", how="left")
    df_rfm = df_rfm.merge(customer_revenue, on="customer_id", how="left")
    df_rfm["tx_count"] = df_rfm["tx_count"].fillna(0)
    df_rfm["total_revenue"] = df_rfm["total_revenue"].fillna(0)

    fig = px.scatter(
        df_rfm,
        x="tx_count",
        y="total_revenue",
        color="segment",
        size="age",
        hover_data=["customer_id", "city"],
        color_discrete_sequence=px.colors.qualitative.Set2,
        opacity=0.6
    )
    fig.update_layout(
        height=450,
        xaxis_title="İşlem Sayısı (Son 90 Gün)",
        yaxis_title="Toplam Harcama (₺)",
        legend_title="Segment"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Müşteri tablosu
    st.markdown("### 📋 Müşteri Listesi")

    # Görüntülenecek sütunlar
    display_cols = ["customer_id", "first_name", "last_name", "city", "segment", "age", "has_app", "email_opted_in"]
    df_display = df_filtered[display_cols].copy()
    df_display.columns = ["ID", "Ad", "Soyad", "Şehir", "Segment", "Yaş", "App", "Email Opt-in"]

    # Arama
    search = st.text_input("🔍 Müşteri Ara (Ad, Soyad, ID)")
    if search:
        mask = (
            df_display["Ad"].str.contains(search, case=False, na=False) |
            df_display["Soyad"].str.contains(search, case=False, na=False) |
            df_display["ID"].str.contains(search, case=False, na=False)
        )
        df_display = df_display[mask]

    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
        hide_index=True
    )

    # Export butonu
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 CSV İndir",
        data=csv,
        file_name="musteri_analizi.csv",
        mime="text/csv"
    )


if __name__ == "__main__":
    main()
