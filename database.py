import sqlite3
import logging

# Konstanta nama database
DB_NAME = 'data_rt.db'

def create_connection():
    """Membuat koneksi ke database SQLite."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        logging.error(f"Gagal koneksi ke database: {e}")
        return None

def create_tables():
    """Memastikan semua tabel yang dibutuhkan sudah ada."""
    conn = create_connection()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        
        # 1. Tabel Warga
        cursor.execute('''CREATE TABLE IF NOT EXISTS warga 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      no_kk TEXT, 
                      nama TEXT, 
                      alamat TEXT,
                      status TEXT DEFAULT 'Aktif',
                      tipe_kk TEXT DEFAULT 'Tetap')''')
        
        # 2. Tabel Kas
        cursor.execute('''CREATE TABLE IF NOT EXISTS kas 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      no_kk TEXT, 
                      jumlah REAL, 
                      tanggal DATE, 
                      keterangan TEXT,
                      tipe TEXT DEFAULT 'Kas Masuk',
                      penanggung_jawab TEXT)''')
        
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error saat membuat tabel: {e}")
    finally:
        conn.close()

def migrate_database():
    """
    Menambahkan kolom yang diperlukan ke tabel yang sudah ada 
    tanpa menghapus data yang tersimpan sebelumnya.
    """
    conn = create_connection()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        
        # Migrasi Tabel Kas
        cursor.execute("PRAGMA table_info(kas)")
        cols_kas = [info[1] for info in cursor.fetchall()]
        
        if 'tipe' not in cols_kas:
            cursor.execute("ALTER TABLE kas ADD COLUMN tipe TEXT DEFAULT 'Kas Masuk'")
        if 'penanggung_jawab' not in cols_kas:
            cursor.execute("ALTER TABLE kas ADD COLUMN penanggung_jawab TEXT")
            
        # Migrasi Tabel Warga
        cursor.execute("PRAGMA table_info(warga)")
        cols_warga = [info[1] for info in cursor.fetchall()]
        
        if 'status' not in cols_warga:
            cursor.execute("ALTER TABLE warga ADD COLUMN status TEXT DEFAULT 'Aktif'")
        if 'tipe_kk' not in cols_warga:
            cursor.execute("ALTER TABLE warga ADD COLUMN tipe_kk TEXT DEFAULT 'Tetap'")
            
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error saat migrasi database: {e}")
    finally:
        conn.close()