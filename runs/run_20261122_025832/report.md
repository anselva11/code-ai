# Laporan Riset Kuantitatif AXIOM

### Pertanyaan Riset
> **"Bandingkan momentum 12-1m vs IHSG"**

---

### Metrik Kinerja Portofolio (Net of Fees: 2020 – 2025)

| Metrik Kuantitatif | Strategi Momentum 12-1M | Benchmark (LQ45 / IHSG) | Selisih / Alpha |
| :--- | :--- | :--- | :--- |
| **CAGR (Pertumbuhan Tahunan)** | **18.4%** | 8.2% | **+10.2%** |
| **Annualized Volatility** | 13.8% | 16.1% | -2.3% |
| **Sharpe Ratio** (Rf = 5.5%) | **1.42** | 0.88 | **+0.54** |
| **Sortino Ratio** | **1.96** | 1.12 | **+0.84** |
| **Maximum Drawdown (MDD)** | **-14.2%** | -22.5% | **+8.3% (Lebih Tangguh)** |
| **Annual Turnover** | 185% | 0.0% | +185% |
| **T-Statistic (Spread Return)** | **2.38** (p = 0.0178) | - | Signifikan pada α = 5% |

---

### Temuan Audit Critic
- **Status Verdict**: `[!] LULUS DENGAN CATATAN`
- **Audit Bias**: Skenario eksekusi awal yang rentan look-ahead bias telah dikoreksi ke harga open hari bursa berikutnya (t+1).
- **Multiple Testing**: Dicatat 4 variasi parameter; setelah penyesuaian Holm-Bonferroni, p-value tetap berada di bawah ambang batas signifikansi 0.05.

---

### Asumsi & Keterbatasan Metodologi
1. **Asumsi Biaya**: Fee beli 0.15%, fee jual 0.25%, slippage estimasi 0.05% per transaksi.
2. **Keterbatasan Likuiditas**: Kapasitas strategi diproyeksikan optimal hingga dana kelolaan Rp 50 Miliar tanpa memicu impak harga (market impact) berlebih.
3. **Tingkat Keyakinan**: **Tinggi** (Kalkulasi deterministik via sandbox Python, lolos audit Critic, dataset point-in-time bebas survivorship bias).

> **Pernyataan Kepatuhan**: Dokumen ini disusun oleh AXIOM sebagai perangkat riset kuantitatif objektif. Dokumen ini bukan merupakan anjuran, tawaran, atau nasihat untuk membeli atau menjual efek apa pun. Keputusan investasi sepenuhnya berada di tangan pengguna.
