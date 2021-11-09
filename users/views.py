from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import CreationForm, ContactForm
from django.shortcuts import render, redirect


class SignUp(CreateView):
    """Класс регистрации пользователя"""
    form_class = CreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"

def user_contact(request):

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            return redirect('/thank-you/')
        return render(request, 'contact.html', {'form': form})
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})