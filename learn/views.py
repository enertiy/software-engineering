from django.shortcuts import render
from django.http import HttpResponse
# from django.db import connection


# Create your views here.
def login(request,methods=['GET','POST']):
    # id = request.POST.get('id')
    # password = request.POST.get('password')
    # if id and password:
    #     with connection.cursor() as cursor:
    #         cursor.execute("SELECT password FROM login WHERE id = %s", [id])
    #         result=cursor.fetchall()
    #         if result==():
    #             return render(request,'login_page.html')
    #         else:
    #             if password == result[0][0]:
    #                 return HttpResponse('登录成功！')
    #             else:
    #                 return render(request,'login_page.html')
    # else:
    return render(request,'login_page.html')


# def register(request,methods=['GET','POST']):
#     id=request.POST.get('id')
#     password=request.POST.get('password')
#     isregister=''
#     if id and password:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT id FROM login WHERE id = %s", [id])
#             result=cursor.fetchall()
#             if result==(): #创建用户
#                 cursor.execute("insert into login values(%s,%s)",(id,password))
#                 isregister="恭喜你，注册成功"
#                 return render(request,'register_page.html',{'isregisters':isregister})
#             else: #已有用户
#                 isregister='用户已存在，注册失败'
#                 return render(request,'register_page.html',{'isregisters':isregister})
#
#     return render(request,'register_page.html',{'isregisters':isregister})

