from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from vote.models import Vote
from vote.forms import VoteForm
from ml.get_words_similarity import get_words_similarity
from .models import Member ,Area, Users, Inquiry, Comment
from django_pandas.io import read_frame
from django.db import connection
import pandas as pd

# import pandas as pd
# import numpy as np


def indexfunc(request):
    return render(request, 'index.html')

def contactfunc(request):
    return render(request, 'contact_form.html')   

def confirmfunc(request):
    username = request.POST.get('username')
    email = request.POST.get('email')
    subject = request.POST.get('subject')
    details = request.POST.get('details')
    Inquiry.objects.create(username = username,
                           email = email,
                           subject = subject, 
                           details = details)
    return render(request, 'contact_confirm.html', {'username':username, 
                                                    'email':email, 
                                                    'subject':subject, 
                                                    'details':details})  

def completefunc(request):
    return render(request, 'contact_complete.html')
        
def resultfunc(request):
    topic = request.POST.get('topic')
    prefecture = request.POST.get('prefecture')
    constituency = request.POST.get('electoral_district')
    #Userテーブルへの行動ログ保存
    Users.objects.create(prefecture = prefecture,
                                   constituency = constituency,
                                   query = topic)
    try:
        # Commentテーブルにおける対象選挙区の候補者の抽出
        candidates = Member.objects.filter(prefecture = prefecture, constituency = constituency)
        candidate_list = Member.objects.filter(prefecture = prefecture, constituency = constituency).values_list('name', flat = True)
        comments = Comment.objects.filter(name__in = [candidate_list])
        comment_df = read_frame(comments, fieldnames=['name', 'sentence', 'comment', 'comment_datetime'])
        member_df = read_frame(candidates, fieldnames=['name', 'party'])

        # キーワードと候補者発言の類似度計算
        candidate_rank, sentence_rank = get_words_similarity(topic, comment_df)
        candidate_rank = pd.merge(candidate_rank, member_df)
        sentence_rank = pd.merge(sentence_rank, member_df)
        candidate_rank = pd.concat([member_df, candidate_rank])
        candidate_rank = candidate_rank[['name', 'party', 'sentence']].drop_duplicates(subset = 'name').fillna('関連発言なし')
        return render(request,'search_result.html',{'prefecture':prefecture, 
                                                    'constituency':constituency,
                                                    'topic':topic,
                                                    'candidate_rank':candidate_rank,
                                                    'sentence_rank':sentence_rank
                                                   })
    except ValueError:
        return render(request, 'error.html')

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
