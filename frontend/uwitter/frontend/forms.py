from django import forms


class PostForm(forms.Form):
    message = forms.CharField(max_length=141, widget=forms.Textarea)
