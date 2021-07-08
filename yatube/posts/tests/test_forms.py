import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.author = User.objects.create_user(username='testuser')
        cls.group = Group.objects.create(
            title='label',
            slug='test-slug',
            description='labels description for testing urls'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
            pub_date='28.06.2021',
            image=SimpleUploadedFile(
                name='test_image.gif',
                content=cls.small_gif,
                content_type='image/gif')
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='Тест комментариев',
            created='08.07.2021'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_post_create(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': PostFormTest.post.text,
            'group': PostFormTest.group.id,
            'image': PostFormTest.post.image
        }
        self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text=PostFormTest.post.text,
            group=PostFormTest.group.id,
            id=PostFormTest.post.id,
            image=PostFormTest.post.image
        ).exists()
        )

    def test_post_edit(self):
        text_edit = 'Отредактированный текст'
        posts_count = Post.objects.count()
        form_data = {
            'text': text_edit,
            'group': PostFormTest.group.id,
        }
        self.authorized_client.post(
            reverse('post_edit',
                    kwargs={'username': PostFormTest.author.username,
                            'post_id': PostFormTest.post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(Post.objects.filter(
            text=text_edit,
            group=PostFormTest.group.id,
            id=PostFormTest.post.id
        ).exists())
        self.assertEqual(Post.objects.count(), posts_count)

    def test_comment(self):
        comment = 'Комментарий'
        comments_count = Comment.objects.count()
        form_data = {
            'text': comment
        }
        self.authorized_client.post(reverse(
            'add_comment',
            kwargs={
                'username': PostFormTest.author.username,
                'post_id': PostFormTest.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
