from typing import Union
import geopandas as gpd
import osmnx as ox
from shapely import Point, Polygon
from backend.tools.crs_utils import get_epsg_code
from backend.tools.tif_utils import read_rasterio_tif
from backend.utils.logger import get_logger

logger = get_logger("GeoProvider")


class GeoProvider:
    """
    提供地理空间信息，不仅局限于边界
    目前是查询OSM提供的地点边界
    以及影像的边界信息
    """

    def __init__(self):
        pass

    def fetch_aoi(self, query: str) -> Union[Polygon, gpd.GeoDataFrame]:
        """
        根据用户查询获取感兴趣区域（AOI）
        首先尝试获取Polygon边界，如果失败则退化为Point"""
        try:
            gdf = ox.geocode_to_gdf(query)
            if gdf.geometry.iloc[0].geom_type not in ["Polygon", "MultiPolygon"]:
                raise ValueError("查询结果不是边界")
            logger.info(f"使用OSMnx方式查询：'{query}'")
            row = gdf.iloc[0]
            xmin = row["bbox_west"]
            xmax = row["bbox_east"]
            ymin = row["bbox_south"]
            ymax = row["bbox_north"]
            coords = [
                (xmin, ymin),
                (xmin, ymax),
                (xmax, ymax),
                (xmax, ymin),
                (xmin, ymin),
            ]
            logger.debug(f"转换Polygon结果：{Polygon(coords)}")
            return Polygon(coords)
        except Exception as e:
            logger.warning(f"OSMnx初始查询'{query}'失败，错误原因： {e}")
            # fallback to Point
            try:
                loc = ox.geocode(query)
                point_gdf = gpd.GeoDataFrame(
                    [{"geometry": Point(loc)}], crs="EPSG:4326"
                )
                logger.warning(f"Fallback to Point geometry for '{query}'")
                return point_gdf
            except Exception as fallback_err:
                logger.error(f"Fallback failed for '{query}': {fallback_err}")
                raise

    def fetch_tif_bounds(self, tif_path: str) -> Polygon:
        """
        获取tif文件的边界
        """
        try:
            dataset = read_rasterio_tif(tif_path)
            if dataset is None:
                logger.error(f"无法读取TIFF文件: {tif_path}")
                raise

            # 使用 rasterio 的 bounds 属性
            bounds = dataset.bounds
            xmin, ymin, xmax, ymax = bounds.left, bounds.bottom, bounds.right, bounds.top

            # 创建多边形
            bounds = Polygon([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)])
            logger.debug(f"成功获取TIFF边界: {bounds}")
            return bounds
        except Exception as e:
            logger.error(f"fetch_tif_bounds 错误: {e}")

    def get_tif_crs(self, tif_path: str) -> str:
        """
        获取tif文件的坐标参考系统 EPSG格式
        """
        dataset = read_rasterio_tif(tif_path)
        tif_crs = dataset.crs
        logger.debug(f"成功获取TIFF坐标参考系统: {get_epsg_code(tif_crs)}")
        return get_epsg_code(tif_crs)
