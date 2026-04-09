# Evasion SubAgents

基于 Claude Code 的免杀技术Subagents集合。

## 项目概述

本项目是一个 Claude Code 插件，通过 SubAgents 和 Skills 实现：

| Agent | 功能 | Skill |
|-------|------|-------|
| **research-agent** | 搜索 GitHub 技术，分析代码模式，更新知识库 | `research` |
| **loadergen-agent** | 从 loader 知识库组合组件，生成 loader | `loader_generate` |
| **evasion-agent** | 将 evasion 技术集成到现有 loader | `evasion_integrate` |
| **c2-evasion-agent** | 分析 C2 框架源码，查找检测规则，修改源码免杀 | `c2_evasion` |
| **tools-evasion-agent** | 分析渗透测试工具，查找检测规则，修改源码免杀 | `tools_evasion` |


## 环境要求

| 依赖 | 版本要求 | 用途 |
|------|----------|------|
| Python | 3.8+ | 知识库管理脚本 |
| MinGW-w64 | 最新版 | 编译 Windows 可执行文件 |
| GitHub CLI (gh) | 2.0+ | 搜索 GitHub 仓库和代码 |
| Claude Code | 最新版 | 主框架 |

### Windows 安装指南

#### 1. 安装 Python

```powershell
# 使用 winget 安装
winget install Python.Python.3.12

# 或从官网下载
# https://www.python.org/downloads/
```

#### 2. 安装 MinGW-w64 (交叉编译器)

```powershell
# 使用 winget 安装
winget install MSYS2.MSYS2

# 安装后，在 MSYS2 终端中运行：
pacman -S mingw-w64-x86_64-gcc

# 添加到 PATH (PowerShell 管理员)
$env:PATH += ";C:\msys64\mingw64\bin"
# 永久添加
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\msys64\mingw64\bin", "User")

# 验证安装
x86_64-w64-mingw32-gcc --version
```

#### 3. 安装 GitHub CLI

```powershell
# 使用 winget 安装
winget install GitHub.cli

# 登录 GitHub
gh auth login

# 验证安装
gh --version
gh auth status
```

#### 4. 安装 Claude Code

```powershell
# 使用 npm 安装 (需要 Node.js)
npm install -g @anthropic-ai/claude-code

# 或使用官方安装器
# https://github.com/anthropics/claude-code

# 验证安装
claude --version
```

### Linux/macOS 安装指南

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip mingw-w64 gh

# macOS (Homebrew)
brew install python mingw-w64 gh

# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 登录 GitHub
gh auth login
```


## 加载插件到 Claude Code

### 方法一：项目目录方式（推荐）

将项目作为 Claude Code 的工作目录：

```bash
# 进入项目目录
cd "D:\Dev\Agent\LoaderSubAgents\LoaderSub Agents"

# 启动 Claude Code
claude

# Claude Code 会自动加载 .claude/ 目录下的配置
```

Claude Code 会自动识别：
- `.claude/agents/` - SubAgent 定义
- `.claude/skills/` - Skill 定义
- `.claude/commands/` - 自定义命令

### 方法二：CLAUDE.md 全局配置

在用户主目录创建全局配置：

```bash
# Windows
notepad %USERPROFILE%\.claude\CLAUDE.md

# Linux/macOS
nano ~/.claude/CLAUDE.md
```

添加项目路径：

```markdown
# 项目路径
- D:\Dev\Agent\LoaderSubAgents\LoaderSub Agents
```


### 验证加载成功

启动 Claude Code 后，使用以下命令验证：

```bash
# 查看可用命令
> /help

