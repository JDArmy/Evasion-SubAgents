## Rule Analysis: Adaptix_Beacon

**Author**: @bartblaze
**Target**: Go Agent (gopher_agent)
**Pattern Count**: 23 (all string patterns - Go function names embedded in binary)
**Reference**: https://github.com/Adaptix-Framework/AdaptixC2

### Patterns Summary

All patterns are **Go function names** that get embedded in the compiled binary's symbol table:

| Pattern | Type | Source Location |
|---------|------|-----------------|
| `$coffer` | "coffer.Load" | Go symbol - not found in source |
| `$func_TaskProcess` | "main.TaskProcess" | tasks.go: CmdProc function |
| `$func_jobDownloadStart` | "main.jobDownloadStart" | Not found - renamed or removed |
| `$func_jobRun` | "main.jobRun" | tasks.go: jobExec function |
| `$func_jobTerminal` | "main.jobTerminal" | tasks.go: jobShell function |
| `$func_jobTunnel` | "main.jobTunnel" | tasks.go: jobSock function |
| `$func_taskCat` | "main.taskCat" | tasks.go: fRead function |
| `$func_taskCd` | "main.taskCd" | tasks.go: fChdir function |
| `$func_taskCp` | "main.taskCp" | tasks.go: fCopy function |
| `$func_taskExecBof` | "main.taskExecBof" | tasks.go: fExecObj function |
| `$func_taskExit` | "main.taskExit" | tasks.go: fTerm function |
| `$func_taskJobKill` | "main.taskJobKill" | tasks.go: fStopJob function |
| `$func_taskJobList` | "main.taskJobList" | tasks.go: fListJobs function |
| `$func_taskKill` | "main.taskKill" | tasks.go: fKillProc function |
| `$func_taskLs` | "main.taskLs" | tasks.go: fList function |
| `$func_taskMkdir` | "main.taskMkdir" | tasks.go: fMkDir function |
| `$func_taskMv` | "main.taskMv" | tasks.go: fMove function |
| `$func_taskPs` | "main.taskPs" | tasks.go: fProcs function |
| `$func_taskPwd` | "main.taskPwd" | tasks.go: fCwd function |
| `$func_taskRm` | "main.taskRm" | tasks.go: fRemove function |
| `$func_taskScreenshot` | "main.taskScreenshot" | tasks.go: fCapture function |
| `$func_taskShell` | "main.taskShell" | tasks.go: fExec function |
| `$func_taskTerminalKill` | "main.taskTerminalKill" | tasks.go: fStopTerm function |
| `$func_taskTunnelKill` | "main.taskTunnelKill" | tasks.go: fStopTun function |
| `$func_taskUpload` | "main.taskUpload" | tasks.go: fWrite function |
| `$func_taskZip` | "main.taskZip" | tasks.go: fArchive function |

### Evasion Strategy

**Option A: Function Renaming** (Priority 1)
- Feasible: Yes - All patterns are Go function names
- Files to modify: tasks.go (main package functions)
- Changes: Rename all functions to generic/innocuous names
- Example: `CmdProc` -> `ProcessCmd`, `jobExec` -> `runJob`, etc.

**Option B: Go Build Flags** (Priority 2)
- Feasible: Partial - `-ldflags="-s -w"` already strips some symbols
- Current flags: `-trimpath -ldflags="-s -w"`
- Note: Go still embeds function names for reflection/panic traces even with stripping
- Additional flags: `-buildmode=pie` (position-independent executable)

**Option C: Garble (Go Obfuscator)** (Priority 3)
- Feasible: Yes
- Tool: https://github.com/burrowers/garble
- Obfuscates Go symbol names at build time
- Changes: Modify Makefile to use garble instead of go build

### Selected Strategy

**Primary: Rename all Go functions to generic names**

This is the most reliable approach. The YARA rule looks for specific function name patterns in the Go binary's symbol table.

### Function Renaming Map

| Original Name | New Name | File |
|---------------|----------|------|
| CmdProc | DataProc | tasks.go |
| jobGetFile | xferGet | tasks.go |
| jobExec | runExec | tasks.go |
| jobExecObjAsync | runObjAsync | tasks.go |
| jobSock | runSock | tasks.go |
| jobShell | runShell | tasks.go |
| fRead | opRead | tasks.go |
| fChdir | opChdir | tasks.go |
| fCopy | opCopy | tasks.go |
| fExecObj | opExecObj | tasks.go |
| fTerm | opTerm | tasks.go |
| fListJobs | opListJobs | tasks.go |
| fStopJob | opStopJob | tasks.go |
| fKillProc | opKillProc | tasks.go |
| fList | opList | tasks.go |
| fMkDir | opMkDir | tasks.go |
| fMove | opMove | tasks.go |
| fProcs | opProcs | tasks.go |
| fCwd | opCwd | tasks.go |
| fRevert | opRevert | tasks.go |
| fRemove | opRemove | tasks.go |
| fCapture | opCapture | tasks.go |
| fExec | opExec | tasks.go |
| fStopTerm | opStopTerm | tasks.go |
| fStopTun | opStopTun | tasks.go |
| fPauseTun | opPauseTun | tasks.go |
| fResumeTun | opResumeTun | tasks.go |
| fWrite | opWrite | tasks.go |
| fArchive | opArchive | tasks.go |

### Implementation

1. Rename all exported and main package functions in tasks.go
2. Update Makefile to add `-buildmode=pie` for additional obfuscation
3. Verify function names are no longer detectable

### Verification Command
```bash
# Check for old function names in binary
strings agent.exe | grep -E "TaskProcess|jobRun|taskCat|taskKill"
# Should return nothing after modification
```

### Status
- All 23 patterns: Require function renaming in Go source
