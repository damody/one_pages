# -*- coding: utf-8 -*-
"""
MCP Client for mcp-yogalayout

透過 stdio JSON-RPC 與 mcp-yogalayout Rust MCP Server 溝通，
計算投影片佈局並取得 layout.json。

使用方式：
    client = YogaLayoutClient()
    client.start()
    layout = client.compute_layout(
        markdown_path="workspace/inputs/slide.md",
        theme_path="workspace/themes/default.json",
        output_dir="workspace/out"
    )
    client.stop()
"""

import subprocess
import json
import os
import time
from typing import Optional, Dict, Any


class MCPError(Exception):
    """MCP 通訊錯誤"""
    pass


class YogaLayoutClient:
    """
    透過 stdio 與 mcp-yogalayout server 溝通

    MCP 協議使用 JSON-RPC 2.0 over stdio：
    - 請求：{"jsonrpc": "2.0", "id": N, "method": "...", "params": {...}}
    - 回應：{"jsonrpc": "2.0", "id": N, "result": {...}}
    """

    DEFAULT_EXE_PATH = r"D:\mcp-yogalayout\target\release\mcp-yogalayout.exe"
    DEFAULT_CWD = r"D:\mcp-yogalayout"
    PROTOCOL_VERSION = "2024-11-05"

    def __init__(self, exe_path: str = None, cwd: str = None):
        """
        初始化 MCP Client

        Args:
            exe_path: mcp-yogalayout 執行檔路徑
            cwd: 工作目錄（Rust 程式的 workspace 根目錄）
        """
        self.exe_path = exe_path or self.DEFAULT_EXE_PATH
        self.cwd = cwd or self.DEFAULT_CWD
        self.process: Optional[subprocess.Popen] = None
        self._request_id = 0
        self._initialized = False

    def start(self):
        """
        啟動 MCP server 並進行初始化握手
        """
        if self.process is not None:
            raise MCPError("MCP server already running")

        if not os.path.exists(self.exe_path):
            raise MCPError(f"MCP server executable not found: {self.exe_path}")

        # 啟動子程序
        self.process = subprocess.Popen(
            [self.exe_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.cwd,
            bufsize=1  # 行緩衝
        )

        # 等待程序啟動
        time.sleep(0.5)

        # 檢查程序是否正常運行
        if self.process.poll() is not None:
            stderr = self.process.stderr.read()
            raise MCPError(f"MCP server failed to start: {stderr}")

        # 發送 initialize 請求
        init_result = self._send_request("initialize", {
            "protocolVersion": self.PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {
                "name": "pywin32-renderer",
                "version": "1.0.0"
            }
        })

        if "error" in init_result:
            raise MCPError(f"Initialize failed: {init_result['error']}")

        # 發送 initialized 通知
        self._send_notification("notifications/initialized", {})

        self._initialized = True

    def stop(self):
        """
        關閉 MCP server
        """
        if self.process:
            try:
                # 發送 shutdown 請求（如果支援）
                # 不等待回應，直接終止
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            finally:
                self.process = None
                self._initialized = False

    def compute_layout(
        self,
        markdown_path: str,
        theme_path: str,
        output_dir: str,
        aspect: str = "16:9",
        orientation: str = "landscape",
        template: str = "auto",
        density: str = "comfortable"
    ) -> Dict[str, Any]:
        """
        呼叫 layout.compute_slide_layout 工具計算佈局

        Args:
            markdown_path: Markdown 檔案路徑（相對於 workspace）
            theme_path: 主題 JSON 檔案路徑（相對於 workspace）
            output_dir: 輸出目錄路徑（相對於 workspace）
            aspect: 長寬比，例如 "16:9"
            orientation: 方向，"landscape" 或 "portrait"
            template: 模板，"auto" / "single_col" / "two_col"
            density: 密度，"comfortable" / "compact"

        Returns:
            dict: layout.json 的內容
        """
        if not self._initialized:
            raise MCPError("MCP client not initialized. Call start() first.")

        # 呼叫工具
        result = self._send_request("tools/call", {
            "name": "layout.compute_slide_layout",
            "arguments": {
                "markdown_path": markdown_path,
                "theme_path": theme_path,
                "output_dir": output_dir,
                "slide": {
                    "aspect": aspect,
                    "orientation": orientation,
                    "unit": "pt"
                },
                "options": {
                    "template": template,
                    "density": density,
                    "allow_two_column": True,
                    "debug_dump": False
                }
            }
        })

        if "error" in result:
            raise MCPError(f"Tool call failed: {result['error']}")

        # 取得回應中的路徑
        tool_result = result.get("result", {})

        # 讀取輸出的 layout.json
        layout_path = os.path.join(self.cwd, output_dir, "layout.json")
        if not os.path.exists(layout_path):
            # 嘗試從 tool_result 取得路徑
            if "content" in tool_result and len(tool_result["content"]) > 0:
                content = tool_result["content"][0]
                if "text" in content:
                    try:
                        paths = json.loads(content["text"])
                        layout_path = paths.get("layout_json_path", layout_path)
                    except:
                        pass

        if not os.path.exists(layout_path):
            raise MCPError(f"Layout JSON not found: {layout_path}")

        with open(layout_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_tools(self) -> list:
        """
        列出可用的 MCP 工具

        Returns:
            list: 工具列表
        """
        if not self._initialized:
            raise MCPError("MCP client not initialized. Call start() first.")

        result = self._send_request("tools/list", {})
        if "error" in result:
            raise MCPError(f"List tools failed: {result['error']}")

        return result.get("result", {}).get("tools", [])

    def _send_request(self, method: str, params: dict) -> dict:
        """
        發送 JSON-RPC 請求並等待回應

        Args:
            method: 方法名稱
            params: 參數字典

        Returns:
            dict: 回應內容
        """
        if self.process is None:
            raise MCPError("MCP server not running")

        self._request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params
        }

        # 發送請求
        request_line = json.dumps(request) + "\n"
        try:
            self.process.stdin.write(request_line)
            self.process.stdin.flush()
        except BrokenPipeError:
            stderr = self.process.stderr.read()
            raise MCPError(f"MCP server pipe broken: {stderr}")

        # 等待回應
        try:
            response_line = self.process.stdout.readline()
            if not response_line:
                stderr = self.process.stderr.read()
                raise MCPError(f"No response from MCP server: {stderr}")
            return json.loads(response_line)
        except json.JSONDecodeError as e:
            raise MCPError(f"Invalid JSON response: {response_line}, error: {e}")

    def _send_notification(self, method: str, params: dict):
        """
        發送 JSON-RPC 通知（無回應）

        Args:
            method: 方法名稱
            params: 參數字典
        """
        if self.process is None:
            raise MCPError("MCP server not running")

        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }

        notification_line = json.dumps(notification) + "\n"
        try:
            self.process.stdin.write(notification_line)
            self.process.stdin.flush()
        except BrokenPipeError:
            pass  # 通知不需要回應，忽略錯誤

    def __enter__(self):
        """Context manager 支援"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 支援"""
        self.stop()
        return False


