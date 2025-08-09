from django import template
from ..models import ProductFeature
from ..translations import FEATURE_VALUE_TRANSLATIONS 

register = template.Library()

@register.simple_tag
def get_feature_value(product, feature):
    try:
        value = ProductFeature.objects.get(product=product, feature=feature).value
        # Use the imported dictionary for translation
        return FEATURE_VALUE_TRANSLATIONS.get(value.lower(), value)
    except ProductFeature.DoesNotExist:
        return "—"