from django.shortcuts import render
from albums.models import *


# Create your views here.
def main(request):
    context = {}
    albums = Album.objects.all()
    context.update({'albums': albums})
    return render(request, 'albums/main.html', context)