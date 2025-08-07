from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.products.models import Product
from apps.accounts.models import CustomUser

#------------------------------------------------------------------------------------------------------

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
#------------------------------------------------------------------------------------------------------

class Scoring(models.Model):
    """
    Model representing a scoring for a product.
    This model includes fields for the product being scored, the user who made the score,
    and the score value.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='scoring_product', verbose_name='کالا')
    scoring_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='scoring_user1', verbose_name=' کاربر امتیاز دهنده ')
    score_value = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name='امتیاز')
    register_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت امتیاز')

    def __str__(self):
        return f'Score {self.score_value} by {self.scoring_user} on {self.product}'

    class Meta:
        verbose_name = 'امتیاز'
        verbose_name_plural = 'امتیازات'
        ordering = ['-register_date']
#------------------------------------------------------------------------------------------------------


class Favorite(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorite_product', verbose_name='کالا')
    favorite_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorite_user1', verbose_name='کاربر علاقه مند')
    regester_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت علاقه مندی')


    def __str__(self):
        return f'Favorite {self.favorite_user} on {self.product}'


    class Meta:
        verbose_name = 'علاقه مندی'
        verbose_name_plural = 'علاقه مندی ها'
        ordering = ['-regester_date'] 