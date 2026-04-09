# Stowaway 检测特征分析

## 概述

除了字符串特征外，Stowaway 还有多种可被检测的行为特征。本文档分析所有潜在的检测向量。

---

## 1. 网络协议指纹

### 1.1 认证握手

| 特征 | 描述 | 检测难度 |
|------|------|----------|
| 认证Token | 16字节 MD5(secret)[:16] | 高 - 需要密钥才能识别 |
| 握手流程 | 客户端发送16字节 → 服务端返回16字节 | 中 - 固定长度握手 |

**位置:** `share/preauth.go`

```
认证流程:
1. 客户端连接 → 发送 AuthToken (16字节)
2. 服务端验证 → 返回 AuthToken (16字节)
3. 双方确认 → 开始加密通信
```

**检测方法:**
- 网络流量中连续两个16字节相同数据包
- 首包固定16字节特征

### 1.2 消息头结构

| 字段 | 长度 | 描述 |
|------|------|------|
| Sender | 10字节 | 发送者UUID |
| Accepter | 10字节 | 接收者UUID |
| MessageType | 2字节 | 消息类型 |
| RouteLen | 4字节 | 路由长度 |
| Route | 变长 | 路由信息 |
| DataLen | 8字节 | 数据长度 |
| Data | 变长 | 加密数据 |

**位置:** `protocol/raw.go`

**检测方法:**
- 固定的10+10+2+4字节头部模式
- UUID特征: `NODE-CTRL-01` (10字节), `NODE-JOIN-00` (10字节), `EMPTY-ROUTE-00` (14字节)

### 1.3 加密特征

| 加密方式 | 实现 | 位置 |
|----------|------|------|
| AES-256-GCM | 默认加密 | `crypto/aes.go` |
| GZIP压缩 | 数据压缩 | `crypto/gzip.go` |
| TLS | 可选加密 | `share/transport/tls.go` |

**数据包结构:**
```
原始数据 → GZIP压缩 → AES-256-GCM加密 → 发送
```

**检测方法:**
- AES-GCM 认证标签 (16字节) 在加密数据末尾
- GZIP 魔数 `1f 8b` 在解密后的数据中

---

## 2. 行为特征

### 2.1 端口复用技术

| 技术 | 平台 | 检测方法 |
|------|------|----------|
| SO_REUSEPORT/SO_REUSEADDR | Windows, macOS, Linux | 端口共享检测 |
| iptables REDIRECT | Linux only | iptables规则检测 |

**位置:** `agent/initial/method.go`

**检测方法:**
- 监控 `setsockopt(SO_REUSEPORT)` 调用
- 检测异常的端口复用行为
- iptables 规则审计

### 2.2 连接模式

| 模式 | 描述 | 检测特征 |
|------|------|----------|
| 主动连接 | agent → admin | 出站长连接 |
| 被动监听 | admin 监听端口 | 入站连接 |
| 重连机制 | 定时重连 | 固定间隔重连 |
| 代理链 | 多跳代理 | 多级TCP连接 |

**检测方法:**
- 长连接心跳检测
- 固定重连间隔 (可通过 `--reconnect` 配置)
- 多跳网络拓扑分析

### 2.3 进程行为

| 行为 | 描述 | 检测方法 |
|------|------|----------|
| Shell执行 | 远程命令执行 | 进程链分析 |
| SOCKS代理 | 流量转发 | 网络连接分析 |
| 端口转发 | 本地/远程端口映射 | 端口监听检测 |
| 文件传输 | 上传/下载 | 文件操作监控 |

---

## 3. 二进制特征

### 3.1 Go 编译特征

| 特征 | 描述 | 检测难度 |
|------|------|----------|
| Go运行时 | 固定的运行时代码 | 低 - 所有Go程序共享 |
| 函数名 | 反射保留的函数名 | 中 - 可混淆 |
| 字符串表 | 所有字符串 | 低 - 可提取 |
| 导入表 | Go模块路径 | 中 - 已修改为ProxyNode |

### 3.2 未修改的特征

| 特征 | 当前值 | 建议 |
|------|--------|------|
| Go版本 | go 1.13 | 升级Go版本 |
| 编译标志 | `-trimpath -ldflags "-w -s"` | 可添加混淆 |
| 模块路径 | ProxyNode/ | ✅ 已修改 |

