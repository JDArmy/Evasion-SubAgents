# Stowaway Behavior Analysis

## Tool Classification

| Category | Description |
|----------|-------------|
| Type | Multi-hop Proxy / Pivoting Tool |
| ATT&CK Techniques | T1090 (Proxy), T1090.001 (Internal Proxy), T1090.002 (External Proxy) |
| Use Case | Network pivoting, lateral movement, SOCKS proxy |

## Process Behavior

### Execution Indicators

| Indicator | Value | Location |
|-----------|-------|----------|
| Binary Names | `stowaway_admin`, `stowaway_agent` | Makefile output |
| Process Arguments | `-l`, `-c`, `-s`, `--socks5-proxy`, `--http-proxy`, `--reconnect`, `--up`, `--down`, `--tls-enable` | CLI parser |
| Console Window | Hidden with `-H=windowsgui` flag | Makefile (windows_nogui_agent) |

### CLI Argument Patterns

```
Admin mode:
  -l <port>                    Listen mode
  -c <ip:port>                 Connect mode
  -s <secret>                  Communication secret
  --socks5-proxy <ip:port>     SOCKS5 proxy
  --socks5-proxyu <user>       SOCKS5 username
  --socks5-proxyp <pass>       SOCKS5 password
  --http-proxy <ip:port>       HTTP proxy
  --down <raw|http|ws>         Downstream protocol
  --tls-enable                 Enable TLS
  --domain <domain>            TLS SNI domain
  --heartbeat                  Enable heartbeat

Agent mode (additional):
  --reconnect <seconds>        Reconnect interval
  --rehost <ip>                Port reuse host
  --report <port>              Port reuse port
  --up <raw|http|ws>           Upstream protocol
  --cs <utf-8|gbk>             Console charset
```

## Network Behavior

### Connection Patterns

| Pattern | Description |
|---------|-------------|
| Protocol | TCP (raw), HTTP, WebSocket |
| Encryption | AES-256-GCM (default), TLS (optional) |
| Ports | User-defined |
| Direction | Bidirectional (admin↔agent) |

### Protocol Identifiers

| Identifier | Value | Location | Purpose |
|------------|-------|----------|---------|
| ADMIN_UUID | `IAMADMINXD` | protocol/protocol.go:69 | Admin identifier |
| TEMP_UUID | `IAMNEWHERE` | protocol/protocol.go:70 | New connection identifier |
| TEMP_ROUTE | `THEREISNOROUTE` | protocol/protocol.go:71 | Empty route marker |

### Message Types

From `protocol/protocol.go`:
- HI, UUID, CHILDUUIDREQ, CHILDUUIDRES
- MYINFO, MYMEMO
- SHELLREQ, SHELLRES, SHELLCOMMAND, SHELLRESULT, SHELLEXIT
- LISTENREQ, LISTENRES
- SSHREQ, SSHRES, SSHCOMMAND, SSHRESULT, SSHEXIT
- SSHTUNNELREQ, SSHTUNNELRES
- FILESTATREQ, FILESTATRES, FILEDATA, FILEERR, FILEDOWNREQ, FILEDOWNRES
- SOCKSSTART, SOCKSTCPDATA, SOCKSUDPDATA, UDPASSSTART, UDPASSRES, SOCKSTCPFIN, SOCKSREADY
- FORWARDTEST, FORWARDSTART, FORWARDREADY, FORWARDDATA, FORWARDFIN
- BACKWARDTEST, BACKWARDSTART, BACKWARDSEQ, BACKWARDREADY, BACKWARDDATA, BACKWARDFIN, BACKWARDSTOP, BACKWARDSTOPDONE
- CONNECTSTART, CONNECTDONE
- NODEOFFLINE, NODEREONLINE, UPSTREAMOFFLINE, UPSTREAMREONLINE
- SHUTDOWN, HEARTBEAT

## File Behavior

### Build Artifacts

