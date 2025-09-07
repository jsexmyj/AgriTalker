from backend.config.config import ConfigManager
from backend.tools.crs_utils import get_epsg_code, reproject_polygon_if_needed
from backend.tools.geo_providers import GeoProvider
from backend.tools.tif_utils import ensure_tiff_extension, read_rasterio_tif, write_tiff
from rasterio.features import geometry_mask
from backend.utils.logger import get_logger
from shapely.geometry import Polygon, mapping
import numpy as np
from rasterio.transform import Affine
import os
from backend.utils.tempfile import mkd_temp


logger = get_logger("Cutter")


class Cutter:
    """
    用于裁剪栅格数据的工具类
    """

    def __init__(self):
        self.geo_provider = GeoProvider()
        self.dataset = None

    def create_mask_from_polygon(
        self, polygon: Polygon, invert: bool = False
    ) -> np.ndarray:
        """
        使用Shapely Polygon和GeoTIFF数据集创建掩膜

        Args:
            polygon: Shapely多边形对象（地理坐标）
            dataset: rasterio 打开的图像数据集
            invert: 是否保留在多边形内部的像素（True 表示 True 代表要保留）

        Returns:
            布尔掩膜数组（True 表示掩蔽像素，False 表示保留）
        """
        try:
            if not polygon.is_valid:
                logger.error("无效的Polygon对象")
                raise ValueError("无效的Polygon对象")

            mask = geometry_mask(
                [mapping(polygon)],
                transform=self.dataset.transform,
                invert=invert,  # True表示polygon内是有效区
                out_shape=(self.dataset.height, self.dataset.width),
            )
            valid_pixels = (~mask).sum()
            # logger.debug(f"掩膜创建完成，保留像素数: {valid_pixels}")

            if valid_pixels == 0:
                logger.warning("掩膜区域为空，polygon可能超出影像范围")

            return mask
        except Exception as e:
            logger.error(f"创建掩膜失败: {e}", exc_info=True)
            raise

    def cut_by_polygon(
        self,
        raster_path: str,
        addres_poly: Polygon, #已经转换坐标系后的polygon
        output_path: str = None,
        polygon_crs: str = "EPSG:4326",
    ) -> str:
        """
        裁剪流程：
        1. 读取 GeoTIFF → 获取影像、transform、投影、shape
        2. 使用 Polygon 创建掩膜（布尔数组）
        3. 对原始图像进行裁剪（使用掩膜过滤）
        4. 写入新的 .tif 文件（使用裁剪后的数据和更新后的 transform）
        """
        try:
            # 要改，有的东西验证里面获取了的
            
            # 加载tiff
            self.dataset = read_rasterio_tif(raster_path)
            image_crs = self.geo_provider.get_tif_crs(tif_path=raster_path)  # rasterio 的 CRS 对象
            # logger.debug(f"影像CRS: {image_crs}")

            
            # 加载掩膜
            mask = self.create_mask_from_polygon(addres_poly)

            # 读取影像数据
            image = self.dataset.read()  # shape: (bands, height, width)
            logger.debug(f"原始影像尺寸: {image.shape}")

            # 保留边界 bbox 范围
            valid_pixels = ~mask  # 有效像素区域
            bbox_rows, bbox_cols = np.where(valid_pixels)
            if len(bbox_rows) == 0 or len(bbox_cols) == 0:
                raise ValueError("掩膜区域为空，无法裁剪")

            min_row, max_row = bbox_rows.min(), bbox_rows.max()
            min_col, max_col = bbox_cols.min(), bbox_cols.max()
            logger.debug(
                f"裁剪范围: 行[{min_row}:{max_row+1}], 列[{min_col}:{max_col+1}]"
            )

            clipped_image = image[:, min_row : max_row + 1, min_col : max_col + 1]
            clipped_mask = mask[min_row : max_row + 1, min_col : max_col + 1]
            # 将掩膜外的区域设为0或nodata
            clipped_image[:, clipped_mask] = 0
            logger.debug(f"裁剪后影像尺寸: {clipped_image.shape}")

            # 更新 transform
            origin_transform: Affine = self.dataset.transform
            new_transform = origin_transform * Affine.translation(min_col, min_row)
            im_geotrans = new_transform.to_gdal()

            # 获取投影信息
            im_proj = get_epsg_code(self.dataset.crs)

            # 修改output_path逻辑
            if output_path is None:
                output_path = ConfigManager.get("cut_polygon_dir")
                if not output_path:
                    temp_dir = os.path.join(
                        "backend", "temp_data", "outputs", "cropped"
                    )
                    os.makedirs(temp_dir, exist_ok=True)
                    output_path = mkd_temp(dir=temp_dir)
            output_path = ensure_tiff_extension(output_path)
            logger.info(f"保存裁剪后的 TIFF 至: {output_path}")

            # 写入tiff
            write_tiff(
                im_data=clipped_image,
                im_geotrans=im_geotrans,
                im_proj=im_proj,
                output_path=output_path,
            )
            return output_path

        except Exception as e:
            logger.error(f"裁剪失败: {e}", exc_info=True)
            raise
        finally:
            if self.dataset:
                self.dataset.close()
