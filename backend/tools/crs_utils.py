import pyproj
from shapely import Polygon
from shapely.ops import transform
from backend.utils.logger import get_logger

logger = get_logger("坐标系验证")


def get_epsg_code(crs_input) -> str:
    """
    接受 EPSG 字符串、整数、rasterio.CRS 或 WKT 字符串，统一转为 EPSG:xxxx 格式。

    Returns:
        标准 EPSG 字符串，如 'EPSG:32650'
    """
    try:
        crs = pyproj.CRS.from_user_input(crs_input)
        epsg = crs.to_epsg()
        if epsg:
            return f"EPSG:{epsg}"
        else:
            logger.warning(f"无法识别 EPSG 编码，返回原始 WKT: {crs_input}")
            return crs.to_wkt()
    except Exception as e:
        logger.error(f"CRS 转 EPSG 失败: {e}", exc_info=True)
        raise


def reproject_polygon_if_needed(
    polygon: Polygon, from_crs: str, to_crs: str
) -> Polygon:
    """
    如有需要，将 polygon 从 from_crs 重投影到 to_crs

    Args:
        polygon: Shapely 多边形对象（原始 CRS）
        from_crs: 原始坐标系（如 'EPSG:4326'）
        to_crs: 目标坐标系（通常是遥感影像的 CRS）

    Returns:
        投影后的 Polygon
    """
    from_crs = get_epsg_code(from_crs)
    to_crs = get_epsg_code(to_crs)
    if pyproj.CRS.from_user_input(from_crs) == pyproj.CRS.from_user_input(to_crs):
        logger.warning("Polygon 坐标系与目标一致，无需转换")
        return polygon

    logger.info(f"Polygon 坐标转换: {from_crs} → {to_crs}")
    try:
        transformer = pyproj.Transformer.from_crs(from_crs, to_crs, always_xy=True)
        polygon = transform(transformer.transform, polygon)
        logger.debug(f"转换后的polygon为：{polygon}")
        return polygon
    except Exception as e:
        logger.error(f"Polygon 坐标转换失败: {e}", exc_info=True)
        raise
