## Hex Pattern Analysis for AdaptixC2

### Elastic Security Rules (Windows_Trojan_Adaptix)

#### Rule: Windows_Trojan_Adaptix_2779784c

**Pattern $a1:**
```
48 81 EC A8 01 00 00 48 8B 84 24 C0 01 00 00 48 C7 00 00 00 00 00 ...
```
- **Type:** Function prologue with large stack allocation
- **Meaning:** `sub rsp, 0x1A8` (424 bytes) + memory operations
- **Source Cause:** Function with large local variables or struct initialization
- **Evasion Method:** Compiler flags change stack allocation and instruction ordering

**Pattern $a2:**
```
48 83 EC 58 48 8B 4C 24 70 E8 ?? ?? ?? ?? 89 44 24 38 ...
```
- **Type:** Function prologue with moderate stack allocation
- **Meaning:** `sub rsp, 0x58` (88 bytes) + function calls
- **Source Cause:** Medium-sized function with local variables
- **Evasion Method:** Compiler flags change optimization and stack layout

#### Rule: Windows_Trojan_Adaptix_b2cda978

**Pattern $a1:**
```
48 89 03 8B 45 EC 48 98 48 8D 14 C5 00 00 00 00 ...
```
- **Type:** Memory operations with conditional logic
- **Evasion Method:** Compiler flags

**Pattern $a2:**
```
48 89 45 D0 48 8B 4D 10 E8 4C 9F 00 00 ...
```
- **Type:** Stack variable storage with function calls
- **Evasion Method:** Compiler flags

**Pattern $a3:**
```
8B 53 54 48 89 C6 31 C0 48 39 C2 74 0B ...
```
- **Type:** Memory copy/set loop
- **Evasion Method:** Compiler flags

**Pattern $a4:**
```
48 89 45 E0 48 83 7D E0 00 75 17 ...
```
- **Type:** Error handling path
- **Evasion Method:** Compiler flags

**Pattern $a5:**
```
48 83 EC 10 89 4D 10 C7 ?? ?? ?? ?? ?? ?? ...
```
- **Type:** XOR-like operations (possibly encryption)
- **Evasion Method:** Compiler flags may help; source refactoring may be needed

### CAPE Rule (AdaptixBeacon)

#### Config Patterns ($conf_1 to $conf_5)

These patterns detect config initialization code. They are compiler-generated and can be evaded with compiler flag changes.

#### Wininet Patterns ($wininet_1, $wininet_2)

```
B9 77 00 00 00  (mov ecx, 0x77 = 'w')
B9 69 00 00 00  (mov ecx, 0x69 = 'i')
B9 6E 00 00 00  (mov ecx, 0x6E = 'n')
B9 65 00 00 00  (mov ecx, 0x65 = 'e')
```

**Analysis:**
- These patterns detect stack string construction for "wininet.dll"
- The beacon already uses obfuscation via `HdChrA()` function (ConnectorHTTP.cpp:62-74)
- The current code uses character-by-character construction with a macro

**Current Code (already obfuscated):**
```cpp
CHAR wininet_c[12];
wininet_c[0]  = HdChrA('w');
wininet_c[1]  = HdChrA('i');
wininet_c[2]  = HdChrA('n');
// ... etc
```

**Status:** Already partially obfuscated. The YARA patterns may still match due to compiler optimization producing similar byte sequences.

---

## Makefile Changes Applied

### Beacon Makefile (Before):
```makefile
EVASION_FLAGS := -O2 \
                 -fomit-frame-pointer \
                 -fno-ident \
                 -ffunction-sections \
                 -fdata-sections \
                 -fmerge-all-constants

OPTIMIZATION_FLAGS := -fno-exceptions \
                     -fno-unwind-tables \
                     -fno-asynchronous-unwind-tables
```

### Beacon Makefile (After):
```makefile
EVASION_FLAGS := -O2 \
                 -fomit-frame-pointer \
                 -fno-ident \
                 -ffunction-sections \
                 -fdata-sections \
                 -fmerge-all-constants \
                 -fno-inline-functions-small \
                 -fno-inline-functions-called-once \
                 -fno-expensive-optimizations \
                 -fno-tree-loop-vectorize \
                 -fno-tree-slp-vectorize \
                 -fno-tree-vect-loop-version \
                 -fno-unwind-tables \
                 -fno-asynchronous-unwind-tables

OPTIMIZATION_FLAGS := -fno-exceptions
```

### Expected Hex Pattern Changes:

| Flag | Effect |
|------|--------|
| `-fno-inline-functions-small` | Prevents inlining of small functions, changes call patterns |
| `-fno-inline-functions-called-once` | Changes function call structure |
| `-fno-expensive-optimizations` | Uses simpler instruction sequences |
| `-fno-tree-loop-vectorize` | Changes loop code generation |
| `-fno-tree-slp-vectorize` | Changes memory operation patterns |
| `-fno-tree-vect-loop-version` | Alters loop prologue/epilogue |
