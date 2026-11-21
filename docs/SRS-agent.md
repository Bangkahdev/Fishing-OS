# SRS Asisten Computer-Use (Draf Awal — Digantikan)

Dokumen ini adalah draf awal (versi 0.1) yang telah **digantikan** oleh:

- [`docs/Fishing_OS_Computer_Use_Assistant_SRS_v1.1.docx`](Fishing_OS_Computer_Use_Assistant_SRS_v1.1.docx) — SRS resmi versi 1.1 (Revisi Akses Administratif, 21 November 2026), berkas otoritatif.
- [`docs/COMPUTER_USE_ASSISTANT_IMPLEMENTATION.md`](COMPUTER_USE_ASSISTANT_IMPLEMENTATION.md) — catatan implementasi dan status fase.
- [`docs/SRS-agent-v1.1.md`](SRS-agent-v1.1.md) — rendering teks SRS v1.1 dalam Markdown untuk tinjauan di repositori.

Perbedaan pokok dengan draf ini: menurut SRS v1.1, Assistant adalah fitur **opsional pada instalasi Fishing OS ke disk**, dikemas sebagai paket resmi, **tidak disertakan pada Live ISO**, dan dikembangkan sebagai bagian dari distro (bukan lab portabel terpisah di akar repositori). Implementasi ada di paket `agent/` dengan 56 unit test yang diverifikasi melalui job `whitebox` di `.github/workflows/test.yml`.

Jangan mengacu pada draf ini untuk keputusan arsitektur atau distribusi.
