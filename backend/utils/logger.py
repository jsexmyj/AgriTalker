from datetime import datetime
import logging
import os

global_log_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def get_logger(
    name=__name__, log_dir=r"backend\temp_data\logs", log_filename=f"{global_log_time}.log"
):
    logger = logging.getLogger(name)

    if not logger.handlers:  # 防止重复添加 handler
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 创建文件处理器
        if log_dir:
            # 确保日志目录存在
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            full_log_path = os.path.join(log_dir, log_filename)

            file_handler = logging.FileHandler(full_log_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # 禁用传播到根日志记录器
        logger.propagate = False

    return logger
