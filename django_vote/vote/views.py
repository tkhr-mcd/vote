from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from vote.models import Vote
from vote.forms import VoteForm
from ml.get_words_similarity import get_words_similarity
from .models import Member ,Area
# import pandas as pd
# import numpy as np


def indexfunc(request):
    return render(request, 'index.html')

def areafunc(request):
    object_list = Member.objects.all()
    return render(request, 'prefecture_page.html',{'object_list':object_list})

def constituencyfunc(request, prefecture):
    constituency_list = Area.objects.filter(prefecture__contains = prefecture)
    return render(request, 'electoral_district.html',{'constituency_list':constituency_list})

def candidatefunc(request, prefecture, constituency):
    candidate_list = Member.objects.filter(prefecture = prefecture, constituency = constituency)
    return render(request, 'candidate_list.html',{'candidate_list':candidate_list, 'prefecture':prefecture, 'constituency':constituency})


def vote_new(request):
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            vote = form.save(commit=False)
            vote.save()
            return redirect(vote_detail, vote_id=vote.pk)
    else:
        form = VoteForm()
    return render(request, "vote/vote_new.html", {'form': form})


def vote_detail(request, vote_id):
    vote = get_object_or_404(Vote, pk=vote_id)
    words = vote.words
    df = get_words_similarity(words)
    context = {'vote': vote, 'df': df}
    
    return render(request, 'vote/vote_detail.html',
                    context)


def testfunc(request):
    object_list = Member.objects.all()
    return render(request, 'test.html',{'object_list':object_list}) 