from django.shortcuts import render

from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignForm

class SignupView(CreateView):
    model = User
    form_class = SignForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('index')