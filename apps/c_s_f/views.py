from django.shortcuts import render, redirect,get_object_or_404
from apps.products.models import Product
from django.contrib import messages
from django.views import View
from django.http import HttpResponse
from django.db.models import Q, Avg
from .forms import CommentForm  
from .models import Comment, Favorite, Scoring
from django.http import JsonResponse 
 

#---------------------------------------------------------------------------

class CommentView(View):
    def get(self, request,*args, **kwargs):
        priductid = request.GET.get('productid')
        commentid = request.GET.get('commentid')
        slug = kwargs['slug']
        initial_dict={
            "product_id": priductid,
            "comment_id": commentid,
        }
        form  =CommentForm(initial=initial_dict)
        return render(request, 'csf_app/partials/create_comment.html', {'form': form, 'slug': slug})




    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        product = get_object_or_404(Product, slug=slug)
        form = CommentForm(request.POST)
        if form.is_valid():
            cdc = form.cleaned_data
            # product = get_object_or_404(Product, slug=slug)
            parent =None
            if(cdc['comment_id']):
                parentid =cdc['comment_id']
                parent= Comment.objects.get(id=parentid)

            Comment.objects.create(
                product=product,
                commentig_user = request.user ,
                comment_text= cdc['comment_text'],
                comment_parent=parent,
                
            )
            messages.success(request, 'نظر شما با موفقیت ثبت شد')
            return redirect('products:product_details', product.slug)
        messages.error(request, 'خطا در ثبت نظر','danger')
        return redirect('products:product_details', product.slug)
#---------------------------------------------------------------------------
    
# def add_score(request):
#     productid = request.GET.get('productid')
#     score = request.GET.get('score')

#     product = Product.objects.get(id=productid)
#     Scoring.objects.create(
#         product = product,
#         scoring_user = request.user,
#         score_value = score,
#     )
#     return HttpResponse('امتیاز شما با موفقیت ثبت شد')



def add_score(request):
    productid = request.GET.get('productid')
    score = request.GET.get('score')

    product = Product.objects.get(id=productid)
    
    # Use update_or_create to prevent duplicate scores for the same user
    Scoring.objects.update_or_create(
        product=product,
        scoring_user=request.user,
        defaults={'score_value': score}
    )

    # Calculate the new average score after updating
    new_average = product.scoring_product.aggregate(Avg('score_value'))['score_value__avg']

    # Return a JSON response with the new average
    return JsonResponse({
        'new_average': product.get_average_score(),  # Make sure this returns a float
        'total_votes': product.scoring_product.count(),
        'message': 'امتیاز شما با موفقیت ثبت شد',
        'status': 'success',
        'new_average': round(new_average, 1) # Round to one decimal place
    })

#---------------------------------------------------------------------------

# def add_to_favorite(request):
#     product_id = request.GET.get('productid')

#     if not product_id:
#         return JsonResponse({'message': 'شناسه کالا نامعتبر است.', 'type': 'error'}, status=400)

#     product = get_object_or_404(Product, id=product_id)
#     user = request.user # Get the current logged-in user

#     # Check if the product is already favorited by the current user
#     favorite_obj = Favorite.objects.filter(favorite_user=user, product=product).first()

#     if favorite_obj:
#         # If it exists, it means the user wants to REMOVE it from favorites
#         favorite_obj.delete()
#         message = 'محصول با موفقیت از علاقه‌مندی‌ها حذف شد.'
#         status_type = 'success'
#     else:
#         # If it doesn't exist, it means the user wants to ADD it to favorites
#         Favorite.objects.create(
#             product=product,
#             favorite_user=user
#         )
#         message = 'محصول با موفقیت به علاقه‌مندی‌ها اضافه شد.'
#         status_type = 'success'

#     return JsonResponse({'message': message, 'type': status_type})

# csf/views.py

# ... (existing imports)

def add_to_favorite(request):
    # Ensure it's a POST request (though Django will handle this with CSRF anyway)
    if request.method == 'POST':
        # Get product_id from POST data (request.POST) instead of GET data (request.GET)
        product_id = request.POST.get('productid') 

        if not product_id:
            return JsonResponse({'message': 'شناسه کالا نامعتبر است.', 'type': 'error'}, status=400)

        # The rest of your logic for adding/removing from favorites
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'message': 'کالا یافت نشد.', 'type': 'error'}, status=404)

        user = request.user 
        
        # Ensure user is authenticated, though toggleFavorite JS already redirects for 401/403
        if not user.is_authenticated:
             return JsonResponse({'message': 'برای انجام این عملیات، ابتدا وارد حساب کاربری خود شوید.', 'type': 'error'}, status=401)


        favorite_obj = Favorite.objects.filter(favorite_user=user, product=product).first()

        is_favorite = False # Flag to tell JS the new state
        if favorite_obj:
            favorite_obj.delete()
            message = 'محصول با موفقیت از علاقه‌مندی‌ها حذف شد.'
            status_type = 'success'
            is_favorite = False
        else:
            Favorite.objects.create(
                product=product,
                favorite_user=user
            )
            message = 'محصول با موفقیت به علاقه‌مندی‌ها اضافه شد.'
            status_type = 'success'
            is_favorite = True # Product is now favorited

        return JsonResponse({'message': message, 'type': status_type, 'is_favorite': is_favorite})
    
    # If it's not a POST request, perhaps return an error or redirect
    return JsonResponse({'message': 'درخواست نامعتبر است.', 'type': 'error'}, status=405) # Method Not Allowed

#---------------------------------------------------------------------------

class UserFavoriteView(View):
    def get(self, request, *args, **kwargs):
        user_favorite_products = Favorite.objects.filter(Q(favorite_user_id=request.user.id))
        return render(request, 'csf_app/user_favorite.html', {'user_favorite_products': user_favorite_products})      


def status_of_favorite_list_view(request):
    if request.user.is_authenticated:
        favorite_count = request.user.favorite_user1.count()
        return HttpResponse(favorite_count)
    else:
        return HttpResponse(0)