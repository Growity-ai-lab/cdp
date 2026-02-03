"""
CDP Demo - Segment Builder Sayfası
Segmentleri görüntüle ve analiz et
"""

import streamlit as st
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys

# src klasörünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from segment_engine import SegmentEngine, PREDEFINED_SEGMENTS, SegmentDefinition

st.set_page_config(
    page_title="Segment Builder - CDP Demo",
    page_icon="🎯",
    layout="wide"
)


def load_data():
    """Veri dosyalarını yükle"""
    data_dir = Path("data")

    if not data_dir.exists() or not (data_dir / "customers.json").exists():
        return None

    return SegmentEngine("data")


def main():
    st.title("🎯 Segment Builder")
    st.markdown("Müşteri segmentlerini oluşturun ve analiz edin")

    # Engine yükle
    engine = load_data()

    if engine is None:
        st.warning("⚠️ Veri bulunamadı. Ana sayfadan veri oluşturun.")
        return

    # Tab yapısı
    tab1, tab2, tab3 = st.tabs(["📋 Hazır Segmentler", "🔧 Özel Segment", "📊 Karşılaştırma"])

    with tab1:
        st.markdown("### Hazır Segment Tanımları")
        st.markdown("CDP'de tanımlı olan segmentler ve performansları")

        # Segment seçimi
        segment_keys = list(PREDEFINED_SEGMENTS.keys())
        segment_names = {k: v.name for k, v in PREDEFINED_SEGMENTS.items()}

        selected_segment = st.selectbox(
            "Segment Seçin",
            options=segment_keys,
            format_func=lambda x: f"{segment_names[x]} ({x})"
        )

        if selected_segment:
            segment_def = PREDEFINED_SEGMENTS[selected_segment]
            results = engine.run_segment(segment_def)
            stats = engine.get_segment_stats(results)

            # Segment bilgisi
            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("#### Segment Tanımı")
                st.info(f"**{segment_def.name}**\n\n{segment_def.description}")

                st.markdown("**Koşullar:**")
                for i, cond in enumerate(segment_def.conditions, 1):
                    field = cond["field"]
                    op = cond["operator"]
                    val = cond["value"]
                    days = cond.get("days", "")
                    days_str = f" (son {days} gün)" if days else ""
                    st.code(f"{i}. {field} {op} {val}{days_str}")

                st.markdown(f"**Mantık:** `{segment_def.logic}`")

            with col2:
                st.markdown("#### Segment Metrikleri")

                # Metrikler
                m1, m2, m3, m4 = st.columns(4)

                with m1:
                    st.metric("Müşteri Sayısı", f"{stats['count']:,}")

                with m2:
                    st.metric("Oran", f"%{stats.get('percentage', 0)}")

                with m3:
                    st.metric("Toplam Gelir", f"₺{stats.get('total_revenue', 0):,.0f}")

                with m4:
                    st.metric("App Kullanım", f"%{stats.get('has_app_pct', 0):.1f}")

            st.divider()

            if stats["count"] > 0:
                # Detaylı grafikler
                col_left, col_right = st.columns(2)

                with col_left:
                    st.markdown("#### Şehir Dağılımı")
                    cities = stats.get("cities", {})
                    if cities:
                        fig = px.bar(
                            x=list(cities.keys()),
                            y=list(cities.values()),
                            color=list(cities.values()),
                            color_continuous_scale="Viridis"
                        )
                        fig.update_layout(
                            height=300,
                            showlegend=False,
                            xaxis_title="",
                            yaxis_title="Müşteri",
                            coloraxis_showscale=False
                        )
                        st.plotly_chart(fig, use_container_width=True)

                with col_right:
                    st.markdown("#### Cinsiyet Dağılımı")
                    gender = stats.get("gender_split", {})
                    if gender:
                        labels = {"M": "Erkek", "F": "Kadın"}
                        fig = px.pie(
                            values=list(gender.values()),
                            names=[labels.get(k, k) for k in gender.keys()],
                            hole=0.4
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)

                # Müşteri listesi
                st.markdown("#### Segment Müşterileri")

                df_results = pd.DataFrame(results)
                display_cols = ["customer_id", "first_name", "last_name", "city", "segment", "has_app"]
                df_display = df_results[display_cols].head(100)
                df_display.columns = ["ID", "Ad", "Soyad", "Şehir", "Segment", "App"]

                st.dataframe(df_display, use_container_width=True, height=300, hide_index=True)

    with tab2:
        st.markdown("### Özel Segment Oluştur")
        st.markdown("Kendi segment tanımınızı oluşturun")

        # Form
        with st.form("custom_segment"):
            col1, col2 = st.columns(2)

            with col1:
                segment_name = st.text_input("Segment Adı", placeholder="VIP İstanbul Müşterileri")

            with col2:
                segment_desc = st.text_input("Açıklama", placeholder="İstanbul'daki yüksek değerli müşteriler")

            st.markdown("#### Koşullar")

            # Koşul 1
            st.markdown("**Koşul 1**")
            c1_col1, c1_col2, c1_col3, c1_col4 = st.columns(4)

            with c1_col1:
                c1_field = st.selectbox(
                    "Alan",
                    options=["city", "segment", "has_app", "email_opted_in", "tx_count", "tx_total_amount"],
                    key="c1_field"
                )
            with c1_col2:
                c1_op = st.selectbox(
                    "Operatör",
                    options=["==", "!=", ">=", "<=", ">", "<", "in"],
                    key="c1_op"
                )
            with c1_col3:
                c1_value = st.text_input("Değer", key="c1_value", placeholder="İstanbul")
            with c1_col4:
                c1_days = st.number_input("Gün (opsiyonel)", min_value=0, value=0, key="c1_days")

            # Koşul 2
            st.markdown("**Koşul 2 (Opsiyonel)**")
            c2_col1, c2_col2, c2_col3, c2_col4 = st.columns(4)

            with c2_col1:
                c2_field = st.selectbox(
                    "Alan",
                    options=["", "city", "segment", "has_app", "email_opted_in", "tx_count", "tx_total_amount"],
                    key="c2_field"
                )
            with c2_col2:
                c2_op = st.selectbox(
                    "Operatör",
                    options=["==", "!=", ">=", "<=", ">", "<", "in"],
                    key="c2_op"
                )
            with c2_col3:
                c2_value = st.text_input("Değer", key="c2_value")
            with c2_col4:
                c2_days = st.number_input("Gün (opsiyonel)", min_value=0, value=0, key="c2_days")

            logic = st.radio("Mantık", options=["AND", "OR"], horizontal=True)

            submitted = st.form_submit_button("🔍 Segmenti Çalıştır", type="primary")

        if submitted and segment_name and c1_value:
            # Koşulları oluştur
            conditions = []

            # Değer dönüşümü
            def parse_value(val, field):
                if field in ["has_app", "email_opted_in"]:
                    return val.lower() in ["true", "1", "evet", "yes"]
                if field in ["tx_count", "tx_total_amount"]:
                    try:
                        return float(val)
                    except:
                        return val
                return val

            cond1 = {
                "field": c1_field,
                "operator": c1_op,
                "value": parse_value(c1_value, c1_field)
            }
            if c1_days > 0:
                cond1["days"] = c1_days
            conditions.append(cond1)

            if c2_field and c2_value:
                cond2 = {
                    "field": c2_field,
                    "operator": c2_op,
                    "value": parse_value(c2_value, c2_field)
                }
                if c2_days > 0:
                    cond2["days"] = c2_days
                conditions.append(cond2)

            # Segment oluştur ve çalıştır
            custom_segment = SegmentDefinition(
                name=segment_name,
                description=segment_desc,
                conditions=conditions,
                logic=logic
            )

            results = engine.run_segment(custom_segment)
            stats = engine.get_segment_stats(results)

            st.success(f"✅ Segment oluşturuldu: **{stats['count']}** müşteri bulundu ({stats.get('percentage', 0)}%)")

            if stats["count"] > 0:
                # Metrikler
                m1, m2, m3, m4 = st.columns(4)

                with m1:
                    st.metric("Müşteri", f"{stats['count']:,}")
                with m2:
                    st.metric("Gelir", f"₺{stats.get('total_revenue', 0):,.0f}")
                with m3:
                    st.metric("App", f"%{stats.get('has_app_pct', 0):.1f}")
                with m4:
                    st.metric("Ort. Yaş", f"{stats.get('avg_age', 0):.1f}")

                # Liste
                df_results = pd.DataFrame(results)
                st.dataframe(
                    df_results[["customer_id", "first_name", "last_name", "city", "segment"]].head(50),
                    use_container_width=True,
                    hide_index=True
                )

    with tab3:
        st.markdown("### Segment Karşılaştırması")
        st.markdown("Tüm segmentleri yan yana karşılaştırın")

        # Tüm segmentleri çalıştır
        segment_data = []
        for key, segment_def in PREDEFINED_SEGMENTS.items():
            results = engine.run_segment(segment_def)
            stats = engine.get_segment_stats(results)
            segment_data.append({
                "Segment": segment_def.name,
                "Müşteri": stats["count"],
                "Oran (%)": stats.get("percentage", 0),
                "Gelir (₺)": stats.get("total_revenue", 0),
                "App (%)": stats.get("has_app_pct", 0),
                "Ort. Yaş": stats.get("avg_age", 0)
            })

        df_segments = pd.DataFrame(segment_data)

        # Tablo
        st.dataframe(
            df_segments,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Gelir (₺)": st.column_config.NumberColumn(format="₺%.0f"),
                "Oran (%)": st.column_config.NumberColumn(format="%.1f%%"),
                "App (%)": st.column_config.NumberColumn(format="%.1f%%")
            }
        )

        st.divider()

        # Karşılaştırma grafikleri
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Müşteri Sayısı")
            fig = px.bar(
                df_segments,
                x="Segment",
                y="Müşteri",
                color="Müşteri",
                color_continuous_scale="Blues"
            )
            fig.update_layout(height=350, showlegend=False, coloraxis_showscale=False)
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Toplam Gelir")
            fig = px.bar(
                df_segments,
                x="Segment",
                y="Gelir (₺)",
                color="Gelir (₺)",
                color_continuous_scale="Greens"
            )
            fig.update_layout(height=350, showlegend=False, coloraxis_showscale=False)
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        # Radar chart
        st.markdown("#### Segment Özellikleri Karşılaştırması")

        # Normalize edilmiş değerler
        df_norm = df_segments.copy()
        for col in ["Müşteri", "Gelir (₺)", "App (%)", "Ort. Yaş"]:
            max_val = df_norm[col].max()
            if max_val > 0:
                df_norm[col] = df_norm[col] / max_val * 100

        categories = ["Müşteri", "Gelir (₺)", "App (%)", "Ort. Yaş"]

        fig = go.Figure()

        for _, row in df_norm.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row[cat] for cat in categories],
                theta=categories,
                fill='toself',
                name=row["Segment"][:20]
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=450,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3)
        )
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
