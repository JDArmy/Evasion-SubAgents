---
description: Generate shellcode loaders by combining components from the loader knowledge base
argument-hint: Optional: count (e.g., "5" for batch) or filters (e.g., "--executor callback")
---

# Loader Generate Command

Generate shellcode loaders from the loader knowledge base.

## Usage

```bash
/loader_generate                      # Single random loader
/loader_generate 5                    # Batch generate 5 loaders
/loader_generate --executor callback  # Specific executor
/loader_generate --allocator NtAllocateVirtualMemory  # Specific allocator
/loader_generate --complexity medium  # Filter by complexity
```

## What This Command Does

1. Queries loader component library from `loader_techniques.json`
2. Checks `scenarios.json` to avoid duplicate combinations
3. Generates random (or specified) component combination
4. Writes C code to `output/`
5. Compiles with MinGW
6. Tests with `samples/calc.bin`
7. Records result in `scenarios.json`

## Components

| Category | Options |
|----------|---------|
| Storage | embedded, resource, remote_url, encrypted_resource |
| Allocator | VirtualAlloc, HeapCreate, NtAllocateVirtualMemory, MappedFile |
| Copier | memcpy, RtlMoveMemory, loop_copy |
| Executor | function_pointer, CreateThread, callback, APC, Fiber |

## Output

- Generated source code: `output/loader_<id>.c`
- Compiled executable: `output/loader_<id>.exe`
- Test result: pass/fail
- Scenario ID in knowledge base

## Example

```bash
/loader_generate 3
# Output:
# Generated 3 loaders:
# 1. loader_001: embedded + VirtualAlloc + callback - PASSED
# 2. loader_002: embedded + HeapCreate + APC - PASSED
# 3. loader_003: embedded + NtAllocateVirtualMemory + Fiber - FAILED (compile error)
```

See `loader_generate` skill for detailed workflow and templates.
