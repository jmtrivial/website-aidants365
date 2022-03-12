from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Fiche
from django.shortcuts import get_object_or_404, render
from .forms import FicheForm


def index(request):
    latest_fiche_list = Fiche.objects.order_by('-date_derniere_modification')[:5]
    context = {'fiche_list': latest_fiche_list}
    return render(request, 'fiches/index.html', context)

def index_fiches(request):
    latest_fiche_list = Fiche.objects.order_by('-date_derniere_modification')
    context = {'fiche_list': latest_fiche_list}
    return render(request, 'fiches/index_fiches.html', context)


def detail(request, id):
    fiche = get_object_or_404(Fiche, pk=id)
    return render(request, 'fiches/detail.html', {'fiche': fiche})

