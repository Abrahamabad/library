from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Book, Category, Member, Loan

class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 3)

class BookForm(StyledModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "isbn", "category", "publisher", "published_year",
                  "shelf_location", "total_copies", "available_copies", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}
    def clean(self):
        cleaned = super().clean()
        total = cleaned.get("total_copies")
        available = cleaned.get("available_copies")
        if total is not None and available is not None and available > total:
            self.add_error("available_copies", "Available copies cannot exceed total copies.")
        if total is not None and total < 1:
            self.add_error("total_copies", "A book must have at least one copy.")
        return cleaned

class CategoryForm(StyledModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]

class MemberForm(StyledModelForm):
    class Meta:
        model = Member
        fields = ["member_code", "first_name", "last_name", "email", "phone", "address", "status"]

class LoanForm(StyledModelForm):
    class Meta:
        model = Loan
        fields = ["book", "member", "borrowed_at", "due_date", "notes"]
        widgets = {
            "borrowed_at": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["book"].queryset = Book.objects.filter(available_copies__gt=0)
        self.fields["member"].queryset = Member.objects.filter(status=Member.Status.ACTIVE)
        self.fields["borrowed_at"].initial = timezone.localdate()
        self.fields["due_date"].initial = timezone.localdate() + timedelta(days=14)
