import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions=None):
    """
    检查文件类型是否允许上传
    
    Args:
        filename (str): 文件名
        allowed_extensions (set): 允许的文件扩展名集合
        
    Returns:
        bool: 文件类型是否允许
    """
    if not allowed_extensions:
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, folder=None):
    """
    保存上传的文件
    
    Args:
        file: 文件对象
        folder (str): 子文件夹名
        
    Returns:
        str: 保存后的文件路径
    """
    filename = secure_filename(file.filename)
    # 使用UUID生成唯一文件名
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # 确定保存路径
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if folder:
        save_path = os.path.join(upload_folder, folder)
    else:
        save_path = upload_folder
        
    # 确保目录存在
    os.makedirs(save_path, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(save_path, unique_filename)
    file.save(file_path)
    
    # 返回相对路径
    return os.path.join(folder, unique_filename) if folder else unique_filename

def get_file_url(file_path):
    """
    获取文件的完整URL
    
    Args:
        file_path (str): 文件相对路径
        
    Returns:
        str: 文件的完整URL
    """
    base_url = current_app.config.get('BASE_URL', '')
    if base_url.endswith('/'):
        base_url = base_url[:-1]
        
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if upload_folder.startswith('static/'):
        upload_url = upload_folder.replace('static/', '/static/', 1)
    else:
        upload_url = f"/static/{upload_folder}"
        
    return f"{base_url}{upload_url}/{file_path}" 