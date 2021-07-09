import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.author = User.objects.create_user(username='anton')
        cls.user = User.objects.create_user(username='testuser')
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
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client1 = Client()
        cls.authorized_client.force_login(cls.author)
        cls.authorized_client1.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def check_post_context(self, context):
        if context.get('post'):
            post = context['post']
        else:
            post = context['page'][0]
        self.assertEqual(post.text, PostViewsTests.post.text)
        self.assertEqual(post.author, PostViewsTests.post.author)
        self.assertEqual(post.group, PostViewsTests.post.group)
        self.assertEqual(post.image, PostViewsTests.post.image)

    def test_cache_index_page(self):
        cache.clear()
        post = Post.objects.create(
            author=PostViewsTests.author,
            group=PostViewsTests.group,
            text='Cache',
            pub_date='07.07.2021',
        )
        response = self.authorized_client.get(reverse('index'))
        cache_content = response.context['page'][0].text
        self.assertEqual(cache_content, post.text)
        post.delete()
        response1 = self.authorized_client.get(reverse('index'))
        self.assertEqual(response1.context, None)
        cache.clear()
        response2 = self.authorized_client.get(reverse('index'))
        cache_content2 = response2.context['page'][0].text
        self.assertNotEqual(cache_content2, None)
        self.assertEqual(cache_content2, PostViewsTests.post.text)

    def test_follow_index(self):
        cache.clear()
        self.authorized_client1.get(reverse('profile_follow', kwargs={
            'username': self.author.username}))
        response = self.authorized_client1.get(reverse('follow_index'))
        obj = response.context['page'][0]
        self.assertEqual(obj, PostViewsTests.post)

    def test_unfollow_index(self):
        cache.clear()
        self.authorized_client1.get(reverse('profile_unfollow', kwargs={
            'username': self.author.username}))
        response = self.authorized_client1.get(reverse('follow_index'))
        obj = response.context['page']
        self.assertNotEqual(obj, PostViewsTests.post)

    def test_pages_use_correct_template(self):
        cache.clear()
        templates_pages_names = {
            reverse('index'): 'index.html',
            reverse(
                'group',
                kwargs={'slug': PostViewsTests.group.slug}): 'group.html',
            reverse('new_post'): 'new_post.html',
            reverse('post_edit',
                    kwargs={'username': PostViewsTests.author,
                            'post_id': PostViewsTests.post.id}):
            'new_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_shows_correct_context(self):
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        self.check_post_context(response.context)

    def test_group_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': PostViewsTests.group.slug}))
        self.assertEqual(
            response.context['group'].title, PostViewsTests.group.title)
        self.assertEqual(
            response.context['group'].slug, PostViewsTests.group.slug)
        self.assertEqual(response.context['group'].description,
                         PostViewsTests.group.description)

    def test_new_edit_post_page_shows_correct_context(self):
        response = self.authorized_client.post(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile',
                    kwargs={'username': PostViewsTests.author.username}))
        self.check_post_context(response.context)

    def test_post_with_group_on_home_page(self):
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        self.check_post_context(response.context)

    def test_post_with_group_on_group_page(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': PostViewsTests.group.slug}))
        self.check_post_context(response.context)

    def test_post_id_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'post',
                kwargs={'username': PostViewsTests.author.username,
                        'post_id': PostViewsTests.post.id}))
        self.check_post_context(response.context)


class PaginatorViewTest(TestCase):
    @ classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.group = Group.objects.create(
            title='label',
            slug='test-slug',
            description='labels description for testing paginator'
        )
        for i in range(13):
            cls.post = Post.objects.create(
                text=f'{i} тестовый текст',
                author=cls.user,
                group=cls.group,
            )
        cls.client = Client()

    def test_paginator_first_page_contains_ten_records(self):
        cache.clear()
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_paginator_second_page_contains_three_records(self):
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_paginator_group_page_contains_ten_records(self):
        response = self.client.get(reverse(
            'group', kwargs={'slug': f'{PaginatorViewTest.group.slug}'}))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_paginator_second_group_page_contains_three_records(self):
        response = self.client.get(reverse(
            'group',
            kwargs={'slug': f'{PaginatorViewTest.group.slug}'}) + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_paginator_profile_page_contains_ten_records(self):
        response = self.client.get(reverse(
            'profile',
            kwargs={'username': f'{PaginatorViewTest.user.username}'}))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_paginator_second_profile_page_contains_three_records(self):
        response = self.client.get(reverse(
            'profile',
            kwargs={
                'username': f'{PaginatorViewTest.user.username}'
            }) + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)


class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(title='TestGroup',
                                         slug='test_slug',
                                         description='Test description')
        cls.follow_user = User.objects.create_user(username='TestAuthor')
        cls.post = Post.objects.create(
            author=cls.follow_user,
            group=cls.group,
            text='Тестовый текст',
            pub_date='28.06.2021',
        )

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.follow_user)
