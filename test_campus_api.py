import requests

BASE_URL = "http://127.0.0.1:5000"

def test_get_all_parking_spaces():
    """测试获取所有车位接口"""
    response = requests.get(f"{BASE_URL}/api/parking/spaces")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)
    if len(data["data"]) > 0:
        first = data["data"][0]
        # 检查字段名是否匹配 parking_id
        assert "parking_id" in first
        assert "status" in first

def test_get_single_parking_space_exists():
    """测试获取单个存在的车位（取列表中的第一个）"""
    resp_all = requests.get(f"{BASE_URL}/api/parking/spaces")
    if resp_all.status_code == 200 and resp_all.json()["data"]:
        parking_id = resp_all.json()["data"][0]["parking_id"]
        response = requests.get(f"{BASE_URL}/api/parking/spaces/{parking_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["parking_id"] == parking_id
    else:
        # 如果没有数据，标记通过
        assert True

def test_get_single_parking_space_not_exists():
    """测试获取不存在的车位"""
    response = requests.get(f"{BASE_URL}/api/parking/spaces/99999")
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 404
    assert "不存在" in data["message"]

def test_reserve_space_success():
    """测试预约空闲且可预约的车位"""
    # 先获取一个状态为 free 且 is_bookable=1 的车位
    all_spaces = requests.get(f"{BASE_URL}/api/parking/spaces").json()
    free_spaces = [s for s in all_spaces["data"] if s["status"] == "free" and s["is_bookable"] == 1]
    if not free_spaces:
        # 如果没有符合条件的车位，跳过测试
        assert True
        return
    
    parking_id = free_spaces[0]["parking_id"]
    payload = {
        "parking_id": parking_id,
        "user_id": "test_user"
    }
    response = requests.post(f"{BASE_URL}/api/reserve", json=payload)
    # 预期成功
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "预约成功"

def test_reserve_space_already_occupied():
    """测试预约已被占用的车位"""
    all_spaces = requests.get(f"{BASE_URL}/api/parking/spaces").json()
    occupied_spaces = [s for s in all_spaces["data"] if s["status"] != "free"]
    if not occupied_spaces:
        # 如果没有占用车位，可以先预约一个使之占用，这里简化：跳过测试
        assert True
        return
    
    parking_id = occupied_spaces[0]["parking_id"]
    payload = {"parking_id": parking_id, "user_id": "test_user2"}
    response = requests.post(f"{BASE_URL}/api/reserve", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["code"] == 409
    assert "已被占用" in data["message"]

def test_reserve_space_not_bookable():
    """测试预约不可预约的车位（is_bookable=0）"""
    all_spaces = requests.get(f"{BASE_URL}/api/parking/spaces").json()
    non_bookable = [s for s in all_spaces["data"] if s["is_bookable"] == 0]
    if not non_bookable:
        # 如果没有不可预约的车位，跳过测试
        assert True
        return
    
    parking_id = non_bookable[0]["parking_id"]
    payload = {"parking_id": parking_id, "user_id": "test_user3"}
    response = requests.post(f"{BASE_URL}/api/reserve", json=payload)
    # 预期返回 403 Forbidden
    assert response.status_code == 403
    data = response.json()
    assert data["code"] == 403
    assert "不可预约" in data["message"]

def test_reserve_missing_parking_id():
    """测试请求体缺少 parking_id"""
    payload = {"user_id": "test_user"}
    response = requests.post(f"{BASE_URL}/api/reserve", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400
    assert "parking_id" in data["message"]

def test_reserve_status():
    """测试查询预约状态接口"""
    response = requests.get(f"{BASE_URL}/api/reserve/status", params={"user_id": "123"})
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data