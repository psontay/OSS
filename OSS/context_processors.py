# GISDjango/context_processors.py
from OSS.model import Category

def global_categories(request):
    # Trả về một dictionary chứa danh sách category cho toàn bộ project
    return {
        'all_categories': Category.objects.all()
    }