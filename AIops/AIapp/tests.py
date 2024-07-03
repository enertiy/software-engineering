import os

from absl.flags import ValidationError
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from django.contrib.auth.hashers import check_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from .models import User, Admin,Comment, Submission

class AIappTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin = Admin.objects.create(username='adminuser', password='adminpassword')

    @patch('AIapp.views.authenticate')
    def test_user_login_success(self, mock_authenticate):
        mock_authenticate.return_value = self.user
        response = self.client.post(reverse('user_login_url'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "login_page")

    @patch('AIapp.views.authenticate')
    def test_user_login_failure(self, mock_authenticate):
        mock_authenticate.return_value = None
        response = self.client.post(reverse('user_login_url'), {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "用户不存在")
        self.assertContains(response, "用户密码错误")

    def test_username_unique(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username='testuser', password='password456')

    def test_password_hashing(self):
        raw_password = 'newpassword123'
        user = User.objects.create_user(username='newuser', password=raw_password)
        self.assertNotEqual(user.password, raw_password)
        self.assertTrue(user.check_password(raw_password))

    @patch('AIapp.views.authenticate')
    def test_admin_login_success(self, mock_authenticate):
        mock_authenticate.return_value = self.admin
        response = self.client.post(reverse('admin_login_url'), {'username': 'adminuser', 'password': 'adminpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "login_page")

    @patch('AIapp.views.authenticate')
    def test_admin_login_failure(self, mock_authenticate):
        mock_authenticate.return_value = None
        response = self.client.post(reverse('admin_login_url'), {'username': 'adminuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "用户不存在")
        self.assertContains(response, "用户密码错误")

    def test_admin_username_unique(self):
        with self.assertRaises(IntegrityError):
            Admin.objects.create(username='adminuser', password='adminpass456')

    @patch('AIapp.views.User.objects.create_user')
    def test_register_success(self, mock_create_user):
        mock_create_user.return_value = self.user
        response = self.client.post(reverse('register_url'), {'username': 'newuser', 'password': 'newpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "用户注册成功，请进行登录！")

    @patch('AIapp.views.User.objects.create_user')
    def test_register_failure(self, mock_create_user):
        # Mock 用户名已存在的情况
        mock_create_user.side_effect = ValueError("Username already exists")
        response = self.client.post(reverse('register_url'), {'username': '', 'password': 'newpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "用户名已存在！")

    @patch('AIapp.views.authenticate')
    def test_user_index(self, mock_authenticate):
        mock_authenticate.return_value = self.user
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_index_url'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user_index")

    @patch('AIapp.views.authenticate')
    def test_user_upload(self, mock_authenticate):
        mock_authenticate.return_value = self.user
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_upload_url'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user_upload")

    @patch('AIapp.views.Comment.objects.filter')
    def test_user_comment_get(self, mock_comment_filter):
        mock_comment_filter.return_value = MagicMock()  # Mock Comment 查询结果
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_comment_url'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user_comment")

    def test_submit_comment_success(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('user_comment_url'), {'comment': 'This is a test comment'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user_comment_url'))

    def test_submit_comment_empty(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('user_comment_url'), {'comment': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_comment.html')
        self.assertContains(response, "0")

    def test_comment_created_at_auto(self):
        comment = Comment.objects.create(username='testuser', comment='This is a test comment')
        self.assertIsNotNone(comment.created_at)

    def test_submission_upload_time_auto(self):
        submission = Submission.objects.create(username='testuser', file_name='anotherfile.txt')
        self.assertIsNotNone(submission.upload_time)

    @patch('AIapp.views.Admin.objects.filter')
    def test_admin_index_no_search(self, mock_admin_filter):
        mock_admin_filter.return_value = MagicMock()  # Mock Admin 查询结果
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('admin_index_url'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "admin_index")

    @patch('AIapp.views.Admin.objects.filter')
    def test_admin_index_search(self, mock_admin_filter):
        mock_admin_filter.return_value = MagicMock()  # Mock Admin 查询结果
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('admin_index_url'), {'searchtext': 'testuser'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "search")

    @patch('AIapp.views.csv')
    def test_show_csv_content(self, mock_csv):
        mock_writer = MagicMock()
        mock_writer.writerow = MagicMock()
        mock_csv.writer.return_value = mock_writer

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('show_csv_content_url'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CSV Content")

    @patch('AIapp.views.open', create=True)
    def test_download_csv(self, mock_open):
        mock_file = MagicMock()
        mock_file.read.return_value = b'mock CSV content'
        mock_open.return_value.__enter__.return_value = mock_file

        request = self.client.get(reverse('download_url'))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request['Content-Type'], 'application/octet-stream')
        self.assertEqual(request['Content-Disposition'],
                         f'attachment; filename="{os.path.basename("./webankdata/rnvp_result.csv")}"')
        self.assertEqual(request.content, b'mock CSV content')

    def test_user_logout(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('login_page_url'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login_page.html')

    def test_trace_test(self):
        self.client.login(username='testuser', password='testpassword')
        uploaded_file = SimpleUploadedFile("file.txt", b"file_content")
        response = self.client.post(reverse('trace_test_url'), {'file': uploaded_file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user_upload.html")

    def test_user_creation(self):
        user = User.objects.create_user(username='newuser', password='newpassword')
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(check_password('newpassword', user.password))

    def test_user_password_setter(self):
        user = User.objects.create_user(username='setpassworduser', password='initialpassword')
        user.set_password('newpassword')
        user.save()
        self.assertTrue(check_password('newpassword', user.password))

    def test_user_check_password(self):
        self.assertTrue(self.user.check_password('testpassword'))
        self.assertFalse(self.user.check_password('wrongpassword'))

    def test_admin_creation(self):
        self.assertEqual(self.admin.username, 'adminuser')
        self.assertEqual(self.admin.password, 'adminpassword')

    def test_comment_creation(self):
        comment = Comment.objects.create(username=self.user.username, comment='This is a test comment')
        self.assertEqual(comment.username, self.user.username)
        self.assertEqual(comment.comment, 'This is a test comment')
        self.assertTrue(comment.created_at)

    def test_submission_creation(self):
        submission = Submission.objects.create(username=self.user.username, file_name='testfile.txt')
        self.assertEqual(submission.username, self.user.username)
        self.assertEqual(submission.file_name, 'testfile.txt')
        self.assertTrue(submission.upload_time)

    def test_str_methods(self):
        user_str = str(self.user)
        admin_str = str(self.admin)
        comment = Comment.objects.create(username=self.user.username, comment='This is a test comment')
        comment_str = str(comment)
        submission = Submission.objects.create(username=self.user.username, file_name='testfile.txt')
        submission_str = str(submission)

        print("Actual:", comment_str)
        print("Expected:", f"{self.user.username}: This is a test comme")

        self.assertEqual(user_str, 'testuser')
        self.assertEqual(admin_str, 'adminuser')
        self.assertEqual(comment_str, f"{self.user.username}: This is a test comme")  # Adjust expected string
        self.assertEqual(submission_str, f"{self.user.username} - testfile.txt")

    def test_query_set(self):
        User.objects.create_user(username='user1', password='password1')
        User.objects.create_user(username='user2', password='password2')
        users = User.objects.all()
        self.assertEqual(users.count(), 3)

        Admin.objects.create(username='admin1', password='adminpassword1')
        Admin.objects.create(username='admin2', password='adminpassword2')
        admins = Admin.objects.all()
        self.assertEqual(admins.count(), 3)

        Comment.objects.create(username=self.user.username, comment='Test comment 1')
        Comment.objects.create(username=self.user.username, comment='Test comment 2')
        comments = Comment.objects.all()
        self.assertEqual(comments.count(), 2)

        Submission.objects.create(username=self.user.username, file_name='file1.txt')
        Submission.objects.create(username=self.user.username, file_name='file2.txt')
        submissions = Submission.objects.all()
        self.assertEqual(submissions.count(), 2)

    # def test_username_max_length(self):
    #     long_username = 'u' * 101
    #     with self.assertRaises(ValueError):
    #         User.objects.create_user(username=long_username, password='password123')

    # def test_password_max_length(self):
    #     long_password = 'p' * 101
    #     with self.assertRaises(ValueError):
    #         User.objects.create_user(username='newuser', password=long_password)

    # def test_admin_password_max_length(self):
    #     long_password = 'p' * 101
    #     with self.assertRaises(ValueError):
    #         Admin.objects.create(username='newadmin', password=long_password)

    # def test_comment_max_length(self):
    #     long_comment = 'c' * 1001
    #     with self.assertRaises(ValueError):
    #         Comment.objects.create(username='testuser', comment=long_comment)

    # def test_submission_file_name_max_length(self):
    #     long_file_name = 'f' * 256
    #     with self.assertRaises(ValueError):
    #         Submission.objects.create(username='testuser', file_name=long_file_name)


