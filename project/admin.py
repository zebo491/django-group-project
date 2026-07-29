from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SiteAbout, Category, MenuItem, BeerItem,
    BreakfastCategory, BreakfastItem, WorkingHours, Reservation
)


# ============ ABOUT US ============

@admin.register(SiteAbout)
class SiteAboutAdmin(admin.ModelAdmin):
    list_display = ("title",)

    def has_add_permission(self, request):
        # Faqat bitta About yozuvi bolishi kerak
        if SiteAbout.objects.exists():
            return False
        return super().has_add_permission(request)


# ============ PRICING (MENU) ============

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category_list", "is_active", "image_preview")
    list_filter = ("categories", "is_active")
    search_fields = ("name",)
    filter_horizontal = ("categories",)

    def category_list(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    category_list.short_description = "Kategoriyalar"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;border-radius:4px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Rasm"


# ============ BEER ============

@admin.register(BeerItem)
class BeerItemAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active", "image_preview")
    list_filter = ("is_active",)
    search_fields = ("name",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;border-radius:4px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Rasm"


# ============ BREAKFAST ============

class BreakfastItemInline(admin.TabularInline):
    model = BreakfastItem
    extra = 1
    fields = ("name", "price", "image", "short_description", "is_active")


@admin.register(BreakfastCategory)
class BreakfastCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "item_count", "image_preview")
    ordering = ("order",)
    inlines = [BreakfastItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Taomlar soni"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;border-radius:4px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Rasm"


@admin.register(BreakfastItem)
class BreakfastItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active", "image_preview")
    list_filter = ("category", "is_active")
    search_fields = ("name",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;border-radius:4px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Rasm"


# ============ ISH VAQTI ============

@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ("day", "is_closed", "open_time", "close_time")
    ordering = ("day",)


# ============ BRON (RESERVATION) ============

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "full_name", "phone", "email", "reservation_date", "reservation_time",
        "guest_count", "status_badge", "created_at",
    )
    list_filter = ("status", "reservation_date")
    search_fields = ("full_name", "email", "phone")
    filter_horizontal = ("menu_items", "beer_items", "breakfast_items")
    readonly_fields = ("token", "created_at", "updated_at")
    date_hierarchy = "reservation_date"

    fieldsets = (
        ("Mijoz malumotlari", {
            "fields": ("full_name", "email", "phone")
        }),
        ("Bron tafsilotlari", {
            "fields": ("reservation_date", "reservation_time", "guest_count", "comment", "status")
        }),
        ("Tanlangan taomlar", {
            "fields": ("menu_items", "beer_items", "breakfast_items")
        }),
        ("Texnik malumot", {
            "fields": ("token", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    actions = ["mark_confirmed", "mark_cancelled"]

    def status_badge(self, obj):
        colors = {"pending": "#f0ad4e", "confirmed": "#5cb85c", "cancelled": "#d9534f"}
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:4px;">{}</span>',
            colors.get(obj.status, "#777"), obj.get_status_display()
        )
    status_badge.short_description = "Holati"

    @admin.action(description="Tanlangan bronlarni TASDIQLASH")
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status="confirmed")
        self.message_user(request, f"{updated} ta bron tasdiqlandi.")

    @admin.action(description="Tanlangan bronlarni BEKOR QILISH")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status="cancelled")
        self.message_user(request, f"{updated} ta bron bekor qilindi.")


    