# myapp/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import SkillProfile, Review

class EditProfileForm(forms.ModelForm):
    # edit email on the User model and skills on SkillProfile
    email = forms.EmailField(required=True, label="Email Address")

    class Meta:
        model = SkillProfile
        fields = ['teach_skill', 'learn_skill']

    def __init__(self, *args, **kwargs):
        # accept a user kwarg to set initial email
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        skill_profile = super().save(commit=False)
        if self.user:
            # update user's email
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            skill_profile.save()
        return skill_profile


class ReviewForm(forms.ModelForm):
    # reviewed will be selected via dropdown (user id) in template or view
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(5,'5'),(4,'4'),(3,'3'),(2,'2'),(1,'1')]),
            'comment': forms.Textarea(attrs={'rows':3, 'placeholder':'Write your feedback...'}),
        }
