---
description: C2 framework evasion analysis and modification. Analyzes C2 source code, finds detection rules (YARA, Sigma, etc.), and directly modifies C2 source code to evade detection.
argument-hint: Required: path to C2 source (e.g., "/path/to/c2")
---

# C2 Evasion Command

Launch the c2-evasion-agent to analyze and modify C2 framework source code for detection evasion.

## Usage

```bash
/c2_evasion /path/to/c2/source
```

## What This Command Does

1. **Spawns c2-evasion-agent** as a subagent
2. **Identifies C2 framework** type and components
3. **Searches detection rules** (YARA, Sigma, Network) via `gh` CLI
4. **Modifies source code** based on found detection rules
5. **Documents all changes** in `./yara/<c2_name>/`

## Execution

Use the Agent tool to spawn the c2-evasion-agent:

```
Agent(
  subagent_type: "c2-evasion-agent",
  prompt: "Analyze and modify C2 source code at: <path>"
)
```
