from django import forms

class CommentForm(forms.Form):
    product_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    comment_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    comment_text= forms.CharField(label="",
                                  error_messages={'required': 'لطفا متن نظر خود را وارد کنید.'},
                                  widget=forms.Textarea(attrs={
                                      'class': 'form-control',
                                      'placeholder': 'متن نظر خود را وارد کنید.',
                                      'rows': 3,
                                      'style': 'resize: none;'
                                  })    


    )