| Artifact | Path Pattern |
|----------|--------------|
| Linux Admin | `release/linux_x86_admin`, `release/linux_x64_admin`, `release/linux_arm64_admin` |
| Linux Agent | `release/linux_x86_agent`, `release/linux_x64_agent`, `release/linux_arm64_agent` |
| Windows Admin | `release/windows_x86_admin.exe`, `release/windows_x64_admin.exe` |
| Windows Agent | `release/windows_x86_agent.exe`, `release/windows_x64_agent.exe` |
| macOS Admin | `release/macos_x64_admin`, `release/macos_arm64_admin` |
| macOS Agent | `release/macos_x64_agent`, `release/macos_arm64_agent` |
| MIPS Agent | `release/mipsel_agent` |
| ARM Agent | `release/arm_eabi5_agent` |
| FreeBSD | `release/freebsd_x86_admin`, `release/freebsd_arm_admin`, etc. |

### Script Files

| File | Purpose |
|------|---------|
| `script/reuse.py` | iptables port reuse script |

## String Constants

### Banner/Version

```
Location: admin/cli/cli.go:13
const STOWAWAY_VERSION = "v2.2"

Location: admin/cli/cli.go:17-28
ASCII art banner with "Author:ph4ntom"
```

### Log Messages

| Message | Location | Pattern |
|---------|----------|---------|
| `Starting agent node passively.Now listening on port` | agent/initial/parser.go:74 | Startup log |
| `Starting agent node actively.Connecting to` | agent/initial/parser.go:77 | Startup log |
| `Reconnecting every` | agent/initial/parser.go:80 | Startup log |
| `Starting admin node on port` | admin/initial/parser.go:77 | Startup log |
| `Trying to connect node actively` | admin/initial/parser.go:80 | Startup log |
| `Waiting for new connection` | admin/admin.go:46 | Startup log |

### Go Module Paths

```
Location: go.mod
module Stowaway

Import paths found in all source files:
- Stowaway/agent/
- Stowaway/admin/
- Stowaway/crypto/
- Stowaway/global/
- Stowaway/protocol/
- Stowaway/share/
```

## Crypto Behavior

| Feature | Implementation | Location |
|---------|---------------|----------|
| AES Encryption | AES-256-GCM | crypto/aes.go |
| GZIP Compression | gzip | crypto/gzip.go |
| TLS | Optional | share/transport/tls.go |
| Pre-auth Token | Generated from secret | share/preauth.go |

## Evasion Techniques

### Port Reuse

| Technique | Platform | Location |
|-----------|----------|----------|
| SO_REUSEPORT/SO_REUSEADDR | Windows, macOS, Linux | agent/initial/method.go |
| iptables | Linux only | agent/initial/method.go |

### Hidden Execution

Windows agent can be built with hidden console:
```makefile
BUILD_ENV = CGO_ENABLED=0
OPTIONS = -trimpath -ldflags "-w -s"
windows_nogui_agent:
    go build -ldflags="-H=windowsgui" ...
```

## Detection Opportunities

### High-Confidence Indicators

1. **Banner String**: `Author:ph4ntom` in ASCII art
2. **UUID Constants**: `IAMADMINXD`, `IAMNEWHERE`, `THEREISNOROUTE`
3. **Module Path**: `Stowaway/` in Go binary
4. **CLI Args**: `--socks5-proxy`, `--socks5-proxyu`, `--socks5-proxyp` combination

### Medium-Confidence Indicators

1. **Binary Names**: `stowaway_admin`, `stowaway_agent`
2. **Build Paths**: `release/windows_x64_admin.exe`, etc.
3. **Script Path**: `/script/reuse.py`
4. **Log Messages**: Startup messages with "agent node", "admin node"

### Low-Confidence Indicators

1. **Port reuse messages**: `start/stop iptables port reuse`
2. **SOCKS5 proxy arguments**: Common in legitimate tools
3. **TLS connection patterns**: Generic encrypted traffic
