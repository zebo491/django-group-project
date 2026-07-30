import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# ============ ABOUT US ============

class SiteAbout(models.Model):
    """About Us bolimi - faqat bitta yozuv boladi."""
    title = models.CharField(max_length=200, default="About Us")
    short_text = models.TextField(help_text="Bosh sahifada darhol koringan qisqa matn")
    full_text = models.TextField(help_text="'Ko'proq' bosilganda ochiladigan toliq matn")
    image = models.ImageField(upload_to="about/", blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "About Us bolimi"
        verbose_name_plural = "About Us bolimi"


# ============ PRICING (MENU) ============

class Category(models.Model):
    """Pricing filtri: Breakfast, Special, Desert, Dinner va h.k."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, help_text="Masalan: breakfast, special, desert, dinner")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Taom kategoriyasi"
        verbose_name_plural = "Taom kategoriyalari"


class MenuItem(models.Model):
    """Pricing qismidagi har bir taom kartochkasi."""
    name = models.CharField(max_length=150)
    categories = models.ManyToManyField(Category, related_name="menu_items")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="menu/")
    short_description = models.CharField(max_length=255, blank=True)
    full_description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Taom (Pricing)"
        verbose_name_plural = "Taomlar (Pricing)"


# ============ BEER ============

class BeerItem(models.Model):
    """Our Beer bolimidagi har bir ichimlik."""
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to="beer/")
    short_description = models.CharField(max_length=255, blank=True)
    full_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ichimlik (Beer)"
        verbose_name_plural = "Ichimliklar (Beer)"


# ============ BREAKFAST ============

class BreakfastCategory(models.Model):
    """Our Breakfast Menu bosilganda chiqadigan rasmli kategoriyalar."""
    title = models.CharField(max_length=150)
    image = models.ImageField(upload_to="breakfast_categories/")
    order = models.PositiveIntegerField(default=0, help_text="Tartib raqami")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order"]
        verbose_name = "Breakfast kategoriyasi"
        verbose_name_plural = "Breakfast kategoriyalari"


class BreakfastItem(models.Model):
    """Har bir Breakfast kategoriyasi ichidagi taomlar."""
    category = models.ForeignKey(BreakfastCategory, related_name="items", on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to="breakfast_items/")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    short_description = models.CharField(max_length=255, blank=True)
    full_description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category.title} - {self.name}"

    class Meta:
        verbose_name = "Breakfast taomi"
        verbose_name_plural = "Breakfast taomlari"


# ============ ISH VAQTI ============

class WorkingHours(models.Model):
    """Restoranning har kunlik ish vaqti - bron qilishni tekshirish uchun."""
    DAYS = [
        (0, "Dushanba"), (1, "Seshanba"), (2, "Chorshanba"),
        (3, "Payshanba"), (4, "Juma"), (5, "Shanba"), (6, "Yakshanba"),
    ]
    day = models.IntegerField(choices=DAYS, unique=True)
    is_closed = models.BooleanField(default=False, help_text="Belgilansa, shu kun umuman ishlamaydi")
    open_time = models.TimeField(blank=True, null=True)
    close_time = models.TimeField(blank=True, null=True)

    def __str__(self):
        return self.get_day_display()

    class Meta:
        verbose_name = "Ish vaqti"
        verbose_name_plural = "Ish vaqtlari"
        ordering = ["day"]


# ============ BRON (RESERVATION) ============

class Reservation(models.Model):
    """Mijoz tomonidan joy bron qilish."""
    STATUS_CHOICES = [
        ("pending", "Kutilmoqda"),
        ("confirmed", "Tasdiqlangan"),
        ("cancelled", "Bekor qilingan"),
    ]

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    full_name = models.CharField(max_length=150, verbose_name="Ism Familya")
    email = models.EmailField()
    phone = models.CharField(max_length=30, verbose_name="Telefon")

    reservation_date = models.DateField(verbose_name="Bron sanasi")
    reservation_time = models.TimeField(verbose_name="Bron vaqti")
    guest_count = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Kishilar soni",
        help_text="1 ta stol uchun maksimum 10 kishi"
    )

    menu_items = models.ManyToManyField(MenuItem, blank=True, related_name="reservations")
    beer_items = models.ManyToManyField(BeerItem, blank=True, related_name="reservations")
    breakfast_items = models.ManyToManyField(BreakfastItem, blank=True, related_name="reservations")

    comment = models.TextField(blank=True, verbose_name="Sharh")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.reservation_date} {self.reservation_time}"

    class Meta:
        verbose_name = "Bron"
        verbose_name_plural = "Bronlar"
        ordering = ["-created_at"]

