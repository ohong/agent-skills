---
name: fast-wifi
description: Diagnose a slow macOS network with the bundled measurement script. Use when the user asks to troubleshoot current Wi-Fi or internet performance.
---

# Fast Wi-Fi

## Goal

Improve the active connection when possible, and prove what changed with before/after measurements. Treat the current network state as authoritative; if the user names an SSID, verify the Mac is actually on it before acting. On public or captive networks, prefer reversible joins, GUI-assisted authentication, and clear evidence over speculative tuning.

## Core Workflow

1. Identify the active interface and route.
   - Prefer `networksetup -listallhardwareports` to confirm Wi-Fi is `en0`.
   - Run `route -n get default`, `scutil --nwi`, `ipconfig getsummary en0`, and `system_profiler SPAirPortDataType`.
   - Use `scripts/wifi_snapshot.sh en0` for a compact first pass.

2. Establish a baseline before changing anything.
   - Record SSID or network evidence, gateway, IP, PHY mode, band, channel width, signal/noise, transmit rate, DNS, proxy state, first-hop latency, public latency, captive/auth state, and `networkQuality -I en0 -s`.
   - Separate idle latency from loaded throughput. First-hop latency to the gateway proves whether the issue starts on the local Wi-Fi/AP path.
   - If comparing close candidates, take at least two samples or treat download/upload differences under about 10% as noise. Prefer the network with lower loss, lower first-hop latency, and better loaded responsiveness when throughput is effectively tied.

3. Interpret the bottleneck.
   - Weak signal: RSSI worse than about `-70 dBm`, poor SNR, low MCS, or low transmit rate.
   - Bad AP/channel contention: good RSSI but narrow channel width, low or bouncing transmit rate, first-hop jitter/loss, or many neighboring APs on the same channel.
   - Public/captive shaping: open network, option 82 or captive-network markers, good RSSI but very low throughput and high first-hop latency.
   - VPN/proxy issue: default route through `utun*`, active VPN process, or configured proxy.
   - Private Relay or per-network privacy issue: captive portals, rate-limited sites, or network-auth pages fail while basic IP connectivity works; inspect "Limit IP address tracking" and Private Wi-Fi Address mode only when symptoms point there.
   - Background traffic issue: speed test responsiveness is poor and Activity Monitor or `nettop` shows sync/backup/media/download traffic competing for the public link.
   - DNS issue: gateway and public pings are healthy, but resolver queries are slow or failing.
   - ISP/uplink issue: first hop is clean but external latency/throughput is poor.

4. Handle public and captive networks.
   - If the Mac is associated but internet access is blocked, open the captive portal before changing network settings. Try Safari to `http://captive.apple.com/` or a plain HTTP site, and inspect System Settings > Wi-Fi details.
   - Use `@Computer` / Computer Use when needed to click visible macOS permission panes, Wi-Fi detail panes, captive portal accept buttons, or browser login popups that CLI tools cannot reach. Describe what you are clicking. Do not enter credentials, payment details, or accept legal terms unless the user has clearly asked you to.
   - On macOS 15+ open/captive networks, rotating Private Wi-Fi Address can cause re-authentication or a new DHCP identity. Consider switching that network to Fixed only when repeated reconnect/auth churn is the problem and the user accepts the privacy tradeoff.
   - If a network or site reports incompatibility with iCloud Private Relay, consider disabling "Limit IP address tracking" for that specific Wi-Fi network only with user approval, then re-test and note the privacy tradeoff.
   - Check Low Data Mode per network. Turn it off for clean speed testing if it is enabled unexpectedly; turn it on only when reducing background traffic on a constrained public network is more important than absolute throughput.

5. Apply only safe local fixes first.
   - Rejoin the intended SSID if the Mac is on the wrong network.
   - Toggle Wi-Fi off/on and rejoin when the link looks stale or the Mac may roam to a better AP.
   - Renew DHCP only when address/router/DNS state looks wrong.
   - Try another official open SSID when available, but verify that the join changed the lease, gateway, or radio state; SSID names may be redacted and `networksetup -getairportnetwork` can be wrong.
   - If background traffic is the bottleneck, identify heavy processes with Activity Monitor or `nettop -P -L 1`; ask before quitting, pausing, or rate-limiting anything.
   - Move preferred networks only when the user clearly wants a specific SSID prioritized.
   - Change DNS only when DNS is specifically the bottleneck; do not use DNS as a generic speed fix.
   - Do not kill apps, forget networks, disable security features, or change router settings without clear user intent.

6. Use admin-only mitigations only with care.
   - `sudo ifconfig awdl0 down` and `sudo ifconfig llw0 down` can reduce periodic Wi-Fi latency spikes from Apple peer interfaces, but they need an admin password and can affect AirDrop/AirPlay/Continuity. Restore with `up` or reboot.
   - Do not request sudo just to run routine diagnostics.

7. Re-measure with the same checks.
   - Repeat first-hop ping, public ping, Wi-Fi link state, and `networkQuality -I en0 -s`.
   - Report the before/after numbers and whether the goal improved, worsened, or is blocked by AP/router/public-network conditions.
   - When no local fix remains, state that plainly and recommend physical relocation, another official SSID, tethering, or waiting instead of continuing to tweak DNS or privacy settings.

## Useful Commands

```sh
networksetup -listallhardwareports
networksetup -getairportnetwork en0
system_profiler SPAirPortDataType
ipconfig getsummary en0
route -n get default
scutil --nwi
networksetup -getdnsservers Wi-Fi
scutil --proxy
scutil --dns
ping -c 20 <gateway>
ping -c 20 1.1.1.1
networkQuality -I en0 -s
nettop -P -L 1
```

`networksetup -getairportnetwork en0` may incorrectly say the Mac is not associated on newer macOS or privacy-constrained networks. If that happens, rely on `system_profiler SPAirPortDataType`, `ipconfig getsummary en0`, and route state.

On some macOS builds, the old `airport` command is unavailable and SSIDs may be redacted from command output. Successful `networksetup -setairportnetwork`, changed DHCP lease/client identity, option 82 markers, gateway, channel, and BSSID/radio state can still prove that a join or roam happened.

## Router or Public-Network Findings

When the evidence points outside the Mac, stop pretending local tweaks will fix it. Give the user the exact router/AP actions that match the evidence:

- For home routers: change 5 GHz channel, prefer 80/160 MHz if stable, enable Wi-Fi 6/6 GHz when available, reboot the AP, disable overloaded QoS, or test Ethernet.
- For double NAT: identify both private hops and suggest testing directly behind the upstream router.
- For public Wi-Fi: recommend moving closer to a different AP, switching to cellular/tethering, trying a different official SSID, or waiting; public networks can be per-client shaped.
- For VPN: test with and without VPN only when the route or process evidence shows VPN involvement.

Be concrete and measurement-led. A good final answer includes the current SSID/network evidence, link rate/channel, first-hop latency, speed result, change attempted, and next best action.

## Helper Script

Run:

```sh
scripts/wifi_snapshot.sh en0
```

The script is read-only and does not require sudo. It gathers the standard diagnostic bundle and runs a short `networkQuality` sample.
