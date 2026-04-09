## Rule Analysis: Windows_Trojan_Adaptix_2779784c

**Author**: Elastic Security
**Target**: C++ Beacon Agent (implant binary)
**Pattern Count**: 2 (hex patterns)
**Reference Sample**: 9bbc6a711cd5ba3a1e7d8303e8c72166479a1a189ad382e2b837b1bf64c51a9d

### Pattern 1: $a1
- **Hex**: `48 81 EC A8 01 00 00 48 8B 84 24 C0 01 00 00 48 C7 00 00 00 00 00 48 8B 84 24 C0 01 00 00 48 C7 40 08 00 00 00 00 48 8B 84 24 C0 01 00 00 48 C7`
- **Type**: Function prologue with stack allocation
- **Meaning**: `sub rsp, 0x1A8` (424 bytes stack allocation) followed by zeroing memory
- **Source Cause**: Large function with significant local variables or struct initialization
- **Source Location**: beacon_agent/src_beacon - C++ beacon code compiled with MinGW

### Pattern 2: $a2
- **Hex**: `48 83 EC 58 48 8B 4C 24 70 E8 ?? ?? ?? ?? 89 44 24 38 C7 44 24 34 00 00 00 00 48 8D 54 24 34 48 8B 4C 24 70 E8 ?? ?? ?? ?? 48 89 44 24 40 48 8B 4C 24 70 E8 ?? ?? ?? ?? 66 89 44 24 30`
- **Type**: Function prologue with stack allocation
- **Meaning**: `sub rsp, 0x58` (88 bytes stack allocation) with function calls
- **Source Cause**: Function with moderate local variables
- **Source Location**: beacon_agent/src_beacon - C++ beacon code

### Evasion Strategy

**Option A: Compiler Flags** (Priority 1)
- Feasible: Yes
- Flags to add: The Makefile already has evasion flags (`-fomit-frame-pointer`, `-O2`, etc.)
- Expected change: Different optimization levels change function prologue patterns
- Note: The current Makefile already includes evasion-focused flags

**Option B: Source Modification** (Priority 2)
- Feasible: Limited - hex patterns are compiler-generated
- Files to modify: Multiple beacon source files
- Changes: Restructure functions, reduce stack usage, use heap allocation

**Option C: Additional Compiler Flags** (Priority 3)
- Feasible: Yes
- Flags to add: `-fno-inline-functions`, `-fno-inline`, different optimization levels
- These can change code generation patterns

### Selected Strategy

**Primary: Modify Makefile compiler flags to change code generation**

The current Makefile already has some evasion flags. Additional flags can further change the compiled patterns:

```makefile
# Add to EVASION_FLAGS:
-fno-inline-functions-small
-fno-inline-functions-called-once
-mbranch-cost=1
-fno-expensive-optimizations
-fno-tree-loop-vectorize
-fno-tree-slp-vectorize
-fno-tree-vect-loop-version
```

### Implementation

1. Modify `beacon_agent/src_beacon/Makefile` to add additional evasion flags
2. These flags change instruction ordering and stack allocation patterns
3. The hex patterns will change after recompilation

### Verification Command
```bash
# After rebuild, check binary for hex patterns
xxd beacon.exe | grep -i "4881eca8 01"
xxd beacon.exe | grep -i "4883ec58"
```

### Status
- Pattern $a1: Can be evaded via compiler flags
- Pattern $a2: Can be evaded via compiler flags
