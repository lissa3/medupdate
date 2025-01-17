from django import forms
from django.core import validators
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _


class SearchForm(forms.Form):
    """Hidden inputs: current language and honeypot;
    form pre-filled with lang from get request
    """

    q = forms.CharField(
        required=False, label="", validators=[validators.MaxLengthValidator(250)]
    )
    first_honeypot = forms.CharField(required=False, widget=forms.HiddenInput)
    lang = forms.CharField(
        max_length=24,
        required=False,
        widget=forms.HiddenInput,
        label="",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lang = self.fields["lang"]
        lang.initial = get_language()
        search = self.fields["q"]
        search.widget.attrs["class"] = "search-txt"  # search.css
        search.widget.attrs["placeholder"] = _("Type to search")

    def clean_first_honeypot(self):
        """Check that nothing's been entered into the honeypot."""
        value = self.cleaned_data["first_honeypot"]
        if value:
            raise forms.ValidationError(_("It should not be here"))

        return value
