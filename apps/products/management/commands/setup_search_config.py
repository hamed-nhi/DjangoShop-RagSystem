# in apps/products/management/commands/setup_search_config.py

from django.core.management.base import BaseCommand
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Drops and recreates the custom PostgreSQL text search configuration.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("--- Starting database search configuration setup ---"))

        # SQL commands to be executed
        drop_config_sql = "DROP TEXT SEARCH CONFIGURATION IF EXISTS persian_english_config CASCADE;"
        drop_dict_sql = "DROP TEXT SEARCH DICTIONARY IF EXISTS persian_synonym_dict;"
        
        create_dict_sql = """
        CREATE TEXT SEARCH DICTIONARY persian_synonym_dict (
            TEMPLATE = synonym,
            SYNONYMS = 'persian_synonyms'
        );
        """
        
        create_config_sql = "CREATE TEXT SEARCH CONFIGURATION persian_english_config (COPY = english);"
        
        alter_config_sql = """
        ALTER TEXT SEARCH CONFIGURATION persian_english_config
        ALTER MAPPING FOR asciiword, hword_asciipart, asciihword, word, hword
        WITH persian_synonym_dict, english_stem;
        """
        
        test_sql = "SELECT to_tsvector('persian_english_config', 'لپ تاپ اپل');"

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    self.stdout.write("Step 1: Cleaning up old objects...")
                    cursor.execute(drop_config_sql)
                    cursor.execute(drop_dict_sql)
                    self.stdout.write(self.style.SUCCESS("Cleanup complete."))

                    self.stdout.write("Step 2: Creating new dictionary...")
                    cursor.execute(create_dict_sql)
                    self.stdout.write(self.style.SUCCESS("Dictionary created."))

                    self.stdout.write("Step 3: Creating new configuration...")
                    cursor.execute(create_config_sql)
                    cursor.execute(alter_config_sql)
                    self.stdout.write(self.style.SUCCESS("Configuration created and altered."))
            
            self.stdout.write(self.style.WARNING("\n--- Verification Step ---"))
            with connection.cursor() as cursor:
                self.stdout.write(f"Running test: {test_sql}")
                cursor.execute(test_sql)
                result = cursor.fetchone()
                self.stdout.write(self.style.SUCCESS(f"Test Result: {result[0]}"))
                self.stdout.write(self.style.SUCCESS("\n🎉 Configuration setup was successful!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nAn error occurred: {e}"))
            self.stdout.write(self.style.ERROR("Setup failed. Please review the error message."))