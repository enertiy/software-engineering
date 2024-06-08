from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt

cursor=connection.cursor()

@csrf_exempt
def login(request,methods=['GET','POST']):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if id and password:
        cursor.execute("SELECT password FROM aiapp_user WHERE username = %s", [username])
        result=cursor.fetchall()
        # 没有对应结果
        if result==():
            return render(request,'login_page.html',{'issignal':'1'})
        else:
            # 判断密码是否正确
            if password == result[0][0]:
                return HttpResponse('登录成功！')
            else:
                return render(request,'login_page.html',{'issignal':'2'})
    else:
        return render(request,'login_page.html',{'issignal':'0'})

@csrf_exempt
def register(request,methods=['GET','POST']):
    username=request.POST.get('username')
    password=request.POST.get('password')
    if id and password:
        try:
            cursor.execute("insert into aiapp_user(username,password) values(%s,%s)",(username,password))
            connection.commit()
            return render(request, 'register_page.html', {'isregisters': '1'})
        except:
            return render(request, 'register_page.html', {'isregisters': '2'})
    else:
        return render(request,'register_page.html',{'isregisters':'0'})


