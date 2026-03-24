# VanceSender EMS

面向 FiveM EMS / 医疗 RP 场景的 `/me` `/do` 文本发送器，集成 AI 生成、AI 改写、医疗辅助工具、桌面壳与 WebUI。

## 功能一览

### 核心发送
- **单条发送 / 批量发送**：模拟键盘将文本发送到 FiveM 聊天框
- **实时进度与取消**：批量发送支持 SSE 进度反馈与中途取消
- **发送历史**：查看最近发送结果并快速重发
- **预设联动**：可直接将预设、医疗模板、AI 结果导入发送列表

### EMS / 医疗辅助
- **医疗场景模板**：常用 EMS 场景模板快速取用
- **医疗快捷短语**：按分类整理的常用医疗 RP 文本
- **随机生命体征**：按伤情程度生成生命体征与 `/do` 描述
- **SBAR 交接生成器**：快速生成交接报告文本
- **医疗连招组合**：预设组合场景一键导入
- **医疗术语速查**：支持分类与关键词检索

### AI 能力
- **AI 生成**：按场景生成 `/me` `/do` 文本
- **流式生成**：支持实时返回生成结果
- **AI 改写**：支持单条文本改写与整套预设改写
- **高级 AI 对话策划**：基于分支节点推进对话 / 剧情
- **AI 生成历史**：支持收藏、加载、删除、清理未收藏记录
- **多服务商支持**：当前配置模型支持 **OpenAI 兼容接口** 与 **Google Gemini**，示例内置 OpenAI / DeepSeek / Gemini

### 桌面与访问方式
- **桌面内嵌窗口**：基于 pywebview 的原生桌面壳
- **浏览器回退模式**：桌面窗口不可用时自动回退浏览器模式
- **系统托盘**：支持启动驻留、托盘恢复主窗口
- **快捷悬浮窗**：默认启用，支持热键（默认 `F7`）和侧键触发
- **局域网访问**：支持 LAN 模式、局域网地址展示与二维码访问
- **可选鉴权**：支持 `Bearer Token` 保护全部 `/api/v1/*`

### 其他
- **预设管理**：创建、编辑、删除、排序、导入导出、批量删除
- **统计面板**：发送次数、成功率、批量发送次数、失败数
- **远程公告**：支持通过公共配置源拉取公告内容
- **更新检查**：启动后检查 GitHub 新版本
- **多语言界面**：当前内置简体中文与 English
- **启动引导页**：可通过配置启用首次启动介绍页

## 快速开始

