from django.template import  RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query

TOP_AMOUNT = 5

def decode_url(url):
    """ Takes url string, returns title string with spaces instead underlines """
    return url.replace('_', ' ')

def encode_url(title):
    """ Takes title string, swaps spaces by underlines and returns url string """
    return title.replace(' ', '_')

def index(request):
    context = RequestContext(request)
    category_list = Category.objects.order_by('-likes')[:TOP_AMOUNT]
    page_top_list = Page.objects.order_by('-views')[:TOP_AMOUNT]
    context_dict = {'categories': category_list,
                    'pages': page_top_list,
                    }

    for category in category_list:
        category.url = encode_url(category.name)

    if request.session.get('last_visit'):
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], '%Y-%m-%d %H:%M:%S')).days > 0:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

    # print request.session['last_visit'], request.session['visits']
    return render_to_response('rango/index.html', context_dict, context)

    # Last_visit & visits counter by client side cookies
    # response = render_to_response('rango/index.html', context_dict, context)

    # visits = int(request.COOKIES.get('visits', '0'))

    # if 'last_visit' in request.COOKIES:
    #     last_visit = request.COOKIES['last_visit']
    #     last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
    #
    #     if (datetime.now() - last_visit_time).days > 0:
    #         response.set_cookie('visits', visits+1)
    #         response.set_cookie('last_visit', datetime.now())
    # else:
    #     response.set_cookie('last_visit', datetime.now())

    # return response

def about(request):
    context = RequestContext(request)
    context_dict = {'boldmessage': 'Hello, I\'m Rango and I\'m green'}

    if request.session.has_key('visits'):
        visits_count = request.session['visits']
    else:
        visits_count = 0

    context_dict['visits'] = visits_count

    return render_to_response('rango/about.html', context_dict, context)

def category(request, category_name_url):
    context = RequestContext(request)
    category_name = decode_url(category_name_url)
    context_dict = {'category_name': category_name,
                    'category_name_url': category_name_url,
                    }

    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    return render_to_response('rango/category.html', context_dict, context)

@login_required
def add_category(request):
    context = RequestContext(request)

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)

            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render_to_response('rango/add_category.html', {'form': form}, context)

@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)

            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response('rango/add_category.html', {}, context)

            page.views = 0

            page.save()

            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response('rango/add_page.html',
            {'category_name_url': category_name_url,
             'category_name': category_name,
             'form': form,},
            context)

def register(request):
    context = RequestContext(request)

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
        'rango/register.html',
        {'user_form': user_form,
         'profile_form': profile_form,
         'registered': registered,},
        context
    )

def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse('Yoir Rango account is disabled.')
        else:
            print 'Invalid login details: {0}, {1}'.format(username, password)
            return HttpResponse('Invalid login details supplied.')
    else:
        return render_to_response('rango/login.html', {}, context)

@login_required
def restricted(request):
    context = RequestContext(request)

    message = "Since you're logged in, you can see this text!"

    return render_to_response(
        'rango/restricted.html',
        {'message': message},
        context
    )

@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('/rango/')

def search(request):
    context = RequestContext(request)
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)

    return render_to_response('rango/search.html', {'result_list': result_list}, context)