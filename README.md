# AXIOM AI AGENTS
**Autonomous Financial Intelligence & Quantitative Research System**

AXIOM AI AGENTS adalah sistem kecerdasan finansial terminal-first dan platform riset kuantitatif multi-agen. Dirancang untuk para analis kuantitatif, peneliti, dan manajer portofolio dengan prinsip:
1. **Auditability First**: Setiap angka berasal dari eksekusi kode deterministik di sandbox Python/SQL (bukan halusinasi LLM).
2. **Zero Look-Ahead Bias**: Eksekusi sinyal backtest dialirkan ke $t+1$ dengan friksi biaya nyata (komisi dan slippage).
3. **Skeptic / Verification Audit**: Verifikasi wajib sebelum kesimpulan akhir disajikan.
4. **Alat Riset, Bukan Penasihat Investasi**: Menghasilkan analisis skenario dan batasan risiko tanpa rekomendasi beli/jual.

---

## 1. Instalasi & Setup Cepat (macOS Apple Silicon & Linux)

```bash
# 1. Masuk ke direktori proyek
cd /Users/anselvarian/Documents/AXIOM

# 2. Buat & aktifkan virtual environment (Python 3.11+)
python3 -m venv .venv
source .venv/bin/activate

# 3. Install paket dalam mode editable
pip install --no-build-isolation -e . --no-deps

# 4. Salin konfigurasi environment
cp .env.example .env

# 5. Jalankan verifikasi pengujian otomatis
pytest tests/ -v

# 6. Periksa status sistem & provider
axiom status
```

---

## 2. Perintah CLI yang Diuji & Berfungsi Penuh

Semua perintah di bawah ini telah teruji end-to-end dengan sumber data nyata dari internet:

| Perintah CLI | Deskripsi & Aksi |
| :--- | :--- |
| `axiom` | Mode interaktif dengan pemrosesan bahasa alami (Natural Language Planner) |
| `axiom status` | Menampilkan identitas sistem, timestamp UTC, status komponen, dan kebijakan freshness |
| `axiom sources` | Menampilkan daftar provider data internet, kebutuhan API key, SLA, dan lisensi |
| `axiom research "NVIDIA" --type company` | Riset fundamental institusional: valuasi (P/E, EV/EBITDA), marjin, neraca, dan grafik tren |
| `axiom market AAPL --asset equity` | Analisis pasar saham: volatilitas terealisasi, RSI, MACD, MA 50/200, dan grafik 1600px |
| `axiom market BTC-USD --asset crypto` | Analisis pasar aset kripto terkini dengan metrik risiko 1-Day VaR & CVaR |
| `axiom macro --region US` | Intelijen makroekonomi: kurva imbal hasil US Treasury, DXY, minyak mentah, dan emas |
| `axiom news "Federal Reserve interest rates"` | Mengambil berita primer dari media finansial terakreditasi via RSS feed verified |
| `axiom quant analyze AAPL --period 5y` | Analisis statistik: CAGR, Sharpe ratio, Sortino, skewness, kurtosis, dan drawdown |
| `axiom quant backtest --strategy momentum --symbol SPY --period 10y` | Simulasi backtest deterministik bebas look-ahead bias (eksekusi open $t+1$) |
| `axiom portfolio analyze portfolio.csv` | Evaluasi alokasi bobot portofolio, konsentrasi HHI, dan matriks korelasi multi-aset |
| `axiom report latest` | Menampilkan ringkasan eksekutif dan metrik dari laporan terbaru di terminal |
| `axiom tui --mock` | Membuka antarmuka visual Textual TUI interaktif |

---

## 3. Format & Struktur Paket Laporan Bertanggal

Setiap kali analisis dijalankan, AXIOM menghasilkan satu folder arsip mandiri di `reports/`:

```text
reports/YYYY-MM-DD_HHMMSS_task-name/
  ├── report.md          # Laporan Markdown lengkap dengan tabel dan pemisahan fakta vs interpretasi
  ├── report.html        # Dashboard HTML institusional berdesain dark-theme responsif
  ├── summary.json       # Metadata terstruktur, metrik kunci, dan status verdict
  ├── sources.csv        # Rekaman audit sumber: URL, publisher, tanggal observasi, retrieval UTC
  ├── assumptions.md     # Deklarasi asumsi eksplisit, batasan data, dan titik ketidakpastian
  └── charts/            # Berkas grafik resolusi tinggi (PNG lebar 1600px, 150 DPI)
```