1. 前往 [GitHub Releases](https://github.com/vancehuds/VanceSender/releases/latest) 下载最新版
2. 解压压缩包
3. 运行 `VanceSender.exe`

### 运行后的访问入口

- WebUI：`http://127.0.0.1:8730/`
- Swagger 文档：`http://127.0.0.1:8730/docs`
- OpenAPI：`http://127.0.0.1:8730/openapi.json`

如果启用了局域网访问，程序也会显示对应的 LAN 地址与文档地址。

## 运行模式

### 1. 桌面内嵌窗口模式
默认模式。若系统可用 pywebview / WebView2，程序会以内嵌桌面窗口启动。

### 2. 浏览器模式
以下情况会自动进入浏览器模式：
- 启动参数使用 `--no-webview`
- 本机缺少 pywebview / WebView2 支持
- 内嵌窗口启动失败

### 3. 局域网模式
可通过以下任一方式启用：
- 启动参数：`python main.py --lan`
- 配置项：`server.lan_access: true`

启用后服务会绑定到 `0.0.0.0`，适合手机、平板或同局域网设备访问。若同时未设置 Token，局域网内任意设备都可访问 API，建议配合 `server.token` 一起使用。

## 运行时文件位置

打包版默认将可写配置和数据放在：

- `%LOCALAPPDATA%\VanceSender\config.yaml`
- `%LOCALAPPDATA%\VanceSender\data\presets\*.json`
- `%LOCALAPPDATA%\VanceSender\data\ai_history\gen_*.json`
- `%LOCALAPPDATA%\VanceSender\data\stats.json`

说明：
- `config.yaml` 会在首次保存设置后生成
- 预设、AI 生成历史、统计数据会持久化保存
- **发送历史仅保存在内存中，程序重启后会清空**
- **未收藏的 AI 生成历史最多保留 100 条，超过后会自动清理旧记录**
- 统计数据采用批量写盘策略，不会在每次发送后立刻落盘；即使正常关闭，最近少量统计也可能尚未来得及写入
- 程序会将内置默认预设复制到可写预设目录中，缺失时自动补齐

## 使用方式

### 发送文本
1. 打开 WebUI 发送面板
2. 输入文本（每行一条；无前缀默认按 `/me` 处理）
3. 导入发送列表后，确保 FiveM 在前台
4. 选择单条发送或批量发送

### 使用医疗辅助工具
- 在医疗助手面板中选择模板、快捷短语或连招组合
- 使用随机生命体征生成功能补充 `/do` 描述
- 需要正式交接时可填写 SBAR 四要素并直接生成交接文本
- 医疗术语速查可用于现场快速组织 RP 用语

### 使用 AI
- **AI 生成**：输入场景、文本类型、风格后生成 RP 文本
- **AI 改写**：支持重写单条文本或整个预设
- **高级 AI 对话策划**：用于分支式推进对话、剧情或问答场景
- **AI 生成历史**：可收藏常用结果，避免被一键清理删除

## 配置说明

`config.yaml.example` 为模板，`config.yaml` 为实际运行配置。

```yaml
server:
  host: 127.0.0.1
  port: 8730
  lan_access: false
  token: ''

launch:
  enable_tray_on_start: true
  close_action: ask              # ask / minimize_to_tray / exit
  open_webui_on_start: false
  open_intro_on_first_start: false
  show_console_on_start: false

sender:
  method: clipboard              # clipboard 或 typing
  chat_open_key: t
  delay_open_chat: 450
  delay_after_paste: 160
  delay_after_send: 260
  delay_between_lines: 1800
  focus_timeout: 8000
  retry_count: 3
  retry_interval: 450
  typing_char_delay: 18

quick_overlay:
  enabled: true
  show_webui_send_status: true
  compact_mode: true
  trigger_hotkey: f7
  mouse_side_button: ''
  poll_interval_ms: 40

public_config:
  source_url: ''
  timeout_seconds: 5
  cache_ttl_seconds: 120

ai:
  providers:
    - id: openai
      name: OpenAI
      type: openai
      api_base: https://api.openai.com/v1
      api_key: sk-your-openai-key
      model: gpt-4o-mini
    - id: deepseek
      name: DeepSeek
      type: openai
      api_base: https://api.deepseek.com/v1
      api_key: sk-your-deepseek-key
      model: deepseek-chat
    - id: gemini
      name: Google Gemini
      type: gemini
      api_key: your-gemini-api-key
      model: gemini-2.0-flash
  default_provider: openai
```

说明：
- 上方 YAML 片段用于展示常见配置项，示例值以仓库内 `config.yaml.example` 为准
- `quick_overlay.compact_mode` 在示例模板中为 `true`，但当该字段缺失时程序运行时回退值为 `false`
- 首次启动介绍页与 WebUI 内部 onboarding 属于两套独立状态，完成标记均由程序自动维护，通常无需手动编辑

### 常用配置项

| 配置项 | 说明 |
|--------|------|
| `server.port` | WebUI / API 服务端口，默认 `8730` |
| `server.lan_access` | 是否允许局域网访问 |
| `server.token` | 非空时启用 Bearer Token 鉴权 |
| `launch.enable_tray_on_start` | 启动时启用系统托盘 |
| `launch.close_action` | 关闭行为：询问 / 最小化到托盘 / 直接退出 |
| `launch.open_webui_on_start` | 启动时自动打开浏览器 |
| `launch.open_intro_on_first_start` | 是否启用首次启动介绍页 |
| `launch.show_console_on_start` | 打包运行时显示控制台日志窗口 |
| `sender.method` | 发送模式：`clipboard` 或 `typing` |
| `sender.chat_open_key` | FiveM 聊天键，默认 `t` |
| `quick_overlay.enabled` | 是否启用快捷悬浮窗 |
| `quick_overlay.trigger_hotkey` | 快捷悬浮窗触发热键，默认 `f7` |
| `quick_overlay.show_webui_send_status` | 悬浮窗显示 WebUI 发送状态 |
| `public_config.source_url` | 远程公告 / 公共配置地址 |
| `ai.providers` | AI 服务商列表，支持 OpenAI 兼容接口与 Gemini |

## API 文档

- 详细接口说明：[`docs/API.md`](docs/API.md)
- 运行时交互文档：`http://127.0.0.1:8730/docs`
- API Base URL：`http://127.0.0.1:8730/api/v1`

当前 API 主要包含：
- `/send/*`：发送、批量发送、取消、状态
- `/presets/*`：预设管理、导入导出、排序等
- `/ai/*`：AI 生成、流式生成、改写、对话策划、历史等
- `/settings/*`：配置、更新检查、远程公告、桌面窗口控制等
- `/stats/*`：发送统计
- `/medical/*`：医疗模板、术语、生命体征、快捷短语、连招、SBAR

当 `server.token` 为空时，不启用鉴权。
当 `server.token` 非空时，所有 `/api/v1/*` 请求都需要：

```http
Authorization: Bearer <your-token>
```

## 项目结构

```text
VanceSenderEMS/
├── main.py
├── requirements.txt
├── package.json
├── vancesender.spec
├── config.yaml.example
├── public-config.yaml
├── README.md
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── schemas.py
│   │   └── routes/
│   │       ├── ai.py
│   │       ├── medical.py
│   │       ├── presets.py
│   │       ├── sender.py
│   │       ├── settings.py
│   │       └── stats.py
│   ├── core/
│   │   ├── ai_client.py
│   │   ├── ai_conversation_tree.py
│   │   ├── ai_gemini.py
│   │   ├── ai_history.py
│   │   ├── config.py
│   │   ├── desktop_shell.py
│   │   ├── medical_combos.py
│   │   ├── medical_glossary.py
│   │   ├── medical_quick_phrases.py
│   │   ├── medical_templates.py
│   │   ├── medical_vitals_generator.py
│   │   ├── presets.py
│   │   ├── quick_overlay.py
│   │   ├── runtime_paths.py
│   │   ├── sender.py
│   │   ├── stats.py
│   │   └── update_checker.py
│   └── web/
│       ├── index.html
│       ├── intro.html
│       ├── help.html
│       ├── css/
│       └── js/
│           ├── app.js
│           ├── help.js
│           ├── i18n.js
│           └── medical.js
├── data/
│   └── presets/
├── docs/
│   ├── API.md
│   ├── github-pages.md
│   ├── update-check-optimization.md
│   └── windows-start-bat.md
└── pages/
    ├── index.html
    └── help.html
```

## 开发环境

### 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python 3.10+、FastAPI、Uvicorn、Pydantic v2 |
| AI 接口 | OpenAI SDK、Google GenAI SDK、HTTPX |
| 桌面集成 | pywebview、pystray、Pillow |
| 前端 | HTML / CSS / JavaScript、Tailwind CSS v3 |
| 打包 | PyInstaller |

### 本地开发

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装前端工具链（用于样式构建）
npm install

# 本地启动
python main.py

# 启用局域网访问
python main.py --lan

# 自定义端口
python main.py --port 9000

# 禁用内嵌桌面窗口，仅使用浏览器模式
python main.py --no-webview
```

### 打包

```bash
pyinstaller vancesender.spec
```

## 常见问题

**Q: 发送没有反应？**
A: 先确认 FiveM 在前台。必要时增大 `delay_open_chat`、`focus_timeout`、`retry_count`。

**Q: 聊天键不是 `T` 怎么办？**
A: 修改 `sender.chat_open_key`，例如 `y`。

**Q: 中文发送异常？**
A: 优先使用 `sender.method: clipboard`。

**Q: 局域网模式下手机无法访问？**
A: 检查 Windows 防火墙、端口放行和当前网络是否互通；如已开启 Token，确认请求携带正确 `Authorization` 头。

**Q: 启动时提示端口被占用？**
A: 程序内置端口占用检测。关闭占用该端口的进程，或改用 `--port` 指定新端口。

**Q: 内嵌窗口无法显示？**
A: 需要系统安装 WebView2 Runtime。若缺失会自动回退到浏览器模式。

**Q: 为什么发送历史重启后没了？**
A: 发送历史是内存数据，不会落盘；预设、AI 生成历史和统计数据会持久化保存。

## 许可证

[GPL v3](LICENSE)
