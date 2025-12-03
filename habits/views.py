from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from habits.models import Habit
from habits.permissions import IsOwner
from habits.serializator import (HabitListSerializer, HabitSerializer,
                                 PublicHabitSerializer)


class HabitPagination(PageNumberPagination):
    """Пагинация для привычек - 5 на страницу"""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для привычек с CRUD операциями"""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_pleasant", "is_public", "frequency"]

    def get_permissions(self):
        """Разные permissions для разных действий"""
        if self.action == "create":
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Фильтрация привычек по пользователю"""
        queryset = super().get_queryset()

        if self.action == "list":
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == "list":
            return HabitListSerializer
        elif self.action == "public":
            return PublicHabitSerializer
        return HabitSerializer

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def public(self, request):
        """Список публичных привычек"""
        public_habits = Habit.objects.filter(is_public=True)
        page = self.paginate_queryset(public_habits)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(public_habits, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """При создании привязываем привычку к текущему пользователю"""
        serializer.save(user=self.request.user)
