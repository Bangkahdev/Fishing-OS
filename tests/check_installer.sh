#!/usr/bin/env bash
# check_installer.sh - Tes whitebox untuk jalur "LiveOS -> terpasang".
#
# Memeriksa hal-hal yang mudah rusak tanpa terlihat:
#   * paket installer (archinstall + alat partisi/format) ada di packages.x86_64
#   * skrip fishingos-install valid, punya shebang bash, dan bisa dijalankan
#   * mode --check/--dry-run/--help berjalan tanpa root
#   * entri desktop ada di skel dan menu aplikasi, menunjuk berkas yang ada
#   * launcher + autostart hanya aktif saat boot "installer"
#   * pilihan boot (LiveOS vs installer) ada di syslinux, GRUB, systemd-boot
#   * profil memberi mode 755 pada skrip installer
#
# Tidak butuh archinstall terpasang: mode --check hanya melaporkan prasyarat.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALLER_REL="profile/airootfs/usr/local/bin/fishingos-install"
INSTALLER="${ROOT}/${INSTALLER_REL}"
LAUNCHER_REL="profile/airootfs/usr/local/bin/fishing-install-launcher"
LAUNCHER="${ROOT}/${LAUNCHER_REL}"
SKEL_DESKTOP="${ROOT}/profile/airootfs/etc/skel/Desktop/fishingos-install.desktop"
MENU_DESKTOP="${ROOT}/profile/airootfs/usr/share/applications/fishingos-install.desktop"
AUTOSTART="${ROOT}/profile/airootfs/etc/xdg/autostart/fishing-install.desktop"
SUDOERS="${ROOT}/profile/airootfs/etc/sudoers.d/99-liveuser"
PACKAGES="${ROOT}/profile/packages.x86_64"
PROFILEDEF="${ROOT}/profile/profiledef.sh"

status=0

err() {
    printf '::error::%s\n' "$*"
    status=1
}

pass_msg() {
    printf '[ok] %s\n' "$*"
}

# Paket wajib untuk memasang sistem ke disk.
REQUIRED_PACKAGES=(
    archinstall
    arch-install-scripts
    parted
    dosfstools
    e2fsprogs
    btrfs-progs
    ntfs-3g
    exfatprogs
)

check_packages() {
    local pkg found
    local -a available=()
    [[ -f "$PACKAGES" ]] || { err "packages.x86_64 tidak ditemukan"; return; }

    while IFS= read -r pkg; do
        pkg="${pkg%%#*}"
        pkg="$(printf '%s' "$pkg" | tr -d '[:space:]')"
        [[ -n "$pkg" ]] && available+=("$pkg")
    done < "$PACKAGES"

    for pkg in "${REQUIRED_PACKAGES[@]}"; do
        found=0
        for candidate in "${available[@]}"; do
            if [[ "$candidate" == "$pkg" ]]; then
                found=1
                break
            fi
        done
        if (( found )); then
            pass_msg "paket installer tersedia: ${pkg}"
        else
            err "packages.x86_64 tidak memuat paket installer '${pkg}'"
        fi
    done
}

check_script() {
    [[ -f "$INSTALLER" ]] || { err "${INSTALLER_REL} tidak ada"; return; }

    if head -n 1 "$INSTALLER" | grep -q '^#!/usr/bin/env bash$'; then
        pass_msg "shebang bash benar"
    else
        err "${INSTALLER_REL}: shebang harus '#!/usr/bin/env bash'"
    fi

    if bash -n "$INSTALLER" 2>/dev/null; then
        pass_msg "sintaks bash valid"
    else
        err "${INSTALLER_REL}: sintaks bash tidak valid"
    fi

    if grep -q $'\r' "$INSTALLER"; then
        err "${INSTALLER_REL}: memakai CRLF (harus LF)"
    fi
    if [[ "$(head -c 3 "$INSTALLER" | od -An -tx1 | tr -d ' \n')" == "efbbbf" ]]; then
        err "${INSTALLER_REL}: memakai BOM UTF-8"
    fi
}

