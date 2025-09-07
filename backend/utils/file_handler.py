import os

def ensure_folder_exists(folder_path):
    """
    验证文件夹路径是否为空，如果文件夹路径为空，则创建文件夹
    """
    if not folder_path:
        raise ValueError("文件夹路径不能为空")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def ensure_file_exists(file_path):
    """
    验证文件路径是否为空，如果文件路径为空，则创建文件
    """
    ensure_folder_exists(os.path.dirname(file_path))
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            pass
    return file_path


