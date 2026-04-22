from django import forms
from django.db.models import Sum

from OSS.model import User, StoreStock

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email' ,'phone_number', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
class StoreStockForm(forms.ModelForm):
    class Meta:
        model = StoreStock
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Nếu đang chỉnh sửa hoặc thêm mới cho một cây cụ thể
        if self.instance and hasattr(self.instance, 'plant'):
            plant = self.instance.plant

            # 1. Tính tổng đã chia cho các chi nhánh (trừ chi nhánh hiện tại nếu đang sửa)
            other_stocks = StoreStock.objects.filter(plant=plant)
            if self.instance.pk:
                other_stocks = other_stocks.exclude(pk=self.instance.pk)

            total_distributed = other_stocks.aggregate(Sum('quantity'))['quantity__sum'] or 0

            # 2. Tính số lượng còn lại có thể nhập
            remaining = plant.quantity - total_distributed

            # 3. Gắn thông báo vào ô 'quantity'
            self.fields['quantity'].help_text = (
                f"<b style='color: #16a34a;'>Hạn mức còn lại: {remaining} cây </b> "
                f"(Tổng kho: {plant.quantity}, Đã chia: {total_distributed})"
            )