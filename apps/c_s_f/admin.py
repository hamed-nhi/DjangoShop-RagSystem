from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('product', 'commentig_user', 'comment_parent', 'approving_user', 'register_date', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('comment_text', 'product__name', 'commentig_user__username', 'approving_user__username')
    list_filter = ('is_active', 'register_date', 'product') 


