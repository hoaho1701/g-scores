from django import forms

class LookupForm(forms.Form):
    sbd = forms.RegexField(
        regex=r"^\d{8}$",
        label="Số báo danh",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ví dụ: 01000001",
            "inputmode": "numeric",
            "maxlength": "8",
        }),
        error_messages={
            "required": "Vui lòng nhập số báo danh.",
            "invalid": "Số báo danh phải bao gồm đúng 8 chữ số.",
        },
    )
