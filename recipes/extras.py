from .models import Tag


def get_all_tags():
    return Tag.objects.all()


def get_filters(request, queryset):
    filters = request.GET.getlist('filters')
    if filters:
        qs = queryset.filter(tag__slug__in=filters).distinct()
        return qs
    return queryset
