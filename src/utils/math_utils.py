# src/utils/math_utils.py

import random
import math

def distance(a, b):
    """Tính khoảng cách Euclidean giữa hai điểm a và b."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def random_position(bounds=(1000, 800)):
    """Trả về vị trí ngẫu nhiên trong giới hạn màn hình."""
    return (random.randint(0, bounds[0]), random.randint(0, bounds[1]))

def chance(percent):
    """Trả về True với xác suất phần trăm cho trước."""
    return random.random() < percent / 100
