import os

from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .models import User, Admin

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
