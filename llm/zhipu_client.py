#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zhipu AI LLM Client
支持直接 API 调用和代理端点调用
"""
import os
import json
from typing import List, Dict, Optional, Iterator
from dataclasses import dataclass
import urllib.request
import urllib.error

@dataclass
class LLMMessage:
    role: str  # "system", "user", "assistant"
    content: str

@dataclass
class LLMResponse:
    content: str
    model: str
    usage: Dict = None
    finish_reason: str = "stop"

class ZhipuClient:
    """
    Zhipu AI (智谱) LLM 客户端
    
    支持:
    1. 直接 API 调用 (api.zhipuai.cn)
    2. 代理端点调用 (本地 28789 端口)
    3. 流式输出
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "glm-4-flash",
        use_proxy: bool = False,
        proxy_url: str = "http://localhost:28789/v1"
    ):
        self.model = model
        self.use_proxy = use_proxy
        
        if use_proxy:
            self.base_url = proxy_url
            self.api_key = "proxy"  # 代理模式可能不需要真实 key
        else:
            self.api_key = api_key or os.getenv("ZHIPU_API_KEY", "")
            self.base_url = base_url or "https://open.bigmodel.cn/api/paas/v4"
            
        if not self.api_key and not self.use_proxy:
            raise ValueError("请提供 ZHIPU_API_KEY 或启用代理模式")

    def chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False
    ) -> LLMResponse:
        """
        发送对话请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            stream: 是否流式输出
            
        Returns:
            LLMResponse 对象
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                if stream:
                    return self._handle_stream(response)
                else:
                    result = json.loads(response.read().decode("utf-8"))
                    return self._parse_response(result)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            raise ConnectionError(f"LLM API 错误 {e.code}: {error_body}")
        except Exception as e:
            raise ConnectionError(f"LLM 请求失败: {e}")

    def chat_simple(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        简单对话接口 (非流式)
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示 (可选)
            
        Returns:
            LLM 回复文本
        """
        messages = []
        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))
        messages.append(LLMMessage(role="user", content=prompt))
        
        response = self.chat(messages)
        return response.content

    def _parse_response(self, result: Dict) -> LLMResponse:
        """解析 API 响应"""
        choice = result.get("choices", [{}])[0]
        message = choice.get("message", {})
        return LLMResponse(
            content=message.get("content", ""),
            model=result.get("model", self.model),
            usage=result.get("usage"),
            finish_reason=choice.get("finish_reason", "stop")
        )

    def _handle_stream(self, response) -> LLMResponse:
        """处理流式响应"""
        full_content = []
        for line in response:
            line = line.decode("utf-8").strip()
            if not line.startswith("data: "):
                continue
            if line == "data: [DONE]":
                break
            try:
                chunk = json.loads(line[6:])
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                if "content" in delta:
                    full_content.append(delta["content"])
                    print(delta["content"], end="", flush=True)
            except json.JSONDecodeError:
                continue
        
        print()  # 换行
        return LLMResponse(content="".join(full_content), model=self.model)

    def generate_command(self, context: str, plan: str, rules: str) -> str:
        """
        生成 Shell 命令 (Agent 核心功能)
        
        Args:
            context: 当前上下文 (文件状态、Git 日志等)
            plan: 执行计划
            rules: 激活的规则
            
        Returns:
            生成的 Shell 命令
        """
        system_prompt = """你是一个专业的 DevOps Agent。你的任务是分析上下文和计划，生成精确的 Shell 命令来完成任务。

规则:
1. 只输出命令本身，不要解释
2. 命令必须是单行
3. 如果需要多个步骤，用 && 连接
4. 始终遵循提供的规则约束
5. 如果计划不明确，生成最合理的命令"""

        user_prompt = f"""当前上下文:
{context}

执行计划:
{plan}

激活的规则:
{rules}

请生成下一个要执行的 Shell 命令:"""

        return self.chat_simple(user_prompt, system_prompt)

    def analyze_error(self, error: str, command: str, context: str) -> str:
        """
        分析错误并生成修复命令
        
        Args:
            error: 错误信息
            command: 原始命令
            context: 当前上下文
            
        Returns:
            修复命令
        """
        system_prompt = """你是一个专业的错误修复专家。分析 Shell 命令的错误输出，生成修复命令。

规则:
1. 只输出修复命令本身
2. 命令必须是单行
3. 如果无法修复，输出 'abort'
4. 考虑常见的错误模式 (拼写错误、权限问题、依赖缺失等)"""

        user_prompt = f"""原始命令: {command}

错误输出:
{error}

当前上下文:
{context}

请生成修复命令:"""

        return self.chat_simple(user_prompt, system_prompt)
