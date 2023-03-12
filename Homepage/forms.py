from django import forms
from .models import FoodCategory

class FoodCategoryForm(forms.ModelForm):
	class Meta:
		model = FoodCategory
		fields = ["categoryName","adminID"]
