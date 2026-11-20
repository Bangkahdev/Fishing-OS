# fishing-agent — Fondasi Computer-Use Assistant

Fondasi lokal Fishing OS yang mengikuti [SRS utama](../docs/SRS.md) dan
[catatan implementasi](../docs/COMPUTER_USE_ASSISTANT_IMPLEMENTATION.md). Komponen
ini berjalan sebagai user biasa dan menyediakan contract executor, policy gate,
task state, audit redaction, cancellation, serta backend input desktop.

Status saat ini:

- [x] Phase 1 — lab, task state, policy/approval, audit, cancellation
- [x] Phase 2 — command executor `argv`, `shell`, `script`, `interactive`
- [x] Backend input desktop dan dry-run
- [] Tahap 3 — pembaca AT-SPI2 + runtime model lokal (VLM)
- [] Tahap 4 — tool dokumen & presentasi (`.pptx`)
- [] Tahap 5 — interaksi UI kompleks (tabel, klik kanan, seleksi, font)
- [] Tahap 6 — evaluasi & fine-tuning opsional

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
| `notify` | `text` |

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
