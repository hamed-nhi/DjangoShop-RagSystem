# apps/ai_assistant/services/tools.py

from typing import List
from langchain_core.tools import tool
from apps.products.models import Product
from apps.orders.shop_card import ShopCart
from . import hybrid_retriever
from middlewares.middlewares import RequestMiddleware
from typing import List, Optional
from .global_services import hybrid_retriever
from django.utils.html import strip_tags

@tool
def search_products(
    query: str,
    brand: Optional[str] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    price_around: Optional[int] = None
) -> str:
    """
    Searches for products based on a text query and optional brand/price filters.
    - query: The user's full search text, including any technical specs like RAM or GPU (e.g., 'gaming laptop with 16GB RAM').
    - brand: The specific brand requested (e.g., 'Lenovo', 'HP').
    - price_min: The minimum price.
    - price_max: The maximum price.
    - price_around: An approximate price.
    """
    print(f"--- Search tool invoked with: query='{query}', brand='{brand}', price_min='{price_min}', price_max='{price_max}' ---")

    # --- Price Logic (No change) ---
    if price_max and not price_min and not price_around:
        price_min = int(price_max * 0.85)
    elif price_around and not price_min and not price_max:
        range_percent = 0.20
        price_min = int(price_around * (1 - range_percent))
        price_max = int(price_around * (1 + range_percent))

    # --- Simplified Filter Construction ---
    filters = []
    if brand:
        filters.append(f"brand_name = '{brand.lower()}'")
    if price_min is not None:
        filters.append(f"price >= {price_min}")
    if price_max is not None:
        filters.append(f"price <= {price_max}")

    meili_filter = " AND ".join(filters) if filters else None

    try:
        product_ids = hybrid_retriever.search(query, k=10, filters=meili_filter)
        if not product_ids:
            return "Unfortunately, no products were found with these specifications."

        products_query = Product.objects.filter(id__in=product_ids)
        
        # --- Simplified Final Filtering ---
        if brand:
            products_query = products_query.filter(brand__brand_title__iexact=brand)
        if price_min is not None:
            products_query = products_query.filter(price__gte=price_min)
        if price_max is not None:
            products_query = products_query.filter(price__lte=price_max)
        
        final_products = list(products_query.order_by('-price')[:5])

        if not final_products:
             return "Unfortunately, no products were found with these specifications in the specified filter range."

        results = ["Here are the best matches found for your query:\n"]
        for p in final_products:
            results.append(f"- Name: {p.product_name} (ID: {p.id})\n  Price: {p.price} تومان")
        return "\n".join(results)
    except Exception as e:
        return f"An error occurred while searching for products: {e}"

@tool
def compare_products(product_ids: List[int]) -> str:
    """زمانی از این ابزار استفاده کن که کاربر صراحتاً درخواست مقایسه دو یا چند محصول را دارد."""
    print(f"--- ابزار مقایسه فراخوانی شد برای محصولات: {product_ids} ---")
    if not product_ids or len(product_ids) < 2:
        return "برای مقایسه حداقل به دو شناسه محصول نیاز است."
    try:
        products = Product.objects.filter(id__in=product_ids).prefetch_related('product_features__feature')
        if products.count() != len(product_ids):
            return "یک یا چند محصول با شناسه‌های داده شده یافت نشد."
        all_features = set()
        product_data = {}
        for p in products:
            features = {pf.feature.feature_name: pf.value for pf in p.product_features.all()}
            product_data[p.id] = {'name': p.product_name, 'features': features}
            all_features.update(features.keys())
        header = "| ویژگی | " + " | ".join([p.product_name[:20] for p in products]) + " |"
        separator = "|---|" * (len(products) + 1)
        rows = [header, separator]
        for feature in sorted(list(all_features)):
            row = f"| {feature} |"
            for p in products:
                value = product_data[p.id]['features'].get(feature, '---')
                row += f" {value} |"
            rows.append(row)
        return "جدول مقایسه محصولات:\n" + "\n".join(rows)
    except Exception as e:
        return f"هنگام مقایسه محصولات خطایی رخ داد: {e}"

@tool
def add_to_cart(product_id: int) -> str:
    """زمانی از این ابزار استفاده کن که کاربر قصد خرید دارد و می‌خواهد محصولی را به سبد خرید اضافه کند."""
    print(f"--- ابزار افزودن به سبد خرید فراخوانی شد برای محصول: {product_id} ---")
    try:
        request = RequestMiddleware(get_response=None).thread_local.current_request
        if not request:
            return "خطای سیستمی: امکان دسترسی به سبد خرید وجود ندارد."
        product = Product.objects.get(id=product_id)
        cart = ShopCart(request)
        cart.add(product, 1)
        return f"محصول '{product.product_name}' با موفقیت به سبد خرید شما اضافه شد."
    except Product.DoesNotExist:
        return f"محصولی با شناسه {product_id} یافت نشد."
    except Exception as e:
        return f"هنگام افزودن محصول به سبد خرید خطایی رخ داد: {e}"



@tool
def get_product_details(product_id: int) -> str:
    """
    Use this tool to get all detailed specifications and features for a single, specific product ID.
    This is useful when the user asks for more details, specifications, or information about one particular item.
    - product_id: The unique identifier of the product to look up.
    """
    print(f"--- Get Product Details tool invoked for ID: {product_id} ---")
    try:
        product = Product.objects.prefetch_related('product_features__feature').get(id=product_id)

        details = [f"Product Details for '{product.product_name}' (ID: {product.id}):\n"]
        details.append(f"- Price: {product.price:,} تومان")
        
        features = product.product_features.all()
        if features:
            details.append("\n- Full Specifications:")
            for pf in features:
                details.append(f"  - {pf.feature.feature_name}: {pf.value}")
        
        return "\n".join(details)

    except Product.DoesNotExist:
        return f"Error: A product with ID {product_id} was not found."
    except Exception as e:
        return f"An error occurred while fetching product details: {e}"