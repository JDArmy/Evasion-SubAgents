---
name: research
description: This skill triggers when user wants to "search GitHub", "research techniques", "analyze code", "find methods", "update knowledge base", or research shellcode/evasion techniques.
version: 1.0.0
---

# Research Skill

Search, analyze, and document techniques from GitHub and other sources.

## GitHub Search Commands

```bash
# Search shellcode loaders
gh search repos "shellcode loader language:C stars:>20"
gh search repos "shellcode loader language:Rust stars:>10"

# Search evasion techniques
gh search repos "AMSI bypass C++"
gh search repos "syscall evasion"
gh search repos "API hashing"

# Search code patterns
gh search code "VirtualAlloc PAGE_EXECUTE_READWRITE" --language c
gh search code "NtAllocateVirtualMemory syscall" --language cpp
```

## Analysis Patterns

### Loading Components
- **Storage**: embedded, resource, remote_url, local_file, encrypted_resource
- **Allocation**: VirtualAlloc, HeapCreate, NtAllocateVirtualMemory, MappedFile
- **Execution**: function_pointer, CreateThread, callback, APC, Fiber

### Evasion Types
- `api_obfuscation` - API hashing, PEB walking, dynamic resolution
- `string_obfuscation` - XOR encryption, stack strings
- `memory_evasion` - Permission flipping, heap allocation
- `execution_evasion` - Direct/indirect syscall
- `anti_analysis` - Anti-debug, anti-VM, sandbox detection
- `amsi_etw_bypass` - AMSI/ETW patching
- `unhooking` - NTDLL unhooking

## Detection Patterns

```c
// API Hashing
DWORD hash = 0x35;
for (i = 0; i < len; i++) hash += str[i] + (hash << 1);
// + PE export table parsing

// Syscall
mov r10, rcx
mov eax, SSN
syscall

// Anti-Debug
IsDebuggerPresent()
CheckRemoteDebuggerPresent()
NtQueryInformationProcess()

// String XOR
for (i = 0; i < len; i++) data[i] ^= KEY;
```

## Knowledge Base Commands

```bash
# Add evasion technique
python lib/knowledge_manager.py add-evasion \
  --name "Technique Name" \
  --type "api_obfuscation" \
  --description "..." \
  --code-template "..." \
  --apis "API1,API2" \
  --complexity "medium"

# Add loader component
python lib/knowledge_manager.py add-component \
  --type "executors" \
  --name "Component Name" \
  --description "..." \
  --apis "API1,API2"
```

## Output Format

After analysis, output:
1. Technique name and type
2. Brief description
3. Complexity (simple/medium/complex)
4. Knowledge base ID
