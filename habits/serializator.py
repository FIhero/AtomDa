from rest_framework import serializers

from .models import Habit
from .validators import (validate_execution_time, validate_frequency,
                         validate_not_both_reward_and_related,
                         validate_pleasant_habit_no_reward_or_related,
                         validate_related_habit_is_pleasant)


class HabitSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для привычек"""

    related_habit_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "related_habit_name",
            "frequency",
            "reward",
            "execution_time",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
            "related_habit_name",
        ]

    def get_related_habit_name(self, obj):
        """Получение названия связанной привычки"""
        if obj.related_habit:
            return obj.related_habit.action[:50]
        return None

    def validate(self, data):
        """Валидация данных привычки"""
        instance = self.instance

        # 1. Проверка времени выполнения
        execution_time = data.get(
            "execution_time", instance.execution_time if instance else None
        )
        if execution_time:
            validate_execution_time(execution_time)

        # 2. Проверка периодичности
        frequency = data.get("frequency", instance.frequency if instance else None)
        if frequency:
            validate_frequency(frequency)

        # 3. Проверка, что не указаны одновременно вознаграждение и связанная привычка
        reward = data.get("reward", instance.reward if instance else "")
        related_habit = data.get(
            "related_habit", instance.related_habit if instance else None
        )
        validate_not_both_reward_and_related(reward, related_habit)

        # 4. Проверка связанной привычки (должна быть приятной)
        if related_habit:
            validate_related_habit_is_pleasant(related_habit)

        # 5. Проверка для приятной привычки
        is_pleasant = data.get(
            "is_pleasant", instance.is_pleasant if instance else False
        )
        if is_pleasant:
            validate_pleasant_habit_no_reward_or_related(
                is_pleasant, reward, related_habit
            )

        return data

    def create(self, validated_data):
        """Создание привычки с привязкой к текущему пользователю"""
        # Получаем пользователя из контекста запроса
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)


class HabitListSerializer(HabitSerializer):
    """Сериализатор для списка привычек"""

    class Meta(HabitSerializer.Meta):
        fields = [
            "id",
            "place",
            "time",
            "action",
            "is_pleasant",
            "frequency",
            "execution_time",
            "is_public",
            "created_at",
        ]


class PublicHabitSerializer(HabitSerializer):
    """Сериализатор для публичных привычек"""

    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta(HabitSerializer.Meta):
        fields = [
            "id",
            "user_email",
            "place",
            "time",
            "action",
            "frequency",
            "execution_time",
            "created_at",
        ]
        read_only_fields = fields
