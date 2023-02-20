from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


from ..models import Group, Post

number_posts: int = settings.NUMBER_OF_POST + 3
User = get_user_model()


class PostPageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_page_user',
        )
        cls.group = Group.objects.create(
            title='test_page_group',
            slug='test_page_slug',
            description='Test description of test_page_group',
            pk=1,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Text_page',
            group=cls.group,
            pk=1,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_templates = {
            reverse('posts:index'): 'posts/index.html',
            (
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ): 'posts/group_list.html',
            (
                reverse('posts:profile', kwargs={
                    'username': self.user.username})
            ): 'posts/profile.html',
            (
                reverse('posts:post_detail', kwargs={
                    'post_id': self.post.pk})
            ): 'posts/post_detail.html',
            (
                reverse('posts:post_edit', kwargs={
                    'post_id': f'{self.post.pk}'})
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for page, template in pages_templates.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post_object = response.context['page_obj'][0]
        post_text_0 = post_object.text
        post_author_0 = post_object.author.username
        post_group_0 = post_object.group.title
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_group_0, self.group.title)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug})
        )
        post_object = response.context['page_obj'][0]
        post_group = response.context['group'].slug
        post_text_0 = post_object.text
        post_author_0 = post_object.author.username
        post_group_0 = post_object.group.title
        self.assertEqual(post_group, self.group.slug)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_group_0, post_object.group.title)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:profile', kwargs={
            'username': self.user.username})
        )
        post_object = response.context['page_obj'][0]
        post_author = response.context['author'].username
        post_text_0 = post_object.text
        post_author_0 = post_object.author.username
        post_group_0 = post_object.group.title
        self.assertEqual(post_author, self.user.username)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_group_0, post_object.group.title)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        post = response.context['post']
        post_text_0 = post.text
        post_author_0 = post.author.username
        post_group_0 = post.group.title
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_group_0, post.group.title)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(
            username='test_paginator_username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='test_paginator_group',
                                          slug='test_paginator_slug')
        bilk_post: list = []
        for i in range(number_posts):
            bilk_post.append(Post(text=f'test_text{i}',
                                  group=self.group,
                                  author=self.user))
        Post.objects.bulk_create(bilk_post)

    def test_paginator_for_first_second_page(self):
        '''Проверка количества постов на первой и второй страницах. '''
        pages: tuple = (reverse('posts:index'),
                        reverse('posts:profile',
                                kwargs={'username': f'{self.user.username}'}),
                        reverse('posts:group_list',
                                kwargs={'slug': f'{self.group.slug}'}))
        for page in pages:
            response_page_1 = self.guest_client.get(page)
            response_page_2 = self.guest_client.get(page + '?page=2')
            self.assertEqual(len(response_page_1.context['page_obj']),
                             10)
            self.assertEqual(len(response_page_2.context['page_obj']), 3)

    def test_post_create_correctly_for_index_group_profile(self):
        """Пост при создании добавлен на главную,
        на страницу группы, в профайл"""
        post = Post.objects.create(
            text='text_post',
            author=self.user,
            group=self.group)
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index)
        self.assertIn(post, group)
        self.assertIn(post, profile)

    def test_post_added_correctly_user2(self):
        """Пост при создании не добавляется в другую группу"""
        other_group = Group.objects.create(
            title='text_group_title', slug='test_group_slug')
        posts_count_group_1 = Post.objects.filter(group=self.group).count()
        Post.objects.create(
            text='Тестовый пост от другого автора',
            author=self.user,
            group=other_group)
        posts_count_group_2 = Post.objects.filter(group=self.group).count()
        self.assertEqual(posts_count_group_2, posts_count_group_1)
