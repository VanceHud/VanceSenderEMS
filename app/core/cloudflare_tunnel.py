from __future__ import annotations

import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


@dataclass(slots=True)
class CloudflareTunnelValidationResult:
    ok: bool
    message: str = ""


def _sanitize_secret(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        return ""
    if len(normalized) <= 6:
        return "*" * len(normalized)
    return normalized[:3] + "***"


def validate_cloudflare_tunnel_public_url(raw_url: str) -> CloudflareTunnelValidationResult:
    normalized = raw_url.strip()
    if not normalized:
        return CloudflareTunnelValidationResult(False, "请填写 Cloudflare Tunnel 公网访问地址")

    try:
        parsed = urlsplit(normalized)
    except ValueError:
        return CloudflareTunnelValidationResult(False, "公网访问地址格式无效")

    if parsed.scheme != "https":
        return CloudflareTunnelValidationResult(False, "公网访问地址必须使用 https")
    if not parsed.netloc:
        return CloudflareTunnelValidationResult(False, "公网访问地址缺少域名")
    if parsed.query or parsed.fragment:
        return CloudflareTunnelValidationResult(False, "公网访问地址不能包含查询参数或片段")
    if parsed.path not in {"", "/"}:
        return CloudflareTunnelValidationResult(False, "公网访问地址只能填写站点根地址")

    return CloudflareTunnelValidationResult(True)


def validate_cloudflare_tunnel_config(
    tunnel_cfg: dict[str, Any],
    *,
    server_token: str,
) -> CloudflareTunnelValidationResult:
    cloudflared_path = str(tunnel_cfg.get("cloudflared_path", "")).strip()
    tunnel_token = str(tunnel_cfg.get("tunnel_token", "")).strip()
    public_url = str(tunnel_cfg.get("public_url", "")).strip()

    if not server_token.strip():
        return CloudflareTunnelValidationResult(False, "请先设置访问令牌（Token）后再启用外网访问")
    if not cloudflared_path:
        return CloudflareTunnelValidationResult(False, "请先填写 cloudflared 可执行文件路径")
    if not Path(cloudflared_path).exists():
        return CloudflareTunnelValidationResult(False, "cloudflared 路径不存在，请检查后重试")
    if not tunnel_token:
        return CloudflareTunnelValidationResult(False, "请先填写 Cloudflare Tunnel Token")

    url_check = validate_cloudflare_tunnel_public_url(public_url)
    if not url_check.ok:
        return url_check

    return CloudflareTunnelValidationResult(True)


class CloudflareTunnelManager:

    def __init__(self) -> None:
        self._process: subprocess.Popen[str] | None = None
        self._lock = threading.Lock()
        self._last_error = ""
        self._runtime_port = 8730
        self._runtime_local_url = "http://127.0.0.1:8730"
        self._public_url = ""
        self._configured = False
        self._enabled = False
        self._cloudflared_path = ""
        self._tunnel_token = ""

    def configure(self, tunnel_cfg: dict[str, Any], *, runtime_port: int) -> None:
        with self._lock:
            self._runtime_port = runtime_port
            self._runtime_local_url = f"http://127.0.0.1:{runtime_port}"
            self._enabled = bool(tunnel_cfg.get("enabled", False))
            self._cloudflared_path = str(tunnel_cfg.get("cloudflared_path", "")).strip()
            self._tunnel_token = str(tunnel_cfg.get("tunnel_token", "")).strip()
            self._public_url = str(tunnel_cfg.get("public_url", "")).strip()
            self._configured = True
            if not self._enabled:
                self._last_error = ""

    def runtime_port(self) -> int:
        with self._lock:
            return self._runtime_port

    def is_enabled(self) -> bool:
        with self._lock:
            return self._enabled

    def is_running(self) -> bool:
        with self._lock:
            return self._is_running_unlocked()

    def _is_running_unlocked(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def _set_error_unlocked(self, message: str) -> None:
        self._last_error = message.strip()

    def _build_command_unlocked(self) -> list[str]:
        return [
            self._cloudflared_path,
            "tunnel",
            "run",
            "--token",
            self._tunnel_token,
        ]

    def start(self, *, server_token: str) -> CloudflareTunnelValidationResult:
        with self._lock:
            if not self._configured:
                result = CloudflareTunnelValidationResult(False, "Cloudflare Tunnel 尚未初始化")
                self._set_error_unlocked(result.message)
                return result

            validation = validate_cloudflare_tunnel_config(
                {
                    "cloudflared_path": self._cloudflared_path,
                    "tunnel_token": self._tunnel_token,
                    "public_url": self._public_url,
                },
                server_token=server_token,
            )
            if not validation.ok:
                self._set_error_unlocked(validation.message)
                return validation

            if self._is_running_unlocked():
                return CloudflareTunnelValidationResult(True, "Cloudflare Tunnel 已在运行")

            command = self._build_command_unlocked()
            try:
                self._process = subprocess.Popen(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    text=True,
                )
            except OSError:
                self._process = None
                result = CloudflareTunnelValidationResult(
                    False,
                    "cloudflared 启动失败，请确认路径、权限和 Token 是否正确",
                )
                self._set_error_unlocked(result.message)
                return result

            self._last_error = ""
            return CloudflareTunnelValidationResult(True, "Cloudflare Tunnel 已启动")

    def start_if_enabled(self, *, server_token: str) -> CloudflareTunnelValidationResult:
        with self._lock:
            if not self._enabled:
                return CloudflareTunnelValidationResult(True, "Cloudflare Tunnel 未启用")
        return self.start(server_token=server_token)

    def stop(self) -> CloudflareTunnelValidationResult:
        with self._lock:
            process = self._process
            if process is None or process.poll() is not None:
                self._process = None
                return CloudflareTunnelValidationResult(True, "Cloudflare Tunnel 当前未运行")

            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass

            self._process = None
            return CloudflareTunnelValidationResult(True, "Cloudflare Tunnel 已停止")

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "enabled": self._enabled,
                "running": self._is_running_unlocked(),
                "public_url": self._public_url,
                "local_origin": self._runtime_local_url,
                "cloudflared_path_set": bool(self._cloudflared_path),
                "tunnel_token_set": bool(self._tunnel_token),
                "last_error": self._last_error,
                "access_mode": "cloudflare_access_required",
                "docs_exposed": not self._is_running_unlocked(),
                "security_warning": (
                    "外网访问必须配合 Cloudflare Access 使用；本应用不会校验 Access JWT。"
                    if self._enabled
                    else ""
                ),
            }
