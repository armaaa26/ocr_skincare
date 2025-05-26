from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import SkincareIngredient

class SkincareIngredientResource(resources.ModelResource):
    class Meta:
        model = SkincareIngredient
        import_id_fields = ('name',)
        fields = ('name', 'benefit', 'side_effect', 'warning')
        skip_unchanged = True
        report_skipped = True       


class SkincareIngredientAdmin(ImportExportModelAdmin):
    resource_class = SkincareIngredientResource
    list_display = ('name', 'benefit', 'side_effect', 'warning')

admin.site.register(SkincareIngredient, SkincareIngredientAdmin)
