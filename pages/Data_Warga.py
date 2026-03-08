import streamlit as st
import pandas as pd
from database import create_connection
from database import create_connection, migrate_database

# Tambahkan ini untuk memastikan database diperbarui saat halaman dibuka
migrate_database()

st.set_page_config(page_title="Data Warga", page_icon="👥", layout="wide")
st.title("👥 Manajemen Data Warga")

# --- 1. FUNGSI DIALOG HAPUS ---
@st.dialog("Konfirmasi Penghapusan Data")
def hapus_warga_dialog(nama_warga):
    st.warning(f"Anda akan menghapus data warga: **{nama_warga}**")
    
    with st.form("form_hapus_warga"):
        alasan = st.radio("Pilih alasan penghapusan:", ["Meninggal", "Pindah", "Lainnya"])
        detail_alasan = st.text_input("Detail alasan (opsional):")
        
        if st.form_submit_button("Hapus Data Sekarang"):
            conn = create_connection()
            c = conn.cursor()
            c.execute("DELETE FROM warga WHERE nama = ?", (nama_warga,))
            conn.commit()
            conn.close()
            st.success(f"Data {nama_warga} berhasil dihapus.")
            del st.session_state.target_hapus
            st.rerun()

# --- 2. FORM TAMBAH/EDIT ---
with st.expander("➕ Tambah atau Edit Warga"):
    with st.form("form_warga", clear_on_submit=False):
        warga_id = st.number_input("ID (Isi ID jika ingin Edit data)", min_value=0, value=0)
        col1, col2 = st.columns(2)
        with col1:
            no_kk = st.text_input("No KK (16 Digit)", max_chars=16)
            nama = st.text_input("Nama Lengkap")
            # Input baru untuk tipe KK
            tipe_kk = st.radio("Tipe KK:", ["Tetap", "Musiman"], horizontal=True)
        with col2:
            alamat = st.text_area("Alamat Lengkap")
        
        if st.form_submit_button("Simpan Data"):
            if len(no_kk) != 16 or not no_kk.isdigit():
                st.error("❌ No KK harus berisi tepat 16 digit angka!")
            else:
                conn = create_connection()
                c = conn.cursor()
                if warga_id == 0:
                    c.execute("INSERT INTO warga (no_kk, nama, alamat, tipe_kk) VALUES (?, ?, ?, ?)", 
                              (no_kk, nama, alamat, tipe_kk))
                else:
                    c.execute("UPDATE warga SET no_kk=?, nama=?, alamat=?, tipe_kk=? WHERE id=?", 
                              (no_kk, nama, alamat, tipe_kk, warga_id))
                conn.commit()
                conn.close()
                st.success(f"Data berhasil disimpan sebagai warga {tipe_kk}!")
                st.rerun()

# --- 3. TABEL & FITUR HAPUS ---
st.subheader("📋 Daftar Seluruh Warga")
conn = create_connection()
df_warga = pd.read_sql("SELECT * FROM warga", conn)
conn.close()

if not df_warga.empty:
    # Menggunakan Tabs untuk memisahkan tampilan warga berdasarkan tipe KK
    tab1, tab2 = st.tabs(["Warga Tetap", "Warga Musiman"])
    
    with tab1:
        st.dataframe(df_warga[df_warga['tipe_kk'] == 'Tetap'], use_container_width=True)
    with tab2:
        st.dataframe(df_warga[df_warga['tipe_kk'] == 'Musiman'], use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🗑️ Hapus Data")
    warga_list = df_warga['nama'].tolist()
    pilihan = st.selectbox("Pilih warga yang akan dihapus:", warga_list)
    
    if st.button("Hapus Data Terpilih"):
        st.session_state.target_hapus = pilihan
        st.rerun()

    if "target_hapus" in st.session_state:
        hapus_warga_dialog(st.session_state.target_hapus)
else:
    st.info("Belum ada data warga tersimpan.")