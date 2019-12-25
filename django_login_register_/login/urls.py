from django.conf.urls import url

from login import views

urlpatterns =[
    url(r'^confirm/',views.user_confirm),
    url(r'^index/', views.index),
    url(r'^login/$', views.login,name='login'),
    url(r'^register/$',views.register,name='register'),
    url(r'^logout/$', views.logout,name='logout'),
]
