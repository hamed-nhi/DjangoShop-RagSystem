# apps/search_app/views.py

from django.shortcuts import render
from apps.products.models import Product, Brand
from django.views import View
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F, Min, Max, Count, Q


# Dictionary for multi-word phrases that should be translated first.
MULTI_WORD_PHRASES = {
    'اچ پی': 'hp',
    'اچ بی': 'hp',

    'ال جی': 'lg',
    'لب تاب': 'laptop', # Handles "لب تاب" before splitting
    "لپ تاپ" : 'laptop',
    'صفحه لمسی': 'touchscreen',
    'کارت گرافیک': 'graphics',
    'حرفه ای': 'professional',
    'کور ای ۵': 'i5', # Common spoken forms
    'کور ای ۷': 'i7',
    'کور ای ۹': 'i9',
}

# Dictionary for single words.


# Dictionary for single words (cleaned version without brand/series names)
SINGLE_WORD_TERMS = {
    'ایسوس': 'asus', 'اسوس': 'asus', 'دل': 'dell', 'اچپی': 'hp', 'ایسر': 'acer', 'ایصر': 'acer',
    'لنوو': 'lenovo', 'اپل': 'apple', 'مایکروسافت': 'microsoft', 'سرفیس': 'surface',
    'ام اس ای': 'msi', 'سامسونگ': 'samsung', 'سامسنگ': 'samsunge', 'گیگابایت': 'gigabyte',
    'آنر': 'honor', 'ریلمی': 'realme', 'الجی': 'lg', 'فوجیتسو': 'fujitsu', 'تکنو': 'tecno',
    'اینفینیکس': 'infinix', 'وینگز': 'wings', 'اولتیموس': 'ultimus', 'پرایمبوک': 'primebook',
    'آیبال': 'iball', 'زبرونیکس': 'zebronics', 'چووی': 'chuwi', 'جیو': 'jio', 'اویتا': 'avita',
    'واکر': 'walker', 'ای اکس ال': 'axl',
    
    # --- Technical & General Terms ---
    'گرافیک': 'graphics', 'انویدیا': 'nvidia', 'جیفورس': 'geforce', 'اینتل': 'intel',
    'پردازنده': 'processor', 'هارد': 'hdd', 'اس اس دی': 'ssd', 'لمسی': 'touch',
    'کرومبوک': 'chromebook', 'لپتاپ': 'laptop', 'لبتاب': 'laptop',
    'گیمینگ': 'gaming', 'بازی': 'gaming', 'دانشجویی': 'student', 'اداری': 'office',
    'ارزان': 'budget', 'اقتصادی': 'budget', 'حرفه': 'professional',
}

# We need a clear list of just the brand names for the specificity check.
# A clear list of brand names and exclusive series in English/technical form.
BRAND_NAMES = {
    'asus', 'dell', 'hp', 'acer', 'lenovo', 'apple', 'microsoft',
    'surface', 'msi', 'samsung', 'samsunge', 'gigabyte', 'honor',
    'realme', 'lg', 'fujitsu', 'tecno', 'infinix', 'wings', 'ultimus',
    'primebook', 'iball', 'zebronics', 'chuwi', 'jio', 'avita', 'walker',
    'axl','zenbook',
    # --- Exclusive Series ---
    'vivobook', 'zenbook', 'tuf', 'rog', # Asus
    'xps', 'inspiron', 'alienware',     # Dell
    'thinkpad', 'ideapad', 'yoga',      # Lenovo
    'macbook',                         # Apple
}

# A clear list of brand names and exclusive series in Persian.
PERSIAN_BRAND_NAMES = {
    'ایسوس', 'اسوس', 'دل', 'اچپی', 'اچ پی', 'ایسر', 'ایصر',
    'لنوو', 'اپل', 'مایکروسافت', 'سرفیس', 'ام اس ای', 'سامسونگ',
    'سامسنگ', 'گیگابایت', 'آنر', 'ریلمی', 'الجی', 'ال جی',
    'فوجیتسو',
    # --- Exclusive Series (Persian) ---
    'ویوبوک', 'زنبوک', 'تاف', 'راگ',
    'ایکس پی اس', 'اینسپایرون',
    'ثینکپد', 'آیدیاپد', 'یوگا',
    'مکبوک',
}


