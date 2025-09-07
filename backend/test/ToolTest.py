import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.config.config import ConfigManager
ConfigManager.load_config()
from backend.service.tool_manager import ToolManager
tool_manager = ToolManager()

# 测试影像裁剪和坐标验证工具
raster_path = "backend/temp_data/uploads/Chengdu_432.tif"
is_cutter = tool_manager.validate_bounds("龙泉驿区", raster_path)
if is_cutter:
    output_path = tool_manager.cutter_tif(raster_path, output_path=None)


