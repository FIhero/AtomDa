from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from habits.validators import validate_execution_time


class Habit(models.Model):
    """Модель привычки"""

    DAILY = 1
    EVERY_2_DAYS = 2
    EVERY_3_DAYS = 3
    EVERY_4_DAYS = 4
    EVERY_5_DAYS = 5
    EVERY_6_DAYS = 6
    WEEKLY = 7

    PERIODICITY_CHOICES = [
        (DAILY, "Ежедневно"),
        (EVERY_2_DAYS, "Каждые 2 дня"),
        (EVERY_3_DAYS, "Каждые 3 дня"),
        (EVERY_4_DAYS, "Каждые 4 дня"),
        (EVERY_5_DAYS, "Каждые 5 дней"),
        (EVERY_6_DAYS, "Каждые 6 дней"),
        (WEEKLY, "Еженедельно"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="habits",
    )
    place = models.CharField(
        max_length=255,
        verbose_name="Место",
        help_text="Место, в котором необходимо выполнять привычку",
    )
    time = models.TimeField(
        verbose_name="Время выполнения",
        help_text="Время, когда необходимо выполнять привычку",
    )
    action = models.CharField(
        max_length=500, verbose_name="Действие", help_text="Опишите что будете делать"
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Приятная привычка",
        help_text="Признак приятной привычки",
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
        help_text="Привычка, которая связана с другой привычкой",
    )
    frequency = models.PositiveSmallIntegerField(
        choices=PERIODICITY_CHOICES,
        default=DAILY,
        verbose_name="Периодичность",
        help_text="Периодичность выполнения привычки для напоминания в днях",
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Вознаграждение",
        help_text="Чем пользователь должен себя вознаградить после выполнения",
    )
    execution_time = models.PositiveSmallIntegerField(
        validators=[validate_execution_time],
        verbose_name="Время на выполнение",
        help_text="Время, которое предположительно потратит пользователь на выполнение привычки (не более 120 секунд)",
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичная привычка",
        help_text="Привычки можно публиковать в общий доступ",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]

    def __str__(self):
        pleasant = " (приятная)" if self.is_pleasant else ""
        return f"{self.action[:30]}{pleasant} - {self.time}"

    def clean(self):
        """Встроенные валидации модели"""
        super().clean()
        errors = {}
        if self.execution_time > 120:
            errors["execution_time"] = (
                "Время выполнения должно быть не больше 120 секунд"
            )

        if self.is_pleasant:
            if self.reward:
                errors["reward"] = "У приятной привычки не может быть вознаграждения"
            if self.related_habit:
                errors["related_habit"] = (
                    "У приятной привычки не может быть связанной привычки"
                )

        if self.related_habit and not self.related_habit.is_pleasant:
            errors["related_habit"] = "Связанная привычка должна быть приятной"

        if self.related_habit and self.reward:
            errors["reward"] = (
                "Нельзя указывать одновременно и вознаграждение, и связанную привычку"
            )
            errors["related_habit"] = (
                "Нельзя указывать одновременно и вознаграждение, и связанную привычку"
            )

        if self.frequency < 1 or self.frequency > 7:
            errors["frequency"] = "Периодичность должна быть от 1 до 7 дней"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Вызов clean при сохранении"""
        self.full_clean()
        super().save(*args, **kwargs)
