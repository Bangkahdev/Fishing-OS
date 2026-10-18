#!/usr/bin/env bash
# user_scenario.sh - Skrip yang dijalankan di dalam VM (via kernel param script=)
# untuk mensimulasi penggunaan nyata Fishing OS DevOps oleh seorang pengguna.
#
# Scenario:
# 1. Login sebagai liveuser (autologin)
# 2. Cek alat DevOps yang tersedia (devops-check)
# 3. Cek versi Docker, kubectl, terraform, ansible
# 4. Simulasi menulis file kode sederhana
# 5. Simulasi inisialisasi proyek DevOps kecil
# 6. Selesai dan shutdown

set -euo pipefail

LOG="/tmp/user_scenario.log"

{
    echo "========================================"
    echo "  Fishing OS DevOps - User Scenario"
    echo "  Simulasi pengguna nyata"
    echo "  Waktu: $(date)"
    echo "========================================"
    echo

    # 1. Informasi sistem
    echo "[1/6] Informasi sistem..."
    hostnamectl || true
    cat /etc/os-release || true
    echo

    # 2. Cek alat DevOps
    echo "[2/6] Menjalankan devops-check..."
    devops-check || true
    echo

    # 3. Cek versi alat kunci
    echo "[3/6] Versi alat kunci DevOps..."
    for cmd in docker kubectl terraform ansible python3 node go git; do
        if command -v "$cmd" >/dev/null 2>&1; then
            printf "  %-12s %s\n" "$cmd" "$("$cmd" --version 2>/dev/null | head -n1 || "$cmd" version 2>/dev/null | head -n1)"
        else
            printf "  %-12s (tidak terpasang)\n" "$cmd"
        fi
    done
    echo

    # 4. Simulasi menulis file kode (contoh Dockerfile sederhana)
    echo "[4/6] Simulasi membuat file proyek DevOps..."
    mkdir -p /home/liveuser/demo-devops
    cat > /home/liveuser/demo-devops/Dockerfile <<'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
EOF

    cat > /home/liveuser/demo-devops/requirements.txt <<'EOF'
flask
requests
EOF

    cat > /home/liveuser/demo-devops/app.py <<'EOF'
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Fishing OS DevOps!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
EOF

    mkdir -p /home/liveuser/demo-devops/.github/workflows
    cat > /home/liveuser/demo-devops/.github/workflows/ci.yml <<'EOF'
name: CI

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t myapp .
EOF

    ls -la /home/liveuser/demo-devops/ || true
    echo

    # 5. Simulasi inisialisasi git
    echo "[5/6] Simulasi inisialisasi proyek..."
    cd /home/liveuser/demo-devops || true
    git init 2>/dev/null || true
    git add . 2>/dev/null || true
    echo "File siap untuk di-commit dan di-deploy."
    echo

    # 6. Selesai
    echo "[6/6] Selesai. Simulasi pengguna selesai."
    echo "========================================"
    echo "  Akhir scenario"
    echo "========================================"

} | tee "$LOG"

# Tunggu sebentar agar output terselesaikan sebelum shutdown
sleep 3
sudo poweroff -f 2>/dev/null || sudo halt -f 2>/dev/null || poweroff -f 2>/dev/null || halt -f 2>/dev/null || true
