# products/management/commands/populate_filters.py

from django.core.management.base import BaseCommand
from django.db import transaction
# from products.models import ProductFeature, FeatureValue
from apps.products.models import ProductFeature, FeatureValue
class Command(BaseCommand):
    help = 'Finds product features with null filter_value, creates corresponding FeatureValue entries, and links them.'

    @transaction.atomic # این دستور باعث میشود که تمام عملیات یا با هم انجام شوند یا هیچکدام
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Starting the migration process...'))

        # پیدا کردن تمام ویژگی‌های محصول که هنوز filter_value ندارند
        features_to_update = ProductFeature.objects.filter(filter_value__isnull=True)
        total_count = features_to_update.count()

        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('No product features to update. Everything is already linked.'))
            return

        self.stdout.write(f'Found {total_count} product features to update.')

        created_count = 0
        updated_count = 0

        for pf in features_to_update:
            # اگر مقدار یا ویژگی اصلی وجود نداشت، از آن رد شو
            if not pf.value or not pf.feature:
                self.stdout.write(self.style.WARNING(f'Skipping ProductFeature ID {pf.id} due to missing data.'))
                continue

            # پیدا کردن یا ساختن یک FeatureValue جدید
            # get_or_create یک تاپل برمیگرداند: (آبجکت، created_boolean)
            feature_value_obj, created = FeatureValue.objects.get_or_create(
                feature=pf.feature,
                value_title=pf.value.strip()  # .strip() برای حذف فاصله‌های اضافی احتمالی
            )

            if created:
                created_count += 1

            # اتصال FeatureValue به ProductFeature
            pf.filter_value = feature_value_obj
            pf.save()
            updated_count += 1
            
            # نمایش پیشرفت کار
            self.stdout.write(f'Updated: {updated_count}/{total_count}', ending='\r')

        self.stdout.write('\n' + self.style.SUCCESS('--- Migration Complete ---'))
        self.stdout.write(f'Total ProductFeatures updated: {updated_count}')
        self.stdout.write(f'Total new FeatureValues created: {created_count}')