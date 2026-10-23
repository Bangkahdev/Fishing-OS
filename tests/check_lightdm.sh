#!/usr/bin/env bash
# Regresi: autologin liveuser tidak boleh punya jeda buatan.
# LightDM menunggu `autologin-user-timeout` detik SEBELUM autologin, jadi
# nilai >0 memperlambat boot. Urutan unit menjamin accounts-daemon siap.
set -euo pipefail

conf="profile/airootfs/etc/lightdm/lightdm.conf"
override="profile/airootfs/etc/systemd/system/lightdm.service.d/override.conf"

fail() {
  echo "[FAIL] $*" >&2
  exit 1
}

[[ -f "$conf" ]] || fail "lightdm.conf tidak ditemukan"
[[ -f "$override" ]] || fail "override.conf tidak ditemukan"

grep -q '^autologin-user=liveuser$' "$conf" ||
  fail "autologin-user harus liveuser"

timeout="$(sed -n 's/^autologin-user-timeout=//p' "$conf")"
[[ "$timeout" == "0" ]] ||
  fail "autologin-user-timeout harus 0 (sekarang: ${timeout:-<kosong>})"

grep -q '^After=.*accounts-daemon\.service' "$override" ||
  fail "override.conf harus After=accounts-daemon.service"
grep -q '^Wants=.*accounts-daemon\.service' "$override" ||
  fail "override.conf harus Wants=accounts-daemon.service"

echo "[PASS] LightDM autologin tanpa jeda dan menunggu accounts-daemon"
