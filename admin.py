from django.contrib import admin
from .models import Book, Category, Member, Loan

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn", "category", "available_copies", "total_copies")
    search_fields = ("title", "author", "isbn")
    list_filter = ("category",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("member_code", "first_name", "last_name", "email", "status")
    search_fields = ("member_code", "first_name", "last_name", "email")
    list_filter = ("status",)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("book", "member", "borrowed_at", "due_date", "status")
    list_filter = ("status", "borrowed_at")
    search_fields = ("book__title", "member__first_name", "member__last_name")
