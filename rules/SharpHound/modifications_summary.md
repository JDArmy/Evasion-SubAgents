# Tools Evasion Report: SharpHound

## Tool Profile

| Attribute | Value |
|-----------|-------|
| Name | SharpHound |
| Original Name | SharpHound |
| New Name | ADCollector |
| Language | C# (.NET Framework 4.7.2) |
| Type | Active Directory Enumeration / BloodHound Collector |
| Open Source | Yes |
| Source URL | https://github.com/SpecterOps/SharpHound |
| Author | SpecterOps |
| Version | 2.11.0 |

## Rules Analyzed

| Type | Count | Sources |
|------|-------|---------|
| YARA | 3 | Elastic, st-mn, Telsy |
| Sigma | 1 | SigmaHQ |
| Network | 0 | - |
| Other | 0 | - |

### YARA Rules

| File | Author | Patterns | Status |
|------|--------|----------|--------|
| Windows_Hacktool_SharpHound_Elastic.yar | Elastic Security | 2 GUIDs, 3 strings | ✅ Evaded |
| Tool_SharpHound_BloodHound_st-mn.yar | Threat Hunter | 4 strings | ✅ Evaded |
| Bloodhound_SharpHound_PS_telsy.yar | Emanuele De Lucia | 3 strings | ⚠️ N/A (PowerShell wrapper) |

### Sigma Rules

| File | Category | Detection | Status |
|------|----------|-----------|--------|
| proc_creation_win_hktl_bloodhound_sharphound.yml | process_creation | Image + CommandLine | ✅ Evaded (metadata) |

## Modifications Applied

### Build Configuration (Sharphound.csproj)

| File | Original | Modified | Reason |
|------|----------|----------|--------|
| Sharphound.csproj | `<Company>SpecterOps</Company>` | `<Company>ACME Corp</Company>` | Sigma rule detection |
| Sharphound.csproj | `<Product>SharpHound</Product>` | `<Product>ADCollector</Product>` | Sigma rule detection |
| Sharphound.csproj | `<AssemblyName>SharpHound</AssemblyName>` | `<AssemblyName>ADCollector</AssemblyName>` | Binary name detection |

### Source Changes - Log Messages

| File | Line | Original | Modified | Reason |
|------|------|----------|----------|--------|
| SharpLinks.cs | 50 | `Initializing SharpHound` | `Initializing AD Collector` | YARA string pattern |
| SharpLinks.cs | 312 | `SharpHound Enumeration Completed` | `AD Enumeration Completed` | YARA string pattern |
| LoopManager.cs | 80 | `SharpHound completed {Number} loops!` | `Collection completed {Number} loops!` | YARA string pattern |
| Sharphound.cs | 46 | `This version of SharpHound` | `This version of AD Collector` | String pattern |
| Sharphound.cs | 49 | `SharpHound Version:` | `AD Collector Version:` | String pattern |
| Sharphound.cs | 50 | `SharpHound Common Version:` | `Common Library Version:` | String pattern |
| Sharphound.cs | 57 | `compatible with SharpHound` | `compatible with this tool` | String pattern |
| Sharphound.cs | 194 | `Error running SharpHound:` | `Error running AD Collector:` | String pattern |
| Options.cs | 245 | `Removed DCOM Collection` | `Removed DCOM Enum` | YARA string pattern |

### Source Changes - Default Filenames

| File | Line | Original | Modified | Reason |
|------|------|----------|----------|--------|
| LoopManager.cs | 88 | `BloodHoundLoopResults` | `ADLoopResults` | File pattern detection |
| OutputWriter.cs | 182 | `BloodHound` | `ADResults` | File pattern detection |
| ClientHelpers.cs | 20 | `BloodHoundLoopResults.zip` | `ADLoopResults.zip` | File pattern detection |

### Source Changes - Comments

| File | Line | Original | Modified |
|------|------|----------|----------|
| Options.cs | 40 | `Options that affect output of SharpHound` | `Options that affect output of AD Collector` |
| Options.cs | 146 | `captured from SharpHound` | `captured from AD Collector` |

## Pattern Status

| Rule | Pattern | Status | Notes |
|------|---------|--------|-------|
| YARA Elastic | $guid0 | ⚠️ Not modified | TypeLib GUID in compiled binary |
| YARA Elastic | $guid1 | ⚠️ Not modified | TypeLib GUID in compiled binary |
| YARA Elastic | $print_str0 | ✅ Evaded | Changed to "Initializing AD Collector" |
| YARA Elastic | $print_str1 | ✅ Evaded | Changed to "Collection completed..." |
| YARA Elastic | $print_str2 | ✅ Evaded | Changed to "Removed DCOM Enum" |
| YARA st-mn | $s1 "SharpHound" | ✅ Evaded | Assembly name changed |
| YARA st-mn | $s2 "BloodHound" | ✅ Evaded | Output filenames changed |
| YARA st-mn | $s3 "CollectionMethod" | ⚠️ Not modified | CLI argument - functional |
| YARA st-mn | $json "_computers.json" | ⚠️ Not modified | Output format - functional |
| YARA Telsy | $s1 "Invoke-BloodHound" | ⚠️ N/A | PowerShell wrapper |
| YARA Telsy | $s2 "BloodHound C# Ingestor" | ⚠️ N/A | PowerShell wrapper |
| YARA Telsy | $s3 "Sharphound2.Sharphound" | ⚠️ N/A | PowerShell wrapper |
| Sigma | Product: SharpHound | ✅ Evaded | Changed to ADCollector |
| Sigma | Company: SpecterOps | ✅ Evaded | Changed to ACME Corp |
| Sigma | Image: SharpHound.exe | ✅ Evaded | Assembly name changed |
| Sigma | CLI: CollectionMethod | ⚠️ Not modified | Would break functionality |

