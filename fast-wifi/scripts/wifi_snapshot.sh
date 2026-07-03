#!/usr/bin/env bash
set -u

iface="${1:-en0}"
ping_count="${PING_COUNT:-10}"

section() {
  printf '\n== %s ==\n' "$1"
}

run() {
  printf '$ %s\n' "$*"
  "$@" 2>&1 || true
}

gateway_for_iface() {
  route -n get default 2>/dev/null | awk '
    $1 == "gateway:" { gateway = $2 }
    $1 == "interface:" { iface = $2 }
    END { if (iface == wanted && gateway != "") print gateway }
  ' wanted="$iface"
}

section "Timestamp"
date

section "Hardware Ports"
run networksetup -listallhardwareports

section "Wi-Fi Association"
run networksetup -getairportnetwork "$iface"

section "Wi-Fi Link"
system_profiler SPAirPortDataType 2>&1 | awk '
  /Current Network Information:/ { in_current = 1 }
  /Other Local Wi-Fi Networks:/ { in_current = 0 }
  in_current && /PHY Mode|Channel:|Security:|Signal \/ Noise|Transmit Rate|MCS Index|Network Type/ { print }
'

section "IP Summary"
run ipconfig getsummary "$iface"

section "Default Route"
run route -n get default

section "Network Reachability"
run scutil --nwi

section "DNS Servers"
run networksetup -getdnsservers Wi-Fi

section "Proxy"
run scutil --proxy

gateway="$(gateway_for_iface)"
if [ -n "$gateway" ]; then
  section "First-Hop Ping ($gateway)"
  run ping -c "$ping_count" "$gateway"
else
  section "First-Hop Ping"
  printf 'No default gateway found for %s.\n' "$iface"
fi

section "Public Ping (1.1.1.1)"
run ping -c "$ping_count" 1.1.1.1

section "DNS Query"
run dig cloudflare.com +stats +tries=1 +time=2

if command -v networkQuality >/dev/null 2>&1; then
  section "Network Quality"
  run networkQuality -I "$iface" -s
else
  section "Network Quality"
  printf 'networkQuality is not available on this system.\n'
fi
