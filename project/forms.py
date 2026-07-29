from datetime import date
from django import forms
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
    