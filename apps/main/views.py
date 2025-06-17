from django.shortcuts import render
from django.conf import settings




def media_admin(request):
    return {"media_url": settings.MEDIA_URL,}




def index (request):
    return render(request, "main_app/index.html")


# def test_view(request):
#     context={
#         'name':'Hamed',
#         'family':'Nahali',
#     }
#     return render(request,'main_app/test.html',context)