### Standar Pembagian Epistemik Laporan:
- **Facts**: Angka atau kutipan yang didukung langsung oleh data numerik terverifikasi.
- **Interpretations**: Analisis dan implikasi yang diturunkan secara logis dari fakta.
- **Assumptions**: Parameter input atau kondisi awal yang diasumsikan.
- **Uncertainties**: Faktor risiko atau kondisi pasar yang dapat membatalkan tesis.
- **Confidence Level**: Dinyatakan kualitatif (`Tinggi`, `Sedang-Tinggi`, `Rendah`) disertai alasan argumennya.

---

## 4. Alur Multi-Agent Workflow

Sistem mengoordinasikan 8 agen spesialis:
1. **Orchestrator Agent**: Membedah pertanyaan riset, menyusun rencana langkah, dan memimpin eksekusi.
2. **Market Data Agent**: Menarik harga, volume, corporate action, dan memvalidasi kebersihan data.
3. **Financial Research Agent**: Menganalisis laporan keuangan 10-K/10-Q, valuasi, marjin, dan FCF.
4. **Macro Agent**: Memetakan dinamika kurva imbal hasil (10Y-2Y), suku bunga bank sentral, DXY, dan komoditas.
5. **Quant Agent**: Menghitung metrik kuantitatif (CAGR, Sharpe, Sortino, Calmar) dan mengeksekusi backtest.
6. **Risk Agent**: Mengestimasi 1-Day & 10-Day VaR (95%, 99%), Expected Shortfall (CVaR), dan skenario shock makro.
7. **Skeptic / Verification Agent**: Mengaudit integritas data, mendeteksi potensi look-ahead bias, dan memverifikasi sumber.
8. **Reporting Agent**: Mengemas laporan riset menjadi bundel Markdown, HTML, CSV sumber, dan visualisasi grafik.

---

## 5. Sumber Data & Atribusi

| Data Provider | Kebutuhan API Key | Status Kesegaran Data | Penggunaan & Kepatuhan |
| :--- | :--- | :--- | :--- |
| **Yahoo Finance** | **Gratis (Tanpa Key)** | `DELAYED` (15m) / `EOD` | Sumber komunitas tidak resmi untuk harga historis & rasio keuangan. |
| **Verified News RSS** | **Gratis (Tanpa Key)** | `PUBLICATION TIMESTAMP` | Berita primer terakreditasi (AP, Reuters, NYT, CNBC, Yahoo). |
| **Exchange Public APIs**| **Gratis (Tanpa Key)** | `DELAYED` / `EOD` | Endpoint publik bursa untuk aset kripto & volume. |
| **FRED St. Louis Fed**| **Opsional (Gratis)** | `END-OF-DAY` | Data deret waktu ekonomi resmi AS (T-bill, Fed Funds, CPI). |
| **SEC EDGAR / XBRL**  | **Gratis (User-Agent)**| `PUBLICATION DATE` | Filing laporan berkala korporasi publik AS. |

> **Aturan Kebijakan**: Data dari sumber komunitas tidak pernah diklaim sebagai feed real-time bursa resmi. Jika terjadi kegagalan jaringan, sistem melaporkan sumber yang bermasalah secara transparan tanpa mengarang angka palsu.

---

## 6. Verifikasi Pengujian Terotomasi (17 Tests)

Semua komponen inti diuji menggunakan `pytest`:
```bash
source .venv/bin/activate
pytest tests/ -v
```

Hasil verifikasi:
- `tests/test_backtest_timing.py`: Membuktikan bahwa eksekusi sinyal pada $t+1$ mencegah look-ahead bias secara deterministik.
- `tests/test_analysis.py`: Memverifikasi kalkulasi teknikal (RSI, MACD, MA), fundamental, kuantitatif (Sharpe, Sortino), dan risiko (VaR, CVaR).
- `tests/test_cli.py`: Memverifikasi eksekusi perintah Typer (`status`, `sources`, `report latest`).
- `tests/test_tui.py`: Memverifikasi 8 skenario interaksi pengguna pada antarmuka Textual TUI (Textual Pilot headless).

---

## 7. Pernyataan Kepatuhan Institusional

AXIOM AI AGENTS dibangun murni sebagai perangkat riset kuantitatif, analisis risiko, dan edukasi finansial. Sistem **TIDAK** melakukan live trading, tidak mengirim order ke broker, tidak mengelola atau memindahkan dana, dan tidak menjanjikan keuntungan finansial. Seluruh keputusan alokasi modal dan risiko investasi sepenuhnya berada di tangan pengguna.
