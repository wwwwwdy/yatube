from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_text = Post.objects.create(
            text='Тестовый текст более чем пятнадцать символов!!!',
            author=User.objects.create_user(username='user1')
        )

    def test_long_text(self):
        expected_object_name = PostModelTest.post_text.text[:15]
        self.assertEqual(expected_object_name, str(PostModelTest.post_text))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок'
        )

    def test_title(self):
        object_name = GroupModelTest.group.title
        self.assertEqual(object_name, str(GroupModelTest.group))
