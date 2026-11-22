# Computer-Use Assistant — Orchestrator, Tool Registry, dan Planner

Dokumen ini menjelaskan lapisan inti Assistant yang menerjemahkan **instruksi
bahasa alami** menjadi **tool call tervalidasi** yang dijalankan dengan aman.
Lapisan ini adalah komponen *Task Orchestrator*, *Tool Registry*, dan *LLM
Planner* pada SRS §3.2. Tujuannya agar maintainer dapat memperluas kapabilitas
tanpa mengorbankan kontrak keamanan.

## 1. Alur end-to-end

```
instruksi pengguna
   │
   ▼
Planner.plan()            -> Plan (daftar PlanStep: tool + arguments)
   │
   ▼
Orchestrator._preflight() -> validasi schema (ToolRegistry) + policy (PolicyGate)
   │                        - elevated tanpa Administrator Mode  -> waiting_for_authentication
   │                        - risiko tinggi / overwrite tanpa approval -> waiting_for_approval
   ▼
handler tool (command/file/system/productivity) -> StepOutcome
   │
   ▼
verifikasi hasil (berkas ada / exit code) -> ControlService state + audit trace
```

Prinsip kunci: **planner tidak pernah mengeksekusi**. Ia hanya menghasilkan
rencana. Registry memvalidasi argumen terhadap schema sebelum handler
dijalankan, sehingga output model mentah tidak dapat memicu aksi (FR-09/FR-10,
NFR-27).

## 2. Komponen

| Modul | Tanggung jawab |
|---|---|
| `registry.py` | `ToolSpec` (kontrak tool), `ToolRegistry` (register/get/dispatch), validator argumen subset JSON Schema, `ToolContext`, `StepOutcome`. |
| `tools.py` | Tool bawaan: `command.run`, `file.list/read/search/write/delete`, `system.inspect`, `productivity.markdown/pptx/csv`. |
| `planner.py` | `Plan`/`PlanStep`, protokol `Planner`, `HeuristicPlanner` deterministik (ID/EN), `get_planner`/`register_planner`. |
| `orchestrator.py` | `Orchestrator.run()`: perencanaan, preflight, eksekusi, verifikasi, state, audit, cancellation. |
| `cli.py` | Subcommand `assist` (plus `--planner`, `--print-plan`, `--plan`, `--approve`, `--enable-admin`, `--dry-run`). |

## 3. Tool Registry dan kontrak tool

Setiap tool adalah `ToolSpec`:

```python
from fishing_agent.registry import ToolSpec, StepOutcome, ToolContext
from fishing_agent.policy import Risk

def handler(arguments: dict, context: ToolContext) -> StepOutcome:
    # arguments sudah tervalidasi sesuai schema
    ...

spec = ToolSpec(
    name="contoh.aksi",
    description="deskripsi singkat untuk planner/UI",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "minLength": 1},
            "mode": {"type": "string", "enum": ["a", "b"], "default": "a"},
        },
        "required": ["path"],
        "additionalProperties": False,
    },
    handler=handler,
    risk=Risk.LOW,            # atau Risk.MEDIUM/HIGH, atau fungsi (arguments, ctx) -> Risk
    privilege="user",         # "user" atau "elevated"
    examples=("contoh.aksi {path: 'x'}",),
)
```

### 3.1 Validator argumen (subset JSON Schema)

`validate_arguments(schema, args)` mendukung:

- `type`: `object | array | string | integer | number | boolean`
- `properties`, `required`, `default`
- `enum`
- `items` (untuk array), `minItems`/`maxItems`, `minimum`/`maximum`, `minLength`/`maxLength`
- `additionalProperties: false` (menolak parameter tak dikenal)

Argumen yang tidak valid menaikkan `ToolValidationError` **sebelum** handler
dijalankan. `ToolRegistry.dispatch()` selalu memvalidasi lebih dulu.

### 3.2 Risiko dan privilege

- `risk` boleh berupa `Risk` tetap atau fungsi `(arguments, context) -> Risk`.
  `command.run` memakai `PolicyGate.risk()` sehingga command berbahaya
  (`mkfs`, `rm -rf`, dll.) otomatis menjadi `Risk.HIGH`.
- `privilege="elevated"` membuat orchestrator meminta Administrator Mode aktif
  sebelum eksekusi (autentikasi native OS `sudo -v`).
- Orkestrator juga memaksa approval bila tool di `_OVERWRITE_TOOLS` menimpa
  berkas yang sudah ada.

### 3.3 ToolContext (dependensi runtime)

