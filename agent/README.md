# fishing-agent — Fondasi Computer-Use Assistant

Fondasi lokal Fishing OS yang mengikuti [SRS utama](../docs/SRS.md),
[SRS Assistant v1.1](../docs/SRS-agent-v1.1.md), dan
[catatan implementasi](../docs/COMPUTER_USE_ASSISTANT_IMPLEMENTATION.md). Komponen
ini berjalan sebagai user biasa dan menyediakan contract executor, policy gate,
task state, audit redaction, cancellation, backend input desktop, serta
perception AT-SPI2 dan screenshot.

Status saat ini:

- [x] Phase 1 — lab, task state, policy/approval, audit, cancellation
- [x] Phase 2 — command executor `argv`, `shell`, `script`, `interactive`
- [x] Backend input desktop dan dry-run
- [x] Perception — penelusuran dan aksi AT-SPI2 via pyatspi, tangkapan layar grim/import, verifikasi state
- [x] Model manager — manifest, checksum, signature GPG, load/unload, status OOM
- [x] GUI/TUI — adapter Tkinter dan TUI stdin/stdout di atas ControlService
- [x] IPC persistent — Unix-domain socket untuk task lintas-interface
- [] Runtime model lokal (VLM) dan benchmark hardware
- [] Tool dokumen & presentasi (`.pptx`)
- [] Interaksi UI kompleks (tabel, klik kanan, seleksi, font)
- [] Evaluasi & fine-tuning opsional

## Kebutuhan

- Python 3.11+ (stdlib saja; tanpa dependensi pihak ketiga).
- Backend input opsional: `xdotool` (X11/XFCE) atau `ydotool` + `wtype`
  (Wayland/Hyprland). Tanpa itu gunakan `--dry-run`.

## Mulai

```bash
export FISHING_AI_LAB=/run/media/$USER/LAB/fishing_ai_lab
cd agent

python -m fishing_agent init
python -m fishing_agent search '*.md'
python -m fishing_agent run --script contoh.json --dry-run
python -m fishing_agent stop      # atau: pkill -f fishing_agent
python -m fishing_agent command --lab "$FISHING_AI_LAB" python -- -c "print(123)"
python -m fishing_agent file list /
python -m fishing_agent file read /etc/hostname
python -m fishing_agent system network status
python -m fishing_agent system packages list
python -m fishing_agent productivity markdown laporan.md --title Laporan --content "Hasil"
python -m fishing_agent productivity pptx presentasi.pptx --slides '[{"title":"Demo","body":"Fishing OS"}]'
python -m fishing_agent model list --manifest models.json
python -m fishing_agent model verify qwen2.5-vl-3b --manifest models.json --signature models.json.sig
python -m fishing_agent model load qwen2.5-vl-3b --manifest models.json
python -m fishing_agent tui
python -m fishing_agent gui
python -m fishing_agent ipc-server /tmp/fishing-assistant.sock
```

Semua perintah menerima `--lab <path>` sebagai pengganti variabel lingkungan.

## Skrip aksi

`contoh.json` — daftar aksi atomik; `params` boleh ditulis sebaris:

```json
[
  { "kind": "move", "x": 640, "y": 360 },
  { "kind": "click" },
  { "kind": "key", "keys": "ctrl+s" },
  { "kind": "type", "text": "Ringkasan materi" },
  { "kind": "wait", "seconds": 0.5 }
]
```

| `kind` | Parameter |
|---|---|
| `move` | `x`, `y` |
| `click` / `rightclick` | `button` (opsional, `left`/`right`) |
| `type` | `text` |
| `key` | `keys` (mis. `ctrl+shift+t`) |
| `wait` | `seconds` |
| `sh` | `argv` (daftar string, tanpa shell) |
| `ui_action` | `role`/`name`, `action` (opsional), `app_id` (opsional), `expected_change` (opsional), `verify` (default `true`) |
| `notify` | `text` |

`ui_action` memakai AT-SPI2 lebih dulu; bila elemen tidak ditemukan, aksi berhenti
dengan error. Verifikasi sebelum/sesudah aksi wajib lulus kecuali
`"verify": false` diberikan secara eksplisit; sumber grounding dicatat pada
`perception` trace.

`command` memakai mode `argv` secara default sehingga argumen tidak diparse
shell. Gunakan mode `shell` atau `script` hanya bila memang diperlukan.
`--privilege elevated` memerlukan `--enable-admin`, yang memanggil `sudo -v`
melalui terminal native; password tidak pernah menjadi input model atau trace.

## File tools

Subcommand `file` mendukung `list`, `metadata`, `search`, `read`, `write`,
`copy`, `move`, dan `delete` pada filesystem lokal sesuai izin OS. Overwrite dan
delete harus memakai `--approved`. File tool tidak mengikuti symlink untuk
operasi baca/mutasi, membatasi ukuran input/output, dan melaporkan error secara
eksplisit.

## Model manager

Manifest model wajib memuat `id`, `version`, dan `checksum` (SHA-256 default).
`model verify` membandingkan checksum berkas di `models/`; bila `--signature`
diberikan, detached signature GPG manifest diverifikasi lebih dulu dan
fingerprint penanda tangan dicetak. `model load` menolak checksum yang salah,
berkas yang hilang, atau status OOM, lalu melaporkan status
`loaded`/`unloaded`/`missing`/`failed`.

## Penghentian

Loop memeriksa tiga jalur pada setiap langkah: `Ctrl+C`, `SIGTERM`/`pkill`, dan
berkas `logs/stop`. Perintah `stop` menulis berkas tersebut; hentikan dengan
`rm` atau `python -m fishing_agent` setelah `clear()`.

## Trace

Setiap sesi menulis `logs/session-<UTC>.jsonl`, satu objek per langkah:

```json
{"action":"move","note":"","parameters":{"x":640,"y":360},"perception":"sesi desktop aktif","status":"ok","step_id":1,"timestamp":"2026-11-21T09:00:00.000Z"}
```

## Batas keamanan

- `search` hanya membaca di `workspace/`; path di luar akar ditolak.
- Aksi `sh` menerima `argv` (tanpa `shell=True`), dan tercatat di trace.
- `--dry-run` tidak menyentuh keyboard/mouse nyata.
- Output command dibatasi dan environment diwariskan secara terbatas.

## System management

Subcommand `system` memakai executor dan policy yang sama untuk `packages`,
`services`, `processes`, `network`, `storage`, dan `hardware`. Contoh operasi
mutasi seperti `packages install` atau `services restart` memerlukan
`--enable-admin`; operasi berisiko tinggi tetap membutuhkan `--approve`.

## Productivity

Subcommand `productivity` membuat Markdown, CSV, dan `.pptx` OOXML minimal secara
lokal. Output presentasi divalidasi sebagai arsip ZIP dan seluruh XML-nya
diparse sebelum perintah dianggap berhasil. Overwrite memerlukan `--approved`.

## Tes

```bash
cd agent
python -m unittest discover -s tests -v
```

Tes juga dijalankan pada job `whitebox` di `.github/workflows/test.yml`.
Build ISO mengekstrak `airootfs.sfs` dan menjalankan `audit-iso` pada
filesystem hasil ekstraksi sebelum artefak Live ISO diunggah.
