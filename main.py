
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# =========================
# DATABASE SQLITE
# =========================
def koneksi_database():
    return sqlite3.connect("prediksi_diabetes.db")


con = koneksi_database()
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS pasien (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_pasien TEXT NOT NULL,
    usia INTEGER NOT NULL,
    gula_darah REAL NOT NULL,
    bmi REAL NOT NULL,
    riwayat_ortu TEXT NOT NULL,
    hasil_prediksi TEXT NOT NULL
)
""")

con.commit()
con.close()


# =========================
# FUNGSI PREDIKSI
# =========================
def prediksi_diabetes(gula, bmi, riwayat):
    if gula >= 200:
        if bmi >= 30 and riwayat == "Ya":
            return "Sangat Tinggi"
        return "Tinggi"

    elif gula >= 140:
        if bmi >= 30 and riwayat == "Ya":
            return "Tinggi"
        return "Sedang"

    else:
        if bmi >= 30:
            if riwayat == "Ya":
                return "Sedang"
            return "Waspada"

        elif riwayat == "Ya":
            return "Waspada"

        else:
            return "Rendah"


# =========================
# FUNGSI SIMPAN DATA
# =========================
def simpan_data():
    nama = entry_nama.get().strip()
    usia = entry_usia.get().strip()
    gula = entry_gula.get().strip()
    bmi = entry_bmi.get().strip()
    riwayat = combo_riwayat.get()

    # Validasi input kosong
    if not nama or not usia or not gula or not bmi or not riwayat:
        messagebox.showwarning(
            "Peringatan",
            "Semua data harus diisi!"
        )
        return

    # Validasi angka
    try:
        usia = int(usia)
        gula = float(gula)
        bmi = float(bmi)

        if usia <= 0 or usia > 120:
            raise ValueError("Usia")

        if gula <= 0 or gula > 1000:
            raise ValueError("Gula")

        if bmi <= 0 or bmi > 100:
            raise ValueError("BMI")

    except ValueError as error:
        if str(error) == "Usia":
            pesan = "Usia harus antara 1 sampai 120 tahun."
        elif str(error) == "Gula":
            pesan = "Kadar gula darah harus lebih dari 0 dan maksimal 1000."
        elif str(error) == "BMI":
            pesan = "BMI harus lebih dari 0 dan maksimal 100."
        else:
            pesan = "Usia harus bilangan bulat, sedangkan gula darah dan BMI harus angka yang valid."

        messagebox.showerror("Input Tidak Valid", pesan)
        return

    # Menghitung prediksi
    hasil = prediksi_diabetes(gula, bmi, riwayat)

    # Simpan ke database
    con = koneksi_database()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO pasien
        (nama_pasien, usia, gula_darah, bmi,
         riwayat_ortu, hasil_prediksi)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nama, usia, gula, bmi, riwayat, hasil))

    con.commit()
    con.close()

    # Menampilkan hasil prediksi
    warna = {
        "Rendah": "#16A34A",
        "Waspada": "#CA8A04",
        "Sedang": "#EA580C",
        "Tinggi": "#DC2626",
        "Sangat Tinggi": "#7F1D1D"
    }

    label_hasil.config(
        text=f"Hasil Prediksi: {hasil}",
        fg=warna[hasil]
    )

    messagebox.showinfo(
        "Berhasil",
        "Data pasien berhasil disimpan!"
    )

    # Bersihkan form
    entry_nama.delete(0, tk.END)
    entry_usia.delete(0, tk.END)
    entry_gula.delete(0, tk.END)
    entry_bmi.delete(0, tk.END)
    combo_riwayat.set("")


# =========================
# FUNGSI LIHAT DATA
# =========================
def lihat_data():
    jendela = tk.Toplevel(root)
    jendela.title("Riwayat Data Pasien")
    jendela.geometry("1000x400")
    jendela.configure(bg="white")

    tk.Label(
        jendela,
        text="RIWAYAT DATA PASIEN",
        font=("Arial", 16, "bold"),
        bg="white"
    ).pack(pady=10)

    frame_tabel = tk.Frame(jendela)
    frame_tabel.pack(fill="both", expand=True, padx=10, pady=10)

    kolom = (
        "id", "nama_pasien", "usia", "gula_darah",
        "bmi", "riwayat_ortu", "hasil_prediksi"
    )

    tabel = ttk.Treeview(
        frame_tabel,
        columns=kolom,
        show="headings"
    )

    judul = {
        "id": "ID",
        "nama_pasien": "Nama Pasien",
        "usia": "Usia",
        "gula_darah": "Gula Darah",
        "bmi": "BMI",
        "riwayat_ortu": "Riwayat Ortu",
        "hasil_prediksi": "Hasil Prediksi"
    }

    lebar = {
        "id": 50,
        "nama_pasien": 180,
        "usia": 70,
        "gula_darah": 110,
        "bmi": 80,
        "riwayat_ortu": 120,
        "hasil_prediksi": 150
    }

    for nama_kolom in kolom:
        tabel.heading(nama_kolom, text=judul[nama_kolom])
        tabel.column(
            nama_kolom,
            width=lebar[nama_kolom],
            anchor="center"
        )

    scroll_y = ttk.Scrollbar(
        frame_tabel,
        orient="vertical",
        command=tabel.yview
    )
    scroll_x = ttk.Scrollbar(
        frame_tabel,
        orient="horizontal",
        command=tabel.xview
    )

    tabel.configure(
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set
    )

    tabel.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")

    frame_tabel.rowconfigure(0, weight=1)
    frame_tabel.columnconfigure(0, weight=1)

    con = koneksi_database()
    cur = con.cursor()

    cur.execute("""
        SELECT id, nama_pasien, usia, gula_darah,
               bmi, riwayat_ortu, hasil_prediksi
        FROM pasien
        ORDER BY id DESC
    """)

    data = cur.fetchall()
    con.close()

    for pasien in data:
        tabel.insert("", "end", values=pasien)

    if not data:
        messagebox.showinfo(
            "Informasi",
            "Belum ada data pasien yang tersimpan.",
            parent=jendela
        )


# =========================
# TAMPILAN TKINTER
# =========================
root = tk.Tk()
root.title("Aplikasi Prediksi Risiko Diabetes")
root.geometry("520x650")
root.configure(bg="#F1F5F9")
root.resizable(False, False)

tk.Label(
    root,
    text="PREDIKSI RISIKO DIABETES",
    font=("Arial", 17, "bold"),
    bg="#1D4ED8",
    fg="white",
    pady=18
).pack(fill="x")

tk.Label(
    root,
    text="Masukkan Data Pasien",
    font=("Arial", 12, "bold"),
    bg="#F1F5F9"
).pack(pady=12)

form = tk.Frame(root, bg="white", padx=25, pady=20)
form.pack(padx=25, fill="x")


def buat_input(teks, baris):
    tk.Label(
        form,
        text=teks,
        font=("Arial", 10),
        bg="white"
    ).grid(row=baris, column=0, sticky="w", pady=9)

    entry = tk.Entry(form, width=28, font=("Arial", 10))
    entry.grid(row=baris, column=1, padx=10, pady=9)
    return entry


entry_nama = buat_input("Nama Pasien", 0)
entry_usia = buat_input("Usia (tahun)", 1)
entry_gula = buat_input("Gula Darah (mg/dL)", 2)
entry_bmi = buat_input("BMI", 3)

tk.Label(
    form,
    text="Riwayat Diabetes Ortu",
    font=("Arial", 10),
    bg="white"
).grid(row=4, column=0, sticky="w", pady=9)

combo_riwayat = ttk.Combobox(
    form,
    values=["Ya", "Tidak"],
    state="readonly",
    width=25,
    font=("Arial", 10)
)
combo_riwayat.grid(row=4, column=1, padx=10, pady=9)

# Tombol simpan
tk.Button(
    root,
    text="Prediksi & Simpan Data",
    command=simpan_data,
    bg="#2563EB",
    fg="white",
    font=("Arial", 11, "bold"),
    width=25,
    pady=8
).pack(pady=15)

# Label hasil
label_hasil = tk.Label(
    root,
    text="Hasil Prediksi: -",
    font=("Arial", 14, "bold"),
    bg="#F1F5F9",
    fg="#334155"
)
label_hasil.pack(pady=5)

# Tombol lihat data
tk.Button(
    root,
    text="Lihat Data Pasien",
    command=lihat_data,
    bg="#0F766E",
    fg="white",
    font=("Arial", 10, "bold"),
    width=25,
    pady=7
).pack(pady=12)

tk.Label(
    root,
    text="Data disimpan menggunakan database SQLite",
    font=("Arial", 8),
    bg="#F1F5F9",
    fg="#64748B"
).pack(side="bottom", pady=10)

root.mainloop()
