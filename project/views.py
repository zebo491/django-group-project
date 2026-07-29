import json
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages

from .models import (
    SiteAbout, Category, MenuItem, BeerItem,
    BreakfastCategory, WorkingHours, Reservation
)
from .forms import ReservationForm


def home(request):
    about = SiteAbout.objects.first()
    categories = Category.objects.prefetch_related("menu_items").all()
    menu_items = MenuItem.objects.filter(is_active=True).prefetch_related("categories")
    beer_items = BeerItem.objects.filter(is_active=True)
    breakfast_categories = BreakfastCategory.objects.prefetch_related("items").all()
    working_hours = WorkingHours.objects.all().order_by("day")
    form = ReservationForm()

    # Breakfast malumotlarini JS uchun toza JSON strukturasiga aylantiramiz
    breakfast_data = {}
    for cat in breakfast_categories:
        breakfast_data[str(cat.id)] = {
            "title": cat.title,
            "items": [
                {
                    "id": it.id,
                    "name": it.name,
                    "price": str(it.price),
                    "image": it.image.url if it.image else "",
                    "desc": it.full_description or it.short_description,
                }
                for it in cat.items.filter(is_active=True)
            ],
        }

    context = {
        "about": about,
        "categories": categories,
        "menu_items": menu_items,
        "beer_items": beer_items,
        "breakfast_categories": breakfast_categories,
        "working_hours": working_hours,
        "form": form,
        "breakfast_data": breakfast_data,
    }
    return render(request, "index.html", context)


@require_POST
def create_reservation(request):
    """AJAX orqali yangi bron yaratish. JSON javob qaytaradi."""
    form = ReservationForm(request.POST)
    if form.is_valid():
        reservation = form.save()
        return JsonResponse({
            "success": True,
            "message": "Joy muvaffaqiyatli bron qilindi! Bron holatini kuzatish uchun havolani saqlab qoying.",
            "token": str(reservation.token),
            "detail_url": f"/reservation/{reservation.token}/",
        })
    return JsonResponse({"success": False, "errors": form.errors}, status=400)


@require_http_methods(["GET", "POST"])
def reservation_detail(request, token):
    """Mijoz oz bronini korishi, tahrirlashi yoki bekor qilishi uchun sahifa (token orqali)."""
    reservation = get_object_or_404(Reservation, token=token)

    if request.method == "POST":
        if "cancel" in request.POST:
            reservation.status = "cancelled"
            reservation.save()
            messages.success(request, "Bron bekor qilindi.")
            return redirect("reservation_detail", token=token)

        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, "Bron yangilandi.")
            return redirect("reservation_detail", token=token)
    else:
        form = ReservationForm(instance=reservation)

    return render(request, "reservation_detail.html", {
        "form": form,
        "reservation": reservation,
    })


def check_working_hours(request):
    """JS orqali sana/vaqt tanlanganda ish vaqtini tekshirish uchun AJAX endpoint."""
    date_str = request.GET.get("date")
    time_str = request.GET.get("time")
    if not date_str:
        return JsonResponse({"ok": False, "message": "Sana korsatilmagan."})

    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"ok": False, "message": "Sana notogri formatda."})

    weekday = d.weekday()
    try:
        wh = WorkingHours.objects.get(day=weekday)
    except WorkingHours.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Bu kun uchun ish vaqti belgilanmagan."})

    if wh.is_closed:
        return JsonResponse({"ok": False, "message": "Bu kunda biz ishlamaymiz."})

    if time_str and wh.open_time and wh.close_time:
        try:
            t = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return JsonResponse({"ok": True, "open_time": str(wh.open_time), "close_time": str(wh.close_time)})
        if not (wh.open_time <= t <= wh.close_time):
            return JsonResponse({
                "ok": False,
                "message": f"Bu vaqtda biz ishlamaymiz. Ish vaqti: {wh.open_time.strftime('%H:%M')} - {wh.close_time.strftime('%H:%M')}."
            })

    return JsonResponse({
        "ok": True,
        "open_time": wh.open_time.strftime("%H:%M") if wh.open_time else None,
        "close_time": wh.close_time.strftime("%H:%M") if wh.close_time else None,
    })
