from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Book, Category, Member, Loan
from .forms import BookForm, CategoryForm, MemberForm, LoanForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "The username or password you entered is incorrect.")
    return render(request, "registration/login.html")

@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return redirect("dashboard")

@login_required
def dashboard(request):
    today = timezone.localdate()
    context = {
        "book_count": Book.objects.count(),
        "member_count": Member.objects.count(),
        "active_loans": Loan.objects.filter(status=Loan.Status.BORROWED).count(),
        "overdue_count": Loan.objects.filter(status=Loan.Status.BORROWED, due_date__lt=today).count(),
        "recent_loans": Loan.objects.select_related("book", "member").all()[:7],
        "popular_categories": Category.objects.annotate(book_count=Count("books")).order_by("-book_count")[:5],
        "today": today,
    }
    return render(request, "catalog/dashboard.html", context)

@login_required
def book_list(request):
    q = request.GET.get("q", "").strip()
    books = Book.objects.select_related("category")
    if q:
        books = books.filter(Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q))
    return render(request, "catalog/book_list.html", {"books": books, "q": q})

@login_required
def book_create(request):
    form = BookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Book added successfully.")
        return redirect("book_list")
    return render(request, "catalog/form.html", {"form": form, "page_title": "Add a book", "back_url": "book_list"})

@login_required
def book_update(request, pk):
    obj = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Book details updated.")
        return redirect("book_list")
    return render(request, "catalog/form.html", {"form": form, "page_title": "Edit book", "back_url": "book_list"})

@login_required
def book_delete(request, pk):
    obj = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        if obj.loans.filter(status=Loan.Status.BORROWED).exists():
            messages.error(request, "This book has an active loan and cannot be deleted.")
        else:
            obj.delete()
            messages.success(request, "Book deleted.")
        return redirect("book_list")
    return render(request, "catalog/confirm_delete.html", {"object": obj, "back_url": "book_list"})

@login_required
def category_list(request):
    categories = Category.objects.annotate(book_count=Count("books"))
    return render(request, "catalog/category_list.html", {"categories": categories})

@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category created.")
        return redirect("category_list")
    return render(request, "catalog/form.html", {"form": form, "page_title": "Add category", "back_url": "category_list"})

@login_required
def category_update(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category updated.")
        return redirect("category_list")
    return render(request, "catalog/form.html", {"form": form, "page_title": "Edit category", "back_url": "category_list"})

@login_required
def category_delete(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        if obj.books.exists():
            messages.error(request, "Move or delete this category's books before deleting it.")
        else:
            obj.delete()
            messages.success(request, "Category deleted.")
        return redirect("category_list")
    return render(request, "catalog/confirm_delete.html", {"object": obj, "back_url": "category_list"})

@login_required
def member_list(request):
    q = request.GET.get("q", "").strip()
    members = Member.objects.all()
    if q:
        members = members.filter(Q(member_code__icontains=q) | Q(first_name__icontains=q) |
                                 Q(last_name__icontains=q) | Q(email__icontains=q))
    return render(request, "catalog/member_list.html", {"members": members, "q": q})

@login_required
def member_create(request):
    form = MemberForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Member registered.")
        return redirect("member_list")
    return render(request, "catalog/form.html", {"form": form, "page_title": "Register member", "back_url": "member_list"})

@login_required
def member_update(request, pk):
    obj = get_object_or_404(Member, pk=pk)
    form = MemberForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Member updated.")
        return redirect("member_list")
    return render(request, "catalog/form.html", {"form": form, "page_title": "Edit member", "back_url": "member_list"})

@login_required
def member_delete(request, pk):
    obj = get_object_or_404(Member, pk=pk)
    if request.method == "POST":
        if obj.loans.filter(status=Loan.Status.BORROWED).exists():
            messages.error(request, "This member has an active loan and cannot be deleted.")
        else:
            obj.delete()
            messages.success(request, "Member deleted.")
        return redirect("member_list")
    return render(request, "catalog/confirm_delete.html", {"object": obj, "back_url": "member_list"})

@login_required
def loan_list(request):
    status = request.GET.get("status", "")
    q = request.GET.get("q", "").strip()
    loans = Loan.objects.select_related("book", "member", "issued_by")
    if status in [Loan.Status.BORROWED, Loan.Status.RETURNED]:
        loans = loans.filter(status=status)
    if q:
        loans = loans.filter(Q(book__title__icontains=q) | Q(member__first_name__icontains=q) |
                             Q(member__last_name__icontains=q) | Q(member__member_code__icontains=q))
    return render(request, "catalog/loan_list.html", {"loans": loans, "status_filter": status, "q": q})

@login_required
def loan_create(request):
    form = LoanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            book = Book.objects.select_for_update().get(pk=form.cleaned_data["book"].pk)
            if book.available_copies < 1:
                form.add_error("book", "No copies are currently available.")
            elif form.cleaned_data["due_date"] < form.cleaned_data["borrowed_at"]:
                form.add_error("due_date", "Due date cannot be before the borrowing date.")
            else:
                loan = form.save(commit=False)
                loan.book = book
                loan.issued_by = request.user
                loan.status = Loan.Status.BORROWED
                loan.save()
                book.available_copies -= 1
                book.save(update_fields=["available_copies"])
                messages.success(request, "Book issued. The loan has been recorded.")
                return redirect("loan_list")
    return render(request, "catalog/form.html", {"form": form, "page_title": "Issue a book", "back_url": "loan_list"})

@login_required
def loan_return(request, pk):
    loan = get_object_or_404(Loan.objects.select_related("book"), pk=pk)
    if request.method == "POST":
        if loan.status == Loan.Status.BORROWED:
            with transaction.atomic():
                loan.status = Loan.Status.RETURNED
                loan.returned_at = timezone.localdate()
                loan.save(update_fields=["status", "returned_at"])
                book = Book.objects.select_for_update().get(pk=loan.book_id)
                book.available_copies = min(book.total_copies, book.available_copies + 1)
                book.save(update_fields=["available_copies"])
            messages.success(request, "Book return recorded.")
        else:
            messages.info(request, "This loan was already returned.")
        return redirect("loan_list")
    return render(request, "catalog/confirm_return.html", {"loan": loan})

@login_required
def reports(request):
    today = timezone.localdate()
    context = {
        "total_books": Book.objects.count(),
        "total_copies": sum(Book.objects.values_list("total_copies", flat=True)),
        "available_copies": sum(Book.objects.values_list("available_copies", flat=True)),
        "total_members": Member.objects.count(),
        "active_loans": Loan.objects.filter(status=Loan.Status.BORROWED).count(),
        "overdue_loans": Loan.objects.filter(status=Loan.Status.BORROWED, due_date__lt=today).count(),
        "returned_loans": Loan.objects.filter(status=Loan.Status.RETURNED).count(),
        "category_stats": Category.objects.annotate(book_count=Count("books")).order_by("-book_count"),
    }
    return render(request, "catalog/reports.html", context)