---

## 4. 网络流量检测

### 4.1 流量模式

```
典型流量特征:
1. TCP长连接
2. 加密数据传输
3. 固定的消息头结构 (34字节基本头)
4. 心跳包 (可选)
```

### 4.2 WebSocket 模式

当使用 `--up ws` 或 `--down ws` 时:

| 特征 | 描述 |
|------|------|
| 协议 | WebSocket |
| 路径 | 默认 `/` |
| 握手 | 标准 WS 握手 |

### 4.3 HTTP 模式

当使用 `--up http` 或 `--down http` 时:

| 特征 | 描述 |
|------|------|
| Content-Type | 自定义 |
| 请求方法 | POST |
| User-Agent | Go HTTP 客户端默认 |

---

## 5. 命令行参数检测

### 5.1 可检测的参数组合

| 参数组合 | 风险 | 建议 |
|----------|------|------|
| `--socks5-proxy` + `--socks5-proxyu` + `--socks5-proxyp` | 高 | 避免同时使用 |
| `--reconnect` + 固定间隔 | 中 | 随机化重连间隔 |
| `--tls-enable` + `--domain` | 低 | 常见配置 |
| `--rehost` + `--report` | 高 | 端口复用特征 |

### 5.2 参数特征 (Sigma 规则可能)

```yaml
# 示例检测规则
detection:
  selection:
    Image|endswith:
      - '\ctrl.exe'
      - '\node.exe'
    CommandLine|contains|all:
      - '--socks5-proxy'
      - '--socks5-proxyu'
      - '--socks5-proxyp'
  condition: selection
```

---

## 6. 减少检测风险的建议

### 6.1 已实施 ✅

- [x] 修改模块路径 (Stowaway → ProxyNode)
- [x] 修改二进制名称 (stowaway_admin → ctrl, stowaway_agent → node)
- [x] 修改协议标识符 (IAMADMINXD → NODE-CTRL-01)
- [x] 修改启动日志
- [x] 修改Banner字符串

### 6.2 建议实施

| 改进 | 难度 | 效果 |
|------|------|------|
| 修改消息头结构 | 高 | 破坏协议指纹 |
| 随机化UUID长度 | 中 | 破坏固定长度检测 |
| 添加流量混淆 | 高 | 模拟正常流量 |
| 修改握手协议 | 中 | 破坏认证指纹 |
| 使用garble混淆 | 低 | 混淆二进制 |

### 6.3 Go 混淆工具

```bash
# 使用 garble 混淆编译
go install mvdan.cc/garble@latest
garble -tiny -literals -seed=random build -o build/node.exe ./agent
garble -tiny -literals -seed=random build -o build/ctrl.exe ./admin
```

---

## 7. 检测规则示例

### 7.1 YARA 规则 (网络行为)

```yara
rule Stowaway_Network_Pattern {
    meta:
        description = "检测 Stowaway 协议特征"
        
    strings:
        // UUID 固定长度特征 (10字节)
        $uuid_pattern = { [10] [10] ?? ?? ?? ?? ?? ?? }
        
        // 消息类型范围
        $message_types = { 00 00 - 2F 00 }
        
    condition:
        // 34字节固定头部
        uint16(20) < 0x30 and
        uint32(22) < 0x1000
}
```

### 7.2 Sigma 规则 (进程行为)

```yaml
title: ProxyNode/Stowaway 行为检测
status: experimental
logsource:
    category: process_creation
detection:
    selection:
        Image|endswith:
            - '\ctrl.exe'
            - '\node.exe'
        CommandLine|contains:
            - '--socks5-proxy'
            - '--tls-enable'
            - '--reconnect'
    condition: selection
```

---

## 8. 总结

| 检测类别 | 当前风险 | 修改后风险 |
|----------|----------|------------|
| 字符串检测 | 高 | 低 ✅ |
| 协议指纹 | 中 | 中 |
| 行为检测 | 中 | 中 |
| 网络流量 | 中 | 中 |
| 命令行参数 | 高 | 高 |

**优先改进建议:**
1. 使用 `garble` 进行二进制混淆
2. 修改协议头结构 (UUID长度、消息格式)
3. 添加流量伪装层
4. 随机化重连间隔
