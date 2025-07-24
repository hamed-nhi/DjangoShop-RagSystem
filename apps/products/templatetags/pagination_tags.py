from django import template

register = template.Library()

@register.simple_tag
def query_transform(request_get, **kwargs):
    """
    تگی که پارامترهای فعلی URL را گرفته و موارد جدید را آپدیت یا اضافه می‌کند.
    """
    updated = request_get.copy()
    for key, value in kwargs.items():
        updated[key] = value
    return updated.urlencode()