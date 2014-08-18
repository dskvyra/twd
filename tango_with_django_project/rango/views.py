from django.template import  RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page

def index(request):
    context = RequestContext(request)
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list,}

    return render_to_response('rango/index.html', context_dict, context)

def about(request):
    context_dict = {'boldmessage': 'Hello, I\'m Rango and I\'m green'}

    return render_to_response('rango/about.html', context_dict)