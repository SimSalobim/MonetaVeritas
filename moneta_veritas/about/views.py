from django.shortcuts import render

# Create your views here.
def about(request):
    template = 'about/description.html'
    return render(request, template)