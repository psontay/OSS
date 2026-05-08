from rest_framework import serializers
from .models import Plant, Category, Order, OrderItem, StoreBranch, StoreStock, User

# 1. Serializer cho Sản phẩm & Danh mục
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class PlantSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Plant
        fields = '__all__'

# 2. Serializer cho Đơn hàng
class OrderItemSerializer(serializers.ModelSerializer):
    plant_name = serializers.ReadOnlyField(source='plant.name')
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_item_count(self, obj):
        return obj.items.count()

# 3. Serializer cho User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'address']


# Thêm vào phần Serializer cho Chi nhánh
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreBranch
        fields = '__all__'

# Thêm vào phần Serializer cho Tồn kho
class StoreStockSerializer(serializers.ModelSerializer):
    plant_name = serializers.ReadOnlyField(source='plant.name')
    branch_name = serializers.ReadOnlyField(source='branch.name')

    class Meta:
        model = StoreStock
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        # Đây là bước cực kỳ quan trọng để bảo mật
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user
# OSS/serializers.py

class CartInputSerializer(serializers.Serializer):
    plant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class CheckoutInputSerializer(serializers.Serializer):
    items = CartInputSerializer(many=True) # Danh sách món hàng
    full_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=500)
    location_coord = serializers.CharField() # "lat,lng"