# =============================================================================
# 便捷函數
# =============================================================================

def compute_layout_simple(
    markdown_content: str,
    output_dir: str = None,
    theme_path: str = "workspace/themes/default.json"
) -> Dict[str, Any]:
    """
    簡化版佈局計算：直接傳入 Markdown 內容

    Args:
        markdown_content: Markdown 文字內容
        output_dir: 輸出目錄（預設為臨時目錄）
        theme_path: 主題路徑

    Returns:
        dict: layout.json 的內容
    """
    import tempfile

    if output_dir is None:
        output_dir = "workspace/out"

    # 寫入臨時 Markdown 檔案
    cwd = YogaLayoutClient.DEFAULT_CWD
    md_path = os.path.join(cwd, "workspace/inputs/_temp.md")
    os.makedirs(os.path.dirname(md_path), exist_ok=True)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    # 計算佈局
    with YogaLayoutClient() as client:
        return client.compute_layout(
            markdown_path="workspace/inputs/_temp.md",
            theme_path=theme_path,
            output_dir=output_dir
        )


# =============================================================================
# 測試
# =============================================================================

if __name__ == "__main__":
    print("MCP Client 測試")
    print(f"執行檔路徑: {YogaLayoutClient.DEFAULT_EXE_PATH}")
    print(f"工作目錄: {YogaLayoutClient.DEFAULT_CWD}")

    # 檢查執行檔是否存在
    if os.path.exists(YogaLayoutClient.DEFAULT_EXE_PATH):
        print("✅ 執行檔存在")
    else:
        print("❌ 執行檔不存在，請先執行 cargo build --release")
