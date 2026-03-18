---
description: Generate shellcode loaders by combining components from knowledge base. Creates working C/C++/Rust loaders using documented techniques. Triggers on "generate loader", "create loader", "shellcode loader", "生成loader".
argument-hint: Optional: count (e.g., "5" for batch) or filters (e.g., "--executor callback")
---

# Loader Generate Command

Launch the loadergen-agent to generate shellcode loaders from the knowledge base.

## Usage

```bash
/loader_generate                      # Single random loader
/loader_generate 5                    # Batch generate 5 loaders
/loader_generate --executor callback  # Specific executor
/loader_generate --allocator NtAllocateVirtualMemory
/loader_generate --complexity medium  # Filter by complexity
/loader_generate --language rust      # Rust loader
```

## What This Command Does

1. **Queries components** from `loader_techniques.json`
2. **Checks duplicates** in `scenarios.json`
3. **Generates code** combining random/specified components
4. **Compiles** with MinGW (C/C++) or Cargo (Rust)
5. **Records result** in knowledge base

## Components

| Category | Options |
|----------|---------|
| Storage | embedded, resource, remote_url, encrypted_resource |
| Allocator | VirtualAlloc, HeapCreate, NtAllocateVirtualMemory |
| Copier | memcpy, RtlMoveMemory, loop_copy |
| Executor | function_pointer, CreateThread, callback, APC, Fiber |

## Output

- Generated source: `output/loader_<id>.c` (or `.cpp`, `.rs`)
- Compiled executable: `output/loader_<id>.exe`
- Knowledge base scenario ID

## Security

- **ONLY** use `samples/calc.bin` for testing
- **NEVER** run generated executables
- Compilation success is sufficient

## Agent

Spawns `loadergen-agent` subagent for code generation.

See `loader_generate` skill for detailed templates and workflow.
