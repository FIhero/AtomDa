import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from habits.models import Habit
from habits.serializator import HabitSerializer
from habits.validators import validate_execution_time, validate_frequency

User = get_user_model()


class HabitModelTest(TestCase):
    """Тесты модели Habit"""

    def setUp(self):
        """Создаём тестового пользователя"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_create_valid_habit(self):
        """Создание валидной привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place='Дома',
            time='08:00:00',
            action='пить стакан воды',
            execution_time=30,
            frequency=1
        )

        self.assertEqual(habit.user.email, 'test@example.com')
        self.assertEqual(habit.action, 'пить стакан воды')
        self.assertEqual(habit.execution_time, 30)
        self.assertTrue(habit.created_at)

    def test_execution_time_validation_max_120(self):
        """Валидация: время выполнения не больше 120 секунд"""
        habit = Habit(
            user=self.user,
            place='Дома',
            time='08:00:00',
            action='пить воду',
            execution_time=150
        )

        with self.assertRaises(ValidationError) as context:
            habit.full_clean()

        self.assertIn('execution_time', str(context.exception))

    def test_execution_time_validation_min_1(self):
        """Валидация: время выполнения не меньше 1 секунды"""
        habit = Habit(
            user=self.user,
            place='Дома',
            time='08:00:00',
            action='пить воду',
            execution_time=0
        )

        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_frequency_validation_1_to_7(self):
        """Валидация: периодичность от 1 до 7 дней"""
        habit = Habit(
            user=self.user,
            place='Дома',
            time='08:00:00',
            action='пить воду',
            execution_time=30,
            frequency=10
        )

        with self.assertRaises(ValidationError) as context:
            habit.full_clean()

        self.assertIn('frequency', str(context.exception))

    def test_pleasant_habit_no_reward(self):
        """Валидация: у приятной привычки не может быть вознаграждения"""
        habit = Habit(
            user=self.user,
            place='Дома',
            time='08:00:00',
            action='принять ванну',
            is_pleasant=True,
            execution_time=60,
            reward='чай'
        )

        with self.assertRaises(ValidationError) as context:
            habit.full_clean()

        self.assertIn('reward', str(context.exception))

    def test_not_both_reward_and_related_habit(self):
        """Валидация: нельзя одновременно указать вознаграждение и связанную привычку"""
        # Сначала создаём приятную привычку для связи
        pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дома',
            time='20:00:00',
            action='принять ванну',
            is_pleasant=True,
            execution_time=60
        )

        habit = Habit(
            user=self.user,
            place='Парк',
            time='07:00:00',
            action='пробежка',
            execution_time=120,
            reward='кофе',
            related_habit=pleasant_habit
        )

        with self.assertRaises(ValidationError) as context:
            habit.full_clean()

        error_str = str(context.exception)
        self.assertIn('reward', error_str)
        self.assertIn('related_habit', error_str)

    def test_related_habit_must_be_pleasant(self):
        """Валидация: связанная привычка должна быть приятной"""
        not_pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='07:00:00',
            action='пробежка',
            is_pleasant=False,
            execution_time=120
        )

        habit = Habit(
            user=self.user,
            place='Дома',
            time='08:00:00',
            action='пить воду',
            execution_time=30,
            related_habit=not_pleasant_habit
        )

        with self.assertRaises(ValidationError) as context:
            habit.full_clean()

        self.assertIn('related_habit', str(context.exception))

    def test_string_representation(self):
        """Тест строкового представления"""
        habit = Habit.objects.create(
            user=self.user,
            place='Дома',
            time='08:00:00',
            action='пить стакан воды с лимоном и мёдом',
            execution_time=30
        )

        self.assertIn('пить стакан воды', str(habit))
        self.assertIn('08:00', str(habit))

    def test_habit_periodicity_choices(self):
        """Тест выбора периодичности"""
        habit = Habit.objects.create(
            user=self.user,
            place='Дома',
            time='08:00:00',
            action='пить воду',
            execution_time=30,
            frequency=7
        )

        self.assertEqual(habit.get_frequency_display(), 'Еженедельно')


class ValidatorsTest(TestCase):
    """Тесты отдельных валидаторов"""

    def test_validate_execution_time_valid(self):
        """Валидация времени выполнения - валидные значения"""
        validate_execution_time(1)
        validate_execution_time(60)
        validate_execution_time(120)

    def test_validate_execution_time_invalid(self):
        """Валидация времени выполнения - невалидные значения"""
        with self.assertRaises(ValidationError) as context:
            validate_execution_time(121)

        self.assertIn('не больше 120 секунд', str(context.exception))

    def test_validate_frequency_valid(self):
        """Валидация периодичности - валидные значения"""
        validate_frequency(1)
        validate_frequency(4)
        validate_frequency(7)

    def test_validate_frequency_invalid(self):
        """Валидация периодичности - невалидные значения"""
        with self.assertRaises(ValidationError) as context:
            validate_frequency(0)
        self.assertIn('реже, чем 1 раз в 7 дней', str(context.exception))

        with self.assertRaises(ValidationError) as context:
            validate_frequency(8)
        self.assertIn('реже, чем 1 раз в 7 дней', str(context.exception))


class HabitSerializerTest(TestCase):
    """Тесты сериализатора привычек"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_habit_serializer_valid_data(self):
        """Сериализатор с валидными данными"""
        data = {
            'place': 'Дома',
            'time': '08:00:00',
            'action': 'пить воду',
            'execution_time': 30,
            'frequency': 1,
            'is_public': False
        }

        serializer = HabitSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_habit_serializer_invalid_execution_time(self):
        """Сериализатор с невалидным временем выполнения"""
        data = {
            'place': 'Дома',
            'time': '08:00:00',
            'action': 'пить воду',
            'execution_time': 150,  # > 120
            'frequency': 1
        }

        serializer = HabitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('execution_time', serializer.errors)

    def test_habit_serializer_create(self):
        """Создание привычки через сериализатор"""
        data = {
            'place': 'Парк',
            'time': '07:00:00',
            'action': 'пробежка',
            'execution_time': 120,
            'frequency': 1,
            'is_public': True
        }

        serializer = HabitSerializer(data=data, context={'request': type('Request', (), {'user': self.user})()})
        self.assertTrue(serializer.is_valid())

        habit = serializer.save()
        self.assertEqual(habit.user, self.user)
        self.assertEqual(habit.action, 'пробежка')