check_modes() {
    local out
    [[ -f "$INSTALLER" ]] || return

    if out="$(bash "$INSTALLER" --help 2>&1)"; then
        pass_msg "mode --help keluar 0"
    else
        err "${INSTALLER_REL} --help gagal"
    fi
    if grep -qi 'liveos' <<< "$out" && grep -qi 'archinstall' <<< "$out"; then
        pass_msg "--help menjelaskan LiveOS dan archinstall"
    else
        err "--help tidak menjelaskan LiveOS/archinstall"
    fi

    if out="$(bash "$INSTALLER" --check 2>&1)"; then
        pass_msg "mode --check keluar 0 tanpa root"
    else
        err "${INSTALLER_REL} --check gagal"
    fi
    if grep -q 'archinstall' <<< "$out"; then
        pass_msg "--check melaporkan archinstall"
    else
        err "--check tidak melaporkan status archinstall"
    fi

    if out="$(bash "$INSTALLER" --dry-run 2>&1)"; then
        pass_msg "mode --dry-run keluar 0"
    else
        err "${INSTALLER_REL} --dry-run gagal"
    fi
    if grep -q '^  archinstall$' <<< "$out"; then
        pass_msg "--dry-run menampilkan perintah archinstall"
    else
        err "--dry-run tidak menampilkan perintah archinstall"
    fi

    if bash "$INSTALLER" --tidak-dikenal >/dev/null 2>&1; then
        err "argumen tak dikenal seharusnya gagal dengan kode != 0"
    else
        pass_msg "argumen tak dikenal ditolak"
    fi
}

check_desktop() {
    local file
    for file in "$SKEL_DESKTOP" "$MENU_DESKTOP"; do
        if [[ -f "$file" ]]; then
            pass_msg "entri desktop ada: ${file#"${ROOT}/"}"
        else
            err "entri desktop tidak ada: ${file#"${ROOT}/"}"
            continue
        fi

        if grep -q '^\[Desktop Entry\]$' "$file" &&
            grep -q '^Type=Application$' "$file" &&
            grep -q '^Name=.' "$file" &&
            grep -q '^Exec=/usr/local/bin/fishing-install-launcher --force$' "$file"; then
            pass_msg "kunci desktop lengkap: ${file#"${ROOT}/"}"
        else
            err "entri desktop tidak lengkap: ${file#"${ROOT}/"}"
        fi

        if grep -q '^NoDisplay=true$' "$file"; then
            err "entri installer tidak boleh NoDisplay=true: ${file#"${ROOT}/"}"
        fi
        if grep -q $'\r' "$file"; then
            err "entri desktop memakai CRLF: ${file#"${ROOT}/"}"
        fi
    done

    if [[ -f "$SKEL_DESKTOP" && -f "$MENU_DESKTOP" ]]; then
        if [[ "$(sha256sum "$SKEL_DESKTOP" | awk '{print $1}')" == \
            "$(sha256sum "$MENU_DESKTOP" | awk '{print $1}')" ]]; then
            pass_msg "entri skel dan menu identik"
        else
            err "entri skel dan menu berbeda isi"
        fi
    fi

    # Exec harus menunjuk launcher yang benar-benar ada di ISO.
    if [[ -f "$LAUNCHER" ]]; then
        pass_msg "Exec menunjuk /usr/local/bin/fishing-install-launcher yang ada"
    else
        err "Exec menunjuk launcher yang tidak ada di airootfs"
    fi
}

check_profiledef() {
    [[ -f "$PROFILEDEF" ]] || { err "profiledef.sh tidak ditemukan"; return; }

    if grep -qF '["/usr/local/bin/fishingos-install"]="0:0:755"' "$PROFILEDEF"; then
        pass_msg "profiledef.sh memberi mode 755 pada installer"
    else
        err "profiledef.sh tidak mengatur izin /usr/local/bin/fishingos-install"
    fi
    if grep -qF '["/usr/local/bin/fishing-install-launcher"]="0:0:755"' "$PROFILEDEF"; then
        pass_msg "profiledef.sh memberi mode 755 pada launcher"
    else
        err "profiledef.sh tidak mengatur izin /usr/local/bin/fishing-install-launcher"
    fi
}

check_launcher() {
    local out
    [[ -f "$LAUNCHER" ]] || { err "${LAUNCHER_REL} tidak ada"; return; }
    if bash -n "$LAUNCHER" 2>/dev/null; then
        pass_msg "sintaks launcher valid"
    else
        err "${LAUNCHER_REL}: sintaks bash tidak valid"
    fi
    if grep -q $'\r' "$LAUNCHER"; then
        err "${LAUNCHER_REL}: memakai CRLF (harus LF)"
    fi
    if grep -qF 'fishing.install=1' "$LAUNCHER" &&
        grep -qF 'sudo -n' "$LAUNCHER"; then
        pass_msg "launcher memakai penanda boot dan sudo tanpa sandi"
    else
        err "launcher tidak memeriksa 'fishing.install=1' atau tidak memakai sudo -n"
    fi

    # Tanpa penanda di /proc/cmdline launcher harus diam dan keluar 0.
    if out="$(bash "$LAUNCHER" 2>&1)"; then
        if [[ -z "$out" ]]; then
            pass_msg "launcher diam saat boot LiveOS"
        else
            err "launcher menghasilkan output tanpa penanda boot: ${out}"
        fi
    else
        err "launcher gagal saat dijalankan tanpa penanda boot"
    fi
    if bash "$LAUNCHER" --help >/dev/null 2>&1; then
        pass_msg "mode --help launcher keluar 0"
    else
        err "mode --help launcher gagal"
    fi

    if [[ -f "$AUTOSTART" ]]; then
        if grep -q '^Exec=/usr/local/bin/fishing-install-launcher$' "$AUTOSTART" &&
            grep -q '^OnlyShowIn=XFCE;$' "$AUTOSTART" &&
            grep -q '^NoDisplay=true$' "$AUTOSTART"; then
            pass_msg "autostart installer terpasang untuk sesi XFCE"
        else
            err "autostart installer tidak lengkap"
        fi
    else
        err "autostart installer tidak ada di etc/xdg/autostart"
    fi

    if grep -qF '/usr/local/bin/fishingos-install' "$SUDOERS" 2>/dev/null; then
        pass_msg "sudoers liveuser mengizinkan installer"
    else
        err "sudoers liveuser tidak mengizinkan /usr/local/bin/fishingos-install"
    fi
}

