## Rule Analysis: backdoor_AdaptixC2_http_beacon (nembo81)

**Author**: Simone Marinari
**Target**: Network traffic / HTTP listener
**Pattern Count**: 5 patterns (2 string, 1 regex, 2 common)

### Pattern Analysis

#### $b1 = "AdaptixC2"
- **Type**: string
- **Meaning**: Framework name in network traffic or server responses
- **Source Location**: Server-side headers or responses

#### $b2 = "X-Beacon-Id"
- **Type**: string (HTTP header)
- **Meaning**: Custom HTTP header used for beacon identification
- **Source Location**: HTTP listener configuration

#### $d1 = /X-[0-9a-zA-Z]{3,10}-Id/
- **Type**: regex
- **Meaning**: Pattern matching custom HTTP headers like X-Beacon-Id, X-Agent-Id, etc.
- **Source Location**: HTTP listener transport code

#### $a1 = "Mozilla/5.0"
- **Type**: string (User-Agent)
- **Meaning**: Common User-Agent string
- **Source Location**: HTTP profile configuration

#### $a2 = "POST /"
- **Type**: string (HTTP method)
- **Meaning**: HTTP POST request pattern
- **Source Location**: HTTP beacon connector

### Source Code Analysis

**In beacon_listener_http/pl_transport.go:**
- Line 59: `ParameterName string` - This is the header name configuration
- The header is configurable and can be changed

**In ConnectorHTTP.cpp:**
- Line 103: Header construction uses `profile.parameter`
- This is where the beacon ID header is built

### Evasion Strategy

**Option A: Server Configuration** (Priority 1)
- Feasible: Yes
- Changes: Modify default header names in configuration
- Expected: Different header name evades regex pattern

**Option B: Source Modification** (Priority 2)
- Feasible: Yes
- Files to modify: Configuration defaults, HTTP listener code
- Changes: Change default header name from "X-Beacon-Id" to something generic

### Selected Strategy
**Modify default HTTP header names** - Change the beacon identification header to use a generic name.

### Implementation

1. Change default header name in configuration files
2. Modify any hardcoded references

### Verification Command
```bash
# Check network traffic for header patterns
grep -r "X-Beacon-Id" AdaptixServer/
grep -r "AdaptixC2" AdaptixServer/
```
