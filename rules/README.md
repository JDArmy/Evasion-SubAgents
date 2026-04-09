# Rules Directory

This directory stores detection rules and analysis results for security tools.

## Directory Structure

```
rules/
├── {tool_name}/                    # One directory per tool
│   ├── yara/                       # YARA rule files
│   │   ├── source1_rule1.yar
│   │   └── source2_rule2.yar
│   ├── sigma/                      # Sigma rule files
│   │   └── rule1.yml
│   ├── network/                    # Network detection rules
│   │   └── rule1.rules
│   ├── other/                      # Other detection formats
│   │   └── rule1.json
│   ├── rule_analysis/              # Per-rule analysis
│   │   ├── rule1.md
│   │   └── rule2.md
│   ├── tool_profile.md             # Tool analysis and profile
│   ├── behavior_analysis.md        # Behavioral signatures
│   ├── rule_inventory.md           # Inventory of all rules found
│   └── modifications_summary.md    # Final evasion report
```

## Purpose

Each tool directory contains:

1. **Detection Rules** (`yara/`, `sigma/`, `network/`, `other/`)
   - Original detection rules found for the tool
   - Preserved with source metadata

2. **Tool Profile** (`tool_profile.md`)
   - Tool name, language, type
   - Core features and functionality
   - Open source status and URL

3. **Behavior Analysis** (`behavior_analysis.md`)
   - Detection categories (process_creation, network_connection, etc.)
   - Indicators per category (Image, CommandLine, ports, etc.)
   - Risk assessment

4. **Rule Inventory** (`rule_inventory.md`)
   - Summary of all rules found
   - Sources and authors
   - Pattern counts

5. **Rule Analysis** (`rule_analysis/`)
   - Per-rule detailed analysis
   - Pattern sources in code
   - Evasion strategies

6. **Modifications Summary** (`modifications_summary.md`)
   - All modifications applied
   - Unevadable items and reasons
   - Detection risk assessment

## Supported Detection Rule Types

| Type | Extension | Source |
|------|-----------|--------|
| YARA | `.yar` | Yara-Rules, Neo23x0/signature-base, Elastic, etc. |
| Sigma | `.yml` | SigmaHQ/sigma |
| Network | `.rules` | Snort, Suricata, Zeek |
| Other | `.json`, `.txt` | Custom formats |

## Usage

### C2 Evasion

The `c2_evasion` skill creates directories for C2 frameworks:

```bash
/c2_evasion ./adaptix-c2
# Creates: rules/AdaptixC2/
```

### Tools Evasion

The `tools_evasion` skill creates directories for penetration testing tools:

```bash
/tools_evasion ./crackmapexec
# Creates: rules/crackmapexec/
```

## Verified Rule Sources

### YARA Repositories
- Yara-Rules/rules
- Neo23x0/signature-base
- elastic/protections-artifacts
- advanced-threat-research/Yara-Rules
- stratosphereips/yara-rules
- InQuest/awesome-yara

### Sigma Repositories
- SigmaHQ/sigma (3000+ rules)
- mdecrevoisier/SIGMA-detection-rules
- P4T12ICK/Sigma-Rule-Repository

## License

For authorized defensive security research only.
