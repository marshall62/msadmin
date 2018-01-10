from django import forms

TYPE_CHOICES = (
    ('multiChoice', 'Multiple Choice'),
    ('shortAnswer', 'Short Answer'),
    ('longAnswer', 'Long Answer'),
)

TIME_CHOICES = (
    ('30', '30 secs'),
    ('60', '1 min'),
    ('120', '2 min'),
    ('180', '3 min'),
    ('300', '5 min'),
    ('unlimited', 'No time limit'),
)
class QuestionForm(forms.Form):
    id = forms.CharField(label='ID', max_length=20)
    name = forms.CharField(label='Name', max_length=100)
    type = forms.ChoiceField(label='Type',widget=forms.Select, choices=TYPE_CHOICES)
    hoverText = forms.CharField(label='Hover Text', max_length=100)
    description = forms.CharField(label='Description', widget=forms.Textarea(attrs={'rows':'4','cols': '80'}))
    warnTime = forms.ChoiceField(label='Warn student to answer time',widget=forms.Select, choices=TYPE_CHOICES)
    # TODO need a more complicated widget for the table of answers


