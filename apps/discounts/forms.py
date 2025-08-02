from django import forms


class CouponForm(forms.Form):
    coupon_code = forms.CharField(label="",
                                error_messages={'required': 'لطفاً کد تخفیف را وارد کنید.'},
                                widget=forms.TextInput(attrs={ 'class': 'form-control','placeholder': 'کد تخفیف خود را وارد کنید'
               
        })
    )
       
 
    # def clean_code(self):
    #     code = self.cleaned_data.get('code')
    #     if not code:
    #         raise forms.ValidationError('لطفاً کد تخفیف را وارد کنید.')
    #     return code