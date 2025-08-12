from django.shortcuts import render
from django.conf import settings
from django.views import View
from .models import Slider
from django.db.models import Q



def media_admin(request):
    return {"media_url": settings.MEDIA_URL,}

# def media_admin(request):
#     return {'media_url': settings.MEDIA_URL.rstrip('/') + '/'} 


def index (request):
    return render (request, "main_app/index.html")


class SliderView(View):
    def get(self,request):
        sliders=Slider.objects.filter(Q(is_active=True))
        return render (request,"main_app/sliders.html",{'sliders':sliders})
    

def handler400(request, exception):
    return render(request, 'errors/400.html', status=400)

def handler403(request, exception):
    return render(request, 'errors/403.html', status=403)

def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)