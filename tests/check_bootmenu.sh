#!/usr/bin/env bash
# check_bootmenu.sh - Validasi konfigurasi menu boot sebelum ISO dibangun.
#
# Menangkap kelas bug yang membuat menu syslinux/GRUB mengulang countdown
# terus-menerus: DEFAULT menunjuk label/entry yang tidak ada, INCLUDE hilang,
# atau berkas konfigurasi berakhiran CRLF (syslinux gagal membacanya).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
status=0

err() {
    printf '::error::%s\n' "$*"
    status=1
}

# Kumpulkan seluruh LABEL, termasuk dari berkas yang di-INCLUDE.
syslinux_labels() {
    local file="$1" seen="$2" inc
    [[ -f "${file}" ]] || return 0
    case " ${seen} " in
        *" ${file} "*) return 0 ;;
    esac
    seen="${seen} ${file}"
    awk 'toupper($1) == "LABEL" { print $2 }' "${file}"
    while IFS= read -r inc; do
        [[ -n "${inc}" ]] || continue
        syslinux_labels "$(dirname "${file}")/${inc}" "${seen}"
    done < <(awk 'toupper($1) == "INCLUDE" { print $2 }' "${file}")
}

check_syslinux() {
    local cfg="$1" labels default
    labels="$(syslinux_labels "${cfg}" "" | tr '\n' ' ')"
    while IFS= read -r default; do
        [[ -n "${default}" ]] || continue
        if [[ " ${labels} " != *" ${default} "* ]]; then
            err "${cfg#"${ROOT}/"}: DEFAULT '${default}' tidak punya LABEL yang cocok"
        fi
    done < <(awk 'toupper($1) == "DEFAULT" { gsub(/\r/, "", $2); print $2 }' "${cfg}")
}

check_grub() {
    local cfg="$1" default
    default="$(awk -F'=' '/^[[:space:]]*default=/ { gsub(/\r/, "", $2); gsub(/[[:space:]]/, "", $2); print $2; exit }' "${cfg}")"
    if [[ -z "${default}" ]]; then
        err "${cfg#"${ROOT}/"}: tidak ada direktif 'default='"
        return
    fi
    if [[ ! "${default}" =~ ^[0-9]+$ ]] &&
        ! grep -qF -- "--id '${default}'" "${cfg}"; then
        err "${cfg#"${ROOT}/"}: default='${default}' tidak punya menuentry --id yang cocok"
    fi
}

check_systemd_boot() {
    local dir="${ROOT}/profile/efiboot/loader" default
    default="$(awk 'tolower($1) == "default" { print $2; exit }' "${dir}/loader.conf")"
    if [[ -z "${default}" ]]; then
        err "profile/efiboot/loader/loader.conf: tidak ada entri 'default'"
    elif [[ ! -f "${dir}/entries/${default}" ]]; then
        err "profile/efiboot/loader/loader.conf: default '${default}' tidak ada di entries/"
    fi
}

check_crlf() {
    local file
    while IFS= read -r -d '' file; do
        if grep -q $'\r' "${file}"; then
            err "${file#"${ROOT}/"}: memakai CRLF (menu boot membutuhkan LF)"
        fi
    done < <(find "${ROOT}/profile" "${ROOT}/tests" -type f \
        \( -name '*.cfg' -o -name '*.conf' -o -name '*.sh' -o -name '*.service' \) -print0)
}

check_bom() {
    local file bytes
    while IFS= read -r -d '' file; do
        bytes="$(head -c 3 "${file}" | od -An -tx1 | tr -d ' \n')"
        if [[ "${bytes}" == "efbbbf" ]]; then
            err "${file#"${ROOT}/"}: memakai BOM UTF-8 (menu boot gagal membacanya)"
        fi
    done < <(find "${ROOT}/profile" -type f \( -name '*.cfg' -o -name '*.conf' \) -print0)
}

for cfg in "${ROOT}"/profile/syslinux/*.cfg; do
    check_syslinux "${cfg}"
done

check_grub "${ROOT}/profile/grub/grub.cfg"
check_grub "${ROOT}/profile/grub/loopback.cfg"
check_systemd_boot
check_crlf
check_bom

if (( status == 0 )); then
    echo "[PASS] Konfigurasi menu boot konsisten"
fi
exit "${status}"
