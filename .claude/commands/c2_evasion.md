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
3. **Per-rule analysis** - Creates separate analysis for EACH rule with evasion strategies
4. **Proactively searches** for sensitive strings (even if YARA rules are hex-only)
5. **Modifies source code** - Compiler flags FIRST, then source changes
6. **Documents all changes** in `./yara/<c2_name>/`

## CRITICAL: Per-Rule Analysis

For EACH YARA/Sigma rule, create `./yara/<c2_name>/rule_analysis/<rule_name>.md`:
- Parse all patterns ($a1, $s1, hex, regex)
- Identify pattern source in code
- Develop evasion strategies with priority:
  1. **Compiler flags** (LOWEST effort, HIGHEST impact)
  2. **Build configuration** changes
  3. **Source code** modifications
  4. **Function/struct refactoring** (last resort)

## Priority Framework

| Priority | Component | Action |
|----------|-----------|--------|
| 1 (HIGHEST) | Implant/Beacon/Agent | MODIFY |
| 2 (HIGH) | Network Exposure | MODIFY |
| 3 (SKIP) | Internal Strings | SKIP |

## Evasion Priority

| Strategy | Priority | Effort |
|----------|----------|--------|
| Compiler flags | 1 (BEST) | Low |
| Build config | 2 | Medium |
| Source changes | 3 | Medium |
| Refactoring | 4 | High |

## Output

```
./yara/<c2_name>/
├── yara_rules/              # Found YARA rules
├── sigma_rules/             # Found Sigma rules
├── network_rules/           # Found network rules
├── rule_analysis/           # Per-rule analysis files
│   ├── Windows_Trojan_X.md
│   └── ...
├── binary_assets/
│   └── analysis.md
├── hex_analysis.md
└── modifications_summary.md
```

## Security

- **ONLY** modify code in user-provided path
- **NEVER** run or test modified binaries
- **NEVER skip a rule** - every rule must have analysis
- **ALWAYS try compiler flags first**
- Document ALL changes

## Agent

Spawns `c2-evasion-agent` subagent for comprehensive analysis and modification.

See `c2_evasion` skill for detailed workflow.
