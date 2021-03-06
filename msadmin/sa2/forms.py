from django import forms

from msadmin.stratauth.models import Class


# The Class page should show the fields of the class
# with a list of strategies displayed as links.  Additional strategies can be added.
class ClassForm(forms.ModelForm):

    class Meta:
        model = Class
        # fields = ('name','teacher', 'strategies')
        fields = ('name','teacher')