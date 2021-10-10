from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from vote.models import Vote
from vote.forms import VoteForm
from ml.get_words_similarity import get_words_similarity
import pandas as pd
import numpy as np

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