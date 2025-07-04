from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    #return HttpResponse("Hello, world. You're at the gama index.")
    return render(request, "gama/index.html")

def analysis(request):
    text = request.POST.get("text", "")
    context = {"text": text}
    return render(request, "gama/analysis.html", context)