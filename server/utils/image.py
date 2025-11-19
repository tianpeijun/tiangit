"""
图片处理工具
"""
from PIL import Image
from pathlib import Path
from typing import Tuple
import uuid
from datetime import datetime

from config.settings import settings
from utils.response import ValidationException


def validate_image(file_content: bytes, filename: str) -> None:
    """验证图片格式和大小"""
    # 验证文件扩展名
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise ValidationException(f"不支持的图片格式，仅支持: {', '.join(settings.ALLOWED_EXTENSIONS)}")
    
    # 验证文件大小
    if len(file_content) > settings.MAX_UPLOAD_SIZE:
        max_size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        raise ValidationException(f"图片大小超过限制（最大{max_size_mb}MB）")
    
    # 验证是否为有效图片
    try:
        img = Image.open(Path(filename))
        img.verify()
    except Exception:
        raise ValidationException("无效的图片文件")


def generate_thumbnail(image_path: Path, size: Tuple[int, int] = None) -> Path:
    """生成缩略图"""
    if size is None:
        size = settings.THUMBNAIL_SIZE
    
    # 打开原图
    img = Image.open(image_path)
    
    # 生成缩略图
    img.thumbnail(size, Image.Resampling.LANCZOS)
    
    # 生成缩略图文件名
    thumbnail_path = image_path.parent / f"{image_path.stem}_thumb{image_path.suffix}"
    
    # 保存缩略图
    img.save(thumbnail_path, quality=85, optimize=True)
    
    return thumbnail_path


def save_uploaded_image(file_content: bytes, original_filename: str, product_id: int) -> dict:
    """保存上传的图片"""
    # 生成存储路径
    today = datetime.now().strftime('%Y%m%d')
    image_dir = settings.UPLOAD_DIR / today / str(product_id)
    image_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成唯一文件名
    ext = Path(original_filename).suffix.lower()
    stored_filename = f"{uuid.uuid4()}{ext}"
    image_path = image_dir / stored_filename
    
    # 保存原图
    with open(image_path, 'wb') as f:
        f.write(file_content)
    
    # 生成缩略图
    thumbnail_path = generate_thumbnail(image_path)
    
    return {
        'original_filename': original_filename,
        'stored_filename': stored_filename,
        'thumbnail_filename': thumbnail_path.name,
        'file_path': str(image_dir),
        'file_size': len(file_content)
    }


def delete_image_files(file_path: str, stored_filename: str, thumbnail_filename: str) -> None:
    """删除图片文件"""
    try:
        # 删除原图
        original_path = Path(file_path) / stored_filename
        if original_path.exists():
            original_path.unlink()
        
        # 删除缩略图
        thumbnail_path = Path(file_path) / thumbnail_filename
        if thumbnail_path.exists():
            thumbnail_path.unlink()
    except Exception as e:
        # 文件删除失败不影响业务流程
        print(f"删除图片文件失败: {e}")
