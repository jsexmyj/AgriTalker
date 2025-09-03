import tempfile
import os
from datetime import datetime

from backend.config.config import ConfigManager



# 1. 创建一个带时间戳的全局临时根目录
PROGRAM_START_TIME = datetime.now().strftime("%Y%m%d_%H%M%S")
CONFIG_TEMP_DIR = ConfigManager.get("temp_dir") or tempfile.gettempdir()
SESSION_TEMP_ROOT = os.path.join(CONFIG_TEMP_DIR, f"{PROGRAM_START_TIME}")
os.makedirs(SESSION_TEMP_ROOT, exist_ok=True)

def mkd_temp(prefix="tmp", suffix="", dir=None):
    """
    在统一的 SESSION_TEMP_ROOT 下创建临时子文件夹

    :param prefix: 子文件夹名称前缀
    :param suffix: 子文件夹名称后缀
    :param subdir: 若指定子目录，则在该子目录下创建（可选）
    :return: 创建的临时目录路径
    """
    base_dir = dir if dir else SESSION_TEMP_ROOT
    os.makedirs(base_dir, exist_ok=True)
    return tempfile.mkdtemp(prefix=prefix, suffix=suffix, dir=base_dir)

def cleanup_all():
    """
    清理整个 SESSION_TEMP_ROOT 目录（慎用）
    """
    import shutil
    shutil.rmtree(SESSION_TEMP_ROOT)