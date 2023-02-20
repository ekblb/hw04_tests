from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_url_user',
        )
        cls.group = Group.objects.create(
            title='test_url_group',
            slug='test_url_slug',
            description='Test description of test_url_group',
            pk=1,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Text_url',
            pk=1,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location(self):
        """Доступность URL-адресов для неавторизованных пользователей."""
        ok_status_code: int = 200
        error_404_status_code: int = 404
        url_status_code_names = {
            '/': ok_status_code,
            f'/group/{self.group.slug}/': ok_status_code,
            f'/profile/{self.post.author.username}/': ok_status_code,
            f'/posts/{self.post.pk}/': ok_status_code,
            '/unexisting_page/': error_404_status_code,
        }
        for url, status_code in url_status_code_names.items():
            with self.subTest(url=url):
                responce = self.guest_client.get(url)
                self.assertEqual(responce.status_code, status_code)

    def test_urls_exists_at_desired_location_authorized(self):
        """Доступность URL-адресов для авторизованных пользователей."""
        ok_status_code: int = 200
        url_status_code_names = {
            f'/posts/{self.post.pk}/edit/': ok_status_code,
            '/create/': ok_status_code,
        }
        for url, status_code in url_status_code_names.items():
            with self.subTest(url=url):
                responce = self.authorized_client.get(url)
                self.assertEqual(responce.status_code, status_code)

    def test_urls_redirect_anonymous(self):
        """Редиректы для неавторизованных пользователей."""
        url1_url2_names = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.pk}/edit/':
            f'/auth/login/?next=/posts/{self.post.pk}/edit/',
        }
        for url1, url2 in url1_url2_names.items():
            with self.subTest(url=url1):
                responce = self.guest_client.get(url1, follow=True)
                self.assertRedirects(responce, url2)

    def test_urls_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        url_template_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author.username}/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }

        for url, template in url_template_names.items():
            with self.subTest(url=url):
                responce = self.authorized_client.get(url)
                self.assertTemplateUsed(responce, template)
