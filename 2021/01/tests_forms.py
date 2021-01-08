# posts/tests/test_forms.py
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group, User

# Constants for url reversing in tests
URL_NEW_POST = 'new_post'
URL_POST = 'post'
# Constants for url reversing in SetUp
URL_POST_EDIT = 'post_edit'


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_sport = Group.objects.create(
            title='Sport',
            slug='sport',
            description='Test Group with title Sport',
        )
        cls.group_algebra = Group.objects.create(
            title='Algebra',
            slug='algebra',
            description='Test Group with title Algebra',
        )
        cls.form = PostForm()

    def setUp(self):
        self.user_eugene = User.objects.create_user(username='Eugene')
        self.authorized = Client()
        self.authorized.force_login(self.user_eugene)
        self.post_first = Post.objects.create(
            text='Test post (first)',
            author=self.user_eugene,
            group=self.group_sport,
        )
        self.reverse_post_edit_eugene = reverse(
            URL_POST_EDIT,
            kwargs={
                'username': self.user_eugene.username,
                'post_id': self.post_first.id,
            }
        )

    def test_create_post(self):
        post_count = Post.objects.count()
        post_added_id = post_count + 1
        form_data = {
            'text': 'Test post (second)',
            'group': self.group_sport.id,
        }
        response = self.authorized.post(
            reverse(URL_NEW_POST),
            data=form_data,
            follow=True,
        )
        reverse_post = reverse(
            URL_POST,
            kwargs={
                'username': self.user_eugene.username,
                'post_id': post_added_id,
            }
        )
        post_added = self.authorized.get(reverse_post).context.get('post')
        self.assertEqual(Post.objects.count(), post_added_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            post_added.text,
            form_data['text'],
        )
        self.assertEqual(
            post_added.group,
            self.group_sport,
        )
        self.assertEqual(
            post_added.author,
            self.user_eugene,
        )
        self.assertTrue(
            Post.objects.filter(text=form_data['text'],
                                id=post_added_id).exists()
        )

    def test_edit_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Test post (first) edited',
            'group': self.group_algebra.id,
        }
        response = self.authorized.post(
            self.reverse_post_edit_eugene,
            data=form_data,
            follow=True,
        )
        response_get_page = self.authorized.get(response.redirect_chain[0][0])
        reverse_post = reverse(
            URL_POST,
            kwargs={
                'username': self.user_eugene.username,
                'post_id': response_get_page.context.get('post').id,
            }
        )
        post_changed = self.authorized.get(reverse_post).context.get('post')
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            post_changed.text,
            form_data['text'],
        )
        self.assertEqual(
            post_changed.group,
            self.group_algebra,
        )
        self.assertEqual(
            post_changed.author,
            self.user_eugene,
        )