# 应看到：
# /research - Search GitHub for shellcode loader and evasion techniques
# /loader_generate - Generate shellcode loaders
# /evasion_integrate - Integrate evasion techniques
# /c2_evasion - C2 framework evasion analysis and modification
# /tools_evasion - Penetration testing tools evasion analysis
```

## 架构

```
evasion-agent-teams/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── research-agent.md        # 研究技术
│   ├── loadergen-agent.md       # 生成 loader
│   ├── evasion-agent.md         # 集成 evasion
│   ├── c2-evasion-agent.md      # C2 免杀
│   └── tools-evasion-agent.md   # 工具免杀
├── skills/
│   ├── research/
│   │   └── SKILL.md             # 搜索分析技能
│   ├── loader_generate/
│   │   └── SKILL.md             # loader 生成技能
│   ├── evasion_integrate/
│   │   └── SKILL.md             # evasion 集成技能
│   ├── c2_evasion/
│   │   └── SKILL.md             # C2 免杀技能
│   └── tools_evasion/
│       └── SKILL.md             # 工具免杀技能
├── commands/
│   ├── research.md              # /research
│   ├── loader_generate.md       # /loader_generate
│   ├── evasion_integrate.md     # /evasion_integrate
│   ├── c2_evasion.md            # /c2_evasion
│   └── tools_evasion.md         # /tools_evasion
├── lib/
│   └── knowledge_manager.py
├── knowledge-base/
│   ├── evasion_techniques.json  # Evasion 技术库
│   ├── loader_techniques.json   # Loader 组件库
│   └── scenarios.json           # 已生成记录
├── samples/
│   └── calc.bin                 # 测试 shellcode
├── output/                      # 输出目录
└── README.md
```

## 命令

### /research

搜索 GitHub 上的技术并更新知识库。

```bash
/research                        # 交互模式
/research "shellcode loader"     # 搜索 loader
/research "API hashing C++"      # 搜索特定技术
```

### /loader_generate

从 loader 知识库生成 shellcode loader。

```bash
/loader_generate                              # 单个随机 loader (默认 calc.bin)
/loader_generate 5                            # 批量生成 5 个
/loader_generate --shellcode path/to/sc.bin   # 使用自定义 shellcode
/loader_generate my.bin                       # 简写: 指定 shellcode 文件
/loader_generate 3 --shellcode custom.bin     # 批量 + 自定义 shellcode
/loader_generate --executor callback          # 指定执行方式
/loader_generate --complexity simple          # 按复杂度筛选
/loader_generate --language rust              # Rust 语言
```

**Shellcode 参数：**

| 参数格式 | 说明 |
|----------|------|
| 无参数 | 使用默认 `samples/calc.bin` |
| `--shellcode <path>` | 指定自定义 bin 文件 |
| `<file.bin>` | 简写形式，直接传入 bin 文件路径 |

**流程：**
1. 查询 `loader_techniques.json` 获取组件库
2. 检查 `scenarios.json` 避免重复
3. 生成组件组合
4. 编译测试
5. 记录结果

### /evasion_integrate

将 evasion 技术集成到用户提供的 loader。

```bash
/evasion_integrate /path/to/loader.c                    # 自动选择技术
/evasion_integrate /path/to/loader.c --type api_obfuscation  # 指定类型
/evasion_integrate /path/to/loader.c --technique T001,T003   # 指定技术ID
```

**流程：**
1. 读取用户提供的 loader 源码
2. 查询 `evasion_techniques.json` 获取技术
3. 分析兼容性
4. 集成技术到代码
5. 编译测试
6. 报告变更

### /c2_evasion

对 C2 框架源码进行免杀改造。

```bash
/c2_evasion /path/to/c2/source          # 分析并修改 C2 源码
/c2_evasion /path/to/c2 --rules-only    # 仅查找检测规则，不修改
```

**流程：**
1. 分析 C2 框架源码结构
2. 搜索 YARA/Sigma 等检测规则
3. 识别特征字符串和模式
4. 修改源码规避检测
5. 验证修改后功能正常

### /tools_evasion

对渗透测试工具进行免杀改造。

```bash
/tools_evasion /path/to/tool/source    # 分析并修改工具源码
```

**流程：**
1. 分析工具源码结构
2. 搜索 YARA/Sigma 等检测规则
3. 识别特征字符串和模式
4. 修改源码规避检测
5. 编译测试验证功能

**支持的检测类型：**
- YARA 规则（字符串、十六进制、正则）
- Sigma 规则（进程创建、网络连接等）
- 网络流量特征

**注意：**
- ⚠️ 修改协议字符串时必须保持长度不变
- ⚠️ 网络工具的固定长度字段不可改变长度

## 知识库

### evasion_techniques.json

Evasion 技术库：

```json
{
  "techniques": [
    {
      "id": "T001",
      "name": "API Hashing",
      "evasion_type": "api_obfuscation",
      "description": "通过哈希值动态解析API",
      "code_template": "...",
      "apis": ["LoadLibrary", "GetProcAddress"],
      "complexity": "medium"
    }
  ]
}
```

**Evasion 类型：**
- `api_obfuscation` - API 混淆
- `string_obfuscation` - 字符串混淆
- `memory_evasion` - 内存规避
- `execution_evasion` - 执行规避
- `anti_analysis` - 反分析
- `amsi_etw_bypass` - AMSI/ETW 绕过
- `unhooking` - 脱钩

### loader_techniques.json

Loader 组件库：

```json
{
  "component_library": {
    "storage_methods": [...],
    "memory_allocators": [...],
    "data_copiers": [...],
    "executors": [...]
  }
}
```

### scenarios.json

已生成的 loader 记录，用于去重。

## 数据流

```
用户请求
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                 Claude Code 主 Agent                 │
└─────────────────────────────────────────────────────┘
    │
    ├── /research ─────────────────────────────────────┐
    │       │                                          │
    │       ▼                                          │
    │   research-agent                                 │
    │       │                                          │
    │       ▼                                          │
    │   搜索 GitHub → 分析代码 → 写入知识库            │
    │                                                   │
    ├── /loader_generate ──────────────────────────────┤
    │       │                                          │
    │       ▼                                          │
    │   loadergen-agent                                │
    │       │                                          │
    │       ▼                                          │
    │   查询组件库 → 检查 scenarios → 生成 → 测试 → 记录│
    │                                                   │
    └── /evasion_integrate /path/to/loader.c ──────────┤
            │                                          │
            ▼                                          │
        evasion-agent                                  │
            │                                          │
            ▼                                          │
        读取 loader → 查询 evasion 库 → 集成 → 测试   │
                                                       │
    ┌──────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│        lib/knowledge_manager.py     │
