from django import forms
from vote.models import Vote

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['words']