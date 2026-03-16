# Evasion Agent Teams 项目说明

## 项目目标

构建一个免杀 subAgent teams，主 agent 是 Claude Code。所有 subagent 都接入 Claude Code，通过对话调用这些子 agent。

## Sub Agents

1. **research-agent**: 使用 gh 工具搜索 shellcode loader 或 evasion 相关代码，将技术点分类总结，写入知识库
2. **loadergen-agent**: 从知识库里提取技术点，实现 shellcode loader 编写
3. **evasion-agent**: 对现有 loader 进行免杀技术集成
4. **c2-evasion-agent**: 分析 C2 框架源码，查找检测规则，直接修改 C2 源码实现免杀

## 目录结构

```
.claude/
├── agents/           # Sub-agent 定义
│   ├── research-agent.md
│   ├── loadergen-agent.md
│   └── evasion-agent.md
├── commands/         # 用户可调用命令
│   ├── research.md
│   ├── loader_generate.md
│   ├── evasion_integrate.md
│   └── c2_evasion.md
├── skills/           # Agent 技能详细说明
│   ├── research.md
│   ├── loader_generate.md
│   ├── evasion_integrate.md
│   └── c2_evasion.md
├── settings.local.json
└── README.md

knowledge-base/       # 知识库
├── loader_techniques.json
├── evasion_techniques.json
└── scenarios.json

lib/                  # 工具库
└── knowledge_manager.py

samples/              # 测试样本
└── calc.bin

output/               # 输出目录
```

## 使用方式

- `/research` - 搜索并研究技术
- `/loader_generate` - 生成 shellcode loader
- `/evasion_integrate` - 对现有 loader 集成免杀技术
- `/c2_evasion` - 对 C2 框架进行免杀改造
