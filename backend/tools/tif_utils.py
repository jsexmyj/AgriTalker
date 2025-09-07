import glob
import os
from typing import List, Tuple
import rasterio
from rasterio.io import DatasetReader
from shapely import Polygon
from backend.utils.logger import get_logger
import numpy as np
from osgeo import gdal


logger = get_logger("tiff_utils")


def write_tiff(
    im_data: np.ndarray, im_geotrans: Tuple, im_proj: str, output_path: str
) -> None:
    """
    保存TIFF文件

    根据数据类型自动选择合适的GDAL数据类型
    支持单波段和多波段影像
    """
    dataset = None
    logger.debug(f"图像数据实际 shape: {im_data.shape}")

    try:
        if not isinstance(im_data, np.ndarray):
            raise TypeError("im_data 必须是 numpy 数组")
        # 根据numpy数据类型确定GDAL数据类型
        dtype_map = {
            "int8": gdal.GDT_Byte,
            "uint8": gdal.GDT_Byte,
            "int16": gdal.GDT_Int16,
            "uint16": gdal.GDT_UInt16,
            "int32": gdal.GDT_Int32,
            "uint32": gdal.GDT_UInt32,
            "float32": gdal.GDT_Float32,
            "float64": gdal.GDT_Float64,
        }

        datatype = dtype_map.get(im_data.dtype.name, gdal.GDT_Float32)

        # 处理数据维度
        if len(im_data.shape) == 3:
            im_bands, im_height, im_width = im_data.shape
        elif len(im_data.shape) == 2:
            im_bands, (im_height, im_width) = 1, im_data.shape
            im_data = im_data[np.newaxis, ...]  # 增加波段维度
        else:
            raise ValueError(f"数据维度不支持: {im_data.shape}")

        # 创建输出文件
        driver = gdal.GetDriverByName("GTiff")
        dataset = driver.Create(
            output_path, int(im_width), int(im_height), int(im_bands), datatype
        )

        if dataset is None:
            raise RuntimeError(f"创建TIFF文件失败: {output_path}")

        dataset.SetGeoTransform(im_geotrans)
        dataset.SetProjection(im_proj)
        # 写入数据
        for i in range(im_bands):
            dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
        logger.info(f"成功保存TIFF: {output_path}")
        del dataset
    except Exception as e:
        logger.error(f"write_tiff 错误: {e}")
        raise


def read_tif(file_path: str) -> gdal.Dataset:
    """
    读取TIFF文件并获取地理参考信息

    这个方法不仅读取影像数据，还提取重要的地理参考信息
    包括仿射变换参数和投影坐标系统

    Args:
        file_path: TIFF文件路径

    Returns:
        GDAL数据集对象
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        dataset = gdal.Open(file_path)
        if dataset is None:
            raise RuntimeError(f"无法打开TIFF文件: {file_path}")

        logger.debug(f"成功读取TIFF: {file_path}")
        return dataset
    except Exception as e:
        logger.error(f"read_tif 错误: {e}")
        raise


def read_rasterio_tif(file_path: str) -> DatasetReader:
    """
    使用 rasterio 读取 TIFF 文件
    rasterio 支持更高级别的操作（如读取为 np.ndarray，获取元信息
    Args:
        file_path: 影像文件路径

    Returns:
        rasterio 的 DatasetReader 对象
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        dataset = rasterio.open(file_path, mode="r")
        logger.debug(f"成功读取 TIFF: {file_path}")
        return dataset
    except Exception as e:
        logger.error(f"read_rasterio_tif 读取失败: {e}", exc_info=True)
        raise


def ensure_tiff_extension(path: str) -> str:
    """确保输出文件以 .tif 结尾"""
    if not path.lower().endswith(".tif") and not path.lower().endswith(".tiff"):
        path += ".tif"
    return path


def get_image_paths(folder):
    """给文件夹获取文件夹中所有tif影像路径"""
    return glob.glob(os.path.join(folder, "*.tif"))

