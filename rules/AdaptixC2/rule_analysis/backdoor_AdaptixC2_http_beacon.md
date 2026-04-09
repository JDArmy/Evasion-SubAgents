## Rule Analysis: backdoor_AdaptixC2_http_beacon

**Author**: Simone Marinari
**Target**: Network traffic and strings in implant
**Pattern Count**: 5 (string/regex patterns)
**Severity**: 100

### Patterns Summary

| Pattern | Type | Value | Target |
|---------|------|-------|--------|
| `$b1` | String | "AdaptixC2" | Network/User-Agent strings |
| `$b2` | String | "X-Beacon-Id" | HTTP Header |
| `$d1` | Regex | `/X-[0-9a-zA-Z]{3,10}-Id/` | HTTP Header pattern |
| `$a1` | String | "Mozilla/5.0" | User-Agent |
| `$a2` | String | "POST /" | HTTP method |

### Condition
`1 of ($b*) or ($d1 and 1 of($a*))`

### Pattern Analysis

#### $b1: "AdaptixC2"
- **Type**: C2 Name string
- **Meaning**: Direct C2 framework name reference
- **Source Cause**: Configuration or hardcoded string
- **Source Location**: Need to search in source code

#### $b2: "X-Beacon-Id"
- **Type**: HTTP Header name
- **Meaning**: Custom header for beacon identification
- **Source Cause**: HTTP communication protocol
- **Source Location**: HTTP connector or config

#### $d1: `/X-[0-9a-zA-Z]{3,10}-Id/`
- **Type**: HTTP Header regex pattern
- **Meaning**: Matches X-Beacon-Id and similar patterns
- **Source Cause**: Same as $b2

#### $a1: "Mozilla/5.0"
- **Type**: User-Agent string
- **Meaning**: Standard browser UA - very common
- **Detection Risk**: LOW - too generic

#### $a2: "POST /"
- **Type**: HTTP method
- **Meaning**: HTTP POST request - very common
- **Detection Risk**: LOW - too generic

### Evasion Strategy

**Option A: String Obfuscation** (Priority 1)
- Feasible: Yes
- Files to modify: beacon HTTP connector code
- Changes: Remove/obfuscate "AdaptixC2" and "X-Beacon-Id" strings

**Option B: Header Renaming** (Priority 2)
- Feasible: Yes
- Change "X-Beacon-Id" to generic header like "X-Session-Id" or "X-Request-Id"
- Files: HTTP listener and beacon HTTP connector

**Option C: Configuration Change** (Priority 3)
- Feasible: Yes
- Make header names configurable rather than hardcoded

### Selected Strategy

**Primary: Rename HTTP header and remove C2 name strings**

1. Search for "AdaptixC2" in all source files
2. Search for "X-Beacon-Id" in source files
3. Rename header to generic name
4. Remove or obfuscate C2 name references

### Implementation

1. Grep for "AdaptixC2" and "X-Beacon-Id" in source
2. Replace with generic/obfuscated values
3. Update both beacon and listener code

### Verification Command
```bash
# Check for strings in source
grep -rn "AdaptixC2" beacon_agent/
grep -rn "X-Beacon-Id" beacon_agent/
grep -rn "AdaptixC2" beacon_listener_http/
grep -rn "X-Beacon-Id" beacon_listener_http/

# Check in binary after rebuild
strings beacon.exe | grep -i "adaptix"
strings beacon.exe | grep -i "beacon-id"
```

### Status
- $b1 ("AdaptixC2"): Requires source search and removal
- $b2 ("X-Beacon-Id"): Requires header renaming
- $d1 (regex): Will be covered by $b2 fix
- $a1 ("Mozilla/5.0"): SKIP - too generic
- $a2 ("POST /"): SKIP - too generic
