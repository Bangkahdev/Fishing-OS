# Fishing OS Computer-Use Assistant — Catatan Implementasi

Dokumen ini melengkapi [SRS.md](./SRS.md) dan
[SRS-agent-v1.1.md](./SRS-agent-v1.1.md). SRS menetapkan perilaku produk;
dokumen ini mencatat apa yang sudah diimplementasikan, lokasi kode, cara
verifikasi, dan pekerjaan yang masih tersisa. Perbarui dokumen ini setiap kali
status fase atau kontrak publik berubah.

## Status ringkas

Tanggal pemeriksaan terakhir: 22 November 2026.

| Fase SRS | Status | Bukti |
|---|---|---|
| Phase 0 — integrasi OS | Sebagian | Struktur `agent/`, artefak paket `packaging/assistant/` (launcher, desktop, user service, `PKGBUILD`, `install.sh`), guard Live ISO, dan CI test sudah ada; opsi installer archinstall belum terintegrasi. |
| Phase 1 — control plane | Fondasi selesai | `service.py`, `task.py`, `policy.py`, `trace.py`, cancellation, IPC local, **orchestrator + tool registry + planner** (`orchestrator.py`, `registry.py`, `tools.py`, `planner.py`), dan unit test. |
| Phase 2 — command/system capability | Fondasi selesai | `command.py`, `files.py`, `system.py`, privilege gate, audit redaction, dan tool bawaan registry. |
| Phase 3 — productivity | Fondasi selesai | `productivity.py` untuk Markdown, CSV, dan PPTX OOXML minimal. |
| Phase 4 — desktop automation | Fondasi sebagian | Backend X11/Wayland, aksi atomik, penelusuran dan aksi AT-SPI2 via pyatspi, screenshot grim/import, verifikasi pasca-aksi, aksi skrip `ui_action`, dan **grounding fallback visual** (`perception.py`, describer pluggable); uji pada sesi Hyprland Fishing OS belum. |
| Phase 5 — hybrid AI | Fondasi selesai | `model_manager.py`: manifest, checksum SHA-256, verifikasi detached signature GPG, load/unload, status OOM/missing; **planner deterministik** sebagai fallback offline; runtime inferensi LLM/VLM dan pilihan model belum dikunci. |
| Phase 6 — GUI/TUI | Fondasi selesai | CLI (termasuk `assist`), TUI stdio, GUI Tkinter adapter, dan Unix IPC control plane tersedia; integrasi launcher desktop GUI/TUI masih perlu dirilis. |
| Phase 7 — release hardening | Sebagian | Paket/model signing, artefak paket `packaging/assistant/`, dan audit/guard Live ISO tersedia; opsi installer archinstall dan release matrix masih perlu integrasi. |

## Alur orchestrator (baru)

Komponen inti SRS §3.2 kini terlaksana dan dapat dijalankan lewat `fishing-assistant assist`:

```
instruksi -> Planner (rencana) -> ToolRegistry (validasi argumen)
          -> PolicyGate (privilege/approval) -> handler (command/file/system/productivity)
          -> verifikasi hasil -> ControlService (state + audit)
```

Lihat `docs/ORCHESTRATOR.md` untuk kontrak tool, cara menambah tool, dan perencana. Contoh:

```bash
fishing-assistant assist "buat presentasi tentang Fishing OS"
fishing-assistant assist "baca file /etc/hostname"
fishing-assistant assist "jalankan git status"
fishing-assistant assist "status paket" --print-plan     # lihat rencana (JSON)
fishing-assistant assist "hapus file data.tmp" --approve # operasi berisiko tinggi
fishing-assistant assist --plan plan.json                # jalankan rencana eksplisit
```

## Struktur modul

| Modul | Tanggung jawab |
|---|---|
| `config.py` | Menentukan lab lokal dan subdirektori `models`, `runtime`, `workspace`, `logs`. |
| `command.py` | Kontrak command `argv`, `shell`, `script`, `interactive`; timeout, output limit, environment, privilege, cancellation. |
| `policy.py` | Risk classification, approval, dan Administrator Mode tanpa menyimpan password. |
| `task.py` | State machine task yang dipakai control plane. |
| `service.py` | Registry task, transisi state, approval, cancellation, dan event audit bersama interface. |
| `registry.py` | **Tool registry**: `ToolSpec`, validasi argumen subset JSON Schema, `ToolContext`, `StepOutcome`, dispatch handler. |
| `tools.py` | **Tool bawaan** yang membungkus command/file/system/productivity dengan risiko dari `PolicyGate`. |
| `planner.py` | **Perencana**: `Plan`/`PlanStep`, protokol `Planner`, `HeuristicPlanner` deterministik (ID/EN), `get_planner`. |
| `orchestrator.py` | **Orchestrator**: instruksi -> rencana -> validasi -> policy -> eksekusi -> verifikasi, dengan state/audit/cancellation. |
| `perception.py` | **UI grounding**: AT-SPI2 dahulu, fallback visual (VLM/Set-of-Mark) via describer pluggable. |
| `ipc.py` | JSON-line Unix-domain socket client/server untuk mengakses `ControlService` secara lokal. |
| `trace.py` | JSONL audit lokal dan redaksi field credential. |
| `files.py` | File operation system-wide, batas ukuran, canonical path lexical, dan perlindungan symlink. |
| `system.py` | Adapter package, service, process, network, storage, dan hardware melalui command contract. |
| `productivity.py` | Markdown, CSV, dan minimal valid OOXML PPTX secara lokal. |
| `executor.py` | Aksi pointer/keyboard, `ui_action` via AT-SPI2, verifikasi pasca-aksi, dan backend dry-run, X11, serta Wayland. |
| `atspi.py` | Reader AT-SPI2 via pyatspi: frame aktif, penelusuran pohon, filter role/name, elemen pada koordinat, dan `perform_action` dengan verifikasi state. |
| `screenshot.py` | Tangkapan layar grim (Wayland/Hyprland) atau import (X11) dengan status tidak tersedia. |
| `verification.py` | Verifikasi state sebelum/sesudah aksi, termasuk perubahan yang diharapkan. |
| `model_manager.py` | Manifest model, verifikasi checksum dan signature GPG, load/unload, dan status OOM/missing. |
| `package_audit.py` | Audit filesystem hasil ekstraksi Live ISO untuk paket, launcher, service, dan model Assistant terlarang. |
| `stop.py` | Cancellation melalui event, signal, atau stop file. |
| `cli.py` | Interface CLI untuk seluruh kapabilitas fondasi. |
| `tui.py` | Adapter TUI stdin/stdout untuk task, approval, status, dan cancellation. |
| `gui_adapter.py` | Adapter Tkinter tipis; memakai `ControlService` dan tidak memiliki executor/policy sendiri. |

