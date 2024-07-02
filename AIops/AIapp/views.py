import os

from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
import subprocess
import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
import subprocess
import csv
from django.contrib.auth.models import User
from .models import *
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.urls import reverse
import datetime
from django.contrib.auth import authenticate, login

cursor = connection.cursor()


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # 用户已登录，重定向到首页或其他页面
                return render(request, 'user_index.html')
            else:
                # 返回一个 '账户未激活' 的消息
                return render(request, 'login_page.html', {'issignal': '2'})
        else:
            # 如果用户名或密码为空，返回一个错误消息
            return render(request, 'login_page.html', {'issignal': '1'})
    else:
        # 如果不是POST请求，显示登录页面
        return render(request, 'login_page.html')


# def admin_login(request, methods=['GET', 'POST']):
#     username = request.POST.get('username')
#     password = request.POST.get('password')
#     if id and password:
#         cursor.execute("SELECT password FROM aiapp_admin WHERE username = %s", [username])
#         result = cursor.fetchall()
#         # 没有对应结果
#         if result is None:
#             return render(request, 'login_page.html', {'issignal': '1'})
#         else:
#             # 判断密码是否正确
#             if password == result[0]:
#                 # return HttpResponse('登录成功！')
#                 submissions = Submission.objects.order_by('-upload_time')
#                 return render(request, 'admin_index.html', {'submissions': submissions.order_by('-upload_time')})
#                 #return render(request, 'admin_index.html',{'submissions':Submission.objects.order_by('-upload_time')})
#             else:
#                 return render(request, 'login_page.html', {'issignal': '2'})
#     else:
#         return render(request, 'login_page.html', {'issignal': '0'})

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            with connection.cursor() as cursor:
                cursor.execute("SELECT password FROM aiapp_admin WHERE username = %s", [username])
                result = cursor.fetchone()  # 获取单条记录
                # 没有对应结果
                if result is None:
                    return render(request, 'login_page.html', {'issignal': '1'})
                else:
                    # 判断密码是否正确
                    if password == result[0]:  # 明文比较
                        submissions = Submission.objects.order_by('-upload_time')
                        return render(request, 'admin_index.html', {'submissions': submissions})
                    else:
                        return render(request, 'login_page.html', {'issignal': '2'})
        else:
            return render(request, 'login_page.html', {'issignal': '0'})
    else:
        return render(request, 'login_page.html')


@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            try:
                # 创建一个新用户实例，但还未保存到数据库
                # user = User(username=username)
                user = User.objects.create_user(username=username, password=password)
                # 使用set_password方法来设置密码，这会为密码进行哈希处理
                user.set_password(password)
                # 保存用户到数据库
                user.save()
                return render(request, 'register_page.html', {'isregisters': '1'})
            except Exception as e:  # 捕获具体的异常
                print(e)  # 打印异常信息或使用logging模块记录日志
                return render(request, 'register_page.html', {'isregisters': '2'})
        else:
            return render(request, 'register_page.html', {'isregisters': '0'})
    else:
        # 如果不是POST请求，则显示注册页面
        return render(request, 'register_page.html')


def user_index(request):
    return render(request, 'user_index.html')


def user_upload(request):
    return render(request, 'user_upload.html')


def user_comment(request):
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        if comment_text:
            try:
                # 使用 Django ORM 来创建评论对象并保存到数据库
                comment = Comment(username=request.user.username, comment=comment_text, created_at=timezone.now())
                comment.save()
                return redirect('user_comment.html', {'isCommentPosted': '1'})
                # return render(request, 'user_comment.html', {'isCommentPosted': '1'})
            except Exception as e:
                # 如果保存失败，返回错误信息
                return render(request, 'user_comment.html', {'isCommentPosted': '2', 'error': str(e)})
        else:
            # 如果评论为空，返回错误信息
            return render(request, 'user_comment.html', {'isCommentPosted': '0', 'error': 'Comment cannot be empty'})
    else:
        # 如果不是POST请求，直接渲染评论页面
        return render(request, 'user_comment.html', {
            'comments': Comment.objects.order_by('-created_at')
        })


def admin_index(request):
    query = request.GET.get('searchtext')
    print(query)
    if query:
        results = Submission.objects.filter(username__icontains=query)
        return render(request, 'admin_index.html', {'submissions': results})
    else:
        results = Submission.objects.all()
        return render(request, 'admin_index.html', {'submissions': Submission.objects.order_by('-upload_time')})


def login_page(request):
    return render(request, 'login_page.html')


@csrf_exempt
def trace_test(request):
    try:
        uploaded_file = request.FILES['file']
        Submission.objects.create(username=request.user.username, file_name=uploaded_file.name,
                                  upload_time=timezone.now())
        print(uploaded_file)
        with open('static' + uploaded_file.name, 'wb+') as destination:
            # 逐块写入上传的文件内容
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        # save_path_1 = 'TraceAnomaly/train_ticket/test_abnormal_small'

        # save_path_2 = 'TraceAnomaly/train_ticket/test_normal_small'

        save_path_1 = './TraceAnomaly/train_ticket/test_abnormal_small'
        save_path_2 = './TraceAnomaly/train_ticket/test_normal_small'
        with open('static' + uploaded_file.name, 'rb') as source_file:
            file_content = source_file.readlines()
        # 将文件内容一分为二
        half_len = len(file_content) // 2
        file_content_1 = file_content[:half_len]
        file_content_2 = file_content[half_len:]

        # 将一半内容写入第一个目标文件
        with open(save_path_1, 'wb+') as destination_1:
            for line in file_content_1:
                destination_1.write(line)

        # 将另一半内容写入第二个目标文件
        with open(save_path_2, 'wb+') as destination_2:
            for line in file_content_2:
                destination_2.write(line)
    except:
        print('NO file')
    return render(request, 'user_upload.html')


def show_csv_content(request):
    print('正在测试中————————————————————————————')
    cmd = 'conda activate traceanomaly && python -m TraceAnomaly.traceanomaly.main'
    # 执行命令
    result = subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # 输出运行结果
    print("Output:", result.stdout.decode())
    csv_filename = './webankdata/rnvp_result.csv'
    # csv_filename = 'F:/software engineer/大作业/software-engineering/AIops/webankdata/rnvp_result.csv'

    # 打开 CSV 文件并读取数据
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        data = list(csv_reader)
    print('完成测试——————————————————————————')
    # 将数据传递给模板
    return render(request, 'show_csv_content.html', {'csv_data': data})


def download_csv(request):
    filename = "./webankdata/rnvp_result.csv"
    # 打开文件并读取内容
    with open(filename, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
        return response

    return render(request, 'user_upload.html')