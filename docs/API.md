# VanceSender EMS API 文档

Base URL：`http://127.0.0.1:8730/api/v1`

运行后可通过以下地址查看在线文档：

- Swagger UI：`http://127.0.0.1:8730/docs`
- OpenAPI JSON：`http://127.0.0.1:8730/openapi.json`

说明：当 Cloudflare Tunnel 正在运行时，这两个地址会被运行时隐藏，以降低外网暴露面。

除 SSE 接口（`/send/batch`、`/ai/generate/stream`）外，请求与响应均为 JSON。

---

## 目录

- [认证（可选）](#认证可选)
- [通用数据结构](#通用数据结构)
- [发送接口](#发送接口)
- [AI 接口](#ai-接口)
- [预设接口](#预设接口)
- [设置与系统接口](#设置与系统接口)
- [统计接口](#统计接口)
- [医疗接口](#医疗接口)
- [常见错误码](#常见错误码)

---

## 认证（可选）

所有 `/api/v1/*` 路由都挂载了统一鉴权依赖：

- 当 `server.token` 为空：不启用认证
- 当 `server.token` 非空：必须携带 Bearer Token

```http
Authorization: Bearer <your-token>
```

认证失败时：

```json
{
  "detail": "未授权访问，请提供有效的 Token"
}
```

并附带响应头：

```http
WWW-Authenticate: Bearer
```

---

## 通用数据结构

### TextLine

```json
{
  "type": "me",
  "content": "推开了房门"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | 支持 `me` / `do` / `b` / `e` |
| `content` | string | 文本内容 |

### MessageResponse

```json
{
  "message": "操作成功",
  "success": true
}
```

---

## 发送接口

### 发送单条文本

```http
POST /api/v1/send
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | 是 | 完整发送文本，如 `/me 打开车门` |
| `source` | string | 否 | `webui`（默认）或 `quick_panel` |

请求示例：

```json
{
  "text": "/me 缓缓推开了房门",
  "source": "webui"
}
```

响应示例：

```json
{
  "success": true,
  "text": "/me 缓缓推开了房门",
  "error": null
}
```

若当前正在批量发送，不会抛 HTTP 错误，而是返回：

```json
{
  "success": false,
  "text": "/me 缓缓推开了房门",
  "error": "正在批量发送中，请等待完成或取消"
}
```

---

### 批量发送文本（SSE）

```http
POST /api/v1/send/batch
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `texts` | string[] | 是 | 待发送文本数组，至少 1 条 |
| `delay_between` | int | 否 | 每条间隔(ms)，范围 `200-30000`，不传使用当前配置值 |
| `source` | string | 否 | `webui`（默认）或 `quick_panel` |

请求示例：

```json
{
  "texts": [
    "/me 缓缓走向车辆",
    "/do 男子的脚步声在停车场中回响",
    "/me 掏出车钥匙，按下解锁按钮"
  ],
  "delay_between": 2000,
  "source": "webui"
}
```

响应头：`Content-Type: text/event-stream`

常见事件：

```text
data: {"status":"sending","index":0,"total":3,"text":"/me 缓缓走向车辆"}

data: {"status":"line_result","index":0,"total":3,"success":true,"error":null,"text":"/me 缓缓走向车辆"}

data: {"status":"completed","total":3,"sent":3,"success":2,"failed":1}
```

可能出现的 `status`：

- `sending`：开始发送某一条
- `line_result`：单条发送结果
- `completed`：全部完成
- `cancelled`：被取消
- `error`：发送失败或已有任务进行中

如果已有批量任务在运行，接口会直接返回一条错误事件流，而不是普通 JSON 错误响应。

---

### 取消批量发送

```http
POST /api/v1/send/stop
```

成功示例：

```json
{
  "message": "已发送取消请求",
  "success": true
}
```

无任务时：

```json
{
  "message": "当前没有正在进行的批量发送",
  "success": false
}
```

---

### 获取发送状态

```http
GET /api/v1/send/status
```

响应示例：

```json
{
  "sending": true,
  "progress": {
    "status": "sending",
    "index": 1,
    "total": 3,
    "text": "/do 男子的脚步声在停车场中回响"
  }
}
```

---

### 获取发送历史

```http
GET /api/v1/send/history?limit=50&offset=0
```

说明：

- 历史记录仅保存在内存中，重启后清空
- 默认 `limit=50`、`offset=0`

响应示例：

```json
{
  "items": [
    {
      "id": "2f8a91c0",
      "text": "/me 抬手示意",
      "source": "webui",
      "success": true,
      "error": null,
      "timestamp": "2026-03-24T08:00:00+00:00"
    }
  ],
  "total": 1
}
```

---

### 清空发送历史

```http
DELETE /api/v1/send/history
```

响应：`MessageResponse`

---

## AI 接口

### 生成文本

```http
POST /api/v1/ai/generate
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `scenario` | string | 是 | 场景描述 |
| `provider_id` | string | 否 | 指定服务商 ID，不传则使用默认服务商 |
| `count` | int | 否 | 期望条数，范围 `1-30` |
| `text_type` | string | 否 | `mixed`（默认）/ `me` / `do` |
| `style` | string | 否 | 生成风格，长度 `1-120` |
| `temperature` | float | 否 | 生成温度，范围 `0-2` |

响应示例：

```json
{
  "texts": [
    { "type": "me", "content": "推开半掩的房门，环顾四周" },
    { "type": "do", "content": "房间内一片狼藉，家具东倒西歪" }
  ],
  "provider_id": "deepseek"
}
```

说明：

- 成功生成后会自动写入 AI 生成历史
- 常见失败状态码：`400`（参数/服务商错误）、`502`（上游 AI 服务失败）
- `detail` 可能是结构化对象，常见字段有 `message`、`error_type`、`provider_id`、`status_code`、`request_id`、`body`

---

### 流式生成文本（SSE）

```http
POST /api/v1/ai/generate/stream
```

请求体与 [生成文本](#生成文本) 相同。

响应头：`Content-Type: text/event-stream`

示例：

```text
data: /me 推开

data: 半掩的房门

data: /do 房间内一片狼藉

data: [DONE]
```

说明：

- 每条 `data:` 是模型输出的一段文本
- 前端负责拼接后再解析
- 正常结束标记为 `[DONE]`
- 成功结束后也会尝试写入 AI 生成历史

---

### 重写文本

```http
POST /api/v1/ai/rewrite
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `texts` | TextLine[] | 是 | 需要重写的文本列表，范围 `1-80` |
| `provider_id` | string | 否 | 指定服务商 ID，不传则使用默认服务商 |
| `style` | string | 否 | 重写风格，长度 `1-120` |
| `requirements` | string | 否 | 额外要求，长度 `1-500` |
| `temperature` | float | 否 | 生成温度，范围 `0-2` |

响应示例：

```json
{
  "texts": [
    { "type": "me", "content": "压低脚步，慢慢逼近那辆车" },
    { "type": "do", "content": "空旷车场里，鞋底与地面的摩擦声被放大" }
  ],
  "provider_id": "deepseek"
}
```

---

### 测试服务商连接

```http
POST /api/v1/ai/test/{provider_id}
```

成功示例：

```json
{
  "message": "连接成功: Hi",
  "success": true,
  "response": "Hi",
  "error_type": null,
  "status_code": null,
  "request_id": null,
  "body": null
}
```

失败示例：

```json
{
  "message": "连接失败: Connection refused | type=APIConnectionError",
  "success": false,
  "response": null,
  "error_type": "APIConnectionError",
  "status_code": null,
  "request_id": null,
  "body": null
}
```

不存在的服务商返回 `404`。

---

### 获取 AI 生成历史

```http
GET /api/v1/ai/history?limit=20&offset=0
```

说明：

- 默认 `limit=20`、`offset=0`
- 历史项包含 `id`、`scenario`、`style`、`text_type`、`provider_id`、`texts`、`starred`、`timestamp`

响应示例：

```json
{
  "items": [
    {
      "id": "gen_1a2b3c4d",
      "scenario": "急救人员正在评估患者状态",
      "style": "专业、克制",
      "text_type": "mixed",
      "provider_id": "deepseek",
      "texts": [
        { "type": "me", "content": "俯身检查患者的呼吸节律" }
      ],
      "starred": false,
      "timestamp": "2026-03-24T08:00:00+00:00"
    }
  ],
  "total": 1
}
```

---

### 切换历史收藏状态

```http
POST /api/v1/ai/history/{gen_id}/star
```

说明：该接口是 **toggle** 语义，再次调用会取消收藏。

不存在的记录返回 `404`。

---

### 删除单条 AI 生成历史

```http
DELETE /api/v1/ai/history/{gen_id}
```

响应：`MessageResponse`

不存在的记录返回 `404`。

---

### 清空非收藏 AI 生成历史

```http
DELETE /api/v1/ai/history
```

说明：仅删除未收藏记录，已收藏记录会保留。

响应示例：

```json
{
  "message": "已清空 12 条非收藏记录",
  "success": true
}
```

---

### 初始化高级 AI 对话树

```http
POST /api/v1/ai/conversation-tree/init
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `scenario` | string | 是 | 场景描述 |
| `plot_style` | string | 否 | 剧情风格，长度 `<=120` |
| `provider_id` | string | 否 | 服务商 ID |
| `temperature` | float | 否 | 生成温度，范围 `0-2` |

响应示例：

```json
{
  "node": [
    { "type": "me", "content": "抬手按住对讲耳麦，低声汇报现场情况" }
  ],
  "paths": [
    { "id": 1, "label": "谨慎回应", "content": "收到，请继续评估并回报生命体征。" }
  ],
  "provider_id": "deepseek",
  "vitals": {
    "bp": "118/76",
    "hr": "92"
  }
}
```

---

### 生成下一轮对话树节点

```http
POST /api/v1/ai/conversation-tree/next
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `scenario` | string | 是 | 原始场景描述 |
| `conversation_history` | object[] | 是 | 对话历史，元素形如 `{role, content}` |
| `chosen_reply` | string | 是 | 对方的实际回复 |
| `plot_tendency` | string | 否 | 剧情倾向，长度 `<=200` |
| `plot_style` | string | 否 | 剧情风格，长度 `<=120` |
| `provider_id` | string | 否 | 服务商 ID |
| `temperature` | float | 否 | 生成温度，范围 `0-2` |

响应结构与初始化接口一致。

---

### 生成对话树收尾节点

```http
POST /api/v1/ai/conversation-tree/wrapup
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `scenario` | string | 是 | 原始场景描述 |
| `conversation_history` | object[] | 是 | 当前对话历史 |
| `provider_id` | string | 否 | 服务商 ID |
| `temperature` | float | 否 | 生成温度，范围 `0-2` |

响应示例：

```json
{
  "node": [
    { "type": "me", "content": "点头示意，结束本轮汇报并转身继续处置" }
  ],
  "provider_id": "deepseek"
}
```

---

## 预设接口

### 列出所有预设

```http
GET /api/v1/presets?tag=ems
```

说明：

- 不传 `tag` 时返回全部预设
- 传 `tag` 时按标签筛选

响应为 `PresetResponse[]`。

---

### 创建预设

```http
POST /api/v1/presets
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 名称，长度 `1-100` |
| `texts` | TextLine[] | 否 | 文本列表，默认空数组 |
| `tags` | string[] | 否 | 标签列表，最多 10 个 |
| `sort_order` | int | 否 | 排序值，默认 `0` |

响应：`201 Created` + 完整预设对象。

---

### 获取单个预设

```http
GET /api/v1/presets/{preset_id}
```

不存在返回 `404`。

---

### 更新预设

```http
PUT /api/v1/presets/{preset_id}
```

可按需传递：`name`、`texts`、`tags`、`sort_order`。

响应为更新后的完整预设对象。

---

### 删除预设

```http
DELETE /api/v1/presets/{preset_id}
```

响应：`MessageResponse`

不存在返回 `404`。

---

### 导出单个预设

```http
GET /api/v1/presets/export/{preset_id}
```

说明：

- 返回 JSON 文件下载流
- 响应头包含 `Content-Disposition`

---

### 导出全部预设

```http
GET /api/v1/presets/export/all
```

说明：

- 返回所有预设组成的 JSON 数组
- 响应头包含 `Content-Disposition: attachment`

---

### 导入预设

```http
POST /api/v1/presets/import
```

请求体支持两种形式：

- 单个预设对象
- 预设对象数组

示例：

```json
[
  {
    "name": "基础评估",
    "texts": [
      { "type": "me", "content": "蹲下检查患者意识状态" }
    ],
    "tags": ["ems", "assessment"],
    "sort_order": 10
  }
]
```

响应示例：

```json
{
  "imported": 1,
  "skipped": 0,
  "errors": [],
  "message": "成功导入 1 个预设"
}
```

---

### 重排预设顺序

```http
POST /api/v1/presets/reorder
```

请求体：

```json
{
  "ids": ["id1", "id2", "id3"]
}
```

响应：`MessageResponse`

---

### 批量删除预设

```http
POST /api/v1/presets/batch-delete
```

请求体：

```json
{
  "ids": ["id1", "id2"]
}
```

响应示例：

```json
{
  "message": "成功删除 2 个预设",
  "deleted": 2,
  "failed": 0
}
```

---

## 设置与系统接口

### 获取全部设置

```http
GET /api/v1/settings
```

返回以下 5 个区块：

- `server`
- `launch`
- `sender`
- `ai`
- `quick_overlay`
- `cloudflare_tunnel`

关键说明：

- `server.token` 不会明文返回，只会通过 `token_set` 表示是否已配置
- provider 的 `api_key` 不会明文返回，只会通过 `api_key_set` 表示是否已配置
- `server` 区块会返回运行时字段，如 `webui_url`、`docs_url`、`ui_mode`、`lan_urls`、`lan_docs_urls`
- 当开启 LAN 且未设置 Token 时，`risk_no_token_with_lan=true`
- `launch` 区块会返回 `onboarding_done` 字段，用于 WebUI onboarding 状态
- `cloudflare_tunnel` 不会返回 `tunnel_token` 或 `cloudflared_path` 明文，只返回是否已设置与运行状态

简化响应示例：

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8730,
    "lan_access": false,
    "token_set": true,
    "webui_url": "http://127.0.0.1:8730",
    "docs_url": "http://127.0.0.1:8730/docs",
    "ui_mode": "desktop",
    "lan_urls": [],
    "risk_no_token_with_lan": false,
    "security_warning": ""
  },
  "cloudflare_tunnel": {
    "enabled": false,
    "running": false,
    "public_url": "https://app.example.com",
    "local_origin": "http://127.0.0.1:8730",
    "cloudflared_path_set": true,
    "tunnel_token_set": true,
    "last_error": "",
    "access_mode": "cloudflare_access_required",
    "docs_exposed": true,
    "security_warning": ""
  },
  "launch": {
    "open_webui_on_start": false,
    "open_intro_on_first_start": false,
    "onboarding_done": false,
    "show_console_on_start": false,
    "enable_tray_on_start": true,
    "close_action": "ask"
  },
  "sender": {
    "method": "clipboard",
    "chat_open_key": "t"
  },
  "ai": {
    "default_provider": "deepseek",
    "providers": [
      {
        "id": "deepseek",
        "name": "DeepSeek",
        "type": "openai",
        "api_base": "https://api.deepseek.com/v1",
        "api_key_set": true,
        "model": "deepseek-chat"
      }
    ]
  },
  "quick_overlay": {
    "enabled": true,
    "show_webui_send_status": true,
    "compact_mode": false,
    "trigger_hotkey": "f7",
    "mouse_side_button": "",
    "poll_interval_ms": 40
  }
}
```

---

### 更新发送设置

```http
PUT /api/v1/settings/sender
```

可按需传递：

| 字段 | 类型 | 范围 |
|------|------|------|
| `method` | string | `clipboard` / `typing` |
| `chat_open_key` | string | 单字符 |
| `delay_open_chat` | int | `50-5000` |
| `delay_after_paste` | int | `50-5000` |
| `delay_after_send` | int | `50-5000` |
| `delay_between_lines` | int | `200-30000` |
| `focus_timeout` | int | `0-30000` |
| `retry_count` | int | `0-5` |
| `retry_interval` | int | `50-5000` |
| `typing_char_delay` | int | `0-200` |

响应：`MessageResponse`

如果请求体没有任何可更新字段，会返回：

```json
{
  "message": "没有需要更新的设置",
  "success": false
}
```

---

### 更新服务器设置

```http
PUT /api/v1/settings/server
```

可按需传递：

| 字段 | 类型 | 说明 |
|------|------|------|
| `lan_access` | bool | 是否开启局域网访问 |
| `token` | string | Bearer Token；传空字符串可关闭鉴权 |

说明：

- 修改 `lan_access` 时，后端会自动同步 `host`
- 仅当请求中包含 `token` 字段时，后端才会清理 token 缓存
- 当 Cloudflare Tunnel 已启用或正在运行时，不允许清空 `token`
- 部分设置需重启生效

响应：`MessageResponse`

---

### 更新 Cloudflare Tunnel 设置

```http
PUT /api/v1/settings/tunnel
```

可按需传递：

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | bool | 是否启用 Cloudflare Tunnel |
| `cloudflared_path` | string | `cloudflared` 可执行文件路径 |
| `tunnel_token` | string | 命名 Tunnel Token；保存后不会回显 |
| `public_url` | string | 公网根地址，必须为 `https://`，且不能带 query / fragment |

说明：

- 仅支持命名 Tunnel，不支持 Quick Tunnel
- 启用前必须先设置 `server.token`
- 本应用不会校验 Cloudflare Access JWT，公网域名应由 Cloudflare Access 保护
- 只返回 `tunnel_token_set` 与 `cloudflared_path_set`，不会回传明文

响应：`MessageResponse`

---

### 启动或停止 Cloudflare Tunnel

```http
POST /api/v1/settings/tunnel/action
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `action` | string | 是 | `start` 或 `stop` |

请求示例：

```json
{
  "action": "start"
}
```

说明：

- `start` 会再次校验本地 Token、`cloudflared_path`、`tunnel_token` 与 `public_url`
- `stop` 会停止当前由应用托管的 `cloudflared` 子进程

响应：`MessageResponse`

---

### 更新启动设置

```http
PUT /api/v1/settings/launch
```

可按需传递：

| 字段 | 类型 | 说明 |
|------|------|------|
| `open_webui_on_start` | bool | 启动时自动打开浏览器 |
| `open_intro_on_first_start` | bool | 首次启动是否打开介绍页 |
| `onboarding_done` | bool | WebUI onboarding 完成状态 |
| `show_console_on_start` | bool | 是否显示控制台日志窗口 |
| `enable_tray_on_start` | bool | 启动时是否启用系统托盘 |
| `start_minimized_to_tray` | bool | 旧字段输入别名，会映射到 `enable_tray_on_start` |
| `close_action` | string | `ask` / `minimize_to_tray` / `exit` |

响应：`MessageResponse`

---

### 更新 AI 设置

```http
PUT /api/v1/settings/ai
```

可按需传递：

| 字段 | 类型 | 说明 |
|------|------|------|
| `default_provider` | string | 默认服务商 ID |
| `system_prompt` | string | 系统提示词 |
| `custom_headers` | object | 自定义请求头，整体替换 |

说明：

- `default_provider` 不存在时返回 `400`
- `custom_headers` 更新为整体替换，不做深度合并

响应：`MessageResponse`

---

### 更新快捷悬浮窗设置

```http
PUT /api/v1/settings/quick-overlay
```

可按需传递：

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | bool | 是否启用悬浮窗 |
| `show_webui_send_status` | bool | 是否显示 WebUI 发送状态 |
| `compact_mode` | bool | 是否启用紧凑模式 |
| `trigger_hotkey` | string | 触发热键 |
| `mouse_side_button` | string | 侧键触发，如 `x1` / `x2` |
| `poll_interval_ms` | int | 轮询间隔，范围 `20-200` |

说明：

- `trigger_hotkey` 与 `mouse_side_button` 会在服务端转成小写后保存
- 修改后通常需重启生效

响应：`MessageResponse`

---

### 列出 AI 服务商

```http
GET /api/v1/settings/providers
```

响应示例：

```json
[
  {
    "id": "deepseek",
    "name": "DeepSeek",
    "type": "openai",
    "api_base": "https://api.deepseek.com/v1",
    "api_key_set": true,
    "model": "deepseek-chat"
  }
]
```

---

### 添加 AI 服务商

```http
POST /api/v1/settings/providers
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 否 | 自定义 ID；不传会自动生成 8 位字符串 |
| `name` | string | 是 | 显示名称 |
| `type` | string | 否 | `openai`（默认）或 `gemini` |
| `api_base` | string | 否 | OpenAI 兼容服务通常需要填写；Gemini 可留空 |
| `api_key` | string | 否 | API Key |
| `model` | string | 否 | 模型名称，默认 `gpt-4o` |

说明：若当前没有默认服务商，新建后会自动设为默认。

响应：`201 Created` + `ProviderResponse`

---

### 更新 AI 服务商

```http
PUT /api/v1/settings/providers/{provider_id}
```

可按需传递：`name`、`type`、`api_base`、`api_key`、`model`。

不存在返回 `404`。

---

### 删除 AI 服务商

```http
DELETE /api/v1/settings/providers/{provider_id}
```

响应：`MessageResponse`

说明：

- 不存在返回 `404`
- 如果删除的是当前默认服务商，后端会自动切换到剩余列表中的第一个服务商；若已无剩余服务商，则清空默认值

---

### 检查版本更新

```http
GET /api/v1/settings/update-check?include_prerelease=false
```

说明：

- `include_prerelease=true` 时允许比较预发布版本
- 返回字段包括 `success`、`current_version`、`latest_version`、`update_available`、`release_url`、`published_at`、`message`、`error_type`、`status_code`

---

### 获取远程公共配置

```http
GET /api/v1/settings/public-config
```

说明：

- 当 `public_config.source_url` 为空时，当前默认拉取地址为 `https://sender.vhuds.com/public-config.yaml`
- `public_config.source_url` 仅支持 `http://` 或 `https://` 地址
- 远程结果会按 `public_config.cache_ttl_seconds` 做内存缓存，请求超时时间由 `public_config.timeout_seconds` 控制
- 若远程配置 `enabled=false`、内容为空、解析后不可展示，接口会返回 `visible=false`
- 拉取失败、超时或网络错误时也会返回 `visible=false`，同时 `success=false`

响应字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | bool | 远程请求流程是否成功；即使远程配置不可见或不展示，也可能为 `true` |
| `visible` | bool | 是否建议在 UI 中显示 |
| `source_url` | string \| null | 实际使用的拉取地址 |
| `title` | string \| null | 展示标题 |
| `content` | string \| null | 展示内容 |
| `message` | string | 状态说明 |
| `fetched_at` | string \| null | 拉取时间 |
| `link_url` | string \| null | 可选跳转链接 |
| `link_text` | string \| null | 可选链接文本 |
| `error_type` | string \| null | 错误类型 |
| `status_code` | int \| null | 上游状态码 |

---

### 获取桌面窗口状态

```http
GET /api/v1/settings/desktop-window
```

响应示例：

```json
{
  "active": true,
  "maximized": false
}
```

---

### 控制桌面窗口

```http
POST /api/v1/settings/desktop-window/action
```

请求体：

```json
{
  "action": "toggle_maximize"
}
```

`action` 支持：

- `minimize`
- `toggle_maximize`
- `close`
- `hide_to_tray`
- `exit`

说明：

- 若当前未启用桌面内嵌窗口，返回 `400`
- 成功时返回最新窗口状态 `{active, maximized}`

---

### 控制快捷面板窗口

```http
POST /api/v1/settings/quick-panel-window/action
```

请求体：

```json
{
  "action": "dismiss"
}
```

`action` 支持：

- `minimize`
- `close`
- `dismiss`

响应：`MessageResponse`

---

### 获取系统通知

```http
GET /api/v1/settings/notifications?clear=false
```

说明：

- `clear=true` 时，读取后清空通知队列
- 返回项包含 `level`、`message`、`timestamp`

响应示例：

```json
{
  "notifications": [
    {
      "level": "warning",
      "message": "config.yaml 格式错误，已回退到默认配置。",
      "timestamp": 1711260000.0
    }
  ]
}
```

---

## 统计接口

### 获取发送统计

```http
GET /api/v1/stats
```

响应示例：

```json
{
  "total_sent": 120,
  "total_success": 115,
  "total_failed": 5,
  "total_batches": 18,
  "success_rate": 95.8,
  "most_used_presets": [
    { "name": "基础评估", "count": 24 }
  ],
  "daily_counts": {
    "2026-03-20": 12,
    "2026-03-21": 8
  }
}
```

说明：

- 统计数据为后端持久化数据
- `daily_counts` 为近 30 天聚合计数

---

### 重置发送统计

```http
DELETE /api/v1/stats
```

响应：`MessageResponse`

---

## 医疗接口

### 获取医疗模板列表

```http
GET /api/v1/medical/templates
```

返回值：

```json
{
  "templates": {
    "急救现场": [
      {
        "id": "trauma_car_accident",
        "name": "🚗 车祸创伤急救",
        "scenario": "你作为急救人员到达一起严重车祸现场..."
      }
    ],
    "医院急诊": [
      {
        "id": "er_triage",
        "name": "🏥 急诊分诊",
        "scenario": "你作为急诊值班医生，一名患者被送到急诊室..."
      }
    ],
    "日常医疗": [
      {
        "id": "routine_checkup",
        "name": "📋 日常体检",
        "scenario": "你作为值班医生，对一名来访者进行常规体格检查..."
      }
    ],
    "特殊情况": [
      {
        "id": "doa_declaration",
        "name": "⚫ 宣告死亡",
        "scenario": "你作为急救医生，经过长时间抢救..."
      }
    ]
  }
}
```

---

### 获取单个医疗模板

```http
GET /api/v1/medical/templates/{template_id}
```

不存在返回 `404`。

---

### 查询医疗术语表

```http
GET /api/v1/medical/glossary?q=休克&category=诊断
```

查询参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `q` | string | 关键词搜索 |
| `category` | string | 分类筛选 |

响应示例：

```json
{
  "items": [
    {
      "term": "休克",
      "full": "Shock",
      "cn": "休克",
      "desc": "组织灌注不足的危急状态,分低血容量/心源性/分布性等",
      "category": "诊断"
    }
  ],
  "total": 1
}
```

---

### 获取术语分类列表

```http
GET /api/v1/medical/glossary/categories
```

返回值：

```json
{
  "categories": ["评估", "体征", "急救", "治疗", "设备", "诊断", "沟通", "解剖", "无线电"]
}
```

---

### 生成随机生命体征

```http
GET /api/v1/medical/random-vitals?severity=moderate
```

`severity` 支持：

- `mild`
- `moderate`
- `severe`
- `critical`

返回值为一组医学上合理的生命体征数据，以及对应的 RP 文本。

---

### 获取医疗快捷短语

```http
GET /api/v1/medical/quick-phrases
```

返回值：

```json
{
  "phrases": {...}
}
```

按分类分组返回。

---

### 获取医疗连招列表

```http
GET /api/v1/medical/combos
```

返回值：

```json
{
  "combos": [...]
}
```

---

### 获取单个医疗连招

```http
GET /api/v1/medical/combos/{combo_id}
```

不存在返回 `404`。

---

### 生成 SBAR 交接文本

```http
POST /api/v1/medical/sbar
```

请求体：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `situation` | string | 是 | 患者情况 |
| `background` | string | 是 | 背景信息 |
| `assessment` | string | 是 | 当前评估 |
| `recommendation` | string | 是 | 建议与下一步 |

请求示例：

```json
{
  "situation": "男性，32 岁，胸痛主诉",
  "background": "办公室突发不适，无明确外伤",
  "assessment": "意识清醒，面色苍白，心率偏快",
  "recommendation": "建议立即做进一步心电与急诊评估"
}
```

响应示例：

```json
{
  "texts": [
    {
      "type": "me",
      "content": "手持患者护理报告板，面向急诊医生简明报告：\"S-情况：男性，32 岁，胸痛主诉\""
    },
    {
      "type": "me",
      "content": "\"B-背景：办公室突发不适，无明确外伤\""
    },
    {
      "type": "do",
      "content": "急救人员提供的评估信息：A-评估：意识清醒，面色苍白，心率偏快"
    },
    {
      "type": "me",
      "content": "\"R-建议：建议立即做进一步心电与急诊评估\""
    },
    {
      "type": "me",
      "content": "将患者护理报告递交给急诊医生，完成正式交接"
    },
    {
      "type": "do",
      "content": "患者护理权正式移交给院内医疗团队"
    }
  ],
  "sbar_summary": {
    "S": "男性，32 岁，胸痛主诉",
    "B": "办公室突发不适，无明确外伤",
    "A": "意识清醒，面色苍白，心率偏快",
    "R": "建议立即做进一步心电与急诊评估"
  }
}
```

---

## 常见错误码

| 状态码 | 含义 |
|--------|------|
| `400` | 请求参数错误 / 业务校验失败 |
| `401` | 未授权（Token 缺失或无效） |
| `404` | 资源不存在 |
| `422` | 请求体验证失败 |
| `502` | 上游 AI 服务失败 |

常见错误格式：

```json
{
  "detail": "错误描述"
}
```

或结构化对象：

```json
{
  "detail": {
    "message": "AI服务请求失败",
    "error_type": "APIStatusError",
    "provider_id": "openai"
  }
}
```
