# Fishing OS Computer-Use Assistant — Catatan Implementasi

Dokumen ini melengkapi [SRS.md](./SRS.md) dan
[SRS-agent-v1.1.md](./SRS-agent-v1.1.md). SRS menetapkan perilaku produk;
dokumen ini mencatat apa yang sudah diimplementasikan, lokasi kode, cara
verifikasi, dan pekerjaan yang masih tersisa. Perbarui dokumen ini setiap kali
status fase atau kontrak publik berubah.

## Status ringkas

Tanggal pemeriksaan terakhir: 21 November 2026.

| Fase SRS | Status | Bukti |
|---|---|---|
| Phase 0 — integrasi OS | Sebagian | Struktur `agent/` dan CI test sudah ada; paket resmi dan installer optional belum terintegrasi. |
| Phase 1 — control plane | Fondasi selesai | `service.py`, `task.py`, `policy.py`, `trace.py`, cancellation, IPC local, dan 56 unit test. |
| Phase 2 — command/system capability | Fondasi selesai | `command.py`, `files.py`, `system.py`, privilege gate, dan audit redaction. |
| Phase 3 — productivity | Fondasi selesai | `productivity.py` untuk Markdown, CSV, dan PPTX OOXML minimal. |
| Phase 4 — desktop automation | Fondasi sebagian | Backend X11/Wayland dan aksi atomik tersedia; AT-SPI2, screenshot, dan verifikasi visual belum tersedia. |
| Phase 5 — hybrid AI | Belum | LLM/VLM runtime dan model manager belum diintegrasikan. |
| Phase 6 — GUI/TUI | Belum | CLI tersedia; GUI/TUI dan IPC lintas-proses belum tersedia. |
| Phase 7 — release hardening | Belum | Paket Fishing OS, installer option, signature/model manifest, dan audit Live ISO belum terintegrasi. |

## Struktur modul

| Modul | Tanggung jawab |
|---|---|
| `config.py` | Menentukan lab lokal dan subdirektori `models`, `runtime`, `workspace`, `logs`. |
| `command.py` | Kontrak command `argv`, `shell`, `script`, `interactive`; timeout, output limit, environment, privilege, cancellation. |
| `policy.py` | Risk classification, approval, dan Administrator Mode tanpa menyimpan password. |
| `task.py` | State machine task yang dipakai control plane. |
| `service.py` | Registry task, transisi state, approval, cancellation, dan event audit bersama interface. |
| `ipc.py` | JSON-line Unix-domain socket client/server untuk mengakses `ControlService` secara lokal. |
| `trace.py` | JSONL audit lokal dan redaksi field credential. |
| `files.py` | File operation system-wide, batas ukuran, canonical path lexical, dan perlindungan symlink. |
| `system.py` | Adapter package, service, process, network, storage, dan hardware melalui command contract. |
| `productivity.py` | Markdown, CSV, dan minimal valid OOXML PPTX secara lokal. |
| `executor.py` | Aksi pointer/keyboard dan backend dry-run, X11, serta Wayland. |
| `stop.py` | Cancellation melalui event, signal, atau stop file. |
| `cli.py` | Interface CLI untuk seluruh kapabilitas fondasi. |

## Kontrak penggunaan

Jalankan dari direktori `agent`:

```bash
python -m unittest discover -s tests -v
python -m fishing_agent init --lab C:\temp\fishing-lab
python -m fishing_agent command --lab C:\temp\fishing-lab python -- -c "print(123)"
python -m fishing_agent file metadata C:\Windows\System32\notepad.exe
python -m fishing_agent system network status --lab C:\temp\fishing-lab
python -m fishing_agent productivity pptx demo.pptx --slides "[{\"title\":\"Demo\",\"body\":\"Fishing OS\"}]"
```

IPC Unix-domain socket tersedia melalui `ControlIPCServer` dan
`ControlIPCClient`. Endpoint hanya dibuat pada path lokal dengan permission
user-only (`0700` untuk parent dan `0600` untuk socket); Windows melewati test
transport karena target produk adalah Fishing OS/Linux.

### Aturan keamanan yang sudah dikunci

1. Mode command default adalah `argv`; shell parsing harus diminta eksplisit.
2. Command elevated menggunakan `sudo` native dan memerlukan Administrator
   Mode; password tidak diterima oleh API model atau ditulis ke trace.
3. Operasi high-risk memerlukan approval berdasarkan `task_id`.
4. Output command dibatasi; environment diwariskan hanya dari daftar yang
   disetujui dan tambahan eksplisit.
5. File tool tidak mengikuti symlink untuk read/mutasi dan tidak menghapus
   tanpa `approved=True` atau `--approved`.
6. Cancellation menghentikan proses yang dapat dihentikan, tetapi tidak
   menjanjikan rollback.
7. Artefak productivity ditulis lokal dan PPTX divalidasi sebagai ZIP/XML.

## Verifikasi

Test suite saat ini mencakup command contract, policy, task state, service,
filesystem, system adapter, productivity output, action executor, trace,
configuration, dan stop behavior. Setiap perubahan modul harus menambahkan test
fokus di `agent/tests/` dan menjalankan:

```bash
cd agent
python -m unittest discover -s tests -v
```

CI menjalankan suite ini melalui job `whitebox` di
`.github/workflows/test.yml`.

## Pekerjaan berikutnya

1. Tambahkan adapter GUI/TUI yang memakai IPC lokal dan bukan executor sendiri.
2. Tambahkan Model Manager dengan manifest, checksum, load/unload, fallback CPU,
   dan status OOM/timeout.
3. Tambahkan AT-SPI2 serta screenshot Wayland/Hyprland dengan verifikasi target.
4. Tambahkan GUI/TUI yang hanya menjadi client control service.
5. Integrasikan package group Assistant, installer optional, repository signing,
   model manifest, dan audit bahwa Live ISO tidak membawa Assistant.
6. Tambahkan integration/black-box test pada Fishing OS Linux; test Windows
   lokal hanya memverifikasi kontrak dan artefak yang portable.

## Kebijakan perubahan

- Jangan menjalankan model, service, atau GUI sebagai root.
- Jangan menambahkan password, token, atau credential ke fixture, test output,
  trace, atau dokumentasi.
- Jangan memperluas allowlist command sebagai pengganti validasi context,
  privilege, approval, dan hasil nyata.
- Pertahankan `argv` sebagai default dan gunakan helper yang sudah ada sebelum
  menambah jalur eksekusi baru.
- Jika requirement SRS berubah, perbarui SRS dan tabel status dokumen ini dalam
  perubahan yang sama.
