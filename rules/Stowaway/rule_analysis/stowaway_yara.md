# YARA Rule Analysis: stowaway.yara

## Rule Overview

| Attribute | Value |
|-----------|-------|
| Rule Name | stowaway |
| Author | @mthcht |
| Source | mthcht/ThreatHunting-Keywords-yara-rules |
| Condition | any of them |

## Pattern Analysis

### 1. Author String

| Pattern | Value |
|---------|-------|
| ID | $string1 |
| Pattern | ` Author:ph4ntom` |
| Type | String (nocase ascii wide) |
| Location | `admin/cli/cli.go:27` |
| Source Code | `fmt.Printf(..., STOWAWAY_VERSION)` with `Author:ph4ntom` in banner |

**Evasion Strategy:**
- Remove or modify the author string in banner
- Change to different author name or remove banner entirely

### 2. CLI Arguments Pattern

| Pattern | Value |
|---------|-------|
| ID | $string2 |
| Pattern | Regex: `\s\-c\s.{0,1000}\s\-s\s.{0,1000}\s\-\-proxy\s.{0,1000}\s\-\-proxyu\s.{0,1000}\s\-\-proxyp\s.{0,1000}\s\-\-reconnect\s` |
| Type | Regex (nocase ascii wide) |
| Location | N/A (command line) |
| Source Code | N/A (runtime usage) |

**Evasion Strategy:**
- Cannot modify - this is command-line usage pattern
- Users should avoid using all these flags together

### 3. ProxyStream String

| Pattern | Value |
|---------|-------|
| ID | $string3 |
| Pattern | Regex: `\sProxyStream\s.{0,1000}Stowaway` |
| Type | Regex (nocase ascii wide) |
| Location | Not found in current source |
| Source Code | May be in external dependency or removed |

**Evasion Strategy:**
- Not found in current source - may be outdated pattern

### 4. Script Path

| Pattern | Value |
|---------|-------|
| ID | $string4 |
| Pattern | `/script/reuse.py` |
| Type | Regex |
| Location | `script/reuse.py` |
| Source Code | File exists in repository |

**Evasion Strategy:**
- Rename script file
- Modify path in documentation

### 5. Git Path

| Pattern | Value |
|---------|-------|
| ID | $string5 |
| Pattern | `/Stowaway.git` |
| Type | Regex (nocase ascii wide) |
| Location | N/A (embedded in binary during build) |
| Source Code | Go module embeds git info |

**Evasion Strategy:**
- Build without git metadata
- Use `-trimpath` flag (already in Makefile)
- Clone without .git directory

### 6-7. Binary Names (Unix)

| Pattern | Value |
|---------|-------|
| ID | $string6, $string7 |
| Pattern | `/stowaway_admin`, `/stowaway_agent` |
| Type | String |
| Location | Makefile output names |
| Source Code | Makefile:8-31 |

**Evasion Strategy:**
- Rename output binaries in Makefile
- Change `-o` output names

### 8-11. Windows Binary Names (Unix Path)

| Pattern | Value |
|---------|-------|
| ID | $string8-11 |
| Pattern | `/windows_x64_admin.exe`, `/windows_x64_agent.exe`, `/windows_x86_admin.exe`, `/windows_x86_agent.exe` |
| Type | Regex (nocase ascii wide) |
| Location | Makefile output names |
| Source Code | Makefile:12-14, 23-24 |

**Evasion Strategy:**
- Rename output binaries in Makefile
- Change output directory structure

### 12. MIPS Binary Name

| Pattern | Value |
|---------|-------|
| ID | $string12 |
| Pattern | `\\mipsel_agent` |
| Type | Regex (nocase ascii wide) |
| Location | Makefile output |
| Source Code | Makefile:28 |

**Evasion Strategy:**
- Rename output binary

### 13-15. Directory Paths

| Pattern | Value |
|---------|-------|
| ID | $string13-15 |
| Pattern | `\\Stowaway\\admin\\`, `\\Stowaway\\agent\\`, `\\Stowaway\\ansicon\\` |
| Type | Regex (nocase ascii wide) |
| Location | Source directory structure |
| Source Code | Go import paths |

**Evasion Strategy:**
- Rename module in go.mod
- Update all import paths
- Rename source directories

### 16-19. Windows Binary Names (Windows Path)

| Pattern | Value |
|---------|-------|
| ID | $string16-19 |
| Pattern | `\\windows_x64_admin.exe`, `\\windows_x64_agent.exe`, `\\windows_x86_admin.exe`, `\\windows_x86_agent.exe` |
| Type | Regex (nocase ascii wide) |
| Location | Makefile output |
| Source Code | Makefile |