Handler menerima `ToolContext` agar tidak membuat executor sendiri:

| Field | Isi |
|---|---|
| `policy` | `PolicyGate` (risk/approval) |
| `administrator` | `AdministratorMode` (status/ masa berlaku) |
| `stop` | `StopController` (cancellation) |
| `trace` | `TraceWriter` (audit JSONL) |
| `executor` | `CommandExecutor` |
| `file_tool` | `FileTool` |
| `system_tool` | `SystemTool` |
| `approved` | bool approval untuk task ini |
| `dry_run` | bool; bila True, orchestrator tidak mengeksekusi |
| `lab`, `working_directory`, `task_id` | konteks lab & task |

## 4. Menambah tool baru

1. Tulis handler `(arguments, context) -> StepOutcome` di modul yang sesuai
   (atau `tools.py` untuk tool bawaan).
2. Daftarkan `ToolSpec` di `register_default_tools()` (`tools.py`) atau lewat
   `registry.register(...)`.
3. Tambahkan unit test di `agent/tests/test_registry.py` (schema) dan
   `agent/tests/test_orchestrator.py` (perilaku end-to-end).
4. Bila tool perlu dipetakan dari bahasa alami, tambahkan cabang di
   `HeuristicPlanner.plan()` (`planner.py`).

Panduan: gunakan helper yang sudah ada (`CommandExecutor`, `FileTool`,
`SystemTool`, fungsi `productivity`) sebelum menambah jalur eksekusi baru.
Jangan menambah `shell=True` implisit; `argv` adalah default.

## 5. Planner

`Planner` adalah protokol dengan satu metode:

```python
def plan(self, instruction: str, context: ToolContext) -> Plan: ...
```

- `HeuristicPlanner` — deterministik, dwibahasa (ID/EN), untuk demo, offline, dan
  test. Memetakan frasa seperti "buat presentasi", "baca file /etc/hostname",
  "jalankan git status", "status paket", "daftar isi folder", dst.
- Rencana eksplisit — CLI `--plan plan.json` memakai `Plan.from_mapping()`
  (lihat `Plan`/`PlanStep`), cocok untuk pengujian dan integrasi.
- Runtime LLM nyata — daftarkan implementasi baru tanpa mengubah CLI:

```python
from fishing_agent.planner import register_planner

class MyLLMPlanner:
    name = "llm"
    def plan(self, instruction, context):
        # panggil model lokal, hasilkan Plan dari tool schema registry
        return Plan(steps=[...], summary="...", planner=self.name)

register_planner("llm", lambda: MyLLMPlanner())
# lalu: fishing-assistant assist "..." --planner llm
```

Format `Plan` (JSON) yang dapat dipakai via `--plan`:

```json
{
  "summary": "contoh",
  "steps": [
    {"tool": "file.write", "arguments": {"path": "a.txt", "content": "halo"}},
    {"tool": "command.run", "arguments": {"command": "echo", "args": ["selesai"]}}
  ]
}
```

## 6. State machine & audit

Orchestrator memakai `ControlService` (state tunggal) dan `TraceWriter` (audit):

```
STOPPED -> STARTING -> READY -> PLANNING -> [WAITING_FOR_AUTHENTICATION | WAITING_FOR_APPROVAL]
        -> EXECUTING -> VERIFYING -> COMPLETED | FAILED | CANCELLED
```

- Setiap langkah menulis audit (`perception`, `action`, `parameters` tersanitasi,
  `status`) — password/token diredaksi oleh `TraceWriter.redact`.
- Cancellation diperiksa sebelum tiap langkah (stop file / sinyal / Ctrl+C);
  proses anak yang dapat dihentikan dibersihkan (tidak menjanjikan rollback).

## 7. CLI `assist`

```bash
fishing-assistant assist "<instruksi>"         # jalankan (planner heuristic)
fishing-assistant assist "<instruksi>" --print-plan   # cetak rencana JSON, tanpa eksekusi
fishing-assistant assist --plan plan.json      # jalankan rencana eksplisit
fishing-assistant assist "<instruksi>" --dry-run      # validasi + preflight, tanpa eksekusi
fishing-assistant assist "<instruksi>" --approve      # setujui operasi berisiko/overwrite
fishing-assistant assist "<instruksi>" --enable-admin # aktifkan Administrator Mode (sudo -v)
```

Kode keluar: `0` sukses/ready, `1` gagal, `2` menunggu approval/autentikasi
(jalankan ulang dengan `--approve`/`--enable-admin`), `130` dibatalkan.