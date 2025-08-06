"""
简单的配置管理 - 加载.env文件
"""

import os


def load_env_file(env_file=".env"):
    """加载.env文件到环境变量"""
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and not os.getenv(key):
                        os.environ[key] = value
