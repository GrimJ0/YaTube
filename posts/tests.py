from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Post, Group
from django.core.cache import cache
# Create your tests here.

class TextMix:
    def setUp(self):
        # создание тестового клиента — подходящая задача для функции setUp()
        self.client = Client()
        # создаём пользователя
        self.user = User.objects.create_user(
            username="sarah", email="connor.s@skynet.com", password="test"
        )
        # создаём пост от имени пользователя
        self.post = Post.objects.create(
            text="Hello",
            author=self.user)

        self.group = Group.objects.create(
            title="test_group",
            slug="test_slug",
            description="test_description"
        )


class TestStringMethods(TextMix, TestCase):

    def test_profile(self):
        response = self.client.get('/sarah/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page']), 1)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(response.context['author'].username, self.user.username)

    def test_user_new_post(self):
        self.client.login(username='sarah', password='test')
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_unidentified_user_new_post(self):
        self.client.logout()
        response = self.client.get('/new/')
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_add_post_home(self):
        response = self.client.get("/")
        self.assertEqual(len(response.context['page']), 1)

    def test_add_post_profile(self):
        response = self.client.get("/sarah/")
        self.assertEqual(len(response.context['page']), 1)

    def test_add_post_profile_view(self):
        response = self.client.get(f"/sarah/{self.post.id}/")
        self.assertEqual(response.status_code, 200)

    def test_cache_index(self):
        self.client.login(username='sarah', password='test')
        self.client.post(reverse('new_post'), data={
            'author': self.user,
            'text': 'test_cach',
        })
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, "test_cach", status_code=200)
        cache.clear()
        response = self.client.get(reverse('index'))
        self.assertContains(response, "test_cach", status_code=200)


class TestPostEditMethod(TextMix, TestCase):

    def test_unidentified_user_edit_post(self):
        self.client.logout()
        response = self.client.get(f"/sarah/{self.post.id}/edit/")
        self.assertRedirects(response, f"/auth/login/?next=/sarah/{self.post.id}/edit/")

    def test_authenticated_user_edit_post(self):
        new_text = "Hello, world!"
        self.client.login(username='sarah', password='test')
        response = self.client.get(f"/sarah/{self.post.id}/edit/")
        self.assertEqual(response.status_code, 200)
        self.client.post(f"/sarah/{self.post.id}/edit/", data={"text": new_text})
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, new_text)

        urls = ['/', '/sarah/', f'/sarah/{self.post.id}/']

        for url in urls:
            response = self.client.get(url)
            self.assertContains(response, new_text)


class TestPostLoadImage(TestCase):

    def setUp(self):
        # создание тестового клиента — подходящая задача для функции setUp()
        self.client = Client()
        # создаём пользователя
        self.user = User.objects.create_user(
            username="jon", email="connor.s@skynet.com", password="test"
        )
        # создаём пост от имени пользователя

        self.group = Group.objects.create(
            title="test_group",
            slug="test_slug",
            description="test_description"
        )
        cache.clear()
        self.client.login(username='jon', password='test')
        with open('media/posts/lt.jpg', 'rb') as img:
            self.client.post(reverse('new_post'), data={
                                                        'author': self.user,
                                                        'text': 'test_text',
                                                        'group': self.group.id,
                                                        'image': img
            })
        self.post = Post.objects.first()
    def test_img_in_text(self):
        response = self.client.get(reverse('index'))
        urls = (
            reverse('index'),
            reverse('post', kwargs={'username': self.user.username, 'post_id': self.post.id}),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('group', kwargs={'slug': self.group.slug})
        )
        for url in urls:
            response = self.client.get(url)
            self.assertContains(response, '<img', status_code=200)

    def test_load_txt(self):
        with open('media/posts/text_txt.txt', 'rb') as img:
            self.client.post(reverse('new_post'), data={
                                                        'author': self.user,
                                                        'text': 'test_2_text',
                                                        'group': self.group.id,
                                                        'image': img
            })
        self.post = Post.objects.first()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        cache.clear()
        self.assertEqual(len(response.context['page']), 1)
