from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import json
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Following, Post, Likes

class NewPost(ModelForm):
    post = forms.CharField(widget=forms.Textarea(attrs={'cols':100, 'rows':3}), label='Add Post')
    class Meta:
        model = Post
        fields = ['post']

@csrf_exempt
def tweet(request, post_id):
    try:
        tweet = Post.objects.get(user=request.user, pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=400)
    
    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("post") is not None:
            tweet.post = data["post"]
            tweet.save()

        if data.get("likes") is not None:
            tweet.likes = data["likes"]
            tweet.save()
        return HttpResponse(status=204)
    else:
        return JsonResponse({"error": "Put Request Required"}, status=400)


def load(request):
    posts = Post.objects.all()
    return JsonResponse([post.serialize() for post in posts], safe=False)

def likes(request):
    likes = Likes.objects.all()
    return JsonResponse([like.serialize() for like in likes], safe=False)

def index(request):
    
    #Allows for post
    if request.method == "POST":
        form = NewPost(request.POST)

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            
            return HttpResponseRedirect(reverse('index'))
        
    posts = Post.objects.all().order_by('-time')
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        #allow for like and unlike using JS
    return render(request, "network/index.html", {
        "form": NewPost(),
        "page_obj": page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        first_name = request.POST["firstName"]
        last_name = request.POST["lastName"]
        picture = request.POST["picture"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, first_name = first_name, last_name = last_name, picture = picture)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def following(request):
    post_following=Following.objects.filter(current_user_id=request.user.id).values_list('followed_user_id', flat=True).distinct() #gets ID of who they follow
    posts = Post.objects.filter(user_id__in=post_following).order_by("-time")
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    #copy like and unlike
    return render(request, "network/following.html", { #make a following template
        "page_obj": page_obj
    })

def profile(request, name):
    user_profile = User.objects.get(username=name)
    post= Post.objects.filter(user__username=name).order_by("-time")
    following_count = Following.objects.filter(current_user_id=user_profile.id).count() #This will display the number of people that this current user follows
    follower_count = Following.objects.filter(followed_user_id=user_profile.id).count() #This will display the number of people that follow this user
    try:
        is_following = Following.objects.get(current_user_id=request.user.id, followed_user_id=user_profile.id)
    except Following.DoesNotExist:
        is_following = None

    paginator = Paginator(post, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':

        if is_following:
            is_following.delete()
        else:
            relationship = Following.objects.create(current_user_id=request.user, followed_user_id=user_profile)
            relationship.save()

        return HttpResponseRedirect(reverse('profile', kwargs={"name": name}))

        #need form to create post method
    return render(request, 'network/profile.html', {
        "user": user_profile,
        "page_obj": page_obj,
        "following_count": following_count,
        "follower_count": follower_count,
        "is_following": is_following
        
    })


