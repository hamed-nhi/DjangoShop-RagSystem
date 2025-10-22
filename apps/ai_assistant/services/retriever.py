# apps/ai_assistant/services/retriever.py
import time
import faiss
import pickle
import numpy as np
import os
import sys
import meilisearch
from django.conf import settings
from sentence_transformers import SentenceTransformer
from apps.products.models import Product

class HybridRetriever:
    def __init__(self):
        sys.stdout.write("Loading models and indexes...\n")
        self.base_dir = os.path.join(settings.BASE_DIR, 'ai_data')
        self.faiss_index_path = os.path.join(self.base_dir, 'products.faiss')
        self.id_map_path = os.path.join(self.base_dir, 'product_ids.pkl')
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.faiss_index = faiss.read_index(self.faiss_index_path)
        with open(self.id_map_path, 'rb') as f:
            self.product_ids_map = pickle.load(f)
        self.meili_client = meilisearch.Client('http://127.0.0.1:7700', 'MASTER_KEY')
        self.meili_index = self.meili_client.index('products')
        sys.stdout.write("Models and indexes loaded successfully.\n")

    def _search_faiss(self, query_text, k=10):
        query_vector = self.model.encode([query_text])
        query_vector = np.array(query_vector).astype('float32')
        distances, indices = self.faiss_index.search(query_vector, k)
        results = []
        for i, index in enumerate(indices[0]):
            if index != -1:
                product_id = self.product_ids_map[index]
                score = 1 / (1 + distances[0][i])
                results.append({'id': product_id, 'score': score})
        return results

    def _search_meilisearch(self, query_text, k=10, filters: str = None):
        """Keyword search with MeiliSearch, with filtering capabilities."""
        options = {'limit': k}
        if filters:
            options['filter'] = filters
            
        search_results = self.meili_index.search(query_text, options)
        results = []
        for doc in search_results['hits']:
            results.append({'id': doc['id'], 'score': doc.get('_rankingScore', 1.0)})
        return results

    def search(self, query_text, k=5, filters: str = None):
        """
        Executes a weighted hybrid search using the RRF algorithm to prioritize keyword-based results.
        """
        print("\n" + "="*60)
        print(f"WEIGHTED HYBRID RETRIEVER ACTIVATED | Query: '{query_text}'")
        print("="*60)

        # --- 1. Execute both searches concurrently ---
        start_faiss = time.perf_counter()
        faiss_results = self._search_faiss(query_text, k=20)
        end_faiss = time.perf_counter()

        start_meili = time.perf_counter()
        meili_results = self._search_meilisearch(query_text, k=20, filters=filters)
        end_meili = time.perf_counter()

        # --- Log raw results ---
        faiss_ids = [res['id'] for res in faiss_results]
        meili_ids = [res['id'] for res in meili_results]
        print(f"-> [TIMER] Faiss Search took: {end_faiss - start_faiss:.4f} seconds")
        print(f"   [LOG] Raw Faiss IDs: {faiss_ids}")
        print(f"-> [TIMER] MeiliSearch took: {end_meili - start_meili:.4f} seconds")
        print(f"   [LOG] Raw MeiliSearch IDs: {meili_ids}")

        # --- 2. Fuse results with weighted RRF ---
        fused_scores = {}
        rrf_k = 60

        # Give more weight to MeiliSearch (keyword-based) results
        MEILI_WEIGHT = 2.0  # <-- Key change
        FAISS_WEIGHT = 1.0  # <-- Key change

        # Process MeiliSearch results with a higher weight
        for i, doc in enumerate(meili_results):
            doc_id = doc['id']
            fused_scores.setdefault(doc_id, 0)
            fused_scores[doc_id] += MEILI_WEIGHT * (1 / (rrf_k + i + 1))

        # Process Faiss results with a standard weight
        for i, doc in enumerate(faiss_results):
            doc_id = doc['id']
            fused_scores.setdefault(doc_id, 0)
            fused_scores[doc_id] += FAISS_WEIGHT * (1 / (rrf_k + i + 1))
            
        reranked_results = sorted(fused_scores.items(), key=lambda item: item[1], reverse=True)
        final_ids = [doc_id for doc_id, score in reranked_results[:k]]
        
        print(f"-> [LOG] Final Fused IDs (Weighted): {final_ids}")
        print("="*60 + "\n")
        
        return final_ids
