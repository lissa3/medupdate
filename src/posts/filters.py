from django.contrib.admin import SimpleListFilter


class SoftDelFilter(SimpleListFilter):
    title = "Soft deleted"
    parameter_name = "is_deleted"

    def lookups(self, request, model_admin):
        """custom lookups"""
        return [
            ("deleted", "Soft deleted"),
            ("active", "Still active"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "deleted":
            return queryset.filter(is_deleted=True)
        elif self.value() == "active":
            return queryset.filter(is_deleted=False)
