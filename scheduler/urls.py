# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib import admin
from core.views import CandidateViewSet, EmployeeViewSet, SlotViewSet

candidate_list = CandidateViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

candidate_detail = CandidateViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

employee_list = EmployeeViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

employee_detail = EmployeeViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

slot_list = SlotViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

slot_detail = SlotViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy'
})

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^candidates/$', candidate_list, name='candidates'),
    url(r'^candidate/(?P<pk>[0-9]+)/$', candidate_detail, name='candidate'),
    url(r'^employees/$', employee_list, name='employees'),
    url(r'^employee/(?P<pk>[0-9]+)/$', employee_detail, name='employee'),
    url(r'^slots/$', slot_list, name='slots'),
    url(r'^slot/(?P<pk>[0-9]+)/$', slot_detail, name='slot'),
]
