from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import UserRegistrationSerializer, UserProfileSerializer

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты модели User"""

    def test_create_user(self):
        """Создание обычного пользователя"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Иван',
            last_name='Иванов',
            city='Москва'
        )

        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Иван')
        self.assertEqual(user.city, 'Москва')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_user_without_email(self):
        """Создание пользователя без email должно вызывать ошибку"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email='', password='testpass123')

        self.assertIn('Email обязателен', str(context.exception))

    def test_create_superuser(self):
        """Создание суперпользователя"""
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )

        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

    def test_user_string_representation(self):
        """Тест строкового представления пользователя"""
        user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )

        self.assertEqual(str(user), 'user@example.com')

    def test_user_has_no_username_field(self):
        """У пользователя не должно быть поля username"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        self.assertIsNone(user.username or None)

    def test_user_email_unique(self):
        """Email должен быть уникальным"""
        User.objects.create_user(
            email='duplicate@example.com',
            password='testpass123'
        )

        with self.assertRaises(Exception):
            User.objects.create_user(
                email='duplicate@example.com',
                password='anotherpass123'
            )

    def test_user_optional_fields(self):
        """Тест необязательных полей пользователя"""
        user = User.objects.create_user(
            email='optional@example.com',
            password='testpass123'
        )
        self.assertEqual(user.phone, '')
        self.assertEqual(user.city, '')
        self.assertEqual(user.avatar.name, 'users/default_user.png')


class UserRegistrationSerializerTest(TestCase):
    """Тесты сериализатора регистрации"""

    def test_valid_registration_data(self):
        """Валидные данные для регистрации"""
        data = {
            'email': 'newuser@example.com',
            'password': 'StrongPass123',
            'password2': 'StrongPass123',
            'first_name': 'Петр',
            'last_name': 'Петров',
            'city': 'Санкт-Петербург'
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_password_mismatch(self):
        """Пароли не совпадают"""
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'different123',
            'first_name': 'Иван'
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_weak_password(self):
        """Слишком простой пароль"""
        data = {
            'email': 'test@example.com',
            'password': '123',
            'password2': '123',
            'first_name': 'Иван'
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_create_user(self):
        """Создание пользователя через сериализатор"""
        data = {
            'email': 'created@example.com',
            'password': 'TestPass123',
            'password2': 'TestPass123',
            'first_name': 'Сергей',
            'last_name': 'Сергеев',
            'city': 'Казань'
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.email, 'created@example.com')
        self.assertEqual(user.first_name, 'Сергей')
        self.assertTrue(user.check_password('TestPass123'))


class UserProfileSerializerTest(TestCase):
    """Тесты сериализатора профиля"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='profile@example.com',
            password='testpass123',
            first_name='Анна',
            last_name='Иванова',
            city='Екатеринбург',
            phone='+79991234567'
        )

    def test_profile_serialization(self):
        """Сериализация профиля пользователя"""
        serializer = UserProfileSerializer(self.user)

        data = serializer.data
        self.assertEqual(data['email'], 'profile@example.com')
        self.assertEqual(data['first_name'], 'Анна')
        self.assertEqual(data['city'], 'Екатеринбург')
        self.assertEqual(data['phone'], '+79991234567')
        self.assertIn('date_joined', data)
        self.assertIn('last_login', data)

    def test_profile_update(self):
        """Обновление профиля пользователя"""
        data = {
            'first_name': 'Анна-Мария',
            'last_name': 'Петрова',
            'city': 'Новосибирск',
            'phone': '+79998765432'
        }

        serializer = UserProfileSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()
        self.assertEqual(updated_user.first_name, 'Анна-Мария')
        self.assertEqual(updated_user.city, 'Новосибирск')
        self.assertEqual(updated_user.phone, '+79998765432')
        self.assertEqual(updated_user.email, 'profile@example.com')


class UserRegistrationViewTest(TestCase):
    """Тесты регистрации пользователя"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/users/register/'

    def test_successful_registration(self):
        """Успешная регистрация пользователя"""
        data = {
            'email': 'newuser@example.com',
            'password': 'StrongPassword123',
            'password2': 'StrongPassword123',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'city': 'Москва'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')

        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.first_name, 'Иван')

    def test_registration_password_mismatch(self):
        """Регистрация с несовпадающими паролями"""
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'different123'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_registration_duplicate_email(self):
        """Регистрация с уже существующим email"""
        User.objects.create_user(
            email='existing@example.com',
            password='testpass123'
        )

        data = {
            'email': 'existing@example.com',
            'password': 'anotherpass123',
            'password2': 'anotherpass123'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class UserProfileViewTest(TestCase):
    """Тесты профиля пользователя"""

    def setUp(self):
        self.client = APIClient()
        self.profile_url = '/api/users/me/'

        self.user = User.objects.create_user(
            email='profileuser@example.com',
            password='testpass123',
            first_name='Мария',
            last_name='Сидорова',
            city='Краснодар'
        )

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_get_profile_authenticated(self):
        """Получение профиля авторизованным пользователем"""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profileuser@example.com')
        self.assertEqual(response.data['first_name'], 'Мария')
        self.assertEqual(response.data['city'], 'Краснодар')

    def test_get_profile_unauthenticated(self):
        """Получение профиля неавторизованным пользователем"""
        client = APIClient()  # Новый клиент без авторизации
        response = client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        """Обновление профиля пользователя"""
        update_data = {
            'first_name': 'Мария-Анна',
            'last_name': 'Иванова',
            'city': 'Сочи',
            'phone': '+79181234567'
        }

        response = self.client.put(self.profile_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Мария-Анна')
        self.assertEqual(response.data['city'], 'Сочи')
        self.assertEqual(response.data['phone'], '+79181234567')

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Мария-Анна')
        self.assertEqual(self.user.phone, '+79181234567')

    def test_partial_update_profile(self):
        """Частичное обновление профиля"""
        update_data = {
            'city': 'Владивосток'
        }

        response = self.client.patch(self.profile_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['city'], 'Владивосток')
        self.assertEqual(response.data['first_name'], 'Мария')


class UserListViewTest(TestCase):
    """Тесты списка пользователей"""

    def setUp(self):
        self.client = APIClient()
        self.users_url = '/api/users/'

        self.regular_user = User.objects.create_user(
            email='regular@example.com',
            password='testpass123'
        )

        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )

    def test_user_list_admin_access(self):
        """Доступ к списку пользователей для админа"""
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        response = self.client.get(self.users_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_user_list_regular_user_access(self):
        """Доступ к списку пользователей для обычного пользователя"""
        refresh = RefreshToken.for_user(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        response = self.client.get(self.users_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list_unauthenticated(self):
        """Доступ к списку пользователей без авторизации"""
        response = self.client.get(self.users_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
