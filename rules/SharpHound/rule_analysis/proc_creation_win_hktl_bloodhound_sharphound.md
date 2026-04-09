# Rule Analysis: proc_creation_win_hktl_bloodhound_sharphound.yml

## Rule Info

| Attribute | Value |
|-----------|-------|
| Source | SigmaHQ/sigma |
| Author | Florian Roth (Nextron Systems) |
| Type | Sigma |
| Category | process_creation |
| Level | high |

## Detection Selections

### Selection 1: Image/Product/Description/Company

| Field | Modifier | Value | Source |
|-------|----------|-------|--------|
| Product | contains | 'SharpHound' | Assembly metadata |
| Description | contains | 'SharpHound' | Assembly metadata |
| Company | contains | 'SpecterOps' | Assembly metadata |
| Company | contains | 'evil corp' | Assembly metadata |
| Image | contains | '\Bloodhound.exe' | Binary path |
| Image | contains | '\SharpHound.exe' | Binary path |

**Source Location**: `Sharphound.csproj` lines 8-14

**Evasion Strategy**:
1. Modify `<Product>`, `<Description>`, `<Company>` in .csproj
2. Rename output binary

### Selection 2: CommandLine Patterns

| Pattern | Location | Detection |
|---------|----------|-----------|
| ' -CollectionMethod All ' | CLI argument | Options.cs |
| ' --CollectionMethods Session ' | CLI argument | Options.cs |
| ' --Loop --Loopduration ' | CLI argument | Options.cs |
| ' --PortScanTimeout ' | CLI argument | Options.cs |
| '.exe -c All -d ' | CLI pattern | Usage |
| 'Invoke-Bloodhound' | PowerShell | Template.ps1 |
| 'Get-BloodHoundData' | PowerShell | External |

**Source Location**: `src/Options.cs`, `src/PowerShell/Template.ps1`

**Evasion Strategy**: Rename CLI arguments (affects usability)

### Selection 3: CommandLine (all required)

| Pattern | Location |
|---------|----------|
| ' -JsonFolder ' | Options.cs |
| ' -ZipFileName ' | Options.cs |

### Selection 4: CommandLine (all required)

| Pattern | Location |
|---------|----------|
| ' DCOnly ' | Options.cs |
| ' --NoSaveCache ' | Options.cs |

## Condition

```
1 of selection_*
```

**Logic**: Match ANY of the 4 selections

## Evasion Plan

### High Impact / Low Effort

| Priority | Target | Strategy | Effort | Impact |
|----------|--------|----------|--------|--------|
| 1 | Assembly metadata | Modify .csproj | Low | High |
| 2 | Binary name | Rename output | Low | High |
| 3 | Company name | Modify .csproj | Low | Medium |

### Medium Impact / Medium Effort

| Priority | Target | Strategy | Effort | Impact |
|----------|--------|----------|--------|--------|
| 4 | CLI arguments | Rename arguments | Medium | High |
| 5 | Log strings | Obfuscate | Low | Medium |

### Implementation Details

**File: Sharphound.csproj**
```xml
<!-- Before -->
<Product>SharpHound</Product>
<Company>SpecterOps</Company>
<AssemblyName>SharpHound</AssemblyName>

<!-- After -->
<Product>ADCollector</Product>
<Company>ACME Corp</Company>
<AssemblyName>ADCollector</AssemblyName>
```

**Note**: CLI argument renaming requires extensive code changes and may break functionality.

## Status

| Selection | Status | Notes |
|-----------|--------|-------|
| selection_img | Pending | Modify assembly metadata |
| selection_cli_1 | Deferred | Would break CLI compatibility |
| selection_cli_2 | Deferred | Would break CLI compatibility |
| selection_cli_3 | Deferred | Would break CLI compatibility |

## Recommendation

Focus on assembly metadata modification. CLI argument patterns are too invasive and would break tool usability.
