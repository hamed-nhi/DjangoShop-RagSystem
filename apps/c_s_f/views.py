from django.shortcuts import render, redirect,get_object_or_404
from apps.products.models import Product
from django.contrib import messages
from django.views import View
from django.http import HttpResponse
from django.db.models import Q
from .forms import CommentForm  
from .models import Comment


 

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
    


