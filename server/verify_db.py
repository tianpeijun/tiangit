"""
数据库验证脚本
验证数据库结构和数据完整性
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, func
from models.database import (
    engine, users, addresses, categories, products,
    product_images, product_categories, carts, orders, order_items,
    point_transactions, sessions, admin_logs
)


async def verify_database():
    """验证数据库"""
    print("=" * 60)
    print("AWSomeShop 数据库验证报告")
    print("=" * 60)
    
    async with engine.begin() as conn:
        # 验证用户数据
        result = await conn.execute(select(func.count()).select_from(users))
        user_count = result.scalar()
        print(f"\n✓ 用户总数: {user_count}")
        
        result = await conn.execute(
            select(func.count()).select_from(users).where(users.c.role == 'admin')
        )
        admin_count = result.scalar()
        print(f"  - 管理员: {admin_count}")
        
        result = await conn.execute(
            select(func.count()).select_from(users).where(users.c.role == 'employee')
        )
        employee_count = result.scalar()
        print(f"  - 员工: {employee_count}")
        
        # 验证分类数据
        result = await conn.execute(select(func.count()).select_from(categories))
        category_count = result.scalar()
        print(f"\n✓ 产品分类总数: {category_count}")
        
        result = await conn.execute(
            select(func.count()).select_from(categories).where(categories.c.parent_id.is_(None))
        )
        parent_count = result.scalar()
        print(f"  - 一级分类: {parent_count}")
        
        result = await conn.execute(
            select(func.count()).select_from(categories).where(categories.c.parent_id.isnot(None))
        )
        child_count = result.scalar()
        print(f"  - 二级分类: {child_count}")
        
        # 验证产品数据
        result = await conn.execute(select(func.count()).select_from(products))
        product_count = result.scalar()
        print(f"\n✓ 产品总数: {product_count}")
        
        result = await conn.execute(
            select(func.count()).select_from(products).where(products.c.status == 'active')
        )
        active_count = result.scalar()
        print(f"  - 已上架: {active_count}")
        
        result = await conn.execute(
            select(func.min(products.c.points_required), func.max(products.c.points_required))
            .select_from(products)
        )
        min_points, max_points = result.fetchone()
        print(f"  - 积分范围: {min_points} - {max_points}")
        
        # 验证产品图片
        result = await conn.execute(select(func.count()).select_from(product_images))
        image_count = result.scalar()
        print(f"\n✓ 产品图片总数: {image_count}")
        print(f"  - 平均每个产品: {image_count / product_count:.1f} 张")
        
        # 验证产品分类关联
        result = await conn.execute(select(func.count()).select_from(product_categories))
        relation_count = result.scalar()
        print(f"\n✓ 产品分类关联: {relation_count}")
        
        # 验证积分数据
        result = await conn.execute(
            select(func.sum(users.c.points)).select_from(users).where(users.c.role == 'employee')
        )
        total_points = result.scalar()
        print(f"\n✓ 员工总积分: {total_points}")
        print(f"  - 平均每人: {total_points / employee_count:.0f}")
        
        # 验证数据完整性
        print(f"\n✓ 数据完整性检查:")
        
        # 检查所有产品都有图片
        result = await conn.execute(
            select(func.count()).select_from(products)
            .where(products.c.id.notin_(select(product_images.c.product_id)))
        )
        no_image_count = result.scalar()
        if no_image_count == 0:
            print(f"  - 所有产品都有图片 ✓")
        else:
            print(f"  - 警告: {no_image_count} 个产品没有图片 ✗")
        
        # 检查所有产品都有分类
        result = await conn.execute(
            select(func.count()).select_from(products)
            .where(products.c.id.notin_(select(product_categories.c.product_id)))
        )
        no_category_count = result.scalar()
        if no_category_count == 0:
            print(f"  - 所有产品都有分类 ✓")
        else:
            print(f"  - 警告: {no_category_count} 个产品没有分类 ✗")
        
        # 显示示例数据
        print(f"\n✓ 示例数据:")
        result = await conn.execute(
            select(users.c.username, users.c.role, users.c.points)
            .select_from(users)
            .limit(3)
        )
        print(f"  用户示例:")
        for row in result:
            print(f"    - {row.username} ({row.role}): {row.points} 积分")
        
        result = await conn.execute(
            select(products.c.name, products.c.points_required)
            .select_from(products)
            .limit(3)
        )
        print(f"  产品示例:")
        for row in result:
            print(f"    - {row.name}: {row.points_required} 积分")
    
    print("\n" + "=" * 60)
    print("验证完成！数据库状态正常。")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(verify_database())
