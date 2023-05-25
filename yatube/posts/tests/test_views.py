from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name1',
                                            email='test1@mail.ru',
                                            password='test_pass',),
            text='Тестовая запись для создания 1 поста',
            group=Group.objects.create(
                title='Заголовок для 1 тестовой группы',
                slug='test_slug1'))

        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name2',
                                            email='test2@mail.ru',
                                            password='test_pass',),
            text='Тестовая запись для создания 2 поста',
            group=Group.objects.create(
                title='Заголовок для 2 тестовой группы',
                slug='test_slug2'))

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='player')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/post_create.html': reverse('posts:post_create'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test_slug1'})
            ),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0,
                         'Тестовая запись для создания 2 поста')
        self.assertEqual(post_author_0, 'test_name2')
        self.assertEqual(post_group_0, 'Заголовок для 2 тестовой группы')

    def test_group_pages_show_correct_context(self):
        """Шаблон группы"""
        response = self.authorized_client.get(reverse
                                              ('posts:group_list',
                                               kwargs={'slug': 'test_slug2'}))
        first_object = response.context["group"]
        group_title_0 = first_object.title
        group_slug_0 = first_object.slug
        self.assertEqual(group_title_0, 'Заголовок для 2 тестовой группы')
        self.assertEqual(group_slug_0, 'test_slug2')

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug1'}))
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        self.assertTrue(post_text_0, 'Тестовая запись для создания 2 поста')

    def test_new_post_show_correct_context(self):
        """Шаблон сформирован с верным отображением контекста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'test_name2'}))
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        self.assertEqual(response.context['author'].username, 'test_name2')
        self.assertEqual(post_text_0, 'Тестовая запись для создания 2 поста')

    def test_post_detail_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['author'], self.post.author)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_name',
                                              email='test@mail.ru',
                                              password='test_pass',)
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug2',
            description='Тестовое описание')
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='mob2556')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        list_urls = {
            reverse("posts:index"): "index",
            reverse("posts:group_list", kwargs={
                    "slug": "test_slug2"}): "group",
            reverse("posts:profile", kwargs={
                    "username": "test_name"}): "profile",
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len(response.context.get
                                 ('page_obj').object_list), 10)

    def test_second_page_contains_three_posts(self):
        list_urls = {
            reverse("posts:index") + "?page=2": "index",
            reverse("posts:group_list", kwargs={
                    "slug": "test_slug2"}) + "?page=2": "group",
            reverse("posts:profile", kwargs={
                    "username": "test_name"}) + "?page=2": "profile",
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len(response.context.get
                                 ('page_obj').object_list), 3)
