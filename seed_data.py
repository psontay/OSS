#!/usr/bin/env python
"""Seed data script for GIS-OSS project."""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OSS.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from OSS.models.category import Category
from OSS.models.plant import Plant
from OSS.models.store_branch import StoreBranch
from OSS.models.store_stock import StoreStock
from django.contrib.gis.geos import Point

print("=== SEEDING DATA ===")

# 1. CATEGORIES
categories_data = [
    {"name": "Cây cảnh trong nhà", "slug": "cay-canh-trong-nha", "description": "Cây thích hợp trồng trong nhà, văn phòng, ít cần ánh nắng trực tiếp."},
    {"name": "Cây cảnh ngoài trời", "slug": "cay-canh-ngoai-troi", "description": "Cây chịu nắng tốt, phù hợp sân vườn, ban công."},
    {"name": "Xương rồng & Sen đá", "slug": "xuong-rong-sen-da", "description": "Các loại cây mọng nước, dễ chăm sóc, ưa nắng."},
    {"name": "Cây thủy sinh", "slug": "cay-thuy-sinh", "description": "Cây sống trong môi trường nước, dùng cho hồ cá, bể thủy sinh."},
    {"name": "Cây cảnh để bàn", "slug": "cay-canh-de-ban", "description": "Cây nhỏ gọn, trang trí bàn làm việc, kệ sách."},
    {"name": "Hoa & Cây cảnh", "slug": "hoa-cay-canh", "description": "Hoa và cây cảnh có hoa đẹp, dùng làm quà tặng."},
]

cats = {}
for cd in categories_data:
    c, created = Category.objects.get_or_create(slug=cd["slug"], defaults=cd)
    cats[c.slug] = c
    if created:
        print(f"  Created category: {c.name}")
    else:
        print(f"  Category exists: {c.name}")

