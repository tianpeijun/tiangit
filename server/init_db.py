"""
数据库初始化脚本
创建所有表并插入测试数据
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import uuid
import random

# 添加项目路径到 sys.path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, insert
from models.database import (
    engine, metadata, users, addresses, categories, products,
    product_images, product_categories, carts, orders, order_items,
    point_transactions, sessions, admin_logs
)
from utils.password import hash_password


async def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    print("✓ 数据库表创建成功")
    
    # 创建默认管理员
    await create_default_admin()
    print("✓ 管理员账户创建成功")
    
    # 创建测试员工
    await create_test_employees()
    print("✓ 测试员工账户创建成功（20个）")
    
    # 创建产品分类
    category_map = await create_categories()
    print("✓ 产品分类创建成功（5个一级分类，20个二级分类）")
    
    # 创建测试产品
    await create_test_products(category_map)
    print("✓ 测试产品创建成功（100个3C产品）")

    print("\n数据库初始化完成！")
    print("\n登录信息：")
    print("管理员 - 用户名: admin, 密码: admin123")
    print("员工 - 用户名: employee001-employee020, 密码: test123")


async def create_default_admin():
    """创建默认管理员账户"""
    admin_data = {
        'username': 'admin',
        'password_hash': hash_password('admin123'),
        'real_name': '系统管理员',
        'employee_id': 'ADMIN001',
        'department': '技术部',
        'position': '系统管理员',
        'role': 'admin',
        'points': 0,
        'is_active': True,
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    async with engine.begin() as conn:
        await conn.execute(insert(users).values(**admin_data))


async def create_test_employees():
    """创建20个测试员工账户"""
    departments = ['技术部', '市场部', '销售部', '人力资源部', '财务部']
    
    async with engine.begin() as conn:
        for i in range(1, 21):
            employee_data = {
                'username': f'employee{i:03d}',
                'password_hash': hash_password('test123'),
                'real_name': f'测试员工{i:02d}',
                'employee_id': f'EMP{i:04d}',
                'department': departments[(i - 1) % len(departments)],
                'position': '员工',
                'role': 'employee',
                'points': 1000,
                'is_active': True,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            await conn.execute(insert(users).values(**employee_data))



async def create_categories():
    """创建3C电子产品分类"""
    category_structure = {
        '手机通讯': ['智能手机', '功能手机', '手机配件', '运营商'],
        '电脑办公': ['笔记本电脑', '台式机', '平板电脑', '显示器', '键鼠'],
        '数码配件': ['移动电源', '数据线', '充电器', '保护壳', '耳机'],
        '智能设备': ['智能手表', '智能手环', '智能音箱', '智能家居'],
        '影音娱乐': ['耳机音箱', '相机摄像', '游戏设备', '影音配件']
    }
    
    category_map = {}
    sort_order = 0
    
    async with engine.begin() as conn:
        for parent_name, children in category_structure.items():
            # 创建一级分类
            result = await conn.execute(
                insert(categories).values(
                    name=parent_name,
                    parent_id=None,
                    sort_order=sort_order,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            )
            parent_id = result.lastrowid
            category_map[parent_name] = parent_id
            sort_order += 1
            
            # 创建二级分类
            child_sort = 0
            for child_name in children:
                result = await conn.execute(
                    insert(categories).values(
                        name=child_name,
                        parent_id=parent_id,
                        sort_order=child_sort,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                )
                category_map[child_name] = result.lastrowid
                child_sort += 1
    
    return category_map



async def create_test_products(category_map):
    """创建100个3C电子产品"""
    products_data = [
        # 手机通讯类（20个）
        {'name': 'iPhone 15 Pro Max 256GB', 'category': '智能手机', 'points': 8999, 'desc': '6.7英寸超视网膜XDR显示屏，A17 Pro芯片，钛金属设计'},
        {'name': 'Samsung Galaxy S24 Ultra', 'category': '智能手机', 'points': 7999, 'desc': '6.8英寸动态AMOLED 2X屏幕，骁龙8 Gen 3，200MP主摄'},
        {'name': 'Xiaomi 14 Pro', 'category': '智能手机', 'points': 4999, 'desc': '6.73英寸AMOLED屏幕，骁龙8 Gen 3，徕卡光学镜头'},
        {'name': 'OPPO Find X7 Ultra', 'category': '智能手机', 'points': 5999, 'desc': '6.82英寸AMOLED屏幕，骁龙8 Gen 3，哈苏影像系统'},
        {'name': 'vivo X100 Pro', 'category': '智能手机', 'points': 5499, 'desc': '6.78英寸AMOLED屏幕，天玑9300，蔡司光学镜头'},
        {'name': 'Honor Magic6 Pro', 'category': '智能手机', 'points': 5299, 'desc': '6.8英寸OLED屏幕，骁龙8 Gen 3，鹰眼相机系统'},
        {'name': 'Huawei Mate 60 Pro', 'category': '智能手机', 'points': 6999, 'desc': '6.82英寸OLED屏幕，麒麟9000S，卫星通信'},
        {'name': 'iPhone 14 128GB', 'category': '智能手机', 'points': 5999, 'desc': '6.1英寸超视网膜XDR显示屏，A15仿生芯片'},
        {'name': 'Redmi K70 Pro', 'category': '智能手机', 'points': 3299, 'desc': '6.67英寸AMOLED屏幕，骁龙8 Gen 2，5000mAh电池'},
        {'name': 'Realme GT5 Pro', 'category': '智能手机', 'points': 3799, 'desc': '6.78英寸AMOLED屏幕，骁龙8 Gen 3，5400mAh电池'},
        {'name': 'Nokia 105 4G', 'category': '功能手机', 'points': 199, 'desc': '1.8英寸屏幕，超长待机，经典设计'},
        {'name': '小米多亲Qin 3', 'category': '功能手机', 'points': 299, 'desc': '4G全网通，AI语音助手，超长续航'},
        {'name': 'AirPods Pro 2', 'category': '手机配件', 'points': 1899, 'desc': '主动降噪，空间音频，USB-C充电'},
        {'name': '小米无线充电器 50W', 'category': '手机配件', 'points': 199, 'desc': '50W快充，智能散热，兼容多设备'},
        {'name': 'Anker 氮化镓充电器 65W', 'category': '手机配件', 'points': 249, 'desc': '65W快充，三口输出，小巧便携'},
        {'name': 'Baseus 数据线 100W', 'category': '手机配件', 'points': 89, 'desc': '100W快充，编织线材，耐用抗拉'},
        {'name': '倍思手机支架', 'category': '手机配件', 'points': 59, 'desc': '磁吸设计，360度旋转，稳固不掉'},
        {'name': 'UAG 手机保护壳', 'category': '手机配件', 'points': 299, 'desc': '军规防摔，轻薄设计，精准开孔'},
        {'name': '中国移动 5G套餐', 'category': '运营商', 'points': 0, 'desc': '5G高速网络，不限流量，全国通用'},
        {'name': '中国联通 5G套餐', 'category': '运营商', 'points': 0, 'desc': '5G高速网络，超大流量，优惠套餐'},

        # 电脑办公类（25个）
        {'name': 'MacBook Pro 16英寸 M3 Pro', 'category': '笔记本电脑', 'points': 15999, 'desc': '16英寸Liquid视网膜XDR显示屏，M3 Pro芯片，18小时续航'},
        {'name': 'MacBook Air 15英寸 M2', 'category': '笔记本电脑', 'points': 9999, 'desc': '15英寸Liquid视网膜显示屏，M2芯片，超薄设计'},
        {'name': 'Dell XPS 15', 'category': '笔记本电脑', 'points': 12999, 'desc': '15.6英寸4K OLED触控屏，Intel i7-13700H，RTX 4060'},
        {'name': 'ThinkPad X1 Carbon Gen 11', 'category': '笔记本电脑', 'points': 11999, 'desc': '14英寸2.8K屏幕，Intel i7-1365U，军规认证'},
        {'name': 'HP Spectre x360 14', 'category': '笔记本电脑', 'points': 10999, 'desc': '13.5英寸3K2K OLED触控屏，Intel i7-1355U，360度翻转'},
        {'name': 'ASUS ROG Zephyrus G14', 'category': '笔记本电脑', 'points': 13999, 'desc': '14英寸2.5K 165Hz屏幕，AMD R9-7940HS，RTX 4070'},
        {'name': 'Lenovo Yoga Pro 14s', 'category': '笔记本电脑', 'points': 7999, 'desc': '14.5英寸2.8K 120Hz屏幕，Intel i7-13700H，轻薄本'},
        {'name': 'Microsoft Surface Laptop 5', 'category': '笔记本电脑', 'points': 9999, 'desc': '13.5英寸PixelSense触控屏，Intel i7-1255U，优雅设计'},
        {'name': 'Mac Studio M2 Ultra', 'category': '台式机', 'points': 29999, 'desc': 'M2 Ultra芯片，64GB统一内存，专业工作站'},
        {'name': 'iMac 24英寸 M3', 'category': '台式机', 'points': 12999, 'desc': '24英寸4.5K视网膜显示屏，M3芯片，一体机设计'},
        {'name': 'Dell OptiPlex 7090', 'category': '台式机', 'points': 6999, 'desc': 'Intel i7-11700，16GB内存，512GB SSD，商用台式机'},
        {'name': 'HP EliteDesk 800 G9', 'category': '台式机', 'points': 7999, 'desc': 'Intel i7-12700，32GB内存，1TB SSD，企业级台式机'},
        {'name': 'iPad Pro 12.9英寸 M2', 'category': '平板电脑', 'points': 8999, 'desc': '12.9英寸Liquid视网膜XDR显示屏，M2芯片，5G版本'},
        {'name': 'iPad Air 10.9英寸 M1', 'category': '平板电脑', 'points': 4999, 'desc': '10.9英寸Liquid视网膜显示屏，M1芯片，轻薄便携'},
        {'name': 'Samsung Galaxy Tab S9 Ultra', 'category': '平板电脑', 'points': 7999, 'desc': '14.6英寸Dynamic AMOLED 2X屏幕，骁龙8 Gen 2，S Pen'},
        {'name': 'Huawei MatePad Pro 13.2', 'category': '平板电脑', 'points': 5999, 'desc': '13.2英寸OLED柔性屏，麒麟9000S，M-Pencil'},
        {'name': 'Dell UltraSharp U2723DE', 'category': '显示器', 'points': 3999, 'desc': '27英寸4K IPS屏幕，USB-C 90W供电，色彩准确'},
        {'name': 'LG 27UP850', 'category': '显示器', 'points': 3499, 'desc': '27英寸4K IPS屏幕，HDR400，USB-C 60W供电'},
        {'name': 'BenQ PD2725U', 'category': '显示器', 'points': 4999, 'desc': '27英寸4K IPS屏幕，专业设计显示器，色彩管理'},
        {'name': 'ASUS ProArt PA279CV', 'category': '显示器', 'points': 3299, 'desc': '27英寸4K IPS屏幕，100% sRGB，专业显示器'},
        {'name': 'Logitech MX Master 3S', 'category': '键鼠', 'points': 799, 'desc': '无线鼠标，8000DPI，静音按键，多设备切换'},
        {'name': 'Logitech MX Keys', 'category': '键鼠', 'points': 899, 'desc': '无线键盘，背光按键，多设备切换，智能感应'},
        {'name': 'Keychron K8 Pro', 'category': '键鼠', 'points': 699, 'desc': '机械键盘，热插拔轴体，无线/有线双模'},
        {'name': 'Razer DeathAdder V3 Pro', 'category': '键鼠', 'points': 999, 'desc': '无线游戏鼠标，30000DPI，90小时续航'},
        {'name': 'Razer BlackWidow V4 Pro', 'category': '键鼠', 'points': 1499, 'desc': '机械游戏键盘，绿轴，RGB灯效，多功能旋钮'},

        # 数码配件类（30个）
        {'name': '小米移动电源3 20000mAh', 'category': '移动电源', 'points': 199, 'desc': '20000mAh大容量，双向快充，双USB-A+USB-C'},
        {'name': 'Anker PowerCore 26800mAh', 'category': '移动电源', 'points': 399, 'desc': '26800mAh超大容量，三口输出，快速充电'},
        {'name': 'Baseus 30000mAh 65W', 'category': '移动电源', 'points': 499, 'desc': '30000mAh容量，65W快充，数显屏幕'},
        {'name': 'RAVPower 20000mAh PD', 'category': '移动电源', 'points': 299, 'desc': '20000mAh容量，PD快充，轻薄便携'},
        {'name': 'Zendure SuperMini 10000mAh', 'category': '移动电源', 'points': 349, 'desc': '10000mAh容量，20W快充，超小体积'},
        {'name': 'Anker USB-C数据线 100W', 'category': '数据线', 'points': 89, 'desc': '100W快充，编织线材，480Mbps传输'},
        {'name': 'Baseus USB-C数据线 240W', 'category': '数据线', 'points': 129, 'desc': '240W超级快充，5A电流，编织线材'},
        {'name': 'Apple USB-C转Lightning', 'category': '数据线', 'points': 149, 'desc': '官方认证，快速充电，数据传输'},
        {'name': 'Ugreen USB-C数据线 100W', 'category': '数据线', 'points': 79, 'desc': '100W快充，尼龙编织，耐用抗拉'},
        {'name': 'Belkin USB-C数据线 60W', 'category': '数据线', 'points': 99, 'desc': '60W快充，凯夫拉编织，超长耐用'},
        {'name': 'Anker 氮化镓充电器 65W', 'category': '充电器', 'points': 249, 'desc': '65W快充，三口输出，小巧便携'},
        {'name': 'Baseus 氮化镓充电器 100W', 'category': '充电器', 'points': 349, 'desc': '100W快充，四口输出，智能分配'},
        {'name': 'Ugreen 氮化镓充电器 140W', 'category': '充电器', 'points': 499, 'desc': '140W超级快充，三口输出，支持笔记本'},
        {'name': '小米氮化镓充电器 67W', 'category': '充电器', 'points': 199, 'desc': '67W快充，双口输出，折叠插脚'},
        {'name': 'Apple 35W双USB-C充电器', 'category': '充电器', 'points': 399, 'desc': '35W快充，双口输出，紧凑设计'},
        {'name': 'UAG iPhone保护壳', 'category': '保护壳', 'points': 299, 'desc': '军规防摔，轻薄设计，精准开孔'},
        {'name': 'Spigen iPhone保护壳', 'category': '保护壳', 'points': 199, 'desc': '防摔保护，透明设计，不发黄'},
        {'name': 'OtterBox Defender', 'category': '保护壳', 'points': 399, 'desc': '三层防护，军规防摔，全包设计'},
        {'name': 'Ringke Fusion', 'category': '保护壳', 'points': 149, 'desc': '透明保护，防摔防刮，轻薄设计'},
        {'name': 'Caseology Parallax', 'category': '保护壳', 'points': 179, 'desc': '几何纹理，防滑防摔，时尚设计'},
        {'name': 'AirPods Pro 2', 'category': '耳机', 'points': 1899, 'desc': '主动降噪，空间音频，USB-C充电'},
        {'name': 'Sony WH-1000XM5', 'category': '耳机', 'points': 2499, 'desc': '头戴式降噪耳机，30小时续航，LDAC'},
        {'name': 'Bose QuietComfort Ultra', 'category': '耳机', 'points': 2799, 'desc': '头戴式降噪耳机，空间音频，24小时续航'},
        {'name': 'Sennheiser Momentum 4', 'category': '耳机', 'points': 2299, 'desc': '头戴式降噪耳机，60小时续航，LDAC'},
        {'name': 'Beats Studio Pro', 'category': '耳机', 'points': 2499, 'desc': '头戴式降噪耳机，空间音频，40小时续航'},
        {'name': 'Jabra Elite 85t', 'category': '耳机', 'points': 1499, 'desc': '真无线降噪耳机，多点连接，25小时续航'},
        {'name': 'Samsung Galaxy Buds2 Pro', 'category': '耳机', 'points': 1299, 'desc': '真无线降噪耳机，360度音频，18小时续航'},
        {'name': '小米Buds 4 Pro', 'category': '耳机', 'points': 899, 'desc': '真无线降噪耳机，空间音频，38小时续航'},
        {'name': 'OPPO Enco X2', 'category': '耳机', 'points': 999, 'desc': '真无线降噪耳机，LHDC 4.0，40小时续航'},
        {'name': 'Huawei FreeBuds Pro 3', 'category': '耳机', 'points': 1299, 'desc': '真无线降噪耳机，Hi-Res音质，31小时续航'},

        # 智能设备类（15个）
        {'name': 'Apple Watch Series 9', 'category': '智能手表', 'points': 2999, 'desc': '血氧检测，心率监测，GPS，18小时续航'},
        {'name': 'Apple Watch Ultra 2', 'category': '智能手表', 'points': 6299, 'desc': '钛金属表壳，双频GPS，36小时续航，专业运动'},
        {'name': 'Samsung Galaxy Watch6', 'category': '智能手表', 'points': 2299, 'desc': '健康监测，睡眠追踪，40小时续航'},
        {'name': 'Huawei Watch GT 4', 'category': '智能手表', 'points': 1999, 'desc': '14天续航，健康监测，100+运动模式'},
        {'name': 'Xiaomi Watch S3', 'category': '智能手表', 'points': 1299, 'desc': '15天续航，健康监测，150+运动模式'},
        {'name': 'Garmin Fenix 7', 'category': '智能手表', 'points': 4999, 'desc': '专业运动手表，多卫星定位，18天续航'},
        {'name': 'Fitbit Charge 6', 'category': '智能手环', 'points': 999, 'desc': '健康追踪，心率监测，7天续航'},
        {'name': 'Xiaomi Band 8 Pro', 'category': '智能手环', 'points': 399, 'desc': '1.74英寸大屏，14天续航，150+运动模式'},
        {'name': 'Huawei Band 8', 'category': '智能手环', 'points': 299, 'desc': '14天续航，健康监测，100+表盘'},
        {'name': 'Honor Band 7', 'category': '智能手环', 'points': 249, 'desc': '14天续航，血氧监测，96种运动模式'},
        {'name': 'HomePod mini', 'category': '智能音箱', 'points': 749, 'desc': '360度音效，Siri语音助手，智能家居控制'},
        {'name': '小米小爱音箱Pro', 'category': '智能音箱', 'points': 299, 'desc': '360度环绕音效，小爱同学，智能家居控制'},
        {'name': 'Amazon Echo Dot 5', 'category': '智能音箱', 'points': 399, 'desc': 'Alexa语音助手，智能家居控制，音质升级'},
        {'name': 'Yeelight智能灯泡', 'category': '智能家居', 'points': 99, 'desc': '1600万色彩，语音控制，定时开关'},
        {'name': '米家智能插座', 'category': '智能家居', 'points': 59, 'desc': '远程控制，定时开关，电量统计'},
        
        # 影音娱乐类（10个）
        {'name': 'Sony WH-1000XM5', 'category': '耳机音箱', 'points': 2499, 'desc': '头戴式降噪耳机，30小时续航，LDAC'},
        {'name': 'Bose SoundLink Revolve+', 'category': '耳机音箱', 'points': 1999, 'desc': '便携蓝牙音箱，360度音效，16小时续航'},
        {'name': 'JBL Charge 5', 'category': '耳机音箱', 'points': 1299, 'desc': '便携蓝牙音箱，IP67防水，20小时续航'},
        {'name': 'Sony A7M4', 'category': '相机摄像', 'points': 15999, 'desc': '全画幅微单相机，3300万像素，4K 60P视频'},
        {'name': 'Canon EOS R6 Mark II', 'category': '相机摄像', 'points': 16999, 'desc': '全画幅微单相机，2420万像素，6K超采样'},
        {'name': 'DJI Mini 4 Pro', 'category': '相机摄像', 'points': 4999, 'desc': '折叠无人机，4K HDR视频，34分钟续航'},
        {'name': 'GoPro Hero 12 Black', 'category': '相机摄像', 'points': 3499, 'desc': '运动相机，5.3K视频，防水10米'},
        {'name': 'PlayStation 5', 'category': '游戏设备', 'points': 3999, 'desc': '次世代游戏主机，4K 120fps，光线追踪'},
        {'name': 'Nintendo Switch OLED', 'category': '游戏设备', 'points': 2499, 'desc': '7英寸OLED屏幕，掌机/主机双模式'},
        {'name': 'Elgato Stream Deck', 'category': '影音配件', 'points': 1499, 'desc': '直播控制台，15个LCD按键，自定义功能'},
    ]
    
    today = datetime.now().strftime('%Y%m%d')
    image_base_dir = Path('static/images')
    image_base_dir.mkdir(parents=True, exist_ok=True)
    
    async with engine.begin() as conn:
        for idx, product_data in enumerate(products_data, 1):
            # 1. 创建产品记录
            result = await conn.execute(
                insert(products).values(
                    name=product_data['name'],
                    description=product_data['desc'],
                    points_required=product_data['points'],
                    status='active',
                    is_deleted=False,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            )
            product_id = result.lastrowid
            
            # 2. 关联产品分类
            category_id = category_map.get(product_data['category'])
            if category_id:
                await conn.execute(
                    insert(product_categories).values(
                        product_id=product_id,
                        category_id=category_id,
                        created_at=datetime.now()
                    )
                )
            
            # 3. 创建产品图片（使用占位图）
            image_count = random.randint(1, 3)
            for i in range(image_count):
                image_uuid = str(uuid.uuid4())
                image_dir = image_base_dir / today / 'init' / str(product_id)
                image_dir.mkdir(parents=True, exist_ok=True)
                
                # 创建占位图文件
                original_filename = f"{image_uuid}.jpg"
                thumbnail_filename = f"{image_uuid}_thumb.jpg"
                original_path = image_dir / original_filename
                thumbnail_path = image_dir / thumbnail_filename
                
                # 创建简单的占位图（纯色图片）
                try:
                    from PIL import Image, ImageDraw, ImageFont
                    
                    # 创建原图 (800x800)
                    img = Image.new('RGB', (800, 800), color=(200, 200, 200))
                    draw = ImageDraw.Draw(img)
                    
                    # 添加产品名称文本
                    text = product_data['name'][:20]
                    # 使用默认字体
                    draw.text((400, 400), text, fill=(100, 100, 100), anchor='mm')
                    img.save(original_path, 'JPEG', quality=85)
                    
                    # 创建缩略图 (320x320)
                    thumbnail = img.resize((320, 320), Image.Resampling.LANCZOS)
                    thumbnail.save(thumbnail_path, 'JPEG', quality=85)
                    
                    file_size = original_path.stat().st_size
                except Exception as e:
                    # 如果PIL不可用，创建空文件
                    original_path.touch()
                    thumbnail_path.touch()
                    file_size = 0
                
                # 保存图片元数据
                await conn.execute(
                    insert(product_images).values(
                        product_id=product_id,
                        original_filename=f"{product_data['name']}_{i+1}.jpg",
                        stored_filename=original_filename,
                        thumbnail_filename=thumbnail_filename,
                        file_path=str(image_dir),
                        file_size=file_size,
                        sort_order=i,
                        created_at=datetime.now()
                    )
                )


if __name__ == "__main__":
    asyncio.run(init_database())
