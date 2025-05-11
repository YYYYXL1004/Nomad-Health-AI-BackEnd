from flask import jsonify, request
from datetime import datetime

# 语言映射
LANGUAGE_MESSAGES = {
    'zh-CN': {
        'success': '操作成功',
        'param_error': '参数错误',
        'auth_failed': '认证失败',
        'server_error': '服务器错误',
        'user_not_found': '用户不存在',
        'account_password_error': '账号或密码错误',
        'account_exists': '该账号已被注册',
        'phone_exists': '该手机号已被注册',
        'phone_not_registered': '该手机号未注册',
        'password_mismatch': '两次输入的密码不一致',
        'old_password_error': '旧密码不正确',
        'birthday_format_error': '生日格式不正确，应为YYYY-MM-DD',
        'phone_used_by_others': '该手机号已被其他用户使用',
        'no_avatar_file': '未上传头像文件',
        'no_file_selected': '未选择文件',
        'unsupported_file_type': '不支持的文件类型',
        'avatar_upload_success': '头像上传成功',
        'password_reset_success': '密码重置成功',
        'password_update_success': '密码修改成功',
        'update_success': '更新成功',
        'login_success': '登录成功',
        'register_success': '注册成功',
        'logout_success': '退出成功'
    },
    'mn-MN': {
        'success': 'Амжилттай',
        'param_error': 'Параметр алдаа',
        'auth_failed': 'Баталгаажуулалт амжилтгүй',
        'server_error': 'Серверийн алдаа',
        'user_not_found': 'Хэрэглэгч олдсонгүй',
        'account_password_error': 'Бүртгэл эсвэл нууц үг буруу байна',
        'account_exists': 'Энэ бүртгэл бүртгэлтэй байна',
        'phone_exists': 'Энэ утасны дугаар бүртгэлтэй байна',
        'phone_not_registered': 'Энэ утасны дугаар бүртгэлтэй биш байна',
        'password_mismatch': 'Нууц үг таарахгүй байна',
        'old_password_error': 'Хуучин нууц үг буруу байна',
        'birthday_format_error': 'Төрсөн өдрийн формат буруу байна, YYYY-MM-DD байх ёстой',
        'phone_used_by_others': 'Энэ утасны дугаарыг өөр хэрэглэгч ашиглаж байна',
        'no_avatar_file': 'Профайл зураг оруулаагүй байна',
        'no_file_selected': 'Файл сонгоогүй байна',
        'unsupported_file_type': 'Дэмжигддэггүй файлын төрөл',
        'avatar_upload_success': 'Профайл зураг амжилттай оруулсан',
        'password_reset_success': 'Нууц үг амжилттай шинэчлэгдсэн',
        'password_update_success': 'Нууц үг амжилттай өөрчлөгдсөн',
        'update_success': 'Амжилттай шинэчлэгдсэн',
        'login_success': 'Амжилттай нэвтэрсэн',
        'register_success': 'Амжилттай бүртгүүлсэн',
        'logout_success': 'Амжилттай гарсан'
    }
}

def get_message(key, default=None):
    """
    根据当前请求的语言获取对应的消息
    
    Args:
        key (str): 消息键名
        default (str): 默认消息
    
    Returns:
        str: 对应语言的消息
    """
    language = request.headers.get('Accept-Language', 'zh-CN')
    if language not in LANGUAGE_MESSAGES:
        language = 'zh-CN'
    
    return LANGUAGE_MESSAGES[language].get(key, default or key)

def api_response(code, message_key, data=None):
    """
    生成统一的API响应格式
    
    Args:
        code (int): 状态码
        message_key (str): 消息键名
        data (Any): 返回的数据
    
    Returns:
        Response: Flask的JSON响应对象
    """
    return jsonify({
        "code": code,
        "message": get_message(message_key),
        "data": data,
        "timestamp": int(datetime.now().timestamp() * 1000)
    }) 