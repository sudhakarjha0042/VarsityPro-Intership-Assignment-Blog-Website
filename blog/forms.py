from django import forms
from .models import Post, Comment, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    bio = forms.CharField(max_length=500, required=False, widget=forms.Textarea(attrs={'rows': 4}))
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User  # Use the built-in User model
        fields = ['username', 'password1', 'password2', 'bio', 'profile_picture']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']  # Add any other fields as needed

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
