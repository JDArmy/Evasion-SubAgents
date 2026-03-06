---
description: Search GitHub for shellcode loader and evasion techniques, analyze and add to knowledge base
argument-hint: Optional search query (e.g., "API hashing", "syscall")
---

# Research Command

Search GitHub for techniques and update the knowledge base.

## Usage

```bash
/research                        # Interactive mode
/research "shellcode loader"     # Search with query
/research "syscall evasion C++"  # Specific technique
```

## What This Command Does

1. Searches GitHub using `gh` CLI
2. Analyzes source code patterns
3. Extracts techniques (loading methods, evasion tricks)
4. Adds to knowledge base

## Output

- Techniques discovered
- Knowledge base IDs added
- Summary of findings

## Security

- **NEVER** compile or execute external code
- **NEVER** use external shellcode
- **ONLY** analyze patterns

See `research` skill for detailed patterns and commands.
