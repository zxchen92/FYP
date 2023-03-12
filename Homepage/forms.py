from django import forms
from django.contrib.auth.models import User
from .models import FoodCategory

class FoodCategoryForm(forms.ModelForm):
	categoryName = forms.CharField(max_length=30)

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(FoodCategoryForm, self).__init__(*args, **kwargs)

	def save(self, commit=True, *args, **kwargs):
		instance = super(FoodCategoryForm, self).save(commit=False, *args, **kwargs)
		instance.categoryName = self.cleaned_data['categoryName']
		instance.adminID = self.request.user.id
		if commit:
			instance.save()
		return instance

	class Meta:
		model = FoodCategory
		fields = ["categoryName"]
