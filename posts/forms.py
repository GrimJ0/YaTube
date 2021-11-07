from django import forms
from .models import Group, Post, Comment

class PostForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False)
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Post
        fields = ['group', 'title', 'text', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text',]
