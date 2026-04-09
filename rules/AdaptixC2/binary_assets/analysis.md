# Binary Assets Analysis for AdaptixC2

## Located Binary Assets

### 1. Stub Files (beacon_agent)
**Path:** `AdaptixServer/extenders/beacon_agent/src_beacon/files/`
**Files:**
- `stub.x64.bin`
- `stub.x86.bin`

**Purpose:** These are shellcode stubs used for beacon injection/loading
**Detection Risk:** High - Static shellcode can be signatured

**Recommendation:**
- Encrypt stub files at rest
- Generate stubs dynamically at compile time
- Use polymorphic shellcode generation

### 2. Configuration Template
**Path:** `AdaptixServer/extenders/beacon_agent/src_beacon/files/config.tpl`
**Purpose:** Template for beacon configuration

### 3. Hash Calculation Script
**Path:** `AdaptixServer/extenders/beacon_agent/src_beacon/files/hashes.py`
**Purpose:** Calculate hashes for API hashing

## Embedded Resources in Source

### Go Agent (gopher_agent)
**Potential embedded strings:**
- Profile configuration is passed as encrypted data
- BOF loader references to "coffer.Load" (detected by YARA)

### C++ Beacon (beacon_agent)
**Potential embedded strings:**
- API names (hashed)
- Error strings (debug builds)
- Profile parameter names

## Detection Mitigation Strategies

### For Stub Files
1. **Compile-time generation**: Generate stub at build time with random variations
2. **Encryption**: XOR encrypt stub file, decrypt at runtime
3. **Polymorphism**: Use metamorphic engine to regenerate stub

### For Configuration
1. **Dynamic configuration**: Generate config structure at runtime
2. **Encryption**: Encrypt all configuration data
3. **Obfuscation**: Split config across multiple locations

### For Strings
1. **String encryption**: Encrypt all strings at compile time
2. **API hashing**: Already implemented, verify coverage
3. **Stack strings**: Use compile-time string encryption macros

## Files to Review

1. `beacon_agent/src_beacon/files/stub.x64.bin` - Needs polymorphism
2. `beacon_agent/src_beacon/files/stub.x86.bin` - Needs polymorphism
3. `ConnectorHTTP.cpp` - wininet.dll string construction
4. `ApiLoader.cpp` - API hashing implementation
