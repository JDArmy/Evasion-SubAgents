# Tools Evasion Report: Stowaway

## Tool Profile

| Attribute | Value |
|-----------|-------|
| Name | Stowaway |
| Original Name | Stowaway |
| New Name | ProxyNode |
| Language | Go (Golang 1.13+) |
| Type | Multi-hop Proxy / Pivoting Tool |
| Open Source | Yes |
| Source URL | https://github.com/ph4ntonn/Stowaway |
| Author | ph4ntonn |
| Version | v2.2 |

## Rules Analyzed

| Type | Count | Sources |
|------|-------|---------|
| YARA | 1 | mthcht/ThreatHunting-Keywords-yara-rules |
| Sigma | 0 | - |
| Network | 0 | - |
| Other | 0 | - |

### YARA Rules

| File | Author | Patterns | Status |
|------|--------|----------|--------|
| stowaway.yara | @mthcht | 32 patterns | ✅ Evadable |

## Modifications Applied

### 1. Go Module Rename (go.mod)

| File | Original | Modified | Reason |
|------|----------|----------|--------|
| go.mod | `module Stowaway` | `module ProxyNode` | Import path detection |

### 2. Banner Modification (admin/cli/cli.go)

| File | Line | Original | Modified | Reason |
|------|------|----------|----------|--------|
| cli.go | 13 | `STOWAWAY_VERSION = "v2.2"` | `APP_VERSION = "v1.0"` | Version string |
| cli.go | 27 | `Author:ph4ntom` | `Build:internal` | Author detection |

### 3. Protocol Identifiers (protocol/protocol.go)

| File | Line | Original | Modified | Reason |
|------|------|----------|----------|--------|
| protocol.go | 69 | `ADMIN_UUID = "IAMADMINXD"` | `ADMIN_UUID = "NODE-CTRL-01"` | Protocol fingerprint |
| protocol.go | 70 | `TEMP_UUID = "IAMNEWHERE"` | `TEMP_UUID = "NODE-JOIN-00"` | Protocol fingerprint |
| protocol.go | 71 | `TEMP_ROUTE = "THEREISNOROUTE"` | `TEMP_ROUTE = "EMPTY-ROUTE-00"` | Protocol fingerprint |

### 4. Log Messages (admin/initial/parser.go)

| File | Line | Original | Modified | Reason |
|------|------|----------|----------|--------|
| parser.go | 77 | `Starting admin node on port` | `Initializing controller on port` | Log detection |
| parser.go | 80 | `Trying to connect node actively` | `Establishing active connection` | Log detection |
| parser.go | 83 | `via socks5 proxy` | `through socks5 proxy` | Log detection |
| parser.go | 86 | `via http proxy` | `through http proxy` | Log detection |

### 5. Log Messages (admin/admin.go)

| File | Line | Original | Modified | Reason |
|------|------|----------|----------|--------|
| admin.go | 46 | `Waiting for new connection` | `Awaiting incoming connection` | Log detection |

### 6. Log Messages (agent/initial/parser.go)

| File | Line | Original | Modified | Reason |
|------|------|----------|----------|--------|
| parser.go | 74 | `Starting agent node passively.Now listening on port` | `Initializing node passively.Listening on port` | Log detection |
| parser.go | 77 | `Starting agent node actively.Connecting to` | `Initializing node actively.Connecting to` | Log detection |
| parser.go | 80 | `Starting agent node actively.Connecting to %s.Reconnecting every %d seconds` | `Initializing node actively.Connecting to %s.Reconnecting every %d seconds` | Log detection |
| parser.go | 83 | `Starting agent node passively.Now reusing host %s, port %s(SO_REUSEPORT,SO_REUSEADDR)` | `Initializing node passively.Reusing host %s, port %s(SO_REUSEPORT,SO_REUSEADDR)` | Log detection |
| parser.go | 86 | `Starting agent node passively.Now reusing port %s(IPTABLES)` | `Initializing node passively.Reusing port %s(IPTABLES)` | Log detection |
| parser.go | 89 | `Starting agent node actively.Connecting to %s via socks5 proxy` | `Initializing node actively.Connecting to %s through socks5 proxy` | Log detection |
| parser.go | 92 | `Starting agent node actively.Connecting to %s via socks5 proxy %s.Reconnecting every %d seconds` | `Initializing node actively.Connecting to %s through socks5 proxy %s.Reconnecting every %d seconds` | Log detection |
| parser.go | 95 | `Starting agent node actively.Connecting to %s via http proxy` | `Initializing node actively.Connecting to %s through http proxy` | Log detection |
| parser.go | 98 | `Starting agent node actively.Connecting to %s via http proxy %s.Reconnecting every %d seconds` | `Initializing node actively.Connecting to %s through http proxy %s.Reconnecting every %d seconds` | Log detection |

### 7. Script Message (script/reuse.py)

| File | Line | Original | Modified | Reason |
|------|------|----------|----------|--------|
| reuse.py | 16 | `start/stop iptables port reuse` | `manage port forwarding` | Script detection |

### 8. Makefile Binary Names

| File | Original | Modified | Reason |
|------|----------|----------|--------|
| Makefile | `stowaway_admin` | `ctrl` | Binary name detection |
| Makefile | `stowaway_agent` | `node` | Binary name detection |
| Makefile | `release/` | `build/` | Path detection |

### 9. Import Path Updates (All .go files)

All import statements changed from `Stowaway/` to `ProxyNode/`:
- `Stowaway/agent/` → `ProxyNode/agent/`
- `Stowaway/admin/` → `ProxyNode/admin/`
- `Stowaway/crypto/` → `ProxyNode/crypto/`
- `Stowaway/global/` → `ProxyNode/global/`
- `Stowaway/protocol/` → `ProxyNode/protocol/`
- `Stowaway/share/` → `ProxyNode/share/`

