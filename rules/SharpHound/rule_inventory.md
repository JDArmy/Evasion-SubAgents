# Rule Inventory for SharpHound

## Summary

| Type | Count | Sources |
|------|-------|---------|
| YARA | 3 | Elastic, st-mn, Telsy |
| Sigma | 1 | SigmaHQ |
| Network | 0 | - |
| Other | 0 | - |

## YARA Rules

| File | Author | Patterns | Target |
|------|--------|----------|--------|
| Windows_Hacktool_SharpHound_Elastic.yar | Elastic Security | 2 GUIDs, 3 strings | Binary |
| Tool_SharpHound_BloodHound_st-mn.yar | Threat Hunter | 4 strings | Binary |
| Bloodhound_SharpHound_PS_telsy.yar | Emanuele De Lucia | 3 strings | PowerShell |

### Detailed Pattern Analysis

#### Windows_Hacktool_SharpHound_Elastic.yar
| Pattern | Type | Detection |
|---------|------|-----------|
| $guid0 = "A517A8DE-5834-411D-ABDA-2D0E1766539C" | GUID | TypeLib GUID |
| $guid1 = "90A6822C-4336-433D-923F-F54CE66BA98F" | GUID | TypeLib GUID |
| $print_str0 = "Initializing SharpHound at {time} on {date}" | String | Log message |
| $print_str1 = "SharpHound completed {Number} loops!..." | String | Log message |
| $print_str2 = "[-] Removed DCOM Collection" | String | CLI output |

#### Tool_SharpHound_BloodHound_st-mn.yar
| Pattern | Type | Detection |
|---------|------|-----------|
| $s1 = "SharpHound" | String | Name |
| $s2 = "BloodHound" | String | Name |
| $s3 = "CollectionMethod" | String | CLI argument |
| $json = "_computers.json" | String | Output file |

#### Bloodhound_SharpHound_PS_telsy.yar
| Pattern | Type | Detection |
|---------|------|-----------|
| $s1 = "function Invoke-BloodHound" | String | PS function |
| $s2 = "Runs the BloodHound C# Ingestor..." | String | PS comment |
| $s3 = "$Assembly.GetType(\"Sharphound2.Sharphound\")..." | String | Reflection code |

## Sigma Rules

| File | Category | Detection |
|------|----------|-----------|
| proc_creation_win_hktl_bloodhound_sharphound.yml | process_creation | Image + CommandLine |

### Detailed Pattern Analysis

#### proc_creation_win_hktl_bloodhound_sharphound.yml

**Selection 1 - Image/Product/Description:**
| Field | Modifier | Value | Detection |
|-------|----------|-------|-----------|
| Product | contains | 'SharpHound' | Assembly metadata |
| Description | contains | 'SharpHound' | Assembly metadata |
| Company | contains | 'SpecterOps' | Assembly metadata |
| Company | contains | 'evil corp' | Assembly metadata |
| Image | contains | '\Bloodhound.exe' | Binary path |
| Image | contains | '\SharpHound.exe' | Binary path |

**Selection 2 - CommandLine:**
| Field | Modifier | Value | Detection |
|-------|----------|-------|-----------|
| CommandLine | contains | ' -CollectionMethod All ' | CLI argument |
| CommandLine | contains | ' --CollectionMethods Session ' | CLI argument |
| CommandLine | contains | ' --Loop --Loopduration ' | CLI argument |
| CommandLine | contains | ' --PortScanTimeout ' | CLI argument |
| CommandLine | contains | '.exe -c All -d ' | CLI pattern |
| CommandLine | contains | 'Invoke-Bloodhound' | PS function |
| CommandLine | contains | 'Get-BloodHoundData' | PS function |

**Selection 3 - CommandLine (all required):**
| Field | Modifier | Value | Detection |
|-------|----------|-------|-----------|
| CommandLine | contains | ' -JsonFolder ' | CLI argument |
| CommandLine | contains | ' -ZipFileName ' | CLI argument |

**Selection 4 - CommandLine (all required):**
| Field | Modifier | Value | Detection |
|-------|----------|-------|-----------|
| CommandLine | contains | ' DCOnly ' | CLI argument |
| CommandLine | contains | ' --NoSaveCache ' | CLI argument |

## Detection Risk Summary

| Detection Type | Patterns | Evasion Difficulty |
|----------------|----------|-------------------|
| Assembly Metadata | Product, Description, Company | Easy - Modify .csproj |
| Assembly Name | SharpHound.exe | Easy - Rename |
| TypeLib GUID | 2 GUIDs | Easy - Regenerate |
| String Constants | Multiple strings | Medium - Encrypt/obfuscate |
| CLI Arguments | Multiple patterns | Medium - Rename arguments |
| Output Files | *_computers.json | Medium - Change naming |
| PowerShell | Invoke-BloodHound | N/A - Separate wrapper |

## References

- https://github.com/BloodHoundAD/BloodHound
- https://github.com/BloodHoundAD/SharpHound
- https://github.com/SpecterOps/SharpHound
- https://bloodhound.specterops.io/