# 2. PLANTS
plants_data = [
    # Indoor plants
    {"name": "Cây Kim Ngân", "price": 150000, "category": "cay-canh-trong-nha",
     "description": "Pachira aquatica - Cây phong thủy mang lại may mắn, tài lộc. Dễ chăm sóc, ưa bóng râm.",
     "min_temp": 16, "max_temp": 32, "min_ph": 5.5, "max_ph": 7.5, "min_humidity": 40, "max_humidity": 80, "max_clay": 50},
    {"name": "Cây Trầu Bà", "price": 80000, "category": "cay-canh-trong-nha",
     "description": "Epipremnum aureum - Cây leo thanh lọc không khí, cực kỳ dễ trồng.",
     "min_temp": 15, "max_temp": 30, "min_ph": 5.5, "max_ph": 7.0, "min_humidity": 50, "max_humidity": 90, "max_clay": 60},
    {"name": "Cây Lưỡi Hổ", "price": 120000, "category": "cay-canh-trong-nha",
     "description": "Sansevieria trifasciata - Cây lọc không khí ban đêm, chịu hạn tốt.",
     "min_temp": 10, "max_temp": 35, "min_ph": 5.0, "max_ph": 8.0, "min_humidity": 30, "max_humidity": 70, "max_clay": 40},
    {"name": "Cau Tiểu Trâm", "price": 200000, "category": "cay-canh-trong-nha",
     "description": "Chamaedorea elegans - Cây cọ nhỏ thanh lịch, thích hợp phòng khách.",
     "min_temp": 18, "max_temp": 28, "min_ph": 6.0, "max_ph": 7.0, "min_humidity": 60, "max_humidity": 90, "max_clay": 30},
    {"name": "Cây Ngọc Ngân", "price": 95000, "category": "cay-canh-trong-nha",
     "description": "Dieffenbachia - Lá xanh đốm trắng đẹp mắt, cây văn phòng phổ biến.",
     "min_temp": 18, "max_temp": 30, "min_ph": 5.5, "max_ph": 7.0, "min_humidity": 50, "max_humidity": 80, "max_clay": 50},
    # Outdoor plants
    {"name": "Hoa Giấy", "price": 250000, "category": "cay-canh-ngoai-troi",
     "description": "Bougainvillea - Hoa rực rỡ nhiều màu, chịu nắng nóng tốt, dễ tạo dáng.",
     "min_temp": 20, "max_temp": 40, "min_ph": 5.5, "max_ph": 7.5, "min_humidity": 30, "max_humidity": 80, "max_clay": 50},
    {"name": "Cây Vạn Tuế", "price": 500000, "category": "cay-canh-ngoai-troi",
     "description": "Cycas revoluta - Cây cảnh cổ điển, sống lâu năm, phù hợp sân vườn rộng.",
     "min_temp": 15, "max_temp": 38, "min_ph": 6.0, "max_ph": 7.5, "min_humidity": 40, "max_humidity": 80, "max_clay": 40},
    {"name": "Cây Lộc Vừng", "price": 350000, "category": "cay-canh-ngoai-troi",
     "description": "Barringtonia acutangula - Cây bóng mát, hoa đỏ rủ đẹp, hợp trồng ven hồ.",
     "min_temp": 18, "max_temp": 35, "min_ph": 5.0, "max_ph": 7.0, "min_humidity": 60, "max_humidity": 95, "max_clay": 70},
    {"name": "Hoa Hồng", "price": 180000, "category": "hoa-cay-canh",
     "description": "Rosa hybrid - Hoa đẹp, hương thơm quyến rũ, cần nhiều nắng và chăm sóc.",
     "min_temp": 15, "max_temp": 30, "min_ph": 6.0, "max_ph": 7.0, "min_humidity": 50, "max_humidity": 80, "max_clay": 40},
    {"name": "Cây Hoa Sứ", "price": 300000, "category": "hoa-cay-canh",
     "description": "Adenium obesum - Thân mọng, hoa đẹp, chịu hạn tốt, phù hợp ban công.",
     "min_temp": 20, "max_temp": 38, "min_ph": 6.0, "max_ph": 8.0, "min_humidity": 30, "max_humidity": 70, "max_clay": 30},
    # Succulents / Cacti
    {"name": "Sen Đá Kim Cương", "price": 60000, "category": "xuong-rong-sen-da",
     "description": "Echeveria elegans - Sen đá phổ biến, hình hoa sen đẹp, dễ nhân giống.",
     "min_temp": 10, "max_temp": 35, "min_ph": 6.0, "max_ph": 7.5, "min_humidity": 20, "max_humidity": 60, "max_clay": 20},
    {"name": "Xương Rồng Tai Thỏ", "price": 85000, "category": "xuong-rong-sen-da",
     "description": "Opuntia microdasys - Hình dáng độc đáo, gai mềm, an toàn cho trẻ em.",
     "min_temp": 15, "max_temp": 38, "min_ph": 6.0, "max_ph": 8.0, "min_humidity": 10, "max_humidity": 50, "max_clay": 25},
    {"name": "Sen Đá Móng Rồng", "price": 70000, "category": "xuong-rong-sen-da",
     "description": "Haworthia fasciata - Lá mọng sọc trắng, chịu bóng bán phần tốt.",
     "min_temp": 10, "max_temp": 32, "min_ph": 6.0, "max_ph": 7.5, "min_humidity": 30, "max_humidity": 65, "max_clay": 25},
    # Aquatic plants
    {"name": "Bèo Nhật", "price": 35000, "category": "cay-thuy-sinh",
     "description": "Limnobium laevigatum - Cây nổi che bóng cho hồ cá, hấp thụ nitrat tốt.",
     "min_temp": 20, "max_temp": 30, "min_ph": 6.0, "max_ph": 8.0, "min_humidity": 70, "max_humidity": 100, "max_clay": 10},
    {"name": "Rong Đuôi Chồn", "price": 40000, "category": "cay-thuy-sinh",
     "description": "Ceratophyllum demersum - Cây ngập nước, oxy hóa tốt, không cần đất nền.",
     "min_temp": 15, "max_temp": 30, "min_ph": 6.0, "max_ph": 8.5, "min_humidity": 80, "max_humidity": 100, "max_clay": 0},
    # Desktop / Bonsai
    {"name": "Bonsai Sam Hương", "price": 1500000, "category": "cay-canh-de-ban",
     "description": "Juniperus chinensis - Bonsai cổ điển, dáng đẹp, cần cắt tỉa định kỳ.",
     "min_temp": 10, "max_temp": 35, "min_ph": 5.5, "max_ph": 7.5, "min_humidity": 40, "max_humidity": 80, "max_clay": 40},
    {"name": "Cây Kim Quýt", "price": 400000, "category": "cay-canh-de-ban",
     "description": "Citrus microcarpa - Quả vàng rực, biểu tượng may mắn ngày Tết.",
     "min_temp": 18, "max_temp": 33, "min_ph": 5.5, "max_ph": 7.0, "min_humidity": 50, "max_humidity": 85, "max_clay": 45},
    {"name": "Cây Ngũ Gia Bì", "price": 220000, "category": "cay-canh-de-ban",
     "description": "Schefflera arboricola - Lá xòe hình ô, phong thủy tốt, lọc không khí.",
     "min_temp": 15, "max_temp": 30, "min_ph": 5.5, "max_ph": 7.0, "min_humidity": 50, "max_humidity": 85, "max_clay": 50},
    # Flowers
    {"name": "Hoa Lan Hồ Điệp", "price": 350000, "category": "hoa-cay-canh",
     "description": "Phalaenopsis - Lan đẹp, hoa lâu tàn, quà tặng cao cấp.",
     "min_temp": 20, "max_temp": 30, "min_ph": 5.5, "max_ph": 6.5, "min_humidity": 60, "max_humidity": 90, "max_clay": 10},
    {"name": "Hoa Đỗ Quyên", "price": 280000, "category": "hoa-cay-canh",
     "description": "Rhododendron simsii - Hoa rực rỡ mùa xuân, thích hợp khí hậu mát.",
     "min_temp": 12, "max_temp": 25, "min_ph": 4.5, "max_ph": 6.0, "min_humidity": 50, "max_humidity": 80, "max_clay": 40},
]

