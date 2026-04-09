## Rule Analysis: Adaptix_Beacon (bartblaze)

**Author**: @bartblaze
**Target**: Gopher Agent (Go binary)
**Pattern Count**: 26 strings

### Pattern Analysis

All patterns are **string patterns** found in Go compiled binaries due to Go's symbol table.

#### $coffer = "coffer.Load"
- **Type**: string (Go symbol)
- **Meaning**: BOF (Beacon Object File) loader function reference
- **Source Location**: Search for boffer/coffer package imports

#### $func_TaskProcess = "main.TaskProcess"
- **Type**: string (Go symbol)
- **Meaning**: Task processing function name in Go binary symbol table
- **Source Location**: `tasks.go` - function CmdProc handles task processing

#### $func_jobDownloadStart = "main.jobDownloadStart"
- **Type**: string (Go symbol)
- **Meaning**: Download job handler
- **Source Location**: Not found - function renamed to `jobGetFile`

#### $func_jobRun = "main.jobRun"
- **Type**: string (Go symbol)
- **Meaning**: Job execution handler
- **Source Location**: `tasks.go:978` - function `jobExec`

#### $func_jobTerminal = "main.jobTerminal"
- **Type**: string (Go symbol)
- **Meaning**: Terminal job handler
- **Source Location**: `tasks.go:1419` - function `jobShell`

#### $func_jobTunnel = "main.jobTunnel"
- **Type**: string (Go symbol)
- **Meaning**: Tunnel job handler
- **Source Location**: `tasks.go:1265` - function `jobSock`

#### $func_taskCat = "main.taskCat"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:161` - function `fRead`

#### $func_taskCd = "main.taskCd"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:189` - function `fChdir`

#### $func_taskCp = "main.taskCp"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:214` - function `fCopy`

#### $func_taskExecBof = "main.taskExecBof"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:244` - function `fExecObj`

#### $func_taskExit = "main.taskExit"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:265` - function `fTerm`

#### $func_taskJobKill = "main.taskJobKill"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:285` - function `fStopJob`

#### $func_taskJobList = "main.taskJobList"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:270` - function `fListJobs`

#### $func_taskKill = "main.taskKill"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:309` - function `fKillProc`

#### $func_taskLs = "main.taskLs"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:325` - function `fList`

#### $func_taskMkdir = "main.taskMkdir"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:347` - function `fMkDir`

#### $func_taskMv = "main.taskMv"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:365` - function `fMove`

#### $func_taskPs = "main.taskPs"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:405` - function `fProcs`

#### $func_taskPwd = "main.taskPwd"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:416` - function `fCwd`

#### $func_taskRm = "main.taskRm"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:430` - function `fRemove`

#### $func_taskScreenshot = "main.taskScreenshot"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:454` - function `fCapture`

#### $func_taskShell = "main.taskShell"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:468` - function `fExec`

#### $func_taskTerminalKill = "main.taskTerminalKill"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:482` - function `fStopTerm`

#### $func_taskTunnelKill = "main.taskTunnelKill"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:498` - function `fStopTun`

#### $func_taskUpload = "main.taskUpload"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:546` - function `fWrite`

#### $func_taskZip = "main.taskZip"
- **Type**: string (Go symbol)
- **Source Location**: `tasks.go:590` - function `fArchive`

### Evasion Strategy

**Option A: Compiler Flags** (Priority 1)
- Feasible: Partial - Go's `-ldflags="-s -w"` strips symbols but function names may remain
- Flags to add: `-ldflags="-s -w"` (strip debug), `-trimpath` (remove file paths)
- Expected change: Symbol table may still contain function names in Go

**Option B: Source Modification** (Priority 2)
- Feasible: Yes
- Files to modify: `tasks.go`
- Changes: Rename all task functions to obfuscated names

**Option C: Garble (Go Obfuscator)**
- Feasible: Yes
- Tool: garble (https://github.com/burrowers/garble)
- Expected change: Obfuscates all Go symbols including function names

### Selected Strategy
**Use garble for Go binary obfuscation** - This is the most effective approach as it automatically obfuscates all symbols.

Alternative: **Manual function renaming** if garble cannot be used.

### Implementation

**Option 1: Using garble**
```bash
go install mvdan.cc/garble@latest
cd AdaptixServer/extenders/gopher_agent/src_gopher
garble -literals -tiny -seed=random build -o gopher.exe
```

**Option 2: Manual renaming in tasks.go**
Rename functions:
- `CmdProc` -> `Dispatch`
- `jobGetFile` -> `jFetch`
- `jobExec` -> `jRun`
- `jobShell` -> `jTerm`
- `jobSock` -> `jPipe`
- `fRead` -> `Op1`
- `fChdir` -> `Op2`
- etc.

### Verification Command
```bash
# Check if function names exist in binary
strings gopher.exe | grep "main.Task"
strings gopher.exe | grep "main.job"
strings gopher.exe | grep "main.task"
strings gopher.exe | grep "coffer"
```
