from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task


class TaskAPITestCase(APITestCase):
    def setUp(self):
        # Создаём тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpass')

        # Создаём тестовые задачи
        self.task1 = Task.objects.create(
            name='Task 1',
            description='Description for Task 1',
            completed=False,
            created_by=self.user
        )
        self.task2 = Task.objects.create(
            name='Task 2',
            description='Description for Task 2',
            completed=True,
            created_by=self.user
        )

    def test_get_task_list(self):
        """Тест получения списка задач"""
        url = reverse('tasks-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Пагинация возвращает 'results'

    def test_create_task(self):
        """Тест создания новой задачи"""
        url = reverse('tasks-list')
        data = {
            'name': 'New Task',
            'description': 'New task description',
            'completed': False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 3)
        self.assertEqual(response.data['name'], 'New Task')
        self.assertEqual(response.data['created_by'], self.user.id)

    def test_get_task_detail(self):
        """Тест получения конкретной задачи"""
        url = reverse('tasks-detail', kwargs={'pk': self.task1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Task 1')

    def test_update_task(self):
        """Тест обновления задачи"""
        url = reverse('tasks-detail', kwargs={'pk': self.task1.pk})
        data = {
            'name': 'Updated Task',
            'description': 'Updated description',
            'completed': True
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.name, 'Updated Task')
        self.assertEqual(self.task1.completed, True)
        self.assertEqual(self.task1.created_by, self.user)

    def test_delete_task(self):
        """Тест удаления задачи"""
        url = reverse('tasks-detail', kwargs={'pk': self.task1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 1)

    def test_filter_tasks_by_status(self):
        """Тест фильтрации задач по статусу"""
        url = reverse('tasks-list') + '?completed=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Task 2')

    def test_unauthenticated_access(self):
        """Тест доступа без аутентификации"""
        self.client.logout()
        url = reverse('tasks-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)