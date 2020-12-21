from django.shortcuts import render, redirect, get_object_or_404
from .forms import ImageCreateForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Image
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from actions.utils import create_action
# my custom decorator
from common.decorators import ajax_required

import redis
from django.conf import settings

# connect to redis
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)



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
            # create an action or activity stream for this action
            create_action(request.user, "bookmarked image", new_item)

            messages.success(request, 'Image added successfully')

            # redirect to new created item detail view
            return redirect(new_item.get_absolute_url())
    else:
        # build form with data provided by the bookmarklet via GET
        form = ImageCreateForm(data=request.GET)
    return render(request, 'images/image/create.html', {'section': 'images', 'form': form})

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # increment total image views by 1 on redis DB
    # store in redis like 'image:2:views and return the value of the key image:2:views
    # The incr() method returns the final value of the key after performing the operation.
    total_views = r.incr(f'image:{image.id}:views')
    # print(total_views)
    # increment image ranking by 1
    r.zincrby('image_ranking', 1, image.id)
    return render(request, 'images/image/detail.html', {'section': 'images', 'image': image, 'total_views':total_views})

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
                create_action(request.user, "likes", image)
            else:
                # delete many to many relationship for user and image
                image.users_like.remove(request.user)
            return JsonResponse({'status' : 'ok'})

        except:
            pass
    return JsonResponse({'error': 'error'})

@login_required
def image_ranking(request):
    # get image ranking dictionary      
    image_ranking = r.zrange('image_ranking', 0, -1,
    desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    # get most viewed images
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request,'images/image/ranking.html',{'section': 'ranking','most_viewed': most_viewed})