check_boot_entries() {
    local syslinux_cfg="${ROOT}/profile/syslinux/archiso_sys-linux.cfg"
    local syslinux_main="${ROOT}/profile/syslinux/archiso_sys.cfg"
    local grub_cfg="${ROOT}/profile/grub/grub.cfg"
    local loopback_cfg="${ROOT}/profile/grub/loopback.cfg"
    local efiboot_dir="${ROOT}/profile/efiboot/loader"
    local block

    # syslinux (BIOS): label khusus installer dengan penanda boot.
    if [[ -f "$syslinux_cfg" ]]; then
        block="$(awk '
            toupper($1) == "LABEL" { inblock = ($2 == "fishinginstall"); next }
            inblock { print }
        ' "$syslinux_cfg")"
        if [[ -n "$block" ]] && grep -qF 'fishing.install=1' <<< "$block"; then
            pass_msg "syslinux: label installer dengan fishing.install=1"
        else
            err "syslinux: LABEL fishinginstall dengan fishing.install=1 tidak ditemukan"
        fi
        if grep -q '^DEFAULT fishing$' "$syslinux_main" 2>/dev/null; then
            pass_msg "syslinux: LiveOS tetap jadi pilihan default"
        else
            err "syslinux: DEFAULT harus tetap 'fishing' (LiveOS)"
        fi
    else
        err "archiso_sys-linux.cfg tidak ditemukan"
    fi

    # GRUB (ISO dan loopback): entry installer dengan penanda dan id stabil.
    for cfg in "$grub_cfg" "$loopback_cfg"; do
        [[ -f "$cfg" ]] || { err "${cfg#"${ROOT}/"} tidak ditemukan"; continue; }
        if grep -A6 -- "--id 'fishingos-install'" "$cfg" | grep -qF 'fishing.install=1'; then
            pass_msg "GRUB: ${cfg#"${ROOT}/"} punya entry installer"
        else
            err "GRUB: ${cfg#"${ROOT}/"} tidak punya entry fishingos-install dengan fishing.install=1"
        fi
        if grep -q '^default=fishingos$' "$cfg"; then
            pass_msg "GRUB: ${cfg#"${ROOT}/"} default tetap LiveOS"
        else
            err "GRUB: ${cfg#"${ROOT}/"} default harus 'fishingos' (LiveOS)"
        fi
    done

    # systemd-boot (UEFI): entri installer terpisah, default tetap LiveOS.
    local entry found=0
    for entry in "$efiboot_dir"/entries/*install*.conf; do
        [[ -f "$entry" ]] || continue
        found=1
        if grep -q '^options .*fishing\.install=1' "$entry"; then
            pass_msg "systemd-boot: ${entry#"${ROOT}/"} membawa fishing.install=1"
        else
            err "systemd-boot: ${entry#"${ROOT}/"} tanpa fishing.install=1"
        fi
    done
    if (( found == 0 )); then
        err "systemd-boot: tidak ada entri installer di loader/entries"
    fi
    if grep -q '^default 01-archiso-x86_64-linux.conf$' "${efiboot_dir}/loader.conf" 2>/dev/null; then
        pass_msg "systemd-boot: LiveOS tetap jadi pilihan default"
    else
        err "systemd-boot: default harus tetap 01-archiso-x86_64-linux.conf (LiveOS)"
    fi
}

check_packages
check_script
check_modes
check_desktop
check_launcher
check_boot_entries
check_profiledef

if (( status == 0 )); then
    echo "[PASS] Jalur installer LiveOS -> terpasang konsisten"
fi
exit "${status}"
