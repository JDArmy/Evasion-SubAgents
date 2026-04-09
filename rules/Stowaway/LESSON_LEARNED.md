# Evasion Lesson Learned: Fixed-Length Protocol Fields

## Incident Date
2026-04-09

## Tool
Stowaway (Go-based multi-hop proxy)

## Problem Description

During source code modification to evade detection, we changed protocol identifier constants:

**Original values:**
```go
const ADMIN_UUID = "IAMADMINXD"      // 10 characters
const TEMP_UUID = "IAMNEWHERE"        // 10 characters
const TEMP_ROUTE = "THEREISNOROUTE"   // 14 characters
```

**Modified values (WRONG):**
```go
const ADMIN_UUID = "NODE-CTRL-01"     // 12 characters ❌
const TEMP_UUID = "NODE-JOIN-00"      // 12 characters ❌
const TEMP_ROUTE = "EMPTY-ROUTE-00"   // 15 characters ❌
```

## Root Cause

The protocol uses **fixed-length fields** in message headers. The code reads exactly 10 bytes for UUID fields:

```go
// protocol/raw.go
senderBuf := make([]byte, 10)      // Fixed 10 bytes for UUID
accepterBuf := make([]byte, 10)    // Fixed 10 bytes for UUID
```

Changing the UUID length from 10 to 12 characters caused:
1. Message header parsing to read wrong bytes
2. Protocol deserialization failure
3. Connection established but immediately dropped with "connection reset by peer"

## Symptom

- Connection was established successfully
- Authentication passed
- But control panel showed no response
- Error message: `read tcp: connection reset by peer`

## Correct Fix

```go
const ADMIN_UUID = "CTRL-00001"     // 10 characters ✅
const TEMP_UUID = "JOIN-00001"       // 10 characters ✅
const TEMP_ROUTE = "NOROUTE00000"    // 14 characters ✅
```

## Key Lessons

### 1. Always Check Fixed-Length Protocol Fields

Before modifying any string constants in networked applications:
1. Search for `make([]byte, N)` where N is a fixed number
2. Search for hardcoded slice lengths like `[:10]`, `[:14]`
3. Check if string constants are used in binary protocols

```bash
# Find potential fixed-length reads
grep -rn "make(\[\]byte" --include="*.go"
grep -rn "\[:10\]" --include="*.go"
```

### 2. Common Fixed-Length Patterns

| Pattern | Description |
|---------|-------------|
| UUID fields | Often fixed 10-36 bytes |
| Message types | Often fixed 1-4 bytes |
| Length prefixes | Often 2-4 bytes |
| Magic bytes | Often 4-8 bytes |
| Route/Path fields | May have fixed max length |

### 3. Verification Checklist

After modifying protocol-related constants:

- [ ] Count character length of new value
- [ ] Compare with original value length
- [ ] Search for hardcoded byte lengths in code
- [ ] Test connection establishment
- [ ] Test message exchange
- [ ] Check both client and server side

### 4. Code Review Pattern

```go
// DANGEROUS - Length changed
const ADMIN_UUID = "NODE-CTRL-01"  // Was 10, now 12

// Safe modification approach:
// 1. Find all usages
grep -rn "ADMIN_UUID" --include="*.go"

// 2. Check for fixed-length reads
grep -rn "make(\[\]byte.*10)" --include="*.go"  // Matches old length

// 3. Verify protocol structure
// Look for: senderBuf, accepterBuf, UUIDLen fields
```

## Prevention Rules

### Rule 1: Length Preservation
When modifying string constants in network protocols:
- **ALWAYS** maintain the exact same character length
- **NEVER** assume variable-length handling

### Rule 2: Binary Protocol Analysis
For Go/C/C++ network tools:
1. Look for `binary.Read()` / `binary.Write()`
2. Look for `io.ReadFull()` with fixed buffer sizes
3. Look for struct tags like `` `len:"10"` ``

### Rule 3: Test Connection First
After modification:
1. Test basic connection establishment
2. Test authentication handshake
3. Test data exchange
4. Only then proceed with full testing

### Rule 4: Protocol Constants Are Special
String constants used in protocols are **NOT** like regular strings:
- Log messages → Can change freely
- Protocol identifiers → MUST maintain length
- Magic bytes → MUST maintain exact value AND length

## Files to Update

Update the following skill documents:
- `tools_evasion/source_modify.md` - Add fixed-length field warning
- `tools_evasion/rule_analysis.md` - Add protocol field analysis section

## Related Detection Rules

This issue does NOT affect YARA detection since the strings are embedded in binary anyway. The length change was purely a functional bug, not a detection issue.

## Conclusion

**When modifying network tools, always check for fixed-length protocol fields before changing string constants.**
