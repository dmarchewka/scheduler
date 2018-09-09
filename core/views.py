# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Candidate, Employee, Slot
from rest_framework import status
from datetime import datetime, timedelta, time
from .serializers import CandidateSerializer, EmployeeSerializer, SlotSerializer


class CandidateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Candidate model
    """

    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Employee model
    """

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class SlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Slot model
    """
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer

    @staticmethod
    def get_employee(request):
        """
        Return employee objects on None
        :param request:
        :return:
        """
        employee_id = request.query_params.get('employee_id', None)
        return Employee.objects.filter(pk=employee_id).first()

    @staticmethod
    def get_employees(request):
        """
        Return employee list or []
        :param request:
        :return:
        """
        ids = request.query_params.get('employee_ids', None)
        result = []
        if ids:
            arr = ids.split(',')
            for item in arr:
                employee = Employee.objects.filter(pk=item)
                if employee:
                    result.append(employee)
                else:
                    raise ValueError('Employee not found')
        return result

    @staticmethod
    def get_candidate(request):
        """
        Return candidate or none
        :param request:
        :return:
        """
        candidate_id = request.query_params.get('candidate_id', None)
        return Candidate.objects.filter(pk=candidate_id).first()

    @staticmethod
    def is_day_id_next_week(day_id):
        """
        Check if date is next week
        :param day_id:
        :return:
        """
        date = datetime.strptime(day_id, "%Y%m%d")
        now = datetime.now()
        next_monday = now + timedelta(days=(7 - now.weekday()))
        next_friday = next_monday + timedelta(days=4)
        if next_monday <= date <= next_friday:
            return True
        else:
            return False

    @staticmethod
    def get_time_hour(start, end):
        """
        Return formatted hour
        :param start:
        :param end:
        :return:
        """
        if start is None or end is None:
            raise ValueError('Start hour and end hour must be provided.')

        hour_end = time(*map(int, end.split(':'))).hour
        tmp = time(*map(int, start.split(':')))
        hour_start = tmp.hour if tmp.minute == 0 else tmp.hour + 1

        if hour_start >= hour_end:
            raise ValueError('Start hour is >= end hour')

        return hour_start, hour_end

    @staticmethod
    def get_slots_set(employee=None, candidate=None):
        """
        Return all slots available for each employee or candidate
        :param employee:
        :param candidate:
        :return:
        """
        result = set()
        slots = Slot.objects.filter(employee=employee, candidate=candidate)
        for slot in slots:
            result.add(datetime.strptime(slot.code, '%Y%m%d%H').strftime('%Y-%m-%d %H:00'))
        return result

    def list(self, request, *args, **kwargs):
        """
        Return intersection between all available slots for candidate and employees
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        candidate = self.get_candidate(request)
        try:
            employees = self.get_employees(request)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        available_slots = self.get_slots_set(None, candidate)
        for employees in employees:
            available_slots.intersection_update(self.get_slots_set(employees, None))
        return Response(data=list(available_slots))

    def create(self, request, *args, **kwargs):
        """
        Create slots for employee or candidate
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        employee = self.get_employee(request)
        candidate = self.get_candidate(request)

        if employee is None and candidate is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        day_id = request.data.get('day_id')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')

        # Check if parameters were passed
        if day_id is None or start_time is None or end_time is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Check if day id is for next week
        if not self.is_day_id_next_week(day_id):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            start_time, end_time = self.get_time_hour(
                                            request.data.get('start_time'),
                                            request.data.get('end_time'))
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        for hour in range(start_time, end_time):
            code = day_id + "%02d" % (hour,)
            if not Slot.objects.filter(candidate=candidate, employee=employee, code=code):
                slot = Slot(candidate=candidate, employee=employee, code=code)
                slot.save()

        return Response(status=status.HTTP_201_CREATED)
