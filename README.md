# 🎬 CineReview — Movie Review & NLP Sentiment Analysis

Website review film berbasis Flask yang mengintegrasikan model NLP (Logistic Regression + TF-IDF) untuk analisis sentimen review secara real-time.

[![Vercel Website](https://img.shields.io/badge/Vercel-Visit%20Website-black?style=for-the-badge&logo=vercel)](https://cine-review-nlp.vercel.app/)

---

## ✨ Fitur

- **30 Film Terkurasi** — Data bank film dengan poster, sinopsis, cast, dan rating
- **5 Film Acak** — Setiap refresh menampilkan 5 film berbeda
- **Analisis Sentimen Real-time** — AJAX tanpa reload halaman
- **Model NLP** — Logistic Regression + TF-IDF terlatih pada IMDB 50K reviews
- **UI Premium** — Dark theme, Bootstrap 5, animasi mikro

---

## 📁 Struktur Project

```
web-movie-review-nlp/
├── app.py                  ← Flask app & NLP routes
├── vercel.json             ← Konfigurasi deployment Vercel
├── requirements.txt        ← Python dependencies
├── .env.example            ← Template environment variables
├── .gitignore
├── models/
│   ├── sentiment_model.pkl     ← Model Logistic Regression
│   └── tfidf_vectorizer.pkl    ← TF-IDF Vectorizer
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/main.js
```

---

## 🚀 Menjalankan Secara Lokal

### 1. Clone / masuk ke folder project
```bash
cd web-movie-review-nlp
```

### 2. Buat virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Buat file `.env` dari template
```bash
copy .env.example .env     # Windows
# cp .env.example .env     # macOS/Linux
```
Lalu edit `.env` dan isi `FLASK_SECRET_KEY` dengan nilai acak:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Jalankan server
```bash
python app.py
```

Buka browser: **http://127.0.0.1:5000**

---

## ☁️ Deploy ke Vercel

### Prasyarat
- Akun [Vercel](https://vercel.com) (gratis)
- Repository sudah di-push ke GitHub

### Langkah Deploy

1. **Login ke Vercel** dan klik **"Add New Project"**
2. **Import repository** GitHub kamu
3. **Framework Preset**: pilih **Other**
4. **Root Directory**: pastikan mengarah ke folder `web-movie-review-nlp`
5. **Environment Variables**: tambahkan di dashboard Vercel:
   | Key | Value |
   |-----|-------|
   | `FLASK_SECRET_KEY` | *(hasil `secrets.token_hex(32)`)* |
   | `FLASK_DEBUG` | `false` |
6. Klik **Deploy** 🚀

> **Catatan**: Vercel menjalankan Flask sebagai Serverless Function. File `.pkl` ikut di-deploy bersama kode karena berada dalam folder `models/`.

---

## 🔐 Keamanan

- File `.env` **tidak pernah** di-commit ke GitHub (ada di `.gitignore`)
- `FLASK_SECRET_KEY` di-load dari environment variable, bukan hardcoded
- Debug mode otomatis `false` saat deploy ke Vercel
- Gunakan **Vercel Environment Variables** untuk menyimpan secrets

---

## 🤖 Model NLP

| Komponen | Detail |
|---|---|
| Dataset | IMDB 50K Movie Reviews |
| Preprocessing | Lowercase, hapus HTML/URL/tanda baca |
| Vectorizer | TF-IDF (`tfidf_vectorizer.pkl`) |
| Classifier | Logistic Regression (`sentiment_model.pkl`) |
| Output | Positif / Negatif + Confidence Score |

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **ML/NLP**: scikit-learn, joblib
- **Frontend**: Bootstrap 5, Vanilla JS (AJAX)
- **Deploy**: Vercel (`@vercel/python`)
