from django.core.exceptions import ValidationError


def validate_execution_time(value):
    """Времени выполнения (максимум 120 секунд)"""
    if value > 120:
        raise ValidationError("Время выполнения должно быть не больше 120 секунд")
    if value < 1:
        raise ValidationError("Время выполнения должно быть не меньше 1 секунды")


def validate_related_habit_is_pleasant(related_habit):
    """Связанная привычка должна быть приятной"""
    if related_habit and not related_habit.is_pleasant:
        raise ValidationError(
            "В связанные привычки могут попадать только привычки с признаком приятной привычки"
        )


def validate_frequency(value):
    """Валидация периодичности (1-7 дней)"""
    if value < 1 or value > 7:
        raise ValidationError("Нельзя выполнять привычку реже, чем 1 раз в 7 дней")


def validate_pleasant_habit_no_reward_or_related(is_pleasant, reward, related_habit):
    """У приятной привычки не может быть вознаграждения или связанной привычки"""
    if is_pleasant and (reward or related_habit):
        raise ValidationError(
            "У приятной привычки не может быть вознаграждения или связанной привычки"
        )


def validate_not_both_reward_and_related(reward, related_habit):
    """Нельзя одновременно указывать вознаграждение и связанную привычку"""
    if reward and related_habit:
        raise ValidationError(
            "Нельзя одновременно указывать и вознаграждение, и связанную привычку"
        )
