# 工具管理器，连接逻辑
from backend.tools.crs_utils import reproject_polygon_if_needed
from backend.tools.geo_providers import GeoProvider
from backend.utils.logger import get_logger
from langchain_core.tools import tool
from backend.tools.cutter import Cutter

logger = get_logger("ToolManager")


class ToolManager:
    def __init__(self):
        self.aoi_bounds = None  # 用于存储查询到的AOI边界
        self.re_aoi = None  # 用于存储重投影后的AOI
        self.tif_crs = None  # 用于存储影像的CRS

    def get_tool_lists(self):
        """获取工具列表，供 LangChain Agent 使用"""

        @tool
        def cutter_tif(query: str, raster_path: str, output_path: str) -> str:
            """
            验证查询的边界是否包含在影像内部，如果合法，则裁剪影像
            Args:
                query: 查询的地点名称
                raster_path: 影像文件路径
                output_path: 裁剪后影像的保存路径

            Returns:
                output_path: 裁剪后影像的保存路径，失败时返回空字符串
            """
            is_cutter = self.validate_bounds(query, raster_path)
            if not is_cutter:
                raise ValueError("AOI边界不合法，无法裁剪影像")
            return self.cutter_tif(raster_path, output_path)

        tools = [cutter_tif]
        return tools

    def validate_bounds(self, query: str, raster_path: str) -> bool:
        """
        验证查询的边界是否与影像边界有交集
        """
        try:
            geo_provider = GeoProvider()
            self.aoi_bounds = geo_provider.fetch_aoi(query)
            self.tif_crs = geo_provider.get_tif_crs(raster_path)
            self.re_aoi = reproject_polygon_if_needed(
                self.aoi_bounds, "EPSG:4326", self.tif_crs
            )
            tif_bounds = geo_provider.fetch_tif_bounds(raster_path)
            if self.re_aoi.equals(tif_bounds) or self.re_aoi.within(tif_bounds):
                logger.info("AOI边界在影像内部，可以执行影像裁剪")
                return True
            else:
                logger.error("AOI边界超过影像边界或仅部分重合，请重新输入查询")
                return False
        except Exception as e:
            logger.error(f"验证边界时发生错误: {e}")
            return False

    def cutter_tif(self, raster_path: str, output_path: str) -> str:
        """
        裁剪影像
        """
        try:
            cutter = Cutter()
            address_polygon = self.re_aoi
            cutter.cut_by_polygon(
                raster_path=raster_path,
                addres_poly=address_polygon,
                output_path=output_path,
                polygon_crs=self.tif_crs,
            )
            return output_path
        except Exception as e:  # 捕获所有异常，防止程序崩溃
            logger.error(f"裁剪影像时发生错误: {e}")
            return ""
