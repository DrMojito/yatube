from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post
from urllib.parse import urljoin

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name1',
                                            email='test@mail.ru',
                                            password='test_pass'),
            text='Тестовая запись для создания нового поста',)

        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug'
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username='player')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_and_group(self):
        """Страницы общего пользования"""
        url_names = (
            '/',
            '/group/test_slug/',
            '/profile/test_name1/',
            f'/posts/{self.post.id}/',
        )
        for adress in url_names:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_for_authorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_url(self):
        """Без авторизации приватные URL недоступны"""
        url_names = (
            '/create/',
            '/admin/',
            f'/posts/{self.post.id}/edit/'
        )
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_redirect_anonymous_on_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/')
        url = urljoin(reverse('login'), "?next=/create/")
        self.assertRedirects(response, url)

    def test_page_404(self):
        response = self.guest_client.get('/qazwsxedc123/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
