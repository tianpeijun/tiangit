"""
文件服务层
"""
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import List
from fastapi import UploadFile

from repositories.product_repository import ProductRepository
from utils.image import validate_image, save_uploaded_image, delete_image_files
from utils.response import ValidationException, NotFoundException


class FileService:
    """文件服务"""
    
    @staticmethod
    async def upload_product_images(
        conn: AsyncConnection,
        product_id: int,
        files: List[UploadFile]
    ) -> List[dict]:
        """上传产品图片"""
        # 检查产品是否存在
        product = await ProductRepository.get_product_by_id(conn, product_id, include_deleted=True)
        if not product:
            raise NotFoundException("产品不存在")
        
        # 检查现有图片数量
        existing_count = await ProductRepository.count_product_images(conn, product_id)
        if existing_count + len(files) > 3:
            raise ValidationException("每个产品最多只能上传3张图片")
        
        uploaded_images = []
        
        for file in files:
            # 读取文件内容
            content = await file.read()
            
            # 验证图片
            validate_image(content, file.filename)
            
            # 保存图片
            image_info = save_uploaded_image(content, file.filename, product_id)
            
            # 保存图片元数据到数据库
            image_data = {
                'product_id': product_id,
                'original_filename': image_info['original_filename'],
                'stored_filename': image_info['stored_filename'],
                'thumbnail_filename': image_info['thumbnail_filename'],
                'file_path': image_info['file_path'],
                'file_size': image_info['file_size'],
                'sort_order': existing_count + len(uploaded_images),
                'created_at': datetime.now()
            }
            
            image_id = await ProductRepository.add_product_image(conn, image_data)
            
            uploaded_images.append({
                'id': image_id,
                'url': f"/static/images/{image_info['file_path'].replace('static/images/', '')}/{image_info['stored_filename']}",
                'thumbnail_url': f"/static/images/{image_info['file_path'].replace('static/images/', '')}/{image_info['thumbnail_filename']}"
            })
        
        return uploaded_images
    
    @staticmethod
    async def delete_product_image(conn: AsyncConnection, image_id: int) -> bool:
        """删除产品图片"""
        # 获取图片信息
        image = await ProductRepository.get_image_by_id(conn, image_id)
        if not image:
            raise NotFoundException("图片不存在")
        
        # 删除文件
        delete_image_files(
            image['file_path'],
            image['stored_filename'],
            image['thumbnail_filename']
        )
        
        # 删除数据库记录
        return await ProductRepository.delete_product_image(conn, image_id)
    
    @staticmethod
    async def delete_all_product_images(conn: AsyncConnection, product_id: int) -> int:
        """删除产品的所有图片"""
        # 获取所有图片
        images = await ProductRepository.get_product_images(conn, product_id)
        
        # 删除文件
        for image in images:
            delete_image_files(
                image['file_path'],
                image['stored_filename'],
                image['thumbnail_filename']
            )
        
        # 删除数据库记录
        return await ProductRepository.delete_product_images(conn, product_id)
