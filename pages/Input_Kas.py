import streamlit as st
import pandas as pd
from database import create_connection

st.set_page_config(page_title="Manajemen Kas", page_icon="💰", layout="wide")
st.title("💰 Manajemen Kas RT 01 RW 02")

# --- 1. FORM INPUT KAS ---
with st.expander("➕ Tambah Transaksi", expanded=True):
    tipe_transaksi = st.radio("Pilih Jenis Transaksi:", ["Kas Masuk", "Kas Keluar"], horizontal=True)
    
    # Ambil data warga untuk Kas Masuk
    conn = create_connection()
    df_warga = pd.read_sql("SELECT nama, no_kk FROM warga", conn)
    conn.close()
    
    with st.form("form_kas", clear_on_submit=True):
        # Logika input berdasarkan tipe
        if tipe_transaksi == "Kas Masuk":
            if not df_warga.empty:
                nama_pilih = st.selectbox("Pilih Warga", df_warga['nama'].tolist())
            else:
                st.warning("Data warga kosong.")
        else:
            # Input untuk Kas Keluar
            jabatan = st.selectbox("Pihak Pengeluar:", ["RT", "Staff RT", "Dasawisma"])
            nama_pengeluar = st.text_input("Nama Lengkap Pengeluar:")
            nama_pilih = None # Reset untuk Kas Keluar
        
        jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=1000)
        keterangan = st.text_input("Peruntukan/Keterangan")
        tanggal = st.date_input("Tanggal")
        
        if st.form_submit_button("Simpan Transaksi"):
            if jumlah > 0:
                # Siapkan data database
                no_kk = df_warga[df_warga['nama'] == nama_pilih]['no_kk'].values[0] if tipe_transaksi == "Kas Masuk" else None
                pj = f"{jabatan} - {nama_pengeluar}" if tipe_transaksi == "Kas Keluar" else None
                
                conn = create_connection()
                c = conn.cursor()
                c.execute("""INSERT INTO kas (no_kk, jumlah, tanggal, keterangan, tipe, penanggung_jawab) 
                             VALUES (?, ?, ?, ?, ?, ?)""", 
                          (no_kk, jumlah, tanggal, keterangan, tipe_transaksi, pj))
                conn.commit()
                conn.close()
                
                st.success(f"✅ {tipe_transaksi} berhasil disimpan.")
                st.rerun()
            else:
                st.error("Jumlah harus lebih dari 0!")

# --- 2. TABEL & SALDO ---
st.subheader("📊 Laporan Keuangan")
conn = create_connection()
df_kas = pd.read_sql("SELECT * FROM kas", conn)
conn.close()

if not df_kas.empty:
    # Merapikan kolom untuk tampilan
    display_df = df_kas.fillna('-') # Ganti nilai kosong dengan '-'
    st.dataframe(display_df, use_container_width=True)
    
    masuk = df_kas[df_kas['tipe'] == 'Kas Masuk']['jumlah'].sum()
    keluar = df_kas[df_kas['tipe'] == 'Kas Keluar']['jumlah'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Masuk", f"Rp {masuk:,}")
    col2.metric("Total Keluar", f"Rp {keluar:,}")
    col3.metric("Saldo Akhir", f"Rp {masuk - keluar:,}")
else:
    st.info("Belum ada transaksi.")