from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(name='format_product_description')
def format_product_description(text):
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    processed = []
    
    for p in paragraphs:
        if re.search(r'[:؛]$', p):
            p = f'<h4 class="desc-subtitle">{p}</h4>'
        else:
            p = f'<p>{p}</p>'
        
        p = re.sub(r'(ویژگی‌های کلیدی|مشخصات فنی|توضیحات تکمیلی)', 
                  r'<strong>\1</strong>', p)
        
        processed.append(p)
    
    return mark_safe('\n'.join(processed))