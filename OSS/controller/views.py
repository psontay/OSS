from django.shortcuts import render, redirect
from OSS.helper.forms_helper import get_model_fields_data, save_model_from_request
from OSS.model import Plant


def test_form(request):
    # Bỏ model muốn tạo tạo form vào đây
    fields = get_model_fields_data(Plant)

    return render(request, "pages/test-form.html", {"fields": fields})

def test_form_save(request):
    instance = save_model_from_request(request, Plant)
    instance.save()

    return redirect("test_form")
def aubout_us(request):
    return render(request, 'pages/about_us.html')