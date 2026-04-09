# Behavior Analysis: SharpHound

## Detection Categories

### 1. Process Creation

| Indicator | Value | Source Location | Detection Risk |
|-----------|-------|-----------------|----------------|
| Image | SharpHound.exe | Assembly name | High |
| Product | SharpHound | Assembly metadata | High |
| Description | SharpHound | Assembly metadata | High |
| Company | SpecterOps | Assembly metadata | High |
| CommandLine | -CollectionMethod | Options.cs:17 | High |
| CommandLine | --CollectionMethods | Options.cs:17 | High |
| CommandLine | --Loop | Options.cs:151 | Medium |
| CommandLine | --PortScanTimeout | Options.cs:113 | Medium |
| CommandLine | Invoke-BloodHound | PowerShell wrapper | High |

### 2. Network Connection

| Indicator | Value | Source Location | Detection Risk |
|-----------|-------|-----------------|----------------|
| DestinationPort | 389 (LDAP) | LDAP enumeration | Medium |
| DestinationPort | 636 (LDAPS) | LDAP SSL | Medium |
| DestinationPort | 445 (SMB) | Computer enumeration | Medium |
| DestinationPort | 135 (RPC) | Session enumeration | Medium |
| Protocol | LDAP | EnumerationDomain.cs | High |
| Protocol | SMB | ComputerFileProducer.cs | Medium |

### 3. File Event

| Indicator | Value | Source Location | Detection Risk |
|-----------|-------|-----------------|----------------|
| TargetFilename | *_computers.json | OutputWriter.cs | High |
| TargetFilename | *_users.json | OutputWriter.cs | High |
| TargetFilename | *_groups.json | OutputWriter.cs | High |
| TargetFilename | *_sessions.json | OutputWriter.cs | High |
| TargetFilename | *.zip (encrypted) | Options.cs:66 | Medium |
| TargetFilename | Cache file | Options.cs:48 | Medium |

### 4. Process Access

| Indicator | Value | Source Location | Detection Risk |
|-----------|-------|-----------------|----------------|
| API | NetSessionEnum | Session enumeration | High |
| API | NetWkstaUserEnum | Session enumeration | High |
| API | NetLocalGroupGetMembers | Local group enum | High |
| API | DsGetDomainControllerInfo | DC enumeration | Medium |
| API | LDAP search | EnumerationDomain.cs | Medium |

### 5. Registry

| Indicator | Value | Source Location | Detection Risk |
|-----------|-------|-----------------|----------------|
| Key | .NET Framework version check | Sharphound.cs:52 | Low |

### 6. API Usage Patterns

| API | Purpose | Source Location | Detection Risk |
|-----|---------|-----------------|----------------|
| System.DirectoryServices | LDAP queries | EnumerationDomain.cs | High |
| System.DirectoryServices.Protocols | LDAP operations | EnumerationDomain.cs | High |
| NetApi32 (NetSessionEnum) | Session enumeration | SharpHoundCommon | High |
| NetApi32 (NetWkstaUserEnum) | Workstation users | SharpHoundCommon | High |
| SAMR | Local group enumeration | SharpHoundCommon | Medium |
| LSA | Policy enumeration | SharpHoundCommon | Medium |

## String Constants Analysis

### Detection-Sensitive Strings

| String | Source Location | Detection Type | Risk |
|--------|-----------------|----------------|------|
| "SharpHound" | Multiple files | Name signature | Critical |
| "BloodHound" | Multiple files | Name signature | Critical |
| "CollectionMethod" | Options.cs:17 | CLI detection | High |
| "Initializing SharpHound" | Elastic YARA | String pattern | High |
| "SharpHound completed" | Elastic YARA | String pattern | High |
| "Removed DCOM Collection" | Options.cs:246 | String pattern | Medium |
| "_computers.json" | Output files | File pattern | High |
| "SpecterOps" | Assembly info | Company name | High |
| "Invoke-BloodHound" | PS wrapper | Function name | High |
| "Get-BloodHoundData" | PS wrapper | Function name | High |

### GUID Patterns

| GUID | Purpose | Detection |
|------|---------|-----------|
| A517A8DE-5834-411D-ABDA-2D0E1766539C | TypeLib GUID (YARA) | High |
| 90A6822C-4336-433D-923F-F54CE66BA98F | TypeLib GUID (YARA) | High |

## Risk Summary

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Process Creation | 0 | 6 | 2 | 0 |
| Network | 0 | 1 | 4 | 0 |
| File Event | 0 | 4 | 2 | 0 |
| Process Access | 0 | 3 | 2 | 0 |
| Strings | 2 | 6 | 1 | 0 |

## Detection Vectors

### Critical Detection Points
1. **Assembly Metadata** - Product, Description, Company names
2. **Binary Name** - SharpHound.exe
3. **GUIDs** - TypeLib GUIDs embedded in .NET assembly

### High Detection Points
1. **CLI Arguments** - CollectionMethod, Loop, etc.
2. **Output Files** - *_computers.json, *_groups.json, etc.
3. **API Calls** - NetSessionEnum, NetWkstaUserEnum
4. **String Constants** - "SharpHound", "BloodHound"

### Medium Detection Points
1. **Network Ports** - 389, 636, 445, 135
2. **File Patterns** - ZIP with password, cache files
3. **Function Names** - Get-BloodHoundData

## Recommendations for Evasion

1. **Assembly Metadata** - Modify Product, Description, Company in .csproj
2. **Assembly Name** - Rename executable
3. **GUIDs** - Regenerate TypeLib GUID in project
4. **String Constants** - Encrypt or obfuscate sensitive strings
5. **CLI Arguments** - Rename argument names (affects usability)
6. **Output Files** - Change naming pattern
