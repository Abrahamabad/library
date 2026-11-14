from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=160)
    isbn = models.CharField(max_length=20, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="books")
    publisher = models.CharField(max_length=160, blank=True)
    published_year = models.PositiveSmallIntegerField(null=True, blank=True)
    shelf_location = models.CharField(max_length=60, blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["title"]
    def __str__(self):
        return f"{self.title} — {self.author}"
    @property
    def borrowed_copies(self):
        return self.total_copies - self.available_copies

class Member(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
    member_code = models.CharField(max_length=24, unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    joined_at = models.DateField(default=timezone.localdate)
    class Meta:
        ordering = ["last_name", "first_name"]
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Loan(models.Model):
    class Status(models.TextChoices):
        BORROWED = "borrowed", "Borrowed"
        RETURNED = "returned", "Returned"
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="loans")
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name="loans")
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    borrowed_at = models.DateField(default=timezone.localdate)
    due_date = models.DateField()
    returned_at = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.BORROWED)
    notes = models.CharField(max_length=250, blank=True)
    class Meta:
        ordering = ["-borrowed_at", "-id"]
    def __str__(self):
        return f"{self.book.title} → {self.member.full_name}"
    @property
    def is_overdue(self):
        return self.status == self.Status.BORROWED and self.due_date < timezone.localdate()
    @property
    def days_overdue(self):
        if self.is_overdue:
            return (timezone.localdate() - self.due_date).days
        return 0
