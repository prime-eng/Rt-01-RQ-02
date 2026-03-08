import streamlit as st
import pandas as pd
from database import create_connection

st.set_page_config(page_title="Laporan Kas", page_icon="📊")
st.title("📊 Laporan Keuangan RT 01 RW 02")

conn = create_connection()

# --- 1. AMBIL DATA ---
df_kas = pd.read_sql("SELECT * FROM kas ORDER BY tanggal DESC", conn)

if not df_kas.empty:
    # Konversi kolom tanggal ke format datetime agar bisa difilter
    df_kas['tanggal'] = pd.to_datetime(df_kas['tanggal'])
    
    # --- 2. FILTER BERDASARKAN BULAN ---
    st.subheader("Filter Laporan")
    bulan_pilihan = st.selectbox("Pilih Bulan", sorted(df_kas['tanggal'].dt.strftime('%B %Y').unique()))
    
    # Filter data berdasarkan pilihan
    df_filtered = df_kas[df_kas['tanggal'].dt.strftime('%B %Y') == bulan_pilihan]
    
    # --- 3. METRIK RINGKASAN ---
    total_bulan_ini = df_filtered['jumlah'].sum()
    st.metric(f"Total Iuran ({bulan_pilihan})", f"Rp {total_bulan_ini:,.0f}")
    
    # --- 4. TABEL LAPORAN ---
    st.subheader(f"Detail Transaksi {bulan_pilihan}")
    st.dataframe(df_filtered[['tanggal', 'no_kk', 'jumlah', 'keterangan']], use_container_width=True)
    
    # --- 5. EKSPOR KE EXCEL (Fitur Tambahan) ---
    st.markdown("---")
    st.subheader("Unduh Laporan")
    
    # Fungsi untuk konversi dataframe ke CSV agar bisa dibuka di Excel
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Unduh Laporan (CSV/Excel)",
        data=csv,
        file_name=f"Laporan_Kas_{bulan_pilihan}.csv",
        mime="text/csv",
    )

else:
    st.info("Belum ada data transaksi kas yang tercatat.")

conn.close()