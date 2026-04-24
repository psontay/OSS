import decimal
from decimal import Decimal
from django.apps import apps
from django.db import models
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point


# =========================
# GET FORM META DATA
# =========================
# =========================
# GET FORM META DATA
# =========================
def get_model_fields_data(ModelClass, pk=None):
    e = get_object_or_404(ModelClass, pk=pk) if pk else None
    fields_data = []

    for field in ModelClass._meta.get_fields():
        if isinstance(field, models.Field):
            name, path, args, kwargs = field.deconstruct()

            if name == "id":
                continue
            
            # 🔥 Khởi tạo val an toàn ngay từ đầu vòng lặp
            val = getattr(e, name, None) if e else None

            # Xử lý giá trị mặc định
            if e:
                # Xử lý riêng cho PointField của GeoDjango
                if field.__class__.__name__ == "PointField" and val:
                    # x là Longitude, y là Latitude
                    kwargs["default"] = f"{val.y},{val.x}"
                else:
                    kwargs["default"] = val if val not in [None, ""] else kwargs.get("default")
            else:
                kwargs["default"] = kwargs.get("default")

            default_val = kwargs.get("default")

            # Convert định dạng số để render HTML an toàn
            if isinstance(default_val, (float, int, decimal.Decimal)):
                kwargs["default"] = str(default_val)
            elif isinstance(default_val, str):
                kwargs["default"] = default_val.replace(",", ".")

            field_data = {
                "name": name,
                "type": field.__class__.__name__,
                "kwargs": kwargs,
                "options": None
            }

            # 🔥 Xử lý options cho ForeignKey
            if field_data["type"] == "ForeignKey":
                model_path = kwargs.get("to")
                if model_path:
                    try:
                        app_label, model_name = model_path.split(".")
                        RelatedModel = apps.get_model(app_label, model_name)
                        field_data["options"] = RelatedModel.objects.all()
                    except Exception:
                        field_data["options"] = []

            fields_data.append(field_data)

    return fields_data, e


# =========================
# SAVE MODEL FROM REQUEST
# =========================
def save_model_from_request(request, model_class, instance=None):
    """
    instance = None -> create mới
    instance != None -> update
    """
    instance = instance or model_class()

    fields_data = []

    for field in instance._meta.get_fields():
        if hasattr(field, "deconstruct"):
            name, path, args, kwargs = field.deconstruct()
            fields_data.append({
                "name": name,
                "type": field.get_internal_type(),
                "kwargs": kwargs
            })

    for field in fields_data:
        field_name = field["name"]
        field_type = field["type"]

        # =========================
        # 1. CHAR / TEXT
        # =========================
        if field_type in ["CharField", "TextField"]:
            val = request.POST.get(field_name)
            if val is not None:
                setattr(instance, field_name, val)

        # =========================
        # 2. FLOAT
        # =========================
        elif field_type == "FloatField":
            val = request.POST.get(field_name)
            if val:
                val = val.replace(",", ".")
                try:
                    setattr(instance, field_name, float(val))
                except:
                    pass

        # =========================
        # 3. DECIMAL (FIX CHUẨN)
        # =========================
        elif field_type == "DecimalField":
            val = request.POST.get(field_name)
            if val:
                val = val.replace(",", ".")
                try:
                    setattr(instance, field_name, Decimal(val))
                except:
                    pass

        # =========================
        # 4. FOREIGN KEY (SAFE)
        # =========================
        elif field_type == "ForeignKey":
            val = request.POST.get(field_name)
            if val:
                rel_model = field["kwargs"].get("to")

                try:
                    app_label, model_name = rel_model.split(".")
                    RelatedModel = apps.get_model(app_label, model_name)
                    related_obj = RelatedModel.objects.filter(id=val).first()

                    if related_obj:
                        setattr(instance, field_name, related_obj)
                except:
                    pass

        # =========================
        # 5. POINT FIELD
        # =========================
        elif field_type == "PointField":
            val = request.POST.get(field_name)
            if val:
                try:
                    lat, lng = map(float, val.split(","))
                    setattr(instance, field_name, Point(lng, lat))
                except:
                    pass

        # =========================
        # 6. IMAGE FIELD (single)
        # =========================
        elif field_type == "ImageField":
            uploaded_file = request.FILES.get(field_name)
            if uploaded_file:
                setattr(instance, field_name, uploaded_file)
        elif field_type == "BooleanField":
            # Nếu checkbox được tick, val sẽ là 'on'. Nếu không tick, val sẽ là None.
            val = request.POST.get(field_name)
            setattr(instance, field_name, True if val else False)
        # =========================
        # 7. DEFAULT
        # =========================
        else:
            val = request.POST.get(field_name)
            if val is not None:
                setattr(instance, field_name, val)

    instance.save()
    return instance