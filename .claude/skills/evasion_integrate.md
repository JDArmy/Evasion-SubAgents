---
name: evasion_integrate
description: This skill triggers when user wants to "add evasion", "integrate evasion", "bypass detection", "apply technique", "二开", or modify an existing loader with evasion techniques.
version: 1.0.0
---

# Evasion Integrate Skill

Integrate evasion techniques into existing shellcode loaders.

## Prerequisites

User must provide:
- Path to existing loader source code
- (Optional) Specific techniques to apply
- (Optional) Target complexity level

## Workflow

### Step 1: Read User Loader

```bash
# Read the provided loader code
cat /path/to/loader.c
```

### Step 2: Query Evasion Techniques

```bash
# List all evasion techniques
python lib/knowledge_manager.py list-evasion

# Filter by type
python lib/knowledge_manager.py list-evasion --type api_obfuscation
python lib/knowledge_manager.py list-evasion --type string_obfuscation
python lib/knowledge_manager.py list-evasion --type anti_analysis

# Get specific technique
python lib/knowledge_manager.py get-evasion --id T001
```

### Step 3: Analyze Compatibility

Check which techniques are compatible with the loader:
- API obfuscation: Works with all loaders
- String obfuscation: Requires strings to hide
- Memory evasion: Depends on allocation method
- Execution evasion: Depends on execution method
- Anti-analysis: Can be added to any loader

### Step 4: Integrate Techniques

Apply techniques to the loader code:

#### API Hashing

```c
// Before
HMODULE hNtdll = LoadLibraryA("ntdll.dll");
LPVOID func = GetProcAddress(hNtdll, "NtAllocateVirtualMemory");

// After
DWORD hash = 0x...; // Pre-computed hash
LPVOID func = GetAPIByHash(hash);
```

#### String XOR

```c
// Before
char* dllName = "kernel32.dll";

// After
char dllName[] = { 0x..., 0x... }; // XOR encrypted
void xor_decrypt(char* data, size_t len) {
    for (size_t i = 0; i < len; i++) data[i] ^= KEY;
}
xor_decrypt(dllName, sizeof(dllName));
```

#### Permission Flipping

```c
// Before
LPVOID addr = VirtualAlloc(NULL, size, MEM_COMMIT, PAGE_EXECUTE_READWRITE);

// After
LPVOID addr = VirtualAlloc(NULL, size, MEM_COMMIT, PAGE_READWRITE);
memcpy(addr, shellcode, size);
VirtualProtect(addr, size, PAGE_EXECUTE_READ, &oldProtect);
```

#### Syscall

```c
// Before
NtAllocateVirtualMemory(...);

// After
DWORD ssn = GetSSN("NtAllocateVirtualMemory");
ExecuteSyscall(ssn, ...);
```

### Step 5: Compile and Test

```bash
# Compile modified loader
x86_64-w64-mingw32-gcc -o output/evasion_loader.exe output/evasion_loader.c

# Test with calc.bin
./output/evasion_loader.exe
tasklist | findstr calc.exe
taskkill /F /IM calc.exe
```

### Step 6: Report Changes

Output a summary:
- Original loader: `/path/to/loader.c`
- Techniques applied: [list]
- APIs modified: [list]
- New detection risk: low/medium/high
- Compilation: success/fail
- Test result: pass/fail

## Technique Categories

| Type | Purpose | Complexity |
|------|---------|------------|
| api_obfuscation | Hide API imports | medium |
| string_obfuscation | Hide strings | simple |
| memory_evasion | Avoid RWX pages | simple |
| execution_evasion | Bypass hooks | complex |
| anti_analysis | Detect debug/VM | medium |
| amsi_etw_bypass | Disable scanning | medium |
| unhooking | Restore hooked DLLs | complex |

## Important Rules

1. ONLY modify user-provided code
2. ONLY use techniques from knowledge base
3. Test with `samples/calc.bin` only
4. Report all changes made
5. Indicate detection risk impact
