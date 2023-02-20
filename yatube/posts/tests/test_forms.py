from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_form_user',
        )
        cls.group = Group.objects.create(
            title='test_form_group',
            slug='test_form_slug',
            description='Test description of test_form_group',
            pk=1,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Text_form',
            group=cls.group,
            pk=1,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Проверка формы создания поста."""
        post_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                group=self.post.group,
            ).exists()
        )

    def test_post_edit(self):
        """Проверка формы редактирования поста."""
        self.post_count = Post.objects.count()
        self.text_edit = self.post.text + 'edit'
        form_edit_data = {
            'text': self.text_edit,
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_edit_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        self.assertEqual(Post.objects.count(), self.post_count)
        self.assertNotEqual(self.test_post_edit, self.post.text)
        self.assertTrue(
            Post.objects.filter(
                text=self.text_edit,
                group=self.group.pk,
            ).exists()
        )
