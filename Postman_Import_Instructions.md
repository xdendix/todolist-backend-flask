# Cara Import Collection Postman

## Langkah-langkah Import:

1. **Buka Postman**
   - Jalankan aplikasi Postman di komputer Anda

2. **Klik Import**
   - Di pojok kiri atas, klik tombol **"Import"**

3. **Pilih File**
   - Klik tab **"File"**
   - Klik **"Upload Files"**
   - Cari dan pilih file: `TodoList_API_Postman_Collection.json`

4. **Import Berhasil**
   - Klik **"Import"**
   - Collection "TodoList Flask API" akan muncul di sidebar kiri

## Setup Environment Variable:

1. **Buat Environment Baru**
   - Klik ikon mata di pojok kanan atas
   - Klik **"Add"** untuk membuat environment baru

2. **Konfigurasi Variable**
   - **Variable name:** `base_url`
   - **Initial value:** `http://127.0.0.1:5000`
   - **Current value:** `http://127.0.0.1:5000`

3. **Aktifkan Environment**
   - Pilih environment yang baru dibuat dari dropdown

## Jalankan Flask App:

Pastikan Flask app Anda sudah berjalan:

```bash
cd /home/xdendix/Documents/Programming/todolist-backend-flask
source todolist_backend_venv/bin/activate
python app.py
```

## Mulai Testing:

1. **Pilih Collection**
   - Klik collection "TodoList Flask API" di sidebar

2. **Jalankan Request**
   - Klik request yang ingin ditest
   - Klik tombol **"Send"**

3. **Test Secara Berurutan:**
   - Health Check
   - Get All Todos
   - Create Todo
   - Get Todo by ID
   - Update Todo
   - Search Todos
   - Delete Todo

## File yang Dibutuhkan:

- ✅ `TodoList_API_Postman_Collection.json` - Collection Postman
- ✅ `POSTMAN_TESTING_GUIDE.md` - Panduan lengkap testing

## Tips:

- Pastikan Flask app berjalan di port 5000
- Gunakan environment variable agar mudah mengubah URL
- Test error cases untuk memastikan validasi bekerja
- Perhatikan response code dan body untuk setiap request

---

**Collection siap digunakan! 🚀**
