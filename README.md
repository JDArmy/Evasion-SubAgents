# Evasion Agent Teams

基于 Claude Code 的免杀技术研究与 Shellcode Loader 生成框架。


## 项目概述

本项目是一个 Claude Code 插件，通过 SubAgents 和 Skills 实现：

| Agent | 功能 | Skill |
|-------|------|-------|
| **research-agent** | 搜索 GitHub 技术，分析代码模式，更新知识库 | `research` |
| **loadergen-agent** | 从 loader 知识库组合组件，生成 loader | `loader_generate` |
| **evasion-agent** | 将 evasion 技术集成到现有 loader | `evasion_integrate` |

## 架构

```
evasion-agent-teams/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── research-agent.md        # 研究技术
│   ├── loadergen-agent.md       # 生成 loader
│   └── evasion-agent.md         # 集成 evasion
├── skills/
│   ├── research/
│   │   └── SKILL.md             # 搜索分析技能
│   ├── loader_generate/
│   │   └── SKILL.md             # loader 生成技能
│   └── evasion_integrate/
│       └── SKILL.md             # evasion 集成技能
├── commands/
│   ├── research.md              # /research
│   ├── loader_generate.md       # /loader_generate
│   └── evasion_integrate.md     # /evasion_integrate
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
/loader_generate                  # 单个随机 loader
/loader_generate 5                # 批量生成 5 个
/loader_generate --executor callback  # 指定执行方式
/loader_generate --complexity simple  # 按复杂度筛选
```

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
| loadergen-agent | 使用外部代码，使用外部 shellcode | 仅使用 samples/calc.bin |
| evasion-agent | 使用外部代码，执行恶意 shellcode | 仅修改用户代码，仅用 calc.bin 测试 |

## License

MIT
