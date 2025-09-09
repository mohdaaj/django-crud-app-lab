# main_app/views.py
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from .forms import FeedingForm
from .models import Finch, Toy


@login_required
def finch_index(request):
    finches = Finch.objects.filter(user=request.user)
    return render(request, 'finches/index.html', {'finches': finches})


# Define the home view function
class Home(LoginView):
    template_name = 'home.html'


def about(request):
    return render(request, 'about.html')


@login_required
def finch_detail(request, finch_id):
    finch = Finch.objects.get(id=finch_id)
    feeding_form = FeedingForm()
    toys_finch_doesnt_have = Toy.objects.exclude(id__in=finch.toys.all().values_list('id'))
    return render(request, 'finches/detail.html', {
        'finch': finch,
        'feeding_form': feeding_form,
        'toys': toys_finch_doesnt_have
    })


@login_required
def add_feeding(request, finch_id):
    form = FeedingForm(request.POST)
    if form.is_valid():
        new_feeding = form.save(commit=False)
        new_feeding.finch_id = finch_id
        new_feeding.save()
    return redirect('finch_detail', finch_id=finch_id)


class FinchCreate(LoginRequiredMixin, CreateView):
    model = Finch
    fields = ['name', 'species', 'age', 'description']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class FinchUpdate(LoginRequiredMixin, UpdateView):
    model = Finch
    fields = ['species', 'description', 'age']


class FinchDelete(LoginRequiredMixin, DeleteView):
    model = Finch
    success_url = '/finches/'


class ToyCreate(LoginRequiredMixin, CreateView):
    model = Toy
    fields = '__all__'


class ToyList(LoginRequiredMixin, ListView):
    model = Toy


class ToyDetail(LoginRequiredMixin, DetailView):
    model = Toy


class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = ['name', 'color']


class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url = '/toys/'


@login_required
def associate_toy(request, finch_id, toy_id):
    Finch.objects.get(id=finch_id).toys.add(toy_id)
    return redirect('finch_detail', finch_id=finch_id)


@login_required
def remove_toy(request, finch_id, toy_id):
    Finch.objects.get(id=finch_id).toys.remove(toy_id)
    return redirect('finch_detail', finch_id=finch_id)


def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('finch_index')  # <-- fixed
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)

