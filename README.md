# LabCare — Backend REST API

LabCare adalah backend untuk mencatat kerusakan fasilitas laboratorium, memantau status penanganan, dan menyimpan riwayat perubahan status.

## Teknologi
- Python 3.10+
- FastAPI dan Pydantic v2
- SQLAlchemy 2
- SQLite
- Pytest dan FastAPI TestClient

## Fitur
- CRUD fasilitas laboratorium
- CRUD laporan kerusakan
- Filter laporan berdasarkan status, prioritas, atau fasilitas
- Aturan perpindahan status: `reported` → `in_progress` → `completed`
- Riwayat status laporan
- Validasi data dan penanganan error 404/409/422
- Dokumentasi API otomatis melalui Swagger UI

## Menjalankan di Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Buka `http://127.0.0.1:8000/docs` untuk mencoba endpoint. Database `labcare.db` dibuat otomatis saat aplikasi dimulai.

## Menjalankan pengujian

```powershell
pytest -v
```

Jalankan dari folder utama proyek (yang berisi `pytest.ini`). Pengujian menggunakan SQLite in-memory terpisah, jadi tidak memakai data pada `labcare.db`.

## Endpoint utama

| Method | Endpoint | Kegunaan |
|---|---|---|
| POST | `/api/v1/facilities` | Membuat fasilitas |
| GET | `/api/v1/facilities` | Melihat semua fasilitas |
| GET | `/api/v1/facilities/{id}` | Melihat satu fasilitas |
| PATCH | `/api/v1/facilities/{id}` | Mengubah fasilitas |
| DELETE | `/api/v1/facilities/{id}` | Menghapus fasilitas yang belum memiliki laporan |
| POST | `/api/v1/reports` | Membuat laporan |
| GET | `/api/v1/reports` | Melihat laporan, bisa difilter |
| GET | `/api/v1/reports/{id}` | Melihat satu laporan |
| PATCH | `/api/v1/reports/{id}` | Mengubah laporan/status |
| DELETE | `/api/v1/reports/{id}` | Menghapus laporan |
| GET | `/api/v1/reports/{id}/histories` | Melihat riwayat status |

Contoh filter: `/api/v1/reports?status=in_progress&priority=high`.

## Contoh data fasilitas

```json
{
  "name": "Komputer Lab 1",
  "code": "KOM-01",
  "room": "Lab A",
  "condition": "good"
}
```

Kondisi fasilitas: `good`, `damaged`, `maintenance`. Kode fasilitas otomatis diubah ke huruf besar dan harus unik (tidak peka huruf besar/kecil). Spasi di awal/akhir teks dibuang.

## Contoh data laporan

```json
{
  "facility_id": 1,
  "title": "Keyboard tidak berfungsi",
  "description": "Beberapa tombol keyboard tidak merespons saat digunakan.",
  "category": "hardware",
  "priority": "medium"
}
```

Kategori: `hardware`, `software`, `network`, `other`. Prioritas: `low`, `medium`, `high`.

Untuk mengubah status, kirim PATCH seperti:

```json
{
  "status": "in_progress",
  "note": "Sedang diperiksa teknisi"
}
```

`note` bersifat opsional dan digunakan bersama perubahan status. Kirim `"assigned_to": null` untuk membatalkan penugasan petugas. Perubahan field, status, dan riwayat disimpan dalam satu transaksi. Status harus bergerak berurutan dari `reported` ke `in_progress`, lalu `completed`.

## Struktur dan SOLID
- `routers/`: menerima request HTTP dan menentukan response.
- `schemas/`: kontrak input/output dan validasi Pydantic.
- `services/`: aturan bisnis serta alur proses.
- `repositories/`: operasi database.
- `models/`: tabel SQLAlchemy.
- `database.py`: engine dan session database.
- `dependencies.py`: merakit dependency dengan FastAPI `Depends`.
- `tests/`: pengujian API dan unit test service.

Pemisahan router/service/repository mendukung SRP. Dependency service disuntikkan melalui fungsi dependency sehingga komponen lebih mudah diganti atau diuji, mendukung DIP. Kontrak repository yang terpisah per domain membantu ISP. OCP dan LSP lebih terlihat saat implementasi dikembangkan dengan repository alternatif yang memenuhi kontrak yang sama; jangan mengklaim prinsip itu hanya karena foldernya terpisah.

## Catatan batasan versi tugas

Versi ini belum menerapkan autentikasi/login, role-based access control, upload gambar, atau deployment cloud. `assigned_to` hanya berupa teks nama petugas, bukan relasi akun pengguna. Fitur tersebut dapat ditambahkan jika memang diminta dosen.
