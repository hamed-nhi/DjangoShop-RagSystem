from django.db import models
from apps.products.models import Product
from apps.accounts.models import CustomUser



class Comment(models.Model):
    """
    Model representing a comment on a product.
    This model includes fields for the product being commented on, the user who made the comment,
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments_product', verbose_name='کالا')
    commentig_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments_user1', verbose_name=' کاربر نظر دهنده ')
    approving_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments_user2', verbose_name=' کاربر تایید کننده ', null=True, blank=True)
    comment_text = models.TextField(verbose_name='متن نظر')
    register_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت نظر')
    is_active = models.BooleanField(default=False, verbose_name='وضعیت نظر')
    comment_parent = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True, related_name='comments_child', verbose_name=' والد نظر ')

    def __str__(self):
        return f'Comment by {self.commentig_user} on {self.product}'

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
        ordering = ['-register_date']