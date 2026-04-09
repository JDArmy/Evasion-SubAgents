# AdaptixC2 Rule Mapping

## Overview

**C2 Framework:** AdaptixC2
**Implant Types:**
- `beacon_agent` (C++ - Windows only)
- `gopher_agent` (Go - Cross-platform)

**Detection Rules Found:**
- Windows_Trojan_Adaptix_Elastic.yar (2 rules, hex patterns)
- Adaptix_Beacon_bartblaze.yar (string patterns - Go function names)
- AdaptixC2_nembo81.yar (string patterns - HTTP headers)
- AdaptixC2.yml (Sigma - hash/keyword based)

---

## Rule 1: Windows_Trojan_Adaptix_2779784c (Elastic)

### Pattern Analysis

| Pattern | Type | Meaning | Source Cause | Target |
|---------|------|---------|--------------|--------|
| $a1 = { 48 81 EC A8 01 00 00 ... } | hex | Function prologue: sub rsp, 0x1A8 | Large stack allocation | beacon_agent (C++) |
| $a2 = { 48 83 EC 58 48 8B 4C 24 70 ... } | hex | Function prologue: sub rsp, 0x58 | Stack allocation | beacon_agent (C++) |

### Evasion Strategy

**Primary: Compiler Flags** (Priority 1)
- Modify beacon_agent Makefile to change optimization levels
- Add -O2 -fomit-frame-pointer to alter function prologues

---

## Rule 2: Windows_Trojan_Adaptix_b2cda978 (Elastic)

### Pattern Analysis

| Pattern | Type | Meaning | Source Cause |
|---------|------|---------|--------------|
| $a1 = { 48 89 03 8B 45 EC 48 98 ... } | hex | Code sequence | Compiled beacon code |
| $a2-$a5 | hex | Code sequences | Compiled beacon code |

### Evasion Strategy
**Primary: Compiler Flags** - Same as Rule 1

---

## Rule 3: Adaptix_Beacon (bartblaze)

### Pattern Analysis

| Pattern | Type | Target | Status |
|---------|------|--------|--------|
| $coffer = "coffer.Load" | string | Go symbol | NOT FOUND |
| $func_TaskProcess = "main.TaskProcess" | string | Go symbol | NOT FOUND |
| $func_jobRun = "main.jobRun" | string | Go symbol | NOT FOUND |
| (all other func_ patterns) | string | Go symbols | NOT FOUND |

### Conclusion
**The bartblaze rule targets an OLDER VERSION of AdaptixC2.** The current version has already renamed these functions.

---

## Rule 4: backdoor_AdaptixC2_http_beacon (nembo81)

### Pattern Analysis

| Pattern | Type | Source Location |
|---------|------|-----------------|
| $b1 = "AdaptixC2" | string | gopher_listener_tcp/ax_config.axs:26 (server-side) |
| $b2 = "X-Beacon-Id" | string | beacon_listener_http/ax_config.axs:38 |
| $d1 = /X-[0-9a-zA-Z]{3,10}-Id/ | regex | HTTP header pattern |

### Evasion Strategy
1. "AdaptixC2" - Server-side only - SKIP
2. "X-Beacon-Id" - HTTP header - MODIFY

---

## Summary

| Rule | Type | Target | Action |
|------|------|--------|--------|
| Windows_Trojan_Adaptix (Elastic) | Hex | beacon_agent | Modify Makefile flags |
| Adaptix_Beacon (bartblaze) | String | gopher_agent | SKIP (already evaded) |
| AdaptixC2_nembo81 | String | HTTP header | Modify X-Beacon-Id |
| AdaptixC2.yml (Sigma) | Hash | Post-compilation | SKIP |