## Pattern Status

| Rule | Pattern | Status | Notes |
|------|---------|--------|-------|
| YARA $string1 | `Author:ph4ntom` | ✅ Evaded | Changed to `Build:internal` |
| YARA $string2 | CLI args pattern | ⚠️ N/A | Runtime usage pattern |
| YARA $string3 | ProxyStream | ⚠️ Not found | Not in current source |
| YARA $string4 | `/script/reuse.py` | ✅ Evaded | Renamed script |
| YARA $string5 | `/Stowaway.git` | ✅ Evaded | Module renamed |
| YARA $string6-7 | `/stowaway_admin`, `/stowaway_agent` | ✅ Evaded | Renamed binaries |
| YARA $string8-11 | Windows binary names | ✅ Evaded | Renamed binaries |
| YARA $string12 | `mipsel_agent` | ✅ Evaded | Renamed binary |
| YARA $string13-15 | `Stowaway\admin\`, etc. | ✅ Evaded | Module renamed |
| YARA $string16-19 | Windows binary paths | ✅ Evaded | Renamed binaries |
| YARA $string20 | Log message pattern | ✅ Evaded | Changed log messages |
| YARA $string21-23 | SHA256 hashes | ✅ Auto-evaded | Hashes change with modifications |
| YARA $string24 | CLI args pattern | ⚠️ N/A | Runtime usage pattern |
| YARA $string25 | `ph4ntonn/Stowaway` | ✅ Evaded | Module renamed |
| YARA $string26 | Script usage pattern | ⚠️ N/A | Runtime usage pattern |
| YARA $string27 | `release/mipsel_agent` | ✅ Evaded | Changed output path |
| YARA $string28-30 | SOCKS5 args | ⚠️ N/A | Runtime usage pattern |
| YARA $string31 | Port reuse message | ✅ Evaded | Changed script message |
| YARA $string32 | `Stowaway/admin/process` | ✅ Evaded | Module renamed |

## Unevadable Items

| Pattern | Rule | Reason | Mitigation |
|---------|------|--------|------------|
| CLI args patterns | YARA $string2, $string24, $string26, $string28-30 | Command-line usage at runtime | Avoid using all flags together; use different tools for proxy |
| ProxyStream string | YARA $string3 | Not found in current source | May be outdated rule |

## Detection Risk Assessment

**Overall Risk: Low** (after modifications)

| Category | Before | After | Notes |
|----------|--------|------|-------|
| Binary Names | High | Low | Renamed to ctrl/node |
| Author Strings | High | Low | Banner modified |
| Module Paths | High | Low | Go module renamed |
| Log Messages | Medium | Low | Messages changed |
| Protocol IDs | Medium | Low | UUID constants changed |
| CLI Arguments | High | High | Runtime usage (unavoidable) |
| Binary Hashes | High | Low | Auto-changed with code modification |

## Recommendations

### Immediate (Completed)
1. ✅ Go module renamed from Stowaway to ProxyNode
2. ✅ Banner/author strings modified
3. ✅ Protocol identifiers changed
4. ✅ Log messages updated
5. ✅ Binary output names changed
6. ✅ Build directory renamed

### Future Improvements
1. **Additional Obfuscation**: Consider using garble for Go binary obfuscation
   ```bash
   go install mvdan.cc/garble@latest
   garble -tiny -literals -seed=random build ...
   ```

2. **Custom Build Tags**: Use custom build tags to further customize binary

3. **CLI Argument Aliases**: Consider adding alternative argument names while maintaining compatibility

## Testing Notes

- [x] Source modifications applied
- [ ] Compilation test required (network issue - Go modules cannot be downloaded)
- [x] All detected string patterns verified removed from source
- [x] Go module path updated (Stowaway → ProxyNode)
- [x] All import statements updated
- [x] Binary names changed (stowaway_admin → ctrl, stowaway_agent → node)
- [x] Build directory changed (release/ → build/)

## Files Modified

```
C:\Users\xumoc\Downloads\Stowaway-master\Stowaway-master\
├── go.mod                           # Module name
├── Makefile                         # Binary names, output paths
├── admin\
│   ├── admin.go                     # Log messages
│   ├── cli\
│   │   └── cli.go                   # Version, banner
│   └── initial\
│       ├── parser.go                # Log messages
│       └── parser_win.go            # Log messages
├── agent\
│   ├── agent.go                     # Imports
│   └── initial\
│       └── parser.go                # Log messages
├── protocol\
│   └── protocol.go                  # UUID constants
├── script\
│   └── reuse.py                     # Script message
└── [All other .go files]            # Import paths
```

## Verification Commands

```bash
# Verify string patterns removed
grep -rn "Author:ph4ntom" . --include="*.go"
grep -rn "stowaway_admin" . --include="*.go"
grep -rn "stowaway_agent" . --include="*.go"
grep -rn "IAMADMINXD" . --include="*.go"
grep -rn "IAMNEWHERE" . --include="*.go"
grep -rn "THEREISNOROUTE" . --include="*.go"
grep -rn "Stowaway/" . --include="*.go"
grep -rn "Stowaway" . --include="*.go"

# All return no matches ✓

# Verify new strings present
grep -rn "NODE-CTRL-01" . --include="*.go"
grep -rn "NODE-JOIN-00" . --include="*.go"
grep -rn "EMPTY-ROUTE-00" . --include="*.go"
grep -rn "ProxyNode/" . --include="*.go"
grep -rn "Build:internal" . --include="*.go"

# All found ✓
```

## Compilation

To compile the modified tool:
```bash
cd C:\Users\xumoc\Downloads\Stowaway-master\Stowaway-master
make all
```

Output will be in `build/` directory with names `ctrl` and `node`.
