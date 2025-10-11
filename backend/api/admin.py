from django.contrib import admin
from . import models
from django.forms import ModelForm, ValidationError
from django.utils.safestring import mark_safe


# ---------- Simple lookup tables ----------
@admin.register(
    models.Status,
    models.DriveType,
    models.CarType,
    models.Feature,
    models.SafetyFeature,
    models.Transmission,
    models.FuelType,
    models.Condition
)

@admin.register(models.Make)
class MakeAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(models.ModelName)
class ModelNameAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(models.Color)
class ColorAdmin(admin.ModelAdmin):
    search_fields = ['name']

class LookupAdmin(admin.ModelAdmin):
    search_fields = ("name", "type")
    list_display = ("id", "__str__")
    ordering = ("id")


# ---------- Inline for listing images ----------
class ListingImageInline(admin.TabularInline):
    model = models.ListingImage
    extra = 1
    
    def get_extra(self, request, obj=None, **kwargs):
        if obj:  # Only show extra fields if editing an existing object
            return 0  # No extra rows by default
        return 1  # One extra row for new images

    def delete(self, request, obj=None, **kwargs):
        if obj:
            obj.delete()


# ---------- CarsListing ----------
@admin.register(models.CarsListing)
class CarsListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "make", "model", "year", "price", "created_at")
    list_filter = (
        "fuel_type",
        "transmission",
        "condition",
        "color",
        "year",
    )
    search_fields = ("title", "description", "vin","model__name", "make__name")
    inlines = [ListingImageInline]
    autocomplete_fields = (
        "make",
        "model",
        "color"
    )


# ---------- ListingImage ----------
@admin.register(models.ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "uploaded_at")
    search_fields = ("listing__title",)
    list_filter = ("uploaded_at",)


# ---------- Inquiry ----------
class InquiryAdminForm(ModelForm):
    class Meta:
        model = models.Inquiry
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        if self.instance and self.instance.pk:
            changed = set(self.changed_data) - {"status"}
            if changed:
                raise ValidationError(
                    f"Only 'status' can be changed in admin. You modified: {', '.join(sorted(changed))}"
                )
        return cleaned


@admin.register(models.Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    form = InquiryAdminForm
    list_display = ("name", "custom_status_coloring", "listing", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "phone", "message")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            all_fields = [f.name for f in self.model._meta.fields]
            return [f for f in all_fields if f != "status"]
        return []
    
    def custom_status_coloring(self, obj):
        if obj.status.name == 'New':
            return mark_safe('<span style="background-color: blue; color: white; padding: 5px 16px; border-radius: 10px; font-weight: bold;">New</span>')
        elif obj.status.name == 'Sold':
            return mark_safe('<span style="background-color: green; color: white; padding: 5px 16px; border-radius: 10px; font-weight: bold;">Sold</span>')
        elif obj.status.name == 'In progress':
            return mark_safe('<span style="background-color: orange; color: white; padding: 5px 16px; border-radius: 10px; font-weight: bold; white-space: nowrap;">In Progress</span>')
        elif obj.status.name == 'Cancelled':
            return mark_safe('<span style="background-color: red; color: white; padding: 5px 16px; border-radius: 10px; font-weight: bold;">Cancelled</span>')
        elif obj.status.name == 'Lost':
            return mark_safe('<span style="background-color: red; color: white; padding: 5px 16px; border-radius: 10px; font-weight: bold;">Lost</span>')
        else:
            return mark_safe('<span style="background-color: red; color: white; padding: 5px 16px; border-radius: 10px; font-weight: bold;">Unknown</span>')
 
    custom_status_coloring.short_description = "Status"