plants = []
for pd in plants_data:
    cat = cats.get(pd.pop("category"))
    plant, created = Plant.objects.get_or_create(name=pd["name"], defaults={**pd, "category": cat, "is_available": True})
    plants.append(plant)
    if created:
        print(f"  Created plant: {plant.name} ({plant.price:,.0f}₫)")
    else:
        print(f"  Plant exists: {plant.name}")

# 3. BRANCHES
branches_data = [
    {"name": "Chi nhánh Quận 1", "address": "123 Lê Lợi, Phường Bến Thành, Quận 1, TP. Hồ Chí Minh",
     "phone": "02838251234", "lat": 10.7769, "lng": 106.7009, "delivery_radius": 5000, "opening_hours": "7:00 - 21:00"},
    {"name": "Chi nhánh Quận 7", "address": "456 Nguyễn Văn Linh, Phường Tân Phong, Quận 7, TP. Hồ Chí Minh",
     "phone": "02837764567", "lat": 10.7322, "lng": 106.7238, "delivery_radius": 7000, "opening_hours": "7:30 - 20:30"},
    {"name": "Chi nhánh Thủ Đức", "address": "789 Võ Văn Ngân, Phường Linh Chiểu, TP. Thủ Đức",
     "phone": "02838967890", "lat": 10.8501, "lng": 106.7719, "delivery_radius": 6000, "opening_hours": "8:00 - 21:00"},
    {"name": "Chi nhánh Gò Vấp", "address": "15 Nguyễn Văn Lượng, Phường 17, Quận Gò Vấp, TP. Hồ Chí Minh",
     "phone": "02839890001", "lat": 10.8375, "lng": 106.6655, "delivery_radius": 5500, "opening_hours": "7:00 - 20:00"},
    {"name": "Chi nhánh Bình Thạnh", "address": "88 Xô Viết Nghệ Tĩnh, Phường 21, Quận Bình Thạnh, TP. Hồ Chí Minh",
     "phone": "02838443322", "lat": 10.8034, "lng": 106.7132, "delivery_radius": 4500, "opening_hours": "7:30 - 20:00"},
]

branches = []
for bd in branches_data:
    lat = bd.pop("lat")
    lng = bd.pop("lng")
    branch, created = StoreBranch.objects.get_or_create(name=bd["name"], defaults={
        **bd, "location": Point(lng, lat, srid=4326), "is_active": True
    })
    branches.append(branch)
    if created:
        print(f"  Created branch: {branch.name} @ ({lat}, {lng})")
    else:
        print(f"  Branch exists: {branch.name}")

# 4. STOCKS — assign plants to branches with varied quantities
import random
random.seed(42)
stock_count = 0
for branch in branches:
    for plant in plants:
        # Each branch stocks most plants, but some plants not in all branches
        if random.random() < 0.7:  # 70% chance a branch stocks this plant
            quantity = random.randint(10, 100)
            _, created = StoreStock.objects.get_or_create(
                branch=branch, plant=plant,
                defaults={"quantity": quantity}
            )
            if created:
                stock_count += 1

print(f"  Created {stock_count} stock records")

# Summary
print(f"\n=== SEED COMPLETE ===")
print(f"  Categories: {Category.objects.count()}")
print(f"  Plants: {Plant.objects.count()}")
print(f"  Branches: {StoreBranch.objects.count()}")
print(f"  Stocks: {StoreStock.objects.count()}")
