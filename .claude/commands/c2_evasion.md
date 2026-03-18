---
description: Analyze C2 framework source code, find detection rules (YARA, Sigma, etc.), and modify source to evade detection. Triggers on "C2 evasion", "analyze C2", "YARA", "modify C2", "bypass detection", "C2免杀".
argument-hint: Required: path to C2 source (e.g., "/path/to/c2")
---

# C2 Evasion Command

Launch the c2-evasion-agent to analyze and modify C2 framework source code.

## Usage

```bash
/c2_evasion /path/to/c2/source
/c2_evasion ./mythic-agent
/c2_evasion ./sliver-client
```

## What This Command Does

1. **Identifies C2 framework** type and components (implant/server)
2. **Searches detection rules** (YARA, Sigma, Network) via `gh` CLI
3. **Maps patterns to source** files and line numbers
4. **Modifies source code** based on detection rules
5. **Documents all changes** in `./yara/<c2_name>/`

## Priority Framework

| Priority | Component | Action |
|----------|-----------|--------|
| 1 (HIGHEST) | Implant/Beacon/Agent | MODIFY |
| 2 (HIGH) | Network Exposure | MODIFY |
| 3 (SKIP) | Internal Strings | SKIP |

## Output

```
./yara/<c2_name>/
├── yara_rules/          # Found YARA rules
├── sigma_rules/         # Found Sigma rules
├── network_rules/       # Found network rules
├── detection_analysis.md
└── modifications_summary.md
```

## Security

- **ONLY** modify code in user-provided path
- **NEVER** run or test modified binaries
- Document ALL changes

## Agent

Spawns `c2-evasion-agent` subagent for comprehensive analysis and modification.

See `c2_evasion` skill for detailed workflow.
