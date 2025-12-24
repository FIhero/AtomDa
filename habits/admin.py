from django.contrib import admin
from django.utils.html import format_html

from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "short_action",
        "place",
        "time",
        "is_pleasant_display",
        "frequency_display",
        "execution_time",
        "is_public_display",
        "created_at",
    )
    list_display_links = ("id", "short_action")
    list_filter = (
        "is_pleasant",
        "is_public",
        "frequency",
        "created_at",
        "user",
    )
    search_fields = ("action", "place", "user__email", "user__username")
    readonly_fields = ("created_at", "updated_at", "preview")
    list_per_page = 20

    fieldsets = (
        ("Основная информация", {"fields": ("user", "place", "time", "action")}),
        (
            "Характеристики привычки",
            {
                "fields": (
                    "is_pleasant",
                    "related_habit",
                    "frequency",
                    "reward",
                    "execution_time",
                )
            },
        ),
        ("Видимость", {"fields": ("is_public",)}),
        (
            "Метаданные",
            {
                "fields": ("created_at", "updated_at", "preview"),
                "classes": ("collapse",),
            },
        ),
    )

    def short_action(self, obj):
        """Сокращенное действие для списка"""
        if len(obj.action) > 40:
            return f"{obj.action[:40]}..."
        return obj.action

    short_action.short_description = "Действие"

    def is_pleasant_display(self, obj):
        """Красивое отображение приятной привычки"""
        if obj.is_pleasant:
            return format_html('<span style="color: green;">✓ Приятная</span>')
        return format_html('<span style="color: blue;">✓ Полезная</span>')

    is_pleasant_display.short_description = "Тип"

    def frequency_display(self, obj):
        """Отображение периодичности"""
        freq_map = {
            1: "Ежедневно",
            2: "Каждые 2 дня",
            3: "Каждые 3 дня",
            4: "Каждые 4 дня",
            5: "Каждые 5 дней",
            6: "Каждые 6 дней",
            7: "Еженедельно",
        }
        return freq_map.get(obj.frequency, str(obj.frequency))

    frequency_display.short_description = "Периодичность"

    def is_public_display(self, obj):
        """Красивое отображение публичности"""
        if obj.is_public:
            return format_html('<span style="color: green;">✓ Публичная</span>')
        return format_html('<span style="color: orange;">✗ Приватная</span>')

    is_public_display.short_description = "Доступ"

    def preview(self, obj):
        """Предпросмотр привычки"""
        return format_html(
            '<div style="padding: 10px; background: #f0f0f0; border-radius: 5px;">'
            "<strong>Формулировка привычки:</strong><br>"
            f"Я буду <em>{obj.action}</em> в <em>{obj.time}</em> в <em>{obj.place}</em>"
            "</div>"
        )

    preview.short_description = "Предпросмотр"

    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related("user", "related_habit")
