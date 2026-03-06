---
description: Integrate evasion techniques into an existing shellcode loader
argument-hint: Required: path to loader source (e.g., "/path/to/loader.c") + optional technique filters
---

# Evasion Integrate Command

Add evasion techniques to an existing shellcode loader.

## Usage

```bash
/evasion_integrate /path/to/loader.c                           # Auto-select techniques
/evasion_integrate /path/to/loader.c --type api_obfuscation    # Specific type
/evasion_integrate /path/to/loader.c --type string_obfuscation,anti_analysis  # Multiple types
/evasion_integrate /path/to/loader.c --complexity simple       # Filter by complexity
/evasion_integrate /path/to/loader.c --technique T001,T003     # Specific technique IDs
```

## What This Command Does

1. Reads the user-provided loader source code
2. Queries evasion techniques from `evasion_techniques.json`
3. Analyzes compatibility with the loader
4. Integrates selected techniques into the code
5. Compiles modified loader
6. Tests with `samples/calc.bin`
7. Reports all changes made

## Evasion Types

| Type | Description | Impact |
|------|-------------|--------|
| api_obfuscation | API hashing, PEB walking | Hides imports |
| string_obfuscation | XOR encryption, stack strings | Hides strings |
| memory_evasion | Permission flipping (RW→RX) | Avoids RWX pages |
| execution_evasion | Direct/indirect syscall | Bypasses hooks |
| anti_analysis | Anti-debug, anti-VM | Detects analysis |
| amsi_etw_bypass | AMSI/ETW patching | Disables scanning |
| unhooking | NTDLL unhooking | Restores hooks |

## Output

- Modified source code: `output/evasion_<id>.c`
- Compiled executable: `output/evasion_<id>.exe`
- Changes summary:
  - Techniques applied
  - APIs modified
  - Detection risk assessment
- Test result: pass/fail

## Example

```bash
/evasion_integrate ./myloader.c --type api_obfuscation,string_obfuscation
# Output:
# Applied techniques:
# - API Hashing (T001): Obfuscated LoadLibraryA, VirtualAlloc
# - String XOR (T005): Encrypted "kernel32.dll", "ntdll.dll"
# Detection risk: medium → low
# Compilation: success
# Test: PASSED (calc.exe executed)
```

## Requirements

- User MUST provide a valid loader source file
- File MUST be C/C++ source code
- Loader SHOULD compile successfully before modification

See `evasion_integrate` skill for detailed integration patterns.
