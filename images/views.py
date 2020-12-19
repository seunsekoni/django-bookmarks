from django.shortcuts import render, redirect, get_object_or_404
from .forms import ImageCreateForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Image
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# my custom decorator
from common.decorators import ajax_required

def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 5)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        images = paginator.page(1)

    except EmptyPage:
        if request.is_ajax():
            # If the request is AJAX and the page is out of range
            # return an empty page
            return HttpResponse('')

        # If page is out of range deliver last page of results
        images = paginator.page(paginator.num_pages)
    
    if request.is_ajax():
        return render(request, 'images/image/list_ajax.html',
                                {'section': 'images', 'images': images})

    return render(request, 'images/image/list.html', {'section': 'images', 'images': images})

# Create your views here.
# create and book image
@login_required
def image_create(request):
    if request.method == "POST":
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_item = form.save(commit=False)

            # assign auth user to the bookmarked image
            new_item.user = request.user
            new_item.save()

            messages.success(request, 'Image added successfully')

            # redirect to new created item detail view
            return redirect(new_item.get_absolute_url())
    else:
        # build form with data provided by the bookmarklet via GET
        form = ImageCreateForm(data=request.GET)
    return render(request, 'images/image/create.html', {'section': 'images', 'form': form})

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    return render(request, 'images/image/detail.html', {'section': 'images', 'image': image})

@ajax_required
@require_POST
@login_required
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    
    if image_id and action:
        try:
            image = get_object_or_404(Image, id=image_id)
            if action == "like":
                # create many to many relationship for user and image
                image.users_like.add(request.user)
            else:
                # delete many to many relationship for user and image
                image.users_like.remove(request.user)
            return JsonResponse({'status' : 'ok'})

        except:
            pass
    return JsonResponse({'error': 'error'})



