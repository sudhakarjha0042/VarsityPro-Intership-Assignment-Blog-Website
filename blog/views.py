from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import CommentForm, PostForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import UserProfile
from .forms import UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect

# User authentication and profile views

from .forms import SignUpForm
# blog/views.py
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post

from django.db.models import Q  # Import Q for complex queries

def post_list(request):
    page_number = request.GET.get('page', 1)
    posts_per_page = 5

    search_query = request.GET.get('q', '')

    # Query the database to get all posts ordered by created_at in descending order
    all_posts = Post.objects.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query)).order_by('-created_at')

    paginator = Paginator(all_posts, posts_per_page)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
    }
    return render(request, 'blog/post/post_list.html', context)




def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # This saves the User model
            # Now create the associated UserProfile
            user_profile = user.userprofile
            user_profile.bio = form.cleaned_data['bio']
            user_profile.profile_picture = form.cleaned_data['profile_picture']
            user_profile.save()
            return redirect('login')  # Redirect to the login page after successful signup
    else:
        form = SignUpForm()
    return render(request, 'blog/authentication/signup.html', {'form': form})



def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["userinput"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("post_list"))
        else:
            return render(request, "blog/authentication/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "blog/authentication/login.html")
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("post_list"))    

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    has_profile_picture = bool(user_profile.profile_picture)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=user_profile)

    # Check if the user has uploaded a profile picture
    print(user_profile.profile_picture)
    print(has_profile_picture)

    return render(request, 'blog/profile/user_profile.html', {'user_profile': user_profile, 'profile_form': profile_form, 'has_profile_picture': has_profile_picture})


@login_required
def edit_profile(request):
    # Retrieve the user's profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    has_profile_picture = bool(user_profile.profile_picture)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=user_profile)

    return render(request, 'blog/profile/edit_profile.html', {'user_profile': user_profile, 'profile_form': profile_form,'has_profile_picture': has_profile_picture})




def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/post/post_detail.html', {'post': post, 'comments': comments, 'form': form})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)  # Initialize the PostForm with POST data
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()  # Create an empty PostForm for GET requests
    return render(request, 'blog/post/post_form.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)  # Initialize the PostForm with POST data and instance
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)  # Initialize the PostForm with the existing post data for GET requests
    return render(request, 'blog/post/post_form.html', {'form': form, 'post': post})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Check if the currently logged-in user is the author of the post
    if request.user == post.author:
            post.delete()
            return redirect('post_list')
    return redirect('post_list')

