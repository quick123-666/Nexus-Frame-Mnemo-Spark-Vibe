#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV 全能安装程序 (All-in-One Installer)
功能：自动检测环境、安装依赖、验证模块、配置项目结构、集成外部组件。
"""

import os
import sys
import subprocess
import shutil
import platform
import json
from pathlib import Path

# 颜色输出支持
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_status(msg, status="INFO"):
    colors = {
        "INFO": Colors.OKCYAN,
        "SUCCESS": Colors.OKGREEN,
        "WARNING": Colors.WARNING,
        "ERROR": Colors.FAIL,
        "STEP": Colors.OKBLUE
    }
    color = colors.get(status, "")
    print(f"{color}[{status}]{Colors.ENDC} {msg}")

def run_cmd(cmd, check=True):
    print(f"{Colors.HEADER}> {cmd}{Colors.ENDC}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print_status(f"Command failed: {e.stderr}", "ERROR")
        return False

class NFMSVInstaller:
    def __init__(self):
        self.project_root = Path(__file__).parent.resolve()
        self.os_type = platform.system()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        # 核心依赖清单
        self.core_deps = [
            "fastapi", "uvicorn[standard]", "pydantic", "websockets",
            "httpx", "aiofiles", "jinja2", "python-multipart",
            "psutil", "colorama", "pyyaml", "requests"
        ]
        
        # 视觉自动化依赖 (Mano-P)
        self.visual_deps = ["mss", "pynput", "pillow", "customtkinter"]
        
        # AI 知识库依赖
        self.ai_deps = ["llmwikify", "fastmcp"]
        
        # 开发/工具依赖
        self.dev_deps = ["pytest", "black", "flake8"]

    def check_environment(self):
        print_status("Step 1: 环境检测", "STEP")
        
        # 检查 Python 版本
        if sys.version_info < (3, 10):
            print_status(f"Python 版本过低: {self.python_version} (需要 >= 3.10)", "ERROR")
            return False
        print_status(f"Python 版本: {self.python_version} (通过)", "SUCCESS")
        
        # 检查 pip
        if not run_cmd("pip --version", check=False):
            print_status("pip 未找到，请先安装 pip", "ERROR")
            return False
            
        # 检查系统信息
        print_status(f"操作系统: {self.os_type} {platform.release()}", "INFO")
        return True

    def install_dependencies(self, category="all"):
        print_status(f"Step 2: 安装依赖 [{category}]", "STEP")
        
        deps_to_install = []
        if category in ["all", "core"]:
            deps_to_install.extend(self.core_deps)
        if category in ["all", "visual"]:
            deps_to_install.extend(self.visual_deps)
        if category in ["all", "ai"]:
            deps_to_install.extend(self.ai_deps)
        if category in ["all", "dev"]:
            deps_to_install.extend(self.dev_deps)
            
        # 去重
        deps_to_install = list(set(deps_to_install))
        
        # 生成 requirements.txt
        req_file = self.project_root / "requirements.txt"
        with open(req_file, "w", encoding="utf-8") as f:
            f.write("\n".join(deps_to_install))
            
        print_status(f"正在安装 {len(deps_to_install)} 个依赖包...", "INFO")
        if run_cmd(f'pip install -r "{req_file}"'):
            print_status("依赖安装成功", "SUCCESS")
            return True
        else:
            print_status("部分依赖安装失败，请检查网络或权限", "WARNING")
            return False

    def verify_modules(self):
        print_status("Step 3: 模块完整性验证", "STEP")
        
        modules = [
            "frame", "knowledge", "llm", "memory-bank", "mnemo", 
            "nexus", "scripts", "spark", "templates", "tools", 
            "vibe", "visual", "web"
        ]
        
        missing = []
        for mod in modules:
            mod_path = self.project_root / mod
            if not mod_path.exists():
                missing.append(mod)
                
        if missing:
            print_status(f"缺失模块: {', '.join(missing)}", "ERROR")
            return False
            
        print_status(f"所有 {len(modules)} 个核心模块均存在", "SUCCESS")
        return True

    def verify_builtin_integrations(self):
        print_status("Step 4: 内置模块验证", "STEP")
        
        # Nexus-Medic-Team 已内置在 nexus/ 目录中
        medic_path = self.project_root / "nexus" / "medic_team.py"
        if medic_path.exists():
            print_status("Nexus-Medic-Team (智能修复): ✅ 已内置", "SUCCESS")
        else:
            print_status("Nexus-Medic-Team: ❌ 未找到 (应位于 ./nexus/medic_team.py)", "ERROR")
            return False
        return True

    def check_external_integrations(self):
        print_status("Step 5: 外部组件集成检查", "STEP")
        
        integrations = {
            "Mercury-Crab-Agent (记忆库)": "../Mercury-Crab-Agent",
            "Mano-P (视觉自动化)": "./visual",
        }
        
        for name, rel_path in integrations.items():
            target = (self.project_root / rel_path).resolve()
            if target.exists():
                print_status(f"{name}: ✅ 已集成", "SUCCESS")
            else:
                print_status(f"{name}: ⚠️ 未找到 (路径: {target})", "WARNING")
                
    def generate_config(self):
        print_status("Step 5: 配置文件生成", "STEP")
        
        config_path = self.project_root / "config.yaml"
        if config_path.exists():
            print_status("config.yaml 已存在，跳过生成", "INFO")
        else:
            # 生成默认配置
            default_config = """# NFM-SV 默认配置
project:
  name: "nexus-frame-mnemo-spark-vibe"
  memory_bank_path: "./memory-bank"
  
llm:
  provider: "openai"
  base_url: "https://api.example.com/v1"
  api_key: "your-api-key-here"
  model: "gpt-4o"
  
frame:
  db_path: "./frame/rules.db"
"""
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(default_config)
            print_status("已生成默认 config.yaml", "SUCCESS")

    def setup_windows_shortcuts(self):
        if self.os_type != "Windows":
            return
            
        print_status("Step 6: 创建 Windows 快捷方式", "STEP")
        
        # 创建启动脚本
        start_bat = self.project_root / "start_nfm_sv.bat"
        content = f'''@echo off
echo 正在启动 NFM-SV...
cd /d "{self.project_root}"
python -m uvicorn web.server:app --host 0.0.0.0 --port 8000 --reload
pause
'''
        with open(start_bat, "w", encoding="utf-8") as f:
            f.write(content)
        print_status("已创建 start_nfm_sv.bat", "SUCCESS")

    def run_full_install(self):
        print(f"\n{Colors.BOLD}=== NFM-SV 全能安装程序 ==={Colors.ENDC}\n")
        
        if not self.check_environment():
            return
            
        self.install_dependencies("all")
        self.verify_modules()
        self.verify_builtin_integrations()
        self.check_external_integrations()
        self.generate_config()
        self.setup_windows_shortcuts()
        
        print(f"\n{Colors.OKGREEN}安装完成！{Colors.ENDC}")
        print("运行方式: python -m uvicorn web.server:app --reload 或双击 start_nfm_sv.bat")

if __name__ == "__main__":
    installer = NFMSVInstaller()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "check":
            installer.check_environment()
        elif cmd == "deps":
            cat = sys.argv[2] if len(sys.argv) > 2 else "all"
            installer.install_dependencies(cat)
        elif cmd == "verify":
            installer.verify_modules()
    else:
        installer.run_full_install()
