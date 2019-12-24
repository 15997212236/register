import os

from django.core.mail import send_mail

os.environ['DJANGO_SETTINGS_MODULE']='管理项目.settings'

if __name__ == '__main__':
    send_mail(
        '这里是主题',
        '这是具体内容',
        'weiweicat@163.com',
        ['2219129001@qq.com']
    )