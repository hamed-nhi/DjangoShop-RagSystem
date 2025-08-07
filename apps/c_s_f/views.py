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
        'message': 'امتیاز شما با موفقیت ثبت شد',
        'new_average': round(new_average, 1) # Round to one decimal place
    })

#---------------------------------------------------------------------------

def add_to_favorite(request):
    product_id = request.GET.get('productid')

    if not product_id:
        return JsonResponse({'message': 'شناسه کالا نامعتبر است.', 'type': 'error'}, status=400)

    product = get_object_or_404(Product, id=product_id)
    user = request.user # Get the current logged-in user

    # Check if the product is already favorited by the current user
    favorite_obj = Favorite.objects.filter(favorite_user=user, product=product).first()

    if favorite_obj:
        # If it exists, it means the user wants to REMOVE it from favorites
        favorite_obj.delete()
        message = 'محصول با موفقیت از علاقه‌مندی‌ها حذف شد.'
        status_type = 'success'
    else:
        # If it doesn't exist, it means the user wants to ADD it to favorites
        Favorite.objects.create(
            product=product,
            favorite_user=user
        )
        message = 'محصول با موفقیت به علاقه‌مندی‌ها اضافه شد.'
        status_type = 'success'

    return JsonResponse({'message': message, 'type': status_type})



#---------------------------------------------------------------------------

class UserFavoriteView(View):
    def get(self, request, *args, **kwargs):
        user_favorite_products = Favorite.objects.filter(Q(favorite_user_id=request.user.id))
        return render(request, 'csf_app/user_favorite.html', {'user_favorite_products': user_favorite_products})            