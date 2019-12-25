# Create your views here.
import hashlib
import datetime

from django.conf import settings
from django.shortcuts import render, redirect
from login import models
from . import forms
#密码加盐
def hash_code(s,salt='管理项目'):#加盐
    h=hashlib.sha256()
    s+=salt
    h.update(s.encode())
    return h.hexdigest()
#邮箱确认时间
def make_confirm_string(user):
    now=datetime.datetime.now().strftime('%Y:%m:%d %H:%M:%S')
    code=hash_code(user.name,now)
    models.ConfirmString.objects.create(code=code,user=user)
    return code

#发送邮件
def send_email(email,code):
    from django.core.mail import EmailMultiAlternatives

    subject = '注册确认邮件'

    text_content = '''感谢注册'''

    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.baidu.com</a>，\
                    </p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def index(request):
    if not request.session.get('is_login',None):
        return redirect('/login/')
    return render(request, '../templates/login/index.html')

# def login(request):
#     """
#     为了能够提示用户信息，需要在login前端界面进行模板渲染
#     :param request:
#     :return:
#     """
#
#     if request.method=='POST':
#         username=request.POST.get('username')
#         password=request.POST.get('password')
#         message='请检查输入的内容：'
#         #判断用户名和密码是否为空
#         if username.strip() and password:
#             try:
#                 #判断用户名和密码是否在数据库里面
#                 user=models.User.objects.get(user=username)
#             except:
#                 message='用户不存在'
#                 #提示用户用户不存在
#                 return render(request,'login/login.html',{'message':message})
#             if user.password==password:
#                 return redirect('/index/')
#             else:
#                 message='密码错误'
#                 return render(request,'login/login.html',{'message':message})
#         else:
#             return render(request,'login/login.html',{'message':message})
#     return render(request,'login/login.html')

def login(request):
    """
    使用表单进行验证
    :param request:
    :return:
    """
    if request.session.get('is_login',None):#从session中取值，看用户是否重复登录
        return redirect('/index/')
    if request.method=='POST':
        login_form=forms.UserForm(request.POST)
        message='请检查输入的内容:'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            try:
                #从数据库验证
                user=models.User.objects.get(name=username)
            except:
                message='用户不存在'
                return render(request, '../templates/login/login.html', locals())
            if not user.has_confirmed:
                message='该用户还未经过验证'
                return render(request,'login/login.html',locals())
            if user.password==hash_code(password):
                request.session['is_login']=True
                request.session['user_id']=user.id
                request.session['user_name']=user.name
                return redirect('/index/')
            else:
                message='密码错误'
                return render(request, '../templates/login/login.html', locals())
        else:
            return render(request, '../templates/login/login.html', locals())
    login_form=forms.UserForm()
    return render(request, '../templates/login/login.html', locals())


def register(request):
    if request.session.get('is_login',None):#用户名已存在，重定向到登录界面
        return redirect('/index/')
    if request.method=='POST':
        #提交注册请求
        register_form=forms.RegisterForm(request.POST)
        message='请检查输入的内容'
        if register_form.is_valid():
            username=register_form.cleaned_data.get('username')
            password1=register_form.cleaned_data.get('password1')
            password2=register_form.cleaned_data.get('password2')
            email=register_form.cleaned_data.get('email')
            sex=register_form.cleaned_data.get('sex')
            if password1!=password2:
                message='两次输入的密码不同'
                return render(request, '../templates/login/register.html', locals())
            else:
                same_name_user=models.User.objects.filter(name=username)
                if same_name_user:
                    message='用户名已经存在'
                    return render(request, '../templates/login/register.html', locals())
                same_email_user=models.User.objects.filter(email=email)
                if same_email_user:
                    message='该邮箱已被注册'
                    return render(request, '../templates/login/register.html', locals())
                new_user=models.User()
                new_user.name=username
                new_user.password=hash_code(password1)
                new_user.email=email
                new_user.sex=sex
                new_user.save()

                code=make_confirm_string(new_user)
                send_email(email,code)
                return redirect('login')
        else:
            return render(request, '../templates/login/register.html', locals())
    register_form=forms.RegisterForm()
    return render(request, '../templates/login/register.html', locals())

def logout(request):
    if not request.session.get('is_login',None):#如果session中没有数据
        return redirect('/login/')
    request.session.flush()
    return render(request, '../templates/login/logout.html')

def user_confirm(request):
    code=request.GET.get('code',None)
    message=''
    try:
        confirm=models.ConfirmString.objects.get(code=code)
    except:
        message='无效的确认请求'
        return render(request,'login/confirm.html',locals())
    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'login/confirm.html', locals())