│  - JSON CRUD                        │
└─────────────────────────────────────┘
    │
    ▼
knowledge-base/
```

## 快速开始

```bash
# 1. 放置测试 shellcode
# 将 calc.bin 放入 samples/

# 2. 启动 Claude Code
cd "evasion-agent-teams"
claude

# 3. 使用命令
> 搜索 GitHub 上的 shellcode loader 技术
> /loader_generate 5
> /evasion_integrate ./output/loader_001.c --type api_obfuscation
```

## 知识库管理

```bash
# 查看统计
python lib/knowledge_manager.py stats

# 添加 evasion 技术
python lib/knowledge_manager.py add-evasion \
  --name "API Hashing" \
  --type "api_obfuscation" \
  --description "通过哈希值动态解析API" \
  --apis "LoadLibrary,GetProcAddress" \
  --complexity "medium"

# 添加 loader 组件
python lib/knowledge_manager.py add-component \
  --type "executors" \
  --name "ThreadPool Callback" \
  --description "使用线程池回调执行"

# 查看组件库
python lib/knowledge_manager.py get-components

# 随机组合
python lib/knowledge_manager.py random-combination

# 导出/导入
python lib/knowledge_manager.py export --output backup.json
python lib/knowledge_manager.py import --input backup.json
```

## 安全规则

| Agent | 禁止 | 允许 |
|-------|------|------|
| research-agent | 编译/执行外部代码，使用外部 shellcode | 分析模式，更新知识库 |
| loadergen-agent | 执行生成的可执行文件 | 使用 samples/calc.bin 或用户指定的 bin 文件 |
| evasion-agent | 执行恶意 shellcode | 修改用户代码，用 calc.bin 或用户指定文件测试 |
| c2-evasion-agent | 执行恶意操作，破坏性修改 | 分析源码，修改规避特征 |
| tools-evasion-agent | 执行恶意操作，破坏性修改 | 分析源码，修改规避特征，编译验证 |

## 故障排除

### 常见问题

#### 1. `x86_64-w64-mingw32-gcc: command not found`

MinGW-w64 未安装或未添加到 PATH。

```powershell
# 检查安装
where x86_64-w64-mingw32-gcc

# 如果找不到，添加到 PATH
$env:PATH += ";C:\msys64\mingw64\bin"
```

#### 2. `gh: command not found` 或 GitHub API 错误

GitHub CLI 未安装或未登录。

```powershell
# 安装
winget install GitHub.cli

# 登录
gh auth login

# 验证
gh auth status
```

#### 3. `/research` 命令无响应

可能原因：
- GitHub CLI 未登录
- 网络连接问题
- API 速率限制

```powershell
# 检查登录状态
gh auth status

# 检查速率限制
gh api rate_limit
```

#### 4. 编译成功但测试失败

确保使用正确的 shellcode 格式：
- `samples/calc.bin` 应为原始二进制 shellcode
- 支持 x64 Windows shellcode

```powershell
# 验证 shellcode 格式
xxd samples/calc.bin | head -5
```

#### 5. 命令未显示在 Claude Code 中

确保目录结构正确：

```
.claude/
├── agents/
│   ├── research-agent.md
│   ├── loadergen-agent.md
│   ├── evasion-agent.md
│   └── c2-evasion-agent.md
├── skills/
│   ├── research.md
│   ├── loader_generate.md
│   ├── evasion_integrate.md
│   └── c2_evasion.md
├── commands/
│   ├── research.md
│   ├── loader_generate.md
│   ├── evasion_integrate.md
│   └── c2_evasion.md
└── settings.local.json
```

检查 `settings.local.json`：

```json
{
  "enabledMcpjsonServers": [],
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```


## License

MIT
