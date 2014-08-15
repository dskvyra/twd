from django.template import  RequestContext
from django.shortcuts import render_to_response

def index(request):
    context = RequestContext(request)
    context_dict = {'boldmessage': 'I\'m bold font from context',}

    return render_to_response('rango/index.html', context_dict, context)

def about(request):
    context_dict = {'boldmessage': 'Hello, I\'m Rango and I\'m green'}

    return render_to_response('rango/about.html', context_dict)