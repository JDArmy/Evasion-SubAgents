# Stowaway Rule Inventory

## Summary

| Type | Count | Sources |
|------|-------|---------|
| YARA | 1 | mthcht/ThreatHunting-Keywords-yara-rules |
| Sigma | 0 | - |
| Network | 0 | - |
| Other | 0 | - |

## YARA Rules

### 1. stowaway.yara (mthcht)

**Source:** https://github.com/mthcht/ThreatHunting-Keywords-yara-rules

**Detection Patterns:**

| Pattern ID | Type | Description | Category |
|------------|------|-------------|----------|
| $string1 | String | ` Author:ph4ntom` | Banner/Author |
| $string2 | Regex | CLI args pattern with `-c -s --proxy --proxyu --proxyp --reconnect` | CLI Arguments |
| $string3 | Regex | `ProxyStream.*Stowaway` | Internal string |
| $string4 | Regex | `/script/reuse.py` | Script path |
| $string5 | Regex | `/Stowaway.git` | Git path |
| $string6 | String | `/stowaway_admin` | Binary name |
| $string7 | String | `/stowaway_agent` | Binary name |
| $string8-11 | Regex | `/windows_x64_admin.exe`, `/windows_x64_agent.exe`, etc. | Binary names |
| $string12 | Regex | `\\mipsel_agent` | Binary name |
| $string13-15 | Regex | `\\Stowaway\\admin\\`, `\\Stowaway\\agent\\`, `\\Stowaway\\ansicon\\` | Directory paths |
| $string16-19 | Regex | `\\windows_x64_admin.exe`, etc. | Binary names (Windows) |
| $string20 | Regex | Log message pattern | Log output |
| $string21-23 | Hash | SHA256 hashes | Binary hashes |
| $string24 | Regex | CLI args pattern | CLI Arguments |
| $string25 | String | `ph4ntonn/Stowaway` | GitHub repo |
| $string26 | Regex | `python reuse.py --start --rhost --rport` | Script usage |
| $string27 | String | `release/mipsel_agent` | Build path |
| $string28-30 | String | `--socks5-proxy socks5`, etc. | CLI Arguments |
| $string31 | String | `'start/stop iptables port reuse'` | Functionality string |
| $string32 | String | `Stowaway/admin/process` | Go import path |

**Condition:** `any of them`

## Sigma Rules

No Sigma rules found for Stowaway.

## Network Rules

No network-based detection rules found.

## Hash-based Detection

The YARA rule includes 3 SHA256 hashes:
- `1df8bc4fb468ccc0fd85b553411d9b3eb7a2ba4c4a4469ae41913eef9a9e65f6`
- `a78d737f30e03d166d4e3e3b2dca71d54f1cbf582206dfe16a1e717ce3dc0ef7`
- `ac9215db682509ab2bdcba7fe924d84dafa1d8aade87172c1c6328b2cb6c9e52`

## Detection Categories

1. **Binary Names**: `stowaway_admin`, `stowaway_agent`, platform-specific names
2. **Author Strings**: `Author:ph4ntom`, `ph4ntonn/Stowaway`
3. **CLI Arguments**: `--socks5-proxy`, `--socks5-proxyu`, `--socks5-proxyp`, `--reconnect`
4. **Paths**: Build paths, Git paths, script paths
5. **Go Import Paths**: `Stowaway/admin/process`, `Stowaway/agent/`
6. **Log Messages**: Startup messages
7. **Binary Hashes**: Known sample hashes
