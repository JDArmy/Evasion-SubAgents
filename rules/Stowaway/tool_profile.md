# Tool Profile: Stowaway

## Basic Information

| Attribute | Value |
|-----------|-------|
| Name | Stowaway |
| Original Name | Stowaway |
| Language | Go (Golang) |
| Version | go 1.13+ |
| Type | Multi-hop Proxy / Pivoting Tool |
| Open Source | Yes |
| Source URL | https://github.com/ph4ntonn/Stowaway |
| Author | ph4ntonn |
| License | MIT |

## Description

Stowaway is a multi-hop proxy tool written in Go, designed for penetration testers. It allows users to proxy external traffic through multiple nodes into internal networks, bypassing network access restrictions and constructing a tree-like node network.

## Components

| Component | File | Description |
|-----------|------|-------------|
| Admin | `admin/admin.go`, `admin/admin_win.go` | Controller interface used by penetration testers |
| Agent | `agent/agent.go` | Controlled node deployed on target systems |

## Features

- Multi-level SOCKS5 proxy (TCP/UDP, IPv4/IPv6)
- Remote shell access
- File upload/download
- Port forwarding (local/remote)
- SSH tunneling
- Port reuse (SO_REUSEPORT, SO_REUSEADDR, iptables)
- Node reconnection
- Traffic encryption (AES-256-GCM, TLS)
- Multiple protocol support (TCP, HTTP, WebSocket)
- Cross-platform (Linux, Windows, macOS, MIPS, ARM, FreeBSD)

## Network Behavior

| Feature | Details |
|---------|---------|
| Default Ports | User-defined via `-l` or `-c` |
| Protocols | TCP, HTTP, WebSocket |
| Encryption | AES-256-GCM, TLS |
| Proxy Support | SOCKS5, HTTP proxy |

## Process Behavior

| Feature | Details |
|---------|---------|
| Process Names | `stowaway_admin`, `stowaway_agent` |
| CLI Arguments | `-l`, `-c`, `-s`, `--socks5-proxy`, `--http-proxy`, `--reconnect`, `--up`, `--down`, `--tls-enable` |

## File Behavior

| Feature | Details |
|---------|---------|
| Output Files | None (in-memory operations) |
| Config Files | None (CLI-based configuration) |

## String Constants

### Protocol Identifiers
- `IAMADMINXD` - Admin UUID identifier
- `IAMNEWHERE` - Temporary UUID for new connections
- `THEREISNOROUTE` - Temporary route identifier

### Log Messages
- `[*] Starting admin node on port`
- `[*] Starting agent node`
- `[*] Waiting for new connection`
- `[*] Trying to connect node actively`

## Build System

- Build tool: Go (Makefile)
- Build flags: `-trimpath -ldflags "-w -s"`
- Output: Multiple platform binaries in `release/` directory

## Detection Vectors

1. **Binary Names**: `stowaway_admin`, `stowaway_agent`
2. **CLI Arguments**: `-s`, `--socks5-proxy`, `--http-proxy`, `--reconnect`, `--tls-enable`
3. **Protocol Strings**: UUID identifiers in network traffic
4. **Log Messages**: Startup and connection messages
5. **Import Paths**: `Stowaway/` module path in Go binaries
