
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.products.models import Product, ProductFeature, Feature


def compute_category_from_product_name(model_name: str, gpu_type: str) -> str:
    """
    Determine the category of a product based on model name keywords and GPU type.
    Returns one of: 'gaming', 'premium', 'budget', 'mainstream'.
    """
    name_lower = model_name.lower()
    # Gaming keywords and discrete GPU
    gaming_keywords = ['gaming', 'rog', 'tuf', 'victus', 'katana', 'nitro',
                       'predator', 'raider', 'loq', 'omen', 'alienware',
                       'bravo', 'gf63', 'stealth', 'flow']
    if any(kw.lower() in name_lower for kw in gaming_keywords) or ('rtx' in gpu_type.lower() or 'gtx' in gpu_type.lower() or 'graph' in gpu_type.lower()):
        return 'gaming'

    # Premium keywords or strong CPU / RAM conditions
    premium_keywords = ['macbook', 'apple', 'spectre', 'xps', 'zenbook',
                        'surface', 'zbook', 'galaxy book']
    premium_cpus = ['core i7', 'core i9', 'm1', 'm2', 'm3']
    if any(kw.lower() in name_lower for kw in premium_keywords):
        return 'premium'

    # Budget conditions: economical brands or weak CPU or low price-like indicator
    budget_keywords = ['v14', 'v15', '15s', '14s', 'extensa', 'aspire',
                       'inspiron', 'modern', 'vivobook', 'megabook', 'inbook', '255']
    budget_brands = ['tecno', 'infinix', 'wings']
    if any(kw.lower() in name_lower for kw in budget_keywords):
        return 'budget'

    # Default mainstream
    return 'mainstream'


class Command(BaseCommand):
    help = 'Update product prices based on category and hardware features'

    def handle(self, *args, **options):
        # Ensure category feature exists
        category_feature, _ = Feature.objects.get_or_create(feature_name='category')
        processor_feature, _ = Feature.objects.get_or_create(feature_name='processor_tier')
        ram_feature, _ = Feature.objects.get_or_create(feature_name='ram_memory')
        resolution_feature, _ = Feature.objects.get_or_create(feature_name='resolution_width')
        gpu_feature, _ = Feature.objects.get_or_create(feature_name='gpu_type')

        # Constants
        rate = Decimal('700') * Decimal('1.19')
        adjustments = {
            'gaming': Decimal('1.27'),
            'premium': Decimal('0.89'),
            'budget': Decimal('0.80'),
            'mainstream': Decimal('0.95'),
        }

        updated_products = []

        # Prefetch product features to reduce DB hits
        products = Product.objects.prefetch_related('productfeature_set__feature')

        for product in products:
            # Build a map feature_name -> value
            features_map = {pf.feature.feature_name: pf.value for pf in product.productfeature_set.all()}

            # Category
            category_value = features_map.get('category')
            if not category_value:
                # compute and create if missing
                category_value = compute_category_from_product_name(
                    product.product_name,
                    features_map.get('gpu_type', '')
                )
                ProductFeature.objects.create(
                    product=product,
                    feature=category_feature,
                    value=category_value
                )

            category_value = category_value.lower()
            coeff = adjustments.get(category_value, adjustments['mainstream'])

            # Base price and new price calculation
            base_price = Decimal(product.price)
            new_price = (base_price * rate * coeff).quantize(Decimal('1'))

            # Update only if changed
            if new_price != base_price:
                product.price = int(new_price)
                updated_products.append(product)
                self.stdout.write(self.style.SUCCESS(
                    f"{product.product_name}: {base_price} -> {new_price}"))

        # Bulk update all at once
        if updated_products:
            Product.objects.bulk_update(updated_products, ['price'])

        self.stdout.write(self.style.SUCCESS(
            f"Updated prices for {len(updated_products)} products"))
