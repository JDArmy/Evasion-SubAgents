## Rule Analysis: AdaptixBeacon_CAPE

**Author**: enzok
**Target**: C++ Beacon Agent (implant binary)
**Pattern Count**: 7 (hex patterns with wildcards)
**Hash**: f78f5803be5704420cbb2e0ac3c57fcb3d9cdf443fbf1233c069760bee115b5d

### Patterns Summary

| Pattern | Type | Description |
|---------|------|-------------|
| `$conf_1` | `{8D ?? ?? E8 [3] 00 4? 89 [1-2] 4? 8B 4C 24 ?? E8 [3] 00 4? 8B 53 48 66 [0-1] 89 04 ?? E8}` | Config initialization pattern |
| `$conf_2` | `{E8 [3] 00 48 8B 4C 24 ?? 48 89 43 78 E8 [3] 00 48 8B 4C 24 ?? 89 83 80 00 00 00 E8 [3] 00 03 83 80 00 00 00 48 8B 4C 24}` | Config initialization with offset 0x78, 0x80 |
| `$conf_3` | `{E8 [3] 00 4? 8B 4C 24 ?? 4? 89 ?? 4? 89 43 58 E8 [3] 00 4? 8B 4C 24 ?? 4? 89 ?? 4? 89 43 60 E8 [3] 00 4? 8B 4C 24 ?? 4? 89 ?? 4? 89 43 68}` | Config initialization with offsets 0x58, 0x60, 0x68 |
| `$conf_4` | `{8D ?? ?? 4? 89 ?? FF ?? 4? 89 ?? 4? 89 ?? 4? 8B ?? FF ?? ?? 4? 8B ?? 48 66 ?? 89 ?? ?? EB}` | Function call pattern with config storage |
| `$conf_5` | `{48 89 ?? 4? 89 ?? FF ?? 4? 89 ?? 4? 89 D9 4? 89 ?? ?? 4? 8B 03 FF ?? ?? 4? 89 ?? 4? 89 ?? 4? 89 ?? ?? 4? 8B 03 FF ?? ?? 4? 89}` | Config field population |
| `$wininet_1` | `{B9 77 00 00 00 [0-4] E8 [4] B9 69 00 00 00 88 ?4 24 [0-4] E8 [4] B9 6E 00 00 00 88 ?4 24}` | Wininet API sequence (w,i,n chars) |
| `$wininet_2` | `{B9 69 00 00 00 88 ?4 24 [0-4] E8 [4] B9 6E 00 00 00 88 ?4 24 [0-4] E8 [4] B9 65 00 00 00 88 ?4 24}` | Wininet API sequence (i,n,e chars) |

### Evasion Strategy

**Option A: Compiler Flags** (Priority 1)
- Feasible: Yes for config patterns
- The config initialization patterns are compiler-generated

**Option B: Source Modification** (Priority 2)
- Feasible: Yes for wininet patterns
- Change API loading method

### Status
- $conf_1 to $conf_5: Compiler flag changes can evade
- $wininet_1, $wininet_2: Requires API loader modification