class SearchResultsView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        sort_type = request.GET.get('sort_type', '0')
        products_list = Product.objects.none()
        is_specific_query = False

        if query:
            # --- 1. IMPROVED QUERY PROCESSING ---
            processed_q = query.lower()

            # First, replace multi-word phrases
            for phrase, translation in MULTI_WORD_PHRASES.items():
                processed_q = processed_q.replace(phrase, translation)
            
            # Then, translate remaining single words
            original_terms = processed_q.split()
            translated_terms = [SINGLE_WORD_TERMS.get(term, term) for term in original_terms]
            final_query_str = " ".join(translated_terms)

            # Detect if the query is brand-specific
            for term in original_terms:
                if term in PERSIAN_BRAND_NAMES:
                    is_specific_query = True
                    break
            if not is_specific_query:
                for term in translated_terms:
                    if term in BRAND_NAMES:
                        is_specific_query = True
                        break

            # Continue with prefix search logic
            search_terms = final_query_str.split()
            processed_query = " & ".join(term + ':*' for term in search_terms)
            search_query_obj = SearchQuery(processed_query, search_type='raw', config='simple')
            
            products_list = Product.objects.filter(search_vector=search_query_obj)
            products_list = products_list.annotate(rank=SearchRank(F('search_vector'), search_query_obj))
        
        # --- The rest of the view remains unchanged ---
        # 2. FACETED SEARCH
        available_brands = Brand.objects.none()
        if query and not is_specific_query:
            available_brands = Brand.objects.filter(product_of_brands__in=products_list).distinct().annotate(
                product_count=Count('product_of_brands', filter=Q(product_of_brands__in=products_list))
            )

        # 3. APPLY FILTERS
        selected_brands = request.GET.getlist('brand')
        if selected_brands:
            products_list = products_list.filter(brand__id__in=selected_brands)
        
        dynamic_price_range = products_list.aggregate(min=Min('price'), max=Max('price'))
        
        price_min_str = request.GET.get('price_min', '').replace(',', '')
        price_max_str = request.GET.get('price_max', '').replace(',', '')
        if price_min_str.isdigit():
            products_list = products_list.filter(price__gte=int(price_min_str))
        if price_max_str.isdigit():
            products_list = products_list.filter(price__lte=int(price_max_str))
            
        # 4. APPLY SORTING
        if sort_type == '1':
            products_list = products_list.order_by('price')
        elif sort_type == '2':
            products_list = products_list.order_by('-price')
        else:
            products_list = products_list.order_by('-rank')

        # 5. PAGINATION & CONTEXT
        paginator = Paginator(products_list, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            "query": query,
            "page_obj": page_obj,
            "available_brands": available_brands,
            "dynamic_price_range": dynamic_price_range,
            "selected_brands": selected_brands,
            "sort_type": sort_type,
        }
        return render(request, 'search_app/search_results.html', context)

# from django.shortcuts import render
# from apps.products.models import Product
# from django.views import View
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# from django.contrib.postgres.search import (
#     SearchQuery, SearchRank, SearchHeadline, TrigramSimilarity
# )
# from django.db.models import Q, F
# # A comprehensive dictionary to translate common Persian terms and typos to their English equivalents.
# PERSIAN_TO_ENGLISH_BRANDS = {
#     # Persian Spellings & Common Typos -> English Brand
#     'ایسوس': 'asus',
#     'اسوس': 'asus',
    
#     'دل': 'dell',
    
#     'اچپی': 'hp',
#     'اچ پی': 'hp',
    
#     'ایسر': 'acer',
#     'ایصر': 'acer',
    
#     'لنوو': 'lenovo',
#     'لنوو': 'lenovo',
    
#     'اپل': 'apple',
    
#     'مایکروسافت': 'microsoft',
#     'سرفیس': 'surface', # 'surface' is a product line of microsoft
    
#     'ام اس ای': 'msi',
    
#     'سامسونگ': 'samsung',
#     'سامسنگ': 'samsunge', # Handles the typo in your brand list
    
#     'گیگابایت': 'gigabyte',
    
#     'آنر': 'honor',
    
#     'ریلمی': 'realme',
    
#     'الجی': 'lg',
#     'ال جی': 'lg',
    
#     'فوجیتسو': 'fujitsu',
    
#     # Brands with less common Persian spellings
#     'تکنو': 'tecno',
#     'اینفینیکس': 'infinix',
#     'وینگز': 'wings',
#     'اولتیموس': 'ultimus',
#     'پرایمبوک': 'primebook',
#     'آیبال': 'iball',
#     'زبرونیکس': 'zebronics',
#     'چووی': 'chuwi',
#     'جیو': 'jio',
#     'اویتا': 'avita',
#     'واکر': 'walker',
#     'ای اکس ال': 'axl',
# }
# class SearchResultsView(View):
#     """
#     Final professional version with a Persian-to-English translator for brand names.
#     """
#     def get(self, request, *args, **kwargs):
#         query = self.request.GET.get('q', '').strip()
#         products_list = Product.objects.none()

#         if query:
#             # --- Start of Translation Logic ---
#             original_terms = query.split()
#             translated_terms = []
#             for term in original_terms:
#                 # If the term is a known Persian brand, translate it. Otherwise, use the original term.
#                 # We use .lower() to make the check case-insensitive.
#                 translated_terms.append(PERSIAN_TO_ENGLISH_BRANDS.get(term.lower(), term))
            
#             # Rebuild the query with translated terms
#             final_query_str = " ".join(translated_terms)
#             # --- End of Translation Logic ---

#             # Prepare the query for prefix matching (e.g., "dell" -> "dell:*")
#             search_terms = final_query_str.split()
#             processed_query = " & ".join(term + ':*' for term in search_terms)
            
#             search_query = SearchQuery(processed_query, search_type='raw', config='simple')
            
#             products_list = Product.objects.annotate(
#                 rank=SearchRank(F('search_vector'), search_query),
#                 # We use the final_query_str for similarity to match against translated terms
#                 similarity=TrigramSimilarity('product_name', final_query_str),
#                 headline=SearchHeadline(
#                     'product_name',
#                     SearchQuery(final_query_str, config='simple'),
#                     start_sel='<span class="highlight">',
#                     stop_sel='</span>',
#                     config='simple' 
#                 )
#             ).order_by('-rank', '-similarity')

#         # --- Pagination ---
#         paginator = Paginator(products_list, 3)
#         page = request.GET.get('page')
#         try:
#             products = paginator.page(page)
#         except PageNotAnInteger:
#             products = paginator.page(1)
#         except EmptyPage:
#             products = paginator.page(paginator.num_pages)

#         context = {
#             "query": query, # We show the user's original query in the template
#             "products": products,
#         }
#         return render(request, 'search_app/search_results.html', context)
