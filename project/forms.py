from datetime import date
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Reservation, WorkingHours


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            "full_name", "email", "phone",
            "reservation_date", "reservation_time", "guest_count",
            "menu_items", "beer_items", "breakfast_items", "comment",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form"}),
            "email": forms.EmailInput(attrs={"class": "form"}),
            "phone": forms.TextInput(attrs={"class": "form"}),
            "reservation_date": forms.DateInput(attrs={"type": "date", "class": "form"}),
            "reservation_time": forms.TimeInput(attrs={"type": "time", "class": "form"}),
            "guest_count": forms.NumberInput(attrs={"class": "form", "min": 1, "max": 10}),
            "comment": forms.Textarea(attrs={"rows": 3, "class": "form textarea"}),
        }

    def clean_reservation_date(self):
        d = self.cleaned_data["reservation_date"]
        if d < date.today():
            raise forms.ValidationError("Otgan sanaga bron qilib bolmaydi.")
        return d

    def clean_guest_count(self):
        g = self.cleaned_data["guest_count"]
        if g < 1 or g > 10:
            raise forms.ValidationError("Bitta stol uchun 1 dan 10 gacha mehmon bolishi mumkin.")
        return g

    def clean(self):
        cleaned = super().clean()
        d = cleaned.get("reservation_date")
        t = cleaned.get("reservation_time")
        if d and t:
            weekday = d.weekday()
            try:
                wh = WorkingHours.objects.get(day=weekday)
            except WorkingHours.DoesNotExist:
                wh = None

            if wh is None or wh.is_closed:
                raise forms.ValidationError("Bu kunda biz ishlamaymiz. Iltimos boshqa kun tanlang.")
            elif wh.open_time and wh.close_time:
                if not (wh.open_time <= t <= wh.close_time):
                    raise forms.ValidationError(
                        f"Bu vaqtda biz ishlamaymiz. Ish vaqti: {wh.open_time.strftime('%H:%M')} - {wh.close_time.strftime('%H:%M')}."
                    )
        return cleaned


class RegisterForm(UserCreationForm):
    """Faqat gmail.com pochtasi bilan royxatdan otish."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Gmail manzilingiz"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form")
        self.fields["password1"].widget.attrs["placeholder"] = "Parol"
        self.fields["password2"].widget.attrs["placeholder"] = "Parolni takrorlang"

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if not email.lower().endswith("@gmail.com"):
            raise forms.ValidationError("Faqat @gmail.com pochta manzili qabul qilinadi.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu email bilan foydalanuvchi allaqachon royxatdan otgan.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class StyledAuthenticationForm(AuthenticationForm):
    """Login formasi, saytga mos stil bilan."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form", "placeholder": "Username"})
        self.fields["password"].widget.attrs.update({"class": "form", "placeholder": "Parol"})
        