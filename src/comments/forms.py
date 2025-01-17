from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from src.comments.models import Comment

User = get_user_model()


class CommentForm(forms.ModelForm):
    body = forms.CharField(
        max_length=2000,
        help_text=_("Comment can't be empty; maximum 2000 chars"),
        widget=forms.Textarea(
            attrs={
                "rows": 15,
                "class": "form-control",
                "placeholder": _("Write your comment here"),
            }
        ),
    )
    comm_parent_id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Comment
        fields = ("body",)
