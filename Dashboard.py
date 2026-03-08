import streamlit as st
import pandas as pd
from database import create_tables, create_connection, migrate_database

# 1. Inisialisasi & Migrasi Database
create_tables()
migrate_database() 

st.set_page_config(
    page_title="Dashboard Data RT",
    page_icon="🏠",
    layout="wide"
)

# --- FUNGSI LOAD CSS ---
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("style.css")

# --- HEADER ---
col_head1, col_head2 = st.columns([1, 5])
with col_head1:
    st.write("### 🏠 RT 01 RW 02")
with col_head2:
    st.title("Dashboard Data RT 01 RW 02 KP.Sekejulang")
    st.subheader("Sistem Administrasi Warga & Keuangan Terpadu")

st.markdown("---")

# --- FITUR PENCARIAN WARGA ---
st.markdown("### 🔍 Pencarian Cepat Warga")
search_query = st.text_input("Cari Nama Lengkap atau No KK:", placeholder="Masukkan nama atau 16 digit No KK...")

conn = create_connection()
try:
    # Load semua data untuk pencarian dan metrik
    df_warga_all = pd.read_sql("SELECT * FROM warga", conn)
    df_warga_aktif = df_warga_all[df_warga_all['status'] == 'Aktif']
    df_kas = pd.read_sql("SELECT * FROM kas", conn)

    # Logika Pencarian
    if search_query:
        # Filter berdasarkan nama (case-insensitive) atau No KK
        hasil_cari = df_warga_all[
            (df_warga_all['nama'].str.contains(search_query, case=False, na=False)) |
            (df_warga_all['no_kk'].str.contains(search_query, na=False))
        ]
        
        if not hasil_cari.empty:
            st.success(f"Ditemukan {len(hasil_cari)} data:")
            st.dataframe(hasil_cari[['no_kk', 'nama', 'tipe_kk', 'status', 'alamat']], use_container_width=True)
        else:
            st.warning("Data warga tidak ditemukan.")
    
    st.markdown("---")

    # --- METRIC & DATA ---
    # Perhitungan Saldo Akurat
    if not df_kas.empty:
        total_masuk = df_kas[df_kas['tipe'] == 'Kas Masuk']['jumlah'].sum() if 'tipe' in df_kas.columns else df_kas['jumlah'].sum()
        total_keluar = df_kas[df_kas['tipe'] == 'Kas Keluar']['jumlah'].sum() if 'tipe' in df_kas.columns else 0
        saldo_akhir = total_masuk - total_keluar
    else:
        total_masuk, total_keluar, saldo_akhir = 0, 0, 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Warga (Aktif)", f"{len(df_warga_aktif)} Jiwa")
    c2.metric("Kas Masuk", f"Rp {total_masuk:,.0f}")
    c3.metric("Kas Keluar", f"Rp {total_keluar:,.0f}")
    c4.metric("Saldo Akhir", f"Rp {saldo_akhir:,.0f}")
    
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
finally:
    conn.close()

st.markdown("---")

# --- AKTIVITAS TERBARU ---
st.markdown("### 📋 5 Transaksi Keuangan Terakhir")
if not df_kas.empty:
    cols_to_show = ['tanggal', 'keterangan', 'tipe', 'jumlah', 'penanggung_jawab']
    existing_cols = [c for c in cols_to_show if c in df_kas.columns]
    df_display = df_kas[existing_cols].sort_values(by='tanggal', ascending=False).head(5)
    df_display = df_display.fillna('-')
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("Belum ada data transaksi.")

st.caption("Dashboard Data RT | RT 01 RW 02 | © 2026 Aplikasi Administrasi Terpadu")
