from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from .models import Contact

# Create your views here.
@ajax_required
@login_required
@require_POST
def user_follow(request):
    user_id_followed = request.POST.get('id')
    action = request.POST.get('action')
    try:
        user = User.objects.get(id=user_id_followed)
        user_following = request.user
        if action == "follow":
            # create the relationship
            Contact.objects.get_or_create(user_from=user_following, user_to=user)
        else:
            # delete the relationship
            Contact.objects.filter(user_from=user_following, user_to=user).delete()
        return JsonResponse({'status':'ok'})
    except User.DoesNotExist:
        return JsonResponse({'error':'error'})
    return JsonResponse({'error':'error'})

def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated Successfully')

                else:
                    return HttpResponse('Disabled account')

            else:
                return HttpResponse('Invalid Login Credentials')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def dashboard(request):
    return render(request,
                    'account/dashboard.html',
                    {'section': 'dashboard'})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        # check if form satisfies all valdation
        if user_form.is_valid():
            cd = user_form.cleaned_data
            # save an instance of the new user but don't persisit to db yet
            new_user = user_form.save(commit=False)
            # set user password by hashing it
            new_user.set_password(cd['password'])
            # persist user into db
            new_user.save()
            # create an empty profile for the user
            Profile.objects.create(user=new_user)


            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})

@login_required
def edit(request):
    if request.method == "POST":
        user_form = UserEditForm(data=request.POST, instance=request.user)
        profile_form = ProfileEditForm(data=request.POST, instance=request.user.profile, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated Successfully')
        else:
            messages.error(request, user_form.errors)

    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile, files=request.FILES)

    return render(request, 'account/edit.html', {

                                                'user_form': user_form,
                                                'profile_form': profile_form,
                                                'section': 'profile'
                                            })

def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'account/user/list.html', {'section': 'people', 'users': users})

def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'account/user/detail.html', {'section': 'people', 'user': user})
