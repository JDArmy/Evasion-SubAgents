# Tool Profile: SharpHound

## Basic Information

| Attribute | Value |
|-----------|-------|
| Name | SharpHound |
| Version | 2.11.0 |
| Language | C# (.NET Framework 4.7.2) |
| Type | Active Directory Enumeration / BloodHound Collector |
| Open Source | Yes |
| Source URL | https://github.com/SpecterOps/SharpHound |
| Author | SpecterOps |
| License | Custom (open) |

## Purpose

SharpHound is the official data collector for BloodHound, a tool for analyzing Active Directory trust relationships. It collects information about:

- **Group memberships** - User/group relationships
- **Session information** - Active sessions on computers
- **Local administrator** - Local admin rights
- **Trust relationships** - Domain trusts
- **ACLs** - Access control lists
- **Computer properties** - AD computer objects
- **User rights** - User privileges
- **Certificate services** - AD CS information

## Key Features

| Feature | Description |
|---------|-------------|
| LDAP Enumeration | Query Active Directory |
| Session Enumeration | NetSessionEnum, NetWkstaUserEnum |
| Local Group Enumeration | NetLocalGroupGetMembers |
| Computer Enumeration | Port scanning, SMB enumeration |
| Output | JSON files, ZIP archives |
| Stealth Mode | Reduced detection footprint |

## Build System

- **Project Type**: .NET Core SDK-style project
- **Target Framework**: net472
- **Build Command**: `dotnet build`
- **Dependencies**: SharpHoundCommon, SharpHoundRPC, Costura.Fody

## Key Files

| File | Purpose |
|------|---------|
| `src/Sharphound.cs` | Main entry point |
| `src/Options.cs` | CLI argument handling |
| `src/EnumerationDomain.cs` | LDAP enumeration |
| `src/Runtime/CollectionTask.cs` | Collection orchestration |
| `src/Producers/*.cs` | Data producers |

## Detection Risk Assessment

| Category | Risk Level | Notes |
|----------|------------|-------|
| Process Creation | High | Known tool name, signatures exist |
| Network Connection | High | LDAP/SMB connections to DC |
| File Event | Medium | JSON output files |
| Registry | Low | Minimal registry access |
| Process Access | Medium | Session enumeration APIs |

## Keywords for Detection Search

- SharpHound
- BloodHound
- BloodHound CE
- SpecterOps
- Active Directory enumeration
- Session enumeration
- LDAP enumeration