**Evasion Strategy:**
- Same as $string8-11

### 20. Log Message Pattern

| Pattern | Value |
|---------|-------|
| ID | $string20 |
| Pattern | Regex: `\]\sStarting\sagent\snode\sactively\.Connecting\sto\s.{0,1000}Reconnecting\severy\s.{0,1000}\sseconds` |
| Type | Regex (nocase ascii wide) |
| Location | `agent/initial/parser.go:80` |
| Source Code | `log.Printf("[*] Starting agent node actively.Connecting to %s.Reconnecting every %d seconds\n", ...)` |

**Evasion Strategy:**
- Modify log message text
- Remove or change format

### 21-23. SHA256 Hashes

| Pattern | Value |
|---------|-------|
| ID | $string21-23 |
| Pattern | SHA256 hashes |
| Type | String (nocase ascii wide) |
| Location | N/A (compiled binaries) |
| Source Code | N/A |

**Evasion Strategy:**
- Hash changes with any code modification
- Not a concern after source changes

### 24. CLI Arguments Pattern 2

| Pattern | Value |
|---------|-------|
| ID | $string24 |
| Pattern | Regex: `linux_x64_agent\s\-\-report\s.{0,1000}\s\-l\s.{0,1000}\s\-s\sph4ntom` |
| Type | Regex |
| Location | N/A (command line usage) |
| Source Code | N/A |

**Evasion Strategy:**
- Avoid using these exact flags together

### 25. GitHub Repo

| Pattern | Value |
|---------|-------|
| ID | $string25 |
| Pattern | `ph4ntonn/Stowaway` |
| Type | String (nocase ascii wide) |
| Location | README, documentation |
| Source Code | Not in compiled binary |

**Evasion Strategy:**
- Remove from README
- Not present in binary unless embedded

### 26. Script Usage Pattern

| Pattern | Value |
|---------|-------|
| ID | $string26 |
| Pattern | Regex: `python\sreuse\.py\s\-\-start\s\-\-rhost\s.{0,1000}\s\-\-rport\s` |
| Type | Regex (nocase ascii wide) |
| Location | N/A (command line usage) |
| Source Code | N/A |

**Evasion Strategy:**
- Avoid using script with these exact flags

### 27. Build Path

| Pattern | Value |
|---------|-------|
| ID | $string27 |
| Pattern | `release/mipsel_agent` |
| Type | String (nocase ascii wide) |
| Location | Makefile output |
| Source Code | Makefile:28 |

**Evasion Strategy:**
- Change output directory name

### 28-30. SOCKS5 Arguments

| Pattern | Value |
|---------|-------|
| ID | $string28-30 |
| Pattern | `--socks5-proxy socks5`, `--socks5-proxyp socks5`, `--socks5-proxyu socks5` |
| Type | String (nocase ascii wide) |
| Location | N/A (command line usage) |
| Source Code | N/A |

**Evasion Strategy:**
- These patterns are odd - the actual flags are `--socks5-proxy`, not with "socks5" suffix
- May be false positive pattern

### 31. Port Reuse Message

| Pattern | Value |
|---------|-------|
| ID | $string31 |
| Pattern | `'start/stop iptables port reuse'` |
| Type | String (nocase ascii wide) |
| Location | `script/reuse.py` |
| Source Code | Check reuse.py content |

**Evasion Strategy:**
- Modify message in script

### 32. Go Import Path

| Pattern | Value |
|---------|-------|
| ID | $string32 |
| Pattern | `Stowaway/admin/process` |
| Type | String (nocase ascii wide) |
| Location | All source files with imports |
| Source Code | Import statements throughout codebase |

**Evasion Strategy:**
- Change module name in go.mod
- Update all import paths

## Evasion Priority

### High Priority (Embedded in Binary)

| Pattern | Impact | Effort |
|---------|--------|--------|
| $string1 | Banner/Author string | Low |
| $string13-15 | Go import paths | Medium |
| $string32 | Go import path | Medium |
| $string6-7, $string8-19, $string27 | Binary names | Low |

### Medium Priority (Build-time)

| Pattern | Impact | Effort |
|---------|--------|--------|
| $string5 | Git path | Low |
| $string4 | Script path | Low |

### Low Priority (Runtime/Usage)

| Pattern | Impact | Effort |
|---------|--------|--------|
| $string2, $string24, $string26, $string28-30 | CLI usage patterns | N/A |
| $string20 | Log message | Low |
| $string21-23 | Binary hashes | Auto-fixed |

### Not Found in Current Source

| Pattern | Status |
|---------|--------|
| $string3 | May be outdated |
| $string25 | In README only |
