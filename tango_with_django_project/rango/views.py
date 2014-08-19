from django.template import  RequestContext
from django.shortcuts import render_to_response, redirect
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query
from django.contrib.auth.models import User

TOP_AMOUNT = 5

def decode_url(url):
    """ Takes url string, returns title string with spaces instead underlines """
    return url.replace('_', ' ')

def encode_url(title):
    """ Takes title string, swaps spaces by underlines and returns url string """
    return title.replace(' ', '_')

def get_category_list():
    cat_list = Category.objects.all()

    for category in cat_list:
        category.url = encode_url(category.name)

    return cat_list

def index(request):
    context = RequestContext(request)
    category_top_list = Category.objects.order_by('-likes')[:TOP_AMOUNT]
    cat_list = get_category_list()
    page_top_list = Page.objects.order_by('-views')[:TOP_AMOUNT]
    context_dict = {'categories_top': category_top_list,
                    'cat_list': cat_list,
                    'pages_top': page_top_list,
                    }

    for category in category_top_list:
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
    cat_list = get_category_list()

    context_dict = {'boldmessage': 'Hello, I\'m Rango and I\'m green',
                    'cat_list': cat_list,}

    if request.session.has_key('visits'):
        visits_count = request.session['visits']
    else:
        visits_count = 0

    context_dict['visits'] = visits_count

    return render_to_response('rango/about.html', context_dict, context)

def category(request, category_name_url):
    context = RequestContext(request)
    category_name = decode_url(category_name_url)
    cat_list = get_category_list()
    context_dict = {'category_name': category_name,
                    'category_name_url': category_name_url,
                    'cat_list': cat_list,}

    try:
        # category = Category.objects.get(name=category_name)
        category = Category.objects.get(name__iexact=category_name)
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['category'] = category
        context_dict['pages'] = pages
    except Category.DoesNotExist:
        pass

    if request.method == 'POST' and request.POST.has_key('query'):
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list

    return render_to_response('rango/category.html', context_dict, context)

@login_required
def add_category(request):
    context = RequestContext(request)
    cat_list = get_category_list()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)

            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render_to_response('rango/add_category.html', {'form': form, 'cat_list': cat_list}, context)

@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)
    cat_list = get_category_list()
    category_name = decode_url(category_name_url)

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)

            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response('rango/add_category.html', {'cat_list': cat_list}, context)

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
             'form': form,
             'cat_list': cat_list},
            context)

def register(request):
    context = RequestContext(request)
    cat_list = get_category_list()

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
         'registered': registered,
         'cat_list': cat_list},
        context
    )

def user_login(request):
    context = RequestContext(request)
    cat_list = get_category_list()

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
        return render_to_response('rango/login.html', {'cat_list': cat_list}, context)

@login_required
def restricted(request):
    context = RequestContext(request)
    cat_list = get_category_list()

    message = "Since you're logged in, you can see this text!"

    return render_to_response(
        'rango/restricted.html',
        {'message': message,
         'cat_list': cat_list},
        context
    )

@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('/rango/')

# def search(request):
#     context = RequestContext(request)
#     cat_list = get_category_list()
#     result_list = []
#
#     if request.method == 'POST':
#         query = request.POST['query'].strip()
#
#         if query:
#             result_list = run_query(query)
#
#     return render_to_response('rango/search.html',
#                               {'result_list': result_list,
#                                'cat_list': cat_list},
#                               context,)

@login_required
def profile(request):
    context = RequestContext(request)
    cat_list = get_category_list()
    context_dict = {'cat_list': cat_list}
    user = User.objects.get(username=request.user)

    try:
        user_profile = UserProfile.objects.get(user=user)
    except:
        user_profile = None

    context_dict['user'] = user
    context_dict['user_profile'] = user_profile

    return render_to_response('rango/profile.html', context_dict, context)

def track_url(request):
    context = RequestContext(request)
    page_id = None
    url = '/rango/'

    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

@login_required
def like_category(request):
    context = RequestContext(request)
    cat_id = None

    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))

        if category:
            likes = category.likes + 1
            category.likes = likes

            category.save()

    return HttpResponse(likes)