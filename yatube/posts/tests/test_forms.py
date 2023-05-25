from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post, Group

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(
            username='post_author')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.guest_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.post_author)
        self.auth_user_comm = Client()

    def test_authorized_user_create_post(self):
        """Проверка создания записи авторизированным клиентом."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.post_author.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group_id, form_data['group'])

    def test_authorized_user_edit_post(self):
        """Проверка редактирования записи авторизированным клиентом."""
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.post_author)
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id}
        response = self.authorized_user.post(
            reverse(
                'posts:post_edit',
                args=[post.id]),
            data=form_data,
            follow=True)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id}))
        post_one = Post.objects.latest('id')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post_one.text, form_data['text'])
        self.assertEqual(post_one.author, self.post_author)
        self.assertEqual(post_one.group_id, form_data['group'])

    def test_nonauthorized_user_create_post(self):
        """Проверка создания записи не авторизированным пользователем."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст поста',
                     'group': self.group.id, }
        response = self.guest_user.post(
            reverse('posts:post_create'),
            data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('login') + '?next=' + reverse('posts:post_create')
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)