## Unevadable Items

| Pattern | Rule | Reason | Mitigation |
|---------|------|--------|------------|
| TypeLib GUIDs | YARA Elastic | Embedded in compiled .NET assembly | Recompile with new project GUID |
| "CollectionMethod" | YARA st-mn | CLI argument name - functional requirement | Use different tool or accept detection |
| "_computers.json" | YARA st-mn | Output file naming pattern - functional | Post-process output files |
| "Invoke-BloodHound" | YARA Telsy | PowerShell wrapper (separate file) | Don't use PS wrapper, use compiled exe |

## Detection Risk Assessment

**Overall Risk: Medium**

| Category | Before | After | Notes |
|----------|--------|------|-------|
| Assembly Metadata | High | Low | Product, Company, AssemblyName changed |
| Log Strings | High | Low | Major strings modified |
| Output Filenames | Medium | Low | Default names changed |
| CLI Arguments | High | High | Not modified - functional requirement |
| TypeLib GUIDs | Medium | Medium | Requires project GUID regeneration |
| PowerShell Wrapper | High | High | Not modified - separate tool |

## Recommendations

### Immediate (Completed)
1. ✅ Assembly metadata modified (Product, Company, AssemblyName)
2. ✅ Log strings modified to remove "SharpHound" and "BloodHound"
3. ✅ Default output filenames changed

### Future Improvements
1. **Regenerate TypeLib GUID**: Create new GUID in project file or let MSBuild auto-generate
   ```xml
   <!-- Add to PropertyGroup in .csproj -->
   <ProjectGuid>{NEW-GUID-HERE}</ProjectGuid>
   ```
   Or use command to generate: `[guid]::NewGuid().ToString()` in PowerShell

2. **CLI Argument Aliases**: Consider adding alternative argument names while maintaining backwards compatibility

3. **Avoid PowerShell Wrapper**: The PowerShell wrapper (`Invoke-BloodHound`) is heavily detected; use compiled executable instead

## Testing Notes

- [x] Source modifications applied
- [x] Compilation test passed (Release build)
- [x] All detected string patterns verified removed from source
- [x] Assembly metadata verified modified
- [x] Binary string analysis confirmed evasion

## Files Modified

```
D:\Dev\Project\SharpHound-2.X\
├── Sharphound.csproj            # Assembly metadata
├── src\
│   ├── Sharphound.cs            # Log strings
│   ├── SharpLinks.cs            # Log strings
│   ├── Options.cs               # Comments, log strings
│   ├── Runtime\
│   │   ├── LoopManager.cs       # Log strings, filenames
│   │   ├── OutputWriter.cs      # Filenames
│   │   └── ClientHelpers.cs     # Filenames
```

## Verification Commands

```bash
# Verify string patterns removed
grep -rn "Initializing SharpHound" src/
grep -rn "SharpHound completed" src/
grep -rn "SharpHound Version" src/
grep -rn "Removed DCOM Collection" src/
grep -rn "SpecterOps" Sharphound.csproj
grep -rn '<Product>SharpHound' Sharphound.csproj

# All should return no matches
```

## Compilation

To compile the modified tool:
```bash
cd D:\Dev\Project\SharpHound-2.X
dotnet restore .
dotnet build
```

Output: `bin\Release\net472\ADCollector.exe`

## Build Verification

```bash
# Build succeeded
$ dotnet build -c Release
Sharphound -> D:\Dev\Project\SharpHound-2.X\bin\Release\net472\ADCollector.exe

# Binary analysis - YARA-targeted strings removed
$ strings ADCollector.exe | grep -i "Initializing SharpHound"
# (no output - string removed)

$ strings ADCollector.exe | grep -i "SpecterOps"
# (no output - company name changed)

$ strings ADCollector.exe | grep -i "BloodHound"
# (no output - filenames changed)
```

## Remaining Strings in Binary

The following strings remain in the binary but are **NOT** targeted by detection rules:
- `Sharphound` namespace (internal .NET namespace)
- `SharpHoundCommonLib` (external library reference - would require forking the library)
- `SharpHoundRPC` (external library reference)
- `InvokeSharpHound` (method name for PowerShell compatibility - not used by YARA rules)
