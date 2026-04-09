## Rule Analysis: Windows_Trojan_Adaptix_b2cda978

**Author**: Elastic Security
**Target**: C++ Beacon Agent (implant binary)
**Pattern Count**: 5 (hex patterns)
**Reference Sample**: e7ae542fdade716484aca626cd52ee8120dea6fd9b8e49e40b5637de47ee4896

### Pattern 1: $a1
- **Hex**: `48 89 03 8B 45 EC 48 98 48 8D 14 C5 00 00 00 00 48 8B 45 20 48 01 D0 48 8B 00 48 85 C0 75 15 48 8B 45 E0 8B 40 10 85 C0 74 0A B8 00 00 00 00`
- **Type**: Instruction sequence (memory operations with conditionals)
- **Meaning**: Memory write, register operations, and conditional jumps
- **Source Cause**: Compiler-generated code for data structure manipulation
- **Source Location**: beacon_agent/src_beacon - various functions

### Pattern 2: $a2
- **Hex**: `48 89 45 D0 48 8B 4D 10 E8 4C 9F 00 00 89 C2 48 8D 85 C0 FB FF FF 49 89 D0 BA 00 00 00 00 48 89 C1 E8 D5 DE FF FF 48 83 7D D0 00 74 11 8B 55 E8 48 8B 45 D0 48 89 C1`
- **Type**: Instruction sequence with function calls
- **Meaning**: Stack variable storage and function calls (E8 = relative call)
- **Source Cause**: Function calls with relative addressing
- **Source Location**: beacon_agent/src_beacon - compiled function code

### Pattern 3: $a3
- **Hex**: `8B 53 54 48 89 C6 31 C0 48 39 C2 74 0B 8A 0C 07 88 0C 06 48 FF C0 EB F0 0F B7 43 14 0F B7 4B 06 48 8D 44 03 18 48 83 E9 01 72 2C 44 8B 40 0C 44 8B 48 14 31 D2 44 8B 50 10 49 01 F0 49 01 F9 49`
- **Type**: Memory copy/set loop with conditional branching
- **Meaning**: Loop structure with memory operations (copy or zeroing)
- **Source Cause**: Data initialization or memory operations
- **Source Location**: beacon_agent/src_beacon - initialization code

### Pattern 4: $a4
- **Hex**: `48 89 45 E0 48 83 7D E0 00 75 17 41 B8 00 00 00 00 BA 00 00 00 00 B9 05 01 00 00 E8 27 E8 FF FF EB 63 4C 8B 4D D0 4C 8D 85 00 FF FF FF 48 8B 55 D8 48 8B 45 20 48 8B 4D E0 48 89 4C 24 20 48 89`
- **Type**: Function with conditional and function calls
- **Meaning**: Error handling path with function calls
- **Source Cause**: Compiler-generated error handling code
- **Source Location**: beacon_agent/src_beacon - error handling

### Pattern 5: $a5
- **Hex**: `48 83 EC 10 89 4D 10 C7 ?? ?? ?? ?? ?? ?? 8B 45 10 89 45 F8 48 8D 45 FC 0F B6 00 3C DD 75 37 48 8D 45 F8 0F B6 55 13 88 10 48 8D 45 F8 48 83 C0 01 0F B6 55 12 88 10 48 8D 45 F8 48 83 C0 02`
- **Type**: Function prologue with XOR-like operations
- **Meaning**: Stack allocation and byte manipulation (possibly encryption/decryption)
- **Source Cause**: Cryptographic or encoding routines
- **Source Location**: beacon_agent/src_beacon - Crypt.cpp or Encoders.cpp

### Evasion Strategy

**Option A: Compiler Flags** (Priority 1)
- Feasible: Yes
- All patterns are compiler-generated instruction sequences
- Changing optimization flags will alter these patterns
- Flags to add/modify: optimization level, inline settings, code generation options

**Option B: Source Modification** (Priority 2)
- Feasible: Limited for hex patterns
- Pattern $a5 may relate to Crypt.cpp - could add instruction barriers or inline assembly
- Other patterns are pure compiler artifacts

**Option C: Link-time Optimization** (Priority 3)
- Feasible: Yes
- Add LTO flags to change final binary layout
- Flags: `-flto`, `-ffat-lto-objects`

### Selected Strategy

**Primary: Modify Makefile with additional compiler flags**

All patterns are compiler-generated. The key is to change code generation:

```makefile
# Modify EVASION_FLAGS in Makefile:
EVASION_FLAGS := -O2 \
                 -fomit-frame-pointer \
                 -fno-ident \
                 -ffunction-sections \
                 -fdata-sections \
                 -fmerge-all-constants \
                 -fno-inline-functions-small \
                 -fno-inline-functions-called-once \
                 -fno-tree-loop-vectorize \
                 -fno-tree-slp-vectorize
```

### Implementation

1. Add additional code generation flags to Makefile
2. Consider using `-Os` (size optimization) instead of `-O2` for different patterns
3. Optionally add `-fno-expensive-optimizations` for different instruction selection

### Verification Command
```bash
# After rebuild, check binary for hex patterns
xxd beacon.exe | grep -i "4889038b45ec"
xxd beacon.exe | grep -i "488945d0488b4d10"
```

### Status
- All patterns: Compiler-generated, evadable via compiler flag changes
