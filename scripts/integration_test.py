#!/usr/bin/env python3
"""
AWSomeShop 集成测试脚本
测试前后端联调和功能验证
"""
import requests
import json
import sys
from typing import Dict, Any, Optional

# 配置
BASE_URL = "http://localhost:8000"
session_id = None
admin_session = None
employee_session = None

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.END}\n")

def api_request(method: str, endpoint: str, data: Optional[Dict] = None, 
                session: Optional[str] = None, files: Optional[Dict] = None) -> Dict[str, Any]:
    """发送 API 请求"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if session:
        headers['X-Session-ID'] = session
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, data=data, files=files)
            else:
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            headers['Content-Type'] = 'application/json'
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response.json()
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None}

# ==================== 测试用例 ====================

def test_admin_login():
    """测试管理员登录"""
    global admin_session
    print_info("测试管理员登录...")
    
    result = api_request("POST", "/api/auth/login", {
        "username": "admin",
        "password": "admin123"
    })
    
    if result["code"] == 200:
        admin_session = result["data"]["session_id"]
        print_success(f"管理员登录成功 - Session: {admin_session[:20]}...")
        return True
    else:
        print_error(f"管理员登录失败: {result['message']}")
        return False

def test_employee_login():
    """测试员工登录"""
    global employee_session
    print_info("测试员工登录...")
    
    result = api_request("POST", "/api/auth/login", {
        "username": "employee001",
        "password": "test123"
    })
    
    if result["code"] == 200:
        employee_session = result["data"]["session_id"]
        user = result["data"]["user"]
        print_success(f"员工登录成功 - {user['real_name']} (积分: {user['points']})")
        return True
    else:
        print_error(f"员工登录失败: {result['message']}")
        return False

def test_get_products():
    """测试获取产品列表"""
    print_info("测试获取产品列表...")
    
    result = api_request("GET", "/api/personal/products", 
                        {"page": 1, "page_size": 10}, 
                        employee_session)
    
    if result["code"] == 200:
        data = result["data"]
        print_success(f"获取产品列表成功 - 共 {data['total']} 个产品，当前页 {len(data['items'])} 个")
        if data['items']:
            product = data['items'][0]
            print_info(f"  示例产品: {product['name']} - {product['points_required']} 积分")
        return True
    else:
        print_error(f"获取产品列表失败: {result['message']}")
        return False

def test_search_products():
    """测试搜索产品"""
    print_info("测试搜索产品...")
    
    result = api_request("GET", "/api/personal/products",
                        {"keyword": "iPhone", "page": 1},
                        employee_session)
    
    if result.get("code") == 200:
        data = result["data"]
        print_success(f"搜索产品成功 - 找到 {data['total']} 个相关产品")
        return True
    else:
        print_error(f"搜索产品失败: {result.get('message', '未知错误')}")
        return False

def test_get_categories():
    """测试获取分类树"""
    print_info("测试获取分类树...")
    
    result = api_request("GET", "/api/manage/categories/tree", None, employee_session)
    
    if result.get("code") == 200:
        categories = result["data"]
        print_success(f"获取分类树成功 - 共 {len(categories)} 个一级分类")
        for cat in categories[:2]:
            print_info(f"  {cat['name']}: {len(cat.get('children', []))} 个子分类")
        return True
    else:
        print_error(f"获取分类树失败: {result.get('message', '未知错误')}")
        return False

def test_cart_operations():
    """测试购物车操作"""
    print_info("测试购物车操作...")
    
    # 1. 添加到购物车
    result = api_request("POST", "/api/personal/cart/add",
                        {"product_id": 1, "quantity": 2},
                        employee_session)
    
    if result["code"] != 200:
        print_error(f"添加到购物车失败: {result['message']}")
        return False
    print_success("添加到购物车成功")
    
    # 2. 获取购物车
    result = api_request("GET", "/api/personal/cart", None, employee_session)
    
    if result["code"] != 200:
        print_error(f"获取购物车失败: {result['message']}")
        return False
    
    cart_data = result["data"]
    print_success(f"获取购物车成功 - {cart_data['total_quantity']} 件商品，共 {cart_data['total_points']} 积分")
    
    # 3. 更新购物车
    if cart_data['items']:
        result = api_request("PUT", "/api/personal/cart/update",
                            {"product_id": 1, "quantity": 1},
                            employee_session)
        
        if result["code"] == 200:
            print_success("更新购物车成功")
        else:
            print_warning(f"更新购物车失败: {result['message']}")
    
    # 4. 清空购物车
    result = api_request("DELETE", "/api/personal/cart/clear", None, employee_session)
    
    if result["code"] == 200:
        print_success("清空购物车成功")
        return True
    else:
        print_error(f"清空购物车失败: {result['message']}")
        return False

def test_points_balance():
    """测试获取积分余额"""
    print_info("测试获取积分余额...")
    
    result = api_request("GET", "/api/personal/points/balance", None, employee_session)
    
    if result["code"] == 200:
        balance = result["data"]["balance"]
        print_success(f"获取积分余额成功 - 当前余额: {balance} 积分")
        return True
    else:
        print_error(f"获取积分余额失败: {result['message']}")
        return False

def test_admin_get_users():
    """测试管理员获取用户列表"""
    print_info("测试管理员获取用户列表...")
    
    result = api_request("GET", "/api/manage/users",
                        {"page": 1, "page_size": 10},
                        admin_session)
    
    if result["code"] == 200:
        data = result["data"]
        print_success(f"获取用户列表成功 - 共 {data['total']} 个用户")
        return True
    else:
        print_error(f"获取用户列表失败: {result['message']}")
        return False

def test_admin_get_products():
    """测试管理员获取产品列表"""
    print_info("测试管理员获取产品列表...")
    
    result = api_request("GET", "/api/manage/products",
                        {"page": 1, "page_size": 10},
                        admin_session)
    
    if result["code"] == 200:
        data = result["data"]
        print_success(f"获取产品列表成功 - 共 {data['total']} 个产品")
        return True
    else:
        print_error(f"获取产品列表失败: {result['message']}")
        return False

def test_admin_grant_points():
    """测试管理员发放积分"""
    print_info("测试管理员发放积分...")
    
    result = api_request("POST", "/api/manage/points/grant",
                        {"user_ids": [2], "amount": 100, "description": "测试发放"},
                        admin_session)
    
    if result.get("code") == 200:
        print_success("发放积分成功")
        return True
    else:
        print_error(f"发放积分失败: {result.get('message', '未知错误')}")
        return False

def test_permission_check():
    """测试权限验证"""
    print_info("测试权限验证 - 员工访问管理端...")
    
    result = api_request("GET", "/api/manage/users",
                        {"page": 1},
                        employee_session)
    
    # 检查是否返回了权限错误（可能是 code=403 或 detail 字段）
    if result.get("code") == 403 or "detail" in result:
        print_success("权限验证正常 - 员工无法访问管理端")
        return True
    else:
        print_error(f"权限验证失败 - 员工不应该能访问管理端 (result: {result})")
        return False

# ==================== 主测试流程 ====================

def run_tests():
    """运行所有测试"""
    print_section("AWSomeShop 集成测试")
    
    tests = [
        ("认证测试", [
            ("管理员登录", test_admin_login),
            ("员工登录", test_employee_login),
        ]),
        ("员工端功能测试", [
            ("获取产品列表", test_get_products),
            ("搜索产品", test_search_products),
            ("获取分类树", test_get_categories),
            ("购物车操作", test_cart_operations),
            ("获取积分余额", test_points_balance),
        ]),
        ("管理端功能测试", [
            ("获取用户列表", test_admin_get_users),
            ("获取产品列表", test_admin_get_products),
            ("发放积分", test_admin_grant_points),
        ]),
        ("安全测试", [
            ("权限验证", test_permission_check),
        ]),
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for section_name, section_tests in tests:
        print_section(section_name)
        
        for test_name, test_func in section_tests:
            total_tests += 1
            try:
                if test_func():
                    passed_tests += 1
                else:
                    failed_tests += 1
            except Exception as e:
                print_error(f"{test_name} 异常: {str(e)}")
                failed_tests += 1
            print()  # 空行
    
    # 测试总结
    print_section("测试总结")
    print(f"总测试数: {total_tests}")
    print_success(f"通过: {passed_tests}")
    if failed_tests > 0:
        print_error(f"失败: {failed_tests}")
    else:
        print_success("所有测试通过！")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n成功率: {success_rate:.1f}%\n")
    
    return failed_tests == 0

if __name__ == "__main__":
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_warning("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"测试执行异常: {str(e)}")
        sys.exit(1)
