from django import forms

from ..model.category import Category
from ..model.plant import Plant
from ..model.store_branch import StoreBranch
from ..model.store_stock import StoreStock
from ..model.user import User

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image']

class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = '__all__'

class BranchForm(forms.ModelForm):
    class Meta:
        model = StoreBranch
        fields = '__all__'

class StockForm(forms.ModelForm):
    class Meta:
        model = StoreStock
        fields = ['branch', 'plant', 'quantity']