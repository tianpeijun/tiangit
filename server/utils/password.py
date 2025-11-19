"""
密码哈希和验证工具
"""
import bcrypt


def hash_password(password: str) -> str:
    """
    使用 bcrypt 哈希密码
    
    Args:
        password: 明文密码
        
    Returns:
        密码哈希值
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    验证密码是否匹配
    
    Args:
        password: 明文密码
        password_hash: 密码哈希值
        
    Returns:
        True 如果密码匹配，否则 False
    """
    password_bytes = password.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


def validate_password_format(password: str) -> tuple[bool, str]:
    """
    验证密码格式
    
    密码要求：
    - 长度 6-8 位
    - 必须包含数字和字母
    
    Args:
        password: 待验证的密码
        
    Returns:
        (是否有效, 错误消息)
    """
    if len(password) < 6 or len(password) > 8:
        return False, "密码长度必须为6-8位"
    
    has_digit = any(c.isdigit() for c in password)
    has_alpha = any(c.isalpha() for c in password)
    
    if not has_digit:
        return False, "密码必须包含数字"
    
    if not has_alpha:
        return False, "密码必须包含字母"
    
    return True, ""
