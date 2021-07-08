from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Anton')
        cls.group = Group.objects.create(
            title='label',
            slug='test-slug',
            description='labels description for testing urls'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
            pub_date='28.06.2021',
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.user = User.objects.create_user(username='AndreyG')
        cls.authorized_client1 = Client()
        cls.authorized_client1.force_login(cls.user)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_grouppage(self):
        response = self.guest_client.get(f'/group/{PostURLTests.group.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_authorized_new_post(self):
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_username_profile(self):
        response = self.guest_client.get(f'/{PostURLTests.author.username}/')
        self.assertEqual(response.status_code, 200)

    def test_username_post(self):
        response = self.guest_client.get(
            f'/{PostURLTests.author.username}/{PostURLTests.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_username_post_edit_anonymous(self):
        response = self.guest_client.get(
            f'/{PostURLTests.author.username}/{PostURLTests.post.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_username_post_edit_authorized_author(self):
        response = self.authorized_client.get(
            f'/{PostURLTests.author.username}/{PostURLTests.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_username_post_edit_authorized_user(self):
        response = self.authorized_client1.get(
            f'/{PostURLTests.author.username}/{PostURLTests.post.id}/edit',
            follow=True)
        self.assertRedirects(
            response,
            f'/{PostURLTests.author.username}/{PostURLTests.post.id}/',
            status_code=301)

    def test_templates(self):
        cache.clear()
        templates_url_names = {
            '/': 'index.html',
            f'/group/{PostURLTests.group.slug}/': 'group.html',
            '/new/': 'new_post.html',
            f'/{PostURLTests.author}/{PostURLTests.post.id}/edit/':
            'new_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        response = self.authorized_client.get('/404/')
        self.assertEqual(response.status_code, 404)

    def test_page_500(self):
        response = self.authorized_client.get('/500/')
        self.assertEqual(response.status_code, 404)

    def test_authorized_user_following(self):
        response = self.authorized_client1.get(
            f'/{PostURLTests.author.username}/follow/')
        self.assertRedirects(response, '/')

    def test_authorized_user_unfollowing(self):
        response = self.authorized_client1.get(
            f'/{PostURLTests.author.username}/unfollow/')
        self.assertRedirects(response, '/')
