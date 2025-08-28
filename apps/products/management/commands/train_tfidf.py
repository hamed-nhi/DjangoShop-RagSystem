# in apps/products/management/commands/train_tfidf.py

import os
import pickle
from django.conf import settings
from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
from apps.products.models import Product

# Define the path to save our trained model
MODEL_DIR = os.path.join(settings.BASE_DIR, 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')

class Command(BaseCommand):
    help = 'Trains and saves a TF-IDF vectorizer based on product knowledge documents.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("🚀 Starting TF-IDF model training..."))

        # 1. Create the directory for the model if it doesn't exist
        os.makedirs(MODEL_DIR, exist_ok=True)

        # 2. Create the corpus from all product documents
        self.stdout.write("Fetching products and creating corpus...")
        products = Product.objects.all()
        corpus = [p.create_rich_knowledge_document() for p in products]
        
        if not corpus:
            self.stdout.write(self.style.ERROR("No product documents found to train on. Exiting."))
            return

        self.stdout.write(f"Corpus created with {len(corpus)} documents.")

        # 3. Initialize and train the TF-IDF Vectorizer
        self.stdout.write("Training TF-IDF Vectorizer...")
        # We can add Persian stop words here if needed in the future, but TF-IDF handles them well
        vectorizer = TfidfVectorizer() 
        vectorizer.fit(corpus)
        self.stdout.write(self.style.SUCCESS("✅ Training complete."))

        # 4. Save the trained vectorizer to a file
        self.stdout.write(f"Saving trained model to: {MODEL_PATH}")
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(vectorizer, f)

        self.stdout.write(self.style.SUCCESS("-" * 50))
        self.stdout.write(self.style.SUCCESS("🎉 TF-IDF model trained and saved successfully!"))
        self.stdout.write(self.style.SUCCESS("-" * 50))