---
name: c2_evasion
description: Analyze C2 framework source code, find detection rules (YARA, Sigma, Snort, etc.), and directly modify source code to evade detection. Use this skill when the user wants to "analyze C2", "C2 evasion", "modify C2", "bypass C2 detection", "YARA analysis", or work with C2 framework detection evasion. Triggers on phrases containing C2, beacon, implant, YARA, detection bypass, evasion modification.
version: 6.0.0
---

# C2 Evasion Skill

Analyze C2 frameworks and modify source code to evade detection for authorized security testing.

## Authorization Context

**AUTHORIZED USE CASE: Defensive Security Research**

This skill is used for:
- Understanding detection signatures to improve security products
- Red team assessments with explicit authorization
- Security product testing and evaluation

## When to Use This Skill

- User provides a C2 framework path and asks for evasion analysis
- User mentions YARA, Sigma, or detection rules
- User says "bypass detection", "evade signature", "modify C2"
- User asks to analyze implants, beacons, or agents

## Core Principle

**Rule-Driven Modification**: All modifications are driven by detection rules found in Phase 2.
Do NOT make random changes. Only modify what detection rules actually target.

## Priority Framework

| Priority | Component | Why | Action |
|----------|-----------|-----|--------|
| 1 (HIGHEST) | Implant/Beacon/Agent | Deployed to targets, scanned by AV/EDR/YARA | MODIFY |
| 2 (HIGH) | Network Exposure | Visible to network scanners | MODIFY |
| 3 (SKIP) | Internal Strings | Not exposed externally | SKIP |

## Workflow

### Phase 1: Identify C2 Components

```bash
# Explore the target path
ls -la <path>
find <path> -name "*.c" -o -name "*.go" -o -name "*.rs" -o -name "*.py"

# Identify implant/agent vs server
# Look for: agent/, implant/, beacon/, client/ directories
# Check README or docs for architecture
```

### Phase 2: Detection Research

Search for detection rules using `gh` CLI:

```bash
# Search YARA rules
gh search code "<c2_name> yara" --extension yar
gh search code "<c2_name> rule" --extension yar

# Search Sigma rules
gh search code "<c2_name> sigma" --extension yml

# Search network rules
gh search code "<c2_name> snort" --extension rules
```

Save all found rules to `./yara/<c2_name>/`:
```
./yara/<c2_name>/
├── yara_rules/
│   └── *.yar
├── sigma_rules/
│   └── *.yml
├── network_rules/
│   └── *.rules
└── detection_analysis.md
```

### Phase 3: Rule-to-Source Mapping

For EACH detection rule, map patterns to source files:

```bash
# For each string pattern in YARA ($s1, $s2, etc.)
grep -rn "pattern_string" <path>
grep -rn "hex_pattern" <path>

# Example
grep -rn "BeaconOutput" ./c2-source/
grep -rn "X-C2-Header" ./c2-source/
```

Create a mapping table:

| Pattern | Source File | Line | Status |
|---------|-------------|------|--------|
| "BeaconOutput" | agent/comm.c:45 | ✓ found |
| { 4D 5A 90 } | N/A (PE header) | ✗ skip |

### Phase 4: Targeted Modification

For each FOUND pattern, apply modifications:

**String Patterns:**
```c
// Before
char* header = "BeaconOutput";

// After
char header[] = { 'B'^0x41, 'e'^0x41, ... }; // XOR encrypted
```

**Network Headers:**
```go
// Before
const C2Header = "X-C2-Header"

// After
var C2Header = strings.Join([]string{"X-", "C2", "-Header"}, "")
```

**Process Names (Sigma):**
```yaml
# Detection: Image|endswith: 'agent.exe'
# Source: Find process name constant
```
```c
// Before
char* processName = "agent.exe";
// After
char* processName = "upd4ter.exe";
```

### Phase 5: Verification

Re-run pattern matching to verify removal:

```bash
# Verify each pattern was removed
grep -rn "BeaconOutput" <path>  # Should return nothing
```

### Phase 6: Documentation

Create `modifications_summary.md`:

```markdown
# C2 Evasion Report

## C2 Framework: <name>
## Rules Analyzed: X YARA, Y Sigma, Z Network

## Modifications Applied

| Pattern | File | Modification | Status |
|---------|------|--------------|--------|
| "BeaconOutput" | comm.c:45 | XOR string encryption | ✓ Evaded |

## Skipped Patterns

| Pattern | Reason |
|---------|--------|
| { 4D 5A 90 } | Standard PE header, cannot modify |

## Detection Risk: Low/Medium/High
```

## Pattern Handling

| Pattern Type | Example | Handling |
|--------------|---------|----------|
| String | `$s1 = "BeaconOutput"` | Grep source, locate file:line, modify |
| Hex (magic) | `$hex = { 4D 5A 90 }` | Skip if standard PE |
| Hex (function) | `$hex = { B8 ?? ?? 00 }` | Identify function, consider modification |
| Sigma | `Image\|endswith: 'agent.exe'` | Locate process name in source/config |
| Network | `content: "X-C2-Header"` | Locate header in server config |

## Important Rules

1. ONLY modify code in the user-provided path
2. ONLY modify patterns found in detection rules
3. ALWAYS verify modification success
4. NEVER test/run the modified binaries
5. Document ALL changes and skipped items

## Output Format

After completion, provide:
1. Detection rules found (count by type)
2. Patterns mapped to source (found/skip)
3. Modifications applied (file, line, change)
4. Verification results
5. Risk assessment
