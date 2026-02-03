"""
CDP Demo - Export Sayfası
Meta, Google, TikTok platformlarına audience export
"""

import streamlit as st
import json
from pathlib import Path
import pandas as pd
import sys
from datetime import datetime

# src klasörünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from segment_engine import SegmentEngine, PREDEFINED_SEGMENTS
from platform_export import PlatformExporter

st.set_page_config(
    page_title="Platform Export - CDP Demo",
    page_icon="📤",
    layout="wide"
)


def load_data():
    """Veri dosyalarını yükle"""
    data_dir = Path("data")

    if not data_dir.exists() or not (data_dir / "customers.json").exists():
        return None, None

    engine = SegmentEngine("data")
    exporter = PlatformExporter("data", "exports")

    return engine, exporter


def main():
    st.title("📤 Platform Export")
    st.markdown("Segmentleri reklam platformlarına export edin")

    # Engine ve exporter yükle
    result = load_data()

    if result[0] is None:
        st.warning("⚠️ Veri bulunamadı. Ana sayfadan veri oluşturun.")
        return

    engine, exporter = result

    # Platform bilgileri
    st.markdown("### 🎯 Desteklenen Platformlar")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1877f2, #42b72a); padding: 1.5rem; border-radius: 10px; color: white;">
            <h3 style="margin: 0; color: white;">📘 Meta</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Facebook & Instagram Custom Audiences</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.9;">SHA256 hashed email & phone</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4285f4, #34a853); padding: 1.5rem; border-radius: 10px; color: white;">
            <h3 style="margin: 0; color: white;">🔍 Google</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Google Ads Customer Match</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.9;">SHA256 hashed email & phone</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #000000, #fe2c55); padding: 1.5rem; border-radius: 10px; color: white;">
            <h3 style="margin: 0; color: white;">🎵 TikTok</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">TikTok Custom Audiences</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.9;">SHA256 hashed identifiers</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Tab yapısı
    tab1, tab2, tab3 = st.tabs(["🎯 Tek Segment Export", "📦 Toplu Export", "📁 Export Geçmişi"])

    with tab1:
        st.markdown("### Segment Seçin ve Export Edin")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Segment seçimi
            segment_keys = list(PREDEFINED_SEGMENTS.keys())
            segment_names = {k: v.name for k, v in PREDEFINED_SEGMENTS.items()}

            selected_segment = st.selectbox(
                "Segment",
                options=segment_keys,
                format_func=lambda x: f"{segment_names[x]}"
            )

            # Platform seçimi
            platforms = st.multiselect(
                "Platformlar",
                options=["meta", "google", "tiktok"],
                default=["meta", "google", "tiktok"],
                format_func=lambda x: {"meta": "📘 Meta", "google": "🔍 Google", "tiktok": "🎵 TikTok"}.get(x, x)
            )

        with col2:
            # Segment özeti
            if selected_segment:
                segment_def = PREDEFINED_SEGMENTS[selected_segment]
                results = engine.run_segment(segment_def)
                stats = engine.get_segment_stats(results)

                st.markdown("#### Segment Özeti")
                st.metric("Müşteri Sayısı", f"{stats['count']:,}")
                st.metric("Email Opt-in", f"%{sum(1 for c in results if c.get('email_opted_in', False)) / max(len(results), 1) * 100:.1f}")

        st.divider()

        # Export butonu
        if st.button("📤 Export Başlat", type="primary", use_container_width=True):
            if not platforms:
                st.error("En az bir platform seçin!")
                return

            with st.spinner(f"'{segment_names[selected_segment]}' segmenti export ediliyor..."):
                exports = exporter.export_segment(selected_segment, platforms)

                if exports:
                    st.success("✅ Export tamamlandı!")

                    for platform, filepath in exports.items():
                        # Dosya içeriğini oku
                        with open(filepath, "r") as f:
                            content = f.read()

                        # Download butonu
                        st.download_button(
                            label=f"📥 {platform.upper()} dosyasını indir",
                            data=content,
                            file_name=Path(filepath).name,
                            mime="text/csv"
                        )

                        # Önizleme
                        with st.expander(f"📄 {platform.upper()} Önizleme"):
                            df = pd.read_csv(filepath)
                            st.dataframe(df.head(10), use_container_width=True, hide_index=True)
                            st.caption(f"Toplam {len(df)} kayıt")
                else:
                    st.warning("Export edilecek müşteri bulunamadı (consent kontrolü).")

    with tab2:
        st.markdown("### Tüm Segmentleri Export Et")
        st.markdown("Tüm tanımlı segmentleri seçili platformlara toplu export edin")

        # Platform seçimi
        bulk_platforms = st.multiselect(
            "Platformlar",
            options=["meta", "google", "tiktok"],
            default=["meta"],
            format_func=lambda x: {"meta": "📘 Meta", "google": "🔍 Google", "tiktok": "🎵 TikTok"}.get(x, x),
            key="bulk_platforms"
        )

        # Segment listesi
        st.markdown("#### Export Edilecek Segmentler")

        segment_preview = []
        for key, seg in PREDEFINED_SEGMENTS.items():
            results = engine.run_segment(seg)
            stats = engine.get_segment_stats(results)
            segment_preview.append({
                "Segment": seg.name,
                "Key": key,
                "Müşteri": stats["count"],
                "Tahmini Export": sum(1 for c in results if c.get("email_opted_in", False))
            })

        df_preview = pd.DataFrame(segment_preview)
        st.dataframe(df_preview, use_container_width=True, hide_index=True)

        total_exports = df_preview["Tahmini Export"].sum()
        st.info(f"📊 Toplam tahmini export: **{total_exports:,}** müşteri × **{len(bulk_platforms)}** platform = **{total_exports * len(bulk_platforms):,}** kayıt")

        if st.button("📦 Toplu Export Başlat", type="primary", use_container_width=True):
            if not bulk_platforms:
                st.error("En az bir platform seçin!")
                return

            progress_bar = st.progress(0)
            status_text = st.empty()

            all_exports = {}
            total = len(PREDEFINED_SEGMENTS)

            for i, (key, seg) in enumerate(PREDEFINED_SEGMENTS.items()):
                status_text.text(f"Export ediliyor: {seg.name}...")
                exports = exporter.export_segment(key, bulk_platforms)
                if exports:
                    all_exports[key] = exports
                progress_bar.progress((i + 1) / total)

            status_text.empty()
            progress_bar.empty()

            st.success(f"✅ Toplu export tamamlandı! {len(all_exports)} segment export edildi.")

            # Özet rapor
            report = exporter.generate_summary_report(all_exports)
            st.code(report, language="text")

    with tab3:
        st.markdown("### Export Geçmişi")
        st.markdown("Daha önce oluşturulan export dosyaları")

        exports_dir = Path("exports")

        if not exports_dir.exists():
            st.info("Henüz export yapılmamış.")
            return

        export_files = list(exports_dir.glob("*.csv"))

        if not export_files:
            st.info("Export dosyası bulunamadı.")
            return

        # Dosyaları listele
        file_data = []
        for f in sorted(export_files, key=lambda x: x.stat().st_mtime, reverse=True):
            stat = f.stat()
            # Dosya adından platform ve segment bilgisi çıkar
            parts = f.stem.split("_")
            platform = parts[0] if parts else "?"
            segment = "_".join(parts[2:-2]) if len(parts) > 4 else "?"

            # Satır sayısı
            with open(f, "r") as file:
                row_count = sum(1 for _ in file) - 1  # Header hariç

            file_data.append({
                "Dosya": f.name,
                "Platform": platform.upper(),
                "Segment": segment,
                "Kayıt": row_count,
                "Boyut": f"{stat.st_size / 1024:.1f} KB",
                "Tarih": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            })

        df_files = pd.DataFrame(file_data)
        st.dataframe(df_files, use_container_width=True, hide_index=True)

        # Dosya seçip indir
        selected_file = st.selectbox(
            "İndirilecek dosyayı seçin",
            options=[f.name for f in export_files],
            key="download_select"
        )

        if selected_file:
            file_path = exports_dir / selected_file
            with open(file_path, "r") as f:
                content = f.read()

            col1, col2 = st.columns([1, 1])

            with col1:
                st.download_button(
                    label="📥 Dosyayı İndir",
                    data=content,
                    file_name=selected_file,
                    mime="text/csv",
                    use_container_width=True
                )

            with col2:
                if st.button("🗑️ Dosyayı Sil", use_container_width=True):
                    file_path.unlink()
                    st.success(f"Dosya silindi: {selected_file}")
                    st.rerun()

            # Önizleme
            with st.expander("📄 Dosya Önizleme"):
                df = pd.read_csv(file_path)
                st.dataframe(df.head(20), use_container_width=True, hide_index=True)

    # Footer
    st.divider()
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
        <h4 style="margin: 0 0 0.5rem 0;">ℹ️ Export Hakkında</h4>
        <ul style="margin: 0; padding-left: 1.5rem; font-size: 0.9rem;">
            <li><strong>KVKK Uyumlu:</strong> Sadece opt-in vermiş müşteriler export edilir</li>
            <li><strong>Hash'li Veriler:</strong> Email ve telefon SHA256 ile hash'lenir</li>
            <li><strong>Platform Formatları:</strong> Her platform için uygun CSV formatı</li>
            <li><strong>API Entegrasyonu:</strong> v0.2'de otomatik upload gelecek</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