## Kontrak penggunaan

Jalankan dari direktori `agent`:

```bash
python -m unittest discover -s tests -v
python -m fishing_agent init --lab C:\temp\fishing-lab
python -m fishing_agent assist "buat presentasi tentang Fishing OS" --lab C:\temp\fishing-lab
python -m fishing_agent assist "baca file /etc/hostname" --lab C:\temp\fishing-lab
python -m fishing_agent assist "status paket" --lab C:\temp\fishing-lab --print-plan
python -m fishing_agent assist --lab C:\temp\fishing-lab --plan plan.json
python -m fishing_agent command --lab C:\temp\fishing-lab python -- -c "print(123)"
python -m fishing_agent file metadata C:\Windows\System32\notepad.exe
python -m fishing_agent system network status --lab C:\temp\fishing-lab
python -m fishing_agent productivity pptx demo.pptx --slides "[{\"title\":\"Demo\",\"body\":\"Fishing OS\"}]"
python -m fishing_agent model list --lab C:\temp\fishing-lab --manifest models.json
python -m fishing_agent model verify qwen2.5-vl-3b --lab C:\temp\fishing-lab --manifest models.json --signature models.json.sig
python -m fishing_agent model load qwen2.5-vl-3b --lab C:\temp\fishing-lab --manifest models.json
python -m fishing_agent tui
python -m fishing_agent gui
python -m fishing_agent ipc-server C:\temp\fishing-assistant.sock
```

UI grounding AT-SPI2 memakai `ATSPiReader.perform_action` untuk menjalankan
Action pada elemen dan langsung membandingkan state sebelum/sesudah:

```python
from fishing_agent.atspi import ATSPiReader

reader = ATSPiReader()
if reader.available:
    result = reader.perform_action(role="push button", name="Simpan", expected_change=("state",))
    if not result["verified"]:
        # target hilang atau state tidak sesuai; jangan lanjut tanpa verifikasi visual
        print(result["note"])
```

Aksi skrip `{"kind": "ui_action", "params": {...}}` memakai jalur yang sama.
Verifikasi wajib lulus agar langkah berikutnya berjalan, kecuali
`"verify": false` diberikan secara eksplisit; sumber grounding ditulis ke
`perception` pada trace.

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
8. **Planner hanya menghasilkan rencana**; `ToolRegistry` memvalidasi argumen
   terhadap schema sebelum handler dijalankan. Tidak ada eksekusi langsung dari
   output model (lihat `docs/ORCHESTRATOR.md`).
9. Operasi berisiko tinggi (mis. `mkfs`, `rm -rf`, `file.delete`) dan penulisan
   yang menimpa berkas yang sudah ada memerlukan approval eksplisit sebelum
   dijalankan; operasi elevated memerlukan Administrator Mode aktif.

## Verifikasi

Test suite saat ini berisi 179 test yang mencakup command contract, policy, task
state, service, filesystem, system adapter, productivity output, action
executor, trace, configuration, stop behavior, AT-SPI2, screenshot, verifikasi
pasca-aksi, model manager termasuk signature GPG, tool registry + schema
validation, planner, orchestrator, perception/grounding, serta **guard paket &
Live ISO**. Setiap perubahan modul harus menambahkan test fokus di
`agent/tests/` dan menjalankan:

```bash
cd agent
python -m unittest discover -s tests -v
```

CI menjalankan suite ini melalui job `whitebox` di
`.github/workflows/test.yml`. Build ISO mengekstrak
`arch/x86_64/airootfs.sfs`, menjalankan `audit-iso` pada filesystem root,
dan menghentikan rilis bila komponen Assistant ditemukan. Guard
`agent/tests/test_packaging_guard.py` juga memeriksa artefak
`packaging/assistant/` valid dan tidak bocor ke `profile/airootfs`.

## Pekerjaan berikutnya

1. Hubungkan GUI/TUI ke `ControlService` via IPC lokal (bukan membuat
   ControlService lokal sendiri), agar satu task terlihat lintas-interface
   (FR-23).
2. Selesaikan opsi installer archinstall untuk memilih Assistant sebagai
   optional feature, repository signing, dan pemasangan model (Phase 0/7).
3. Tambahkan integration/black-box test pada Fishing OS Linux; test Windows
   lokal hanya memverifikasi kontrak dan artefak yang portable.
4. Uji AT-SPI2 dan input Wayland pada sesi Hyprland Fishing OS nyata; pasang
   `VisualDescriber` nyata (VLM/Set-of-Mark) untuk `perception.py` (saat ini
   describer default "unavailable").
5. Runtime inferensi LLM/VLM: pilih model, kuantisasi, offload, dan benchmark
   RAM/VRAM pada hardware referensi; sambungkan via `register_planner()`.

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
