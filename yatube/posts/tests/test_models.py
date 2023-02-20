from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_mod_user',
        )
        cls.group = Group.objects.create(
            title='test_mod_group',
            slug='test_mod_slug',
            description='Test description of test_mod_group',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Text_mod',
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Корректная работа __str__ у моделей."""
        post = PostModelTest.post
        group = PostModelTest.group
        str_post = post.__str__()
        str_group = group.__str__()
        self.assertEqual(str_post, self.post.text)
        self.assertEqual(str_group, self.post.group.title)
