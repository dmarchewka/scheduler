# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Candidate, Employee, Slot
import urllib
from datetime import datetime, timedelta


class TestCandidate(APITestCase):

    @staticmethod
    def build_url(base_url, get_args):
        url = reverse(base_url)
        if get_args:
            url += '?' + urllib.urlencode(get_args)
        return url

    def test_candidate(self):
        """
        Ensure we can create a new account object.
        """
        url_list = reverse('candidates')
        data = {'first_name': 'John', 'last_name': 'Smith'}
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Candidate.objects.count(), 1)
        self.assertEqual(Candidate.objects.get().first_name, 'John')

        data = {'first_name': 'Test', 'last_name': 'Man'}
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Candidate.objects.count(), 2)

        response = self.client.get(url_list)
        self.assertListEqual(response.data, [{"id": 1, "first_name": "John", "last_name": "Smith"},
                                             {"id": 2, "first_name": "Test", "last_name": "Man"}])

        url = reverse('candidate', args=[1])
        response = self.client.get(url)
        self.assertDictEqual(response.data, {"id": 1, "first_name": "John", "last_name": "Smith"})
        data = {"first_name": "Denis"}
        self.client.patch(url, data, format='json')
        response = self.client.get(url)
        self.assertDictEqual(response.data, {"id": 1, "first_name": "Denis", "last_name": "Smith"})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Candidate.objects.count(), 1)
        self.assertEqual(Candidate.objects.get().first_name, 'Test')

        candidate_url = reverse('candidate', args=[3])
        response = self.client.get(candidate_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_emploees(self):
        url_list = reverse('employees')
        data = {'first_name': 'John', 'last_name': 'Smith', 'position': 'manager'}
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(Employee.objects.get().first_name, 'John')

        data = {'first_name': 'Test', 'last_name': 'Man', 'position': 'vp'}
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 2)

        response = self.client.get(url_list)
        self.assertListEqual(response.data,
                             [{"id": 1, "first_name": "John", "last_name": "Smith", "position": "manager"},
                              {"id": 2, "first_name": "Test", "last_name": "Man", "position": "vp"}])

        url = reverse('employee', args=[1])
        response = self.client.get(url)
        self.assertDictEqual(response.data,
                             {"id": 1, "first_name": "John", "last_name": "Smith", "position": "manager"})
        data = {"first_name": "Denis"}
        self.client.patch(url, data, format='json')
        response = self.client.get(url)
        self.assertDictEqual(response.data,
                             {"id": 1, "first_name": "Denis", "last_name": "Smith", "position": "manager"})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(Employee.objects.get().first_name, 'Test')

        candidate_url = reverse('employee', args=[3])
        response = self.client.get(candidate_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_slot_create_employee(self):
        url_list = reverse('employees')
        data = {'first_name': 'John', 'last_name': 'Smith', 'position': 'manager'}
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee_id = Employee.objects.get().id

        slot_list = self.build_url('slots', {'employee_id': employee_id})
        data = {'employee': employee_id, 'start_time': '10:00', 'end_time': '12:00'}
        response = self.client.post(slot_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'employee': employee_id, 'day_id': '20121212', 'start_time': '10:00', 'end_time': '12:00'}
        response = self.client.post(slot_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'employee': employee_id, 'day_id': '20301212', 'start_time': '10:00', 'end_time': '12:00'}
        response = self.client.post(slot_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        date = datetime.now() + timedelta(days=(7 - datetime.now().weekday() + 1))

        data = {'employee': employee_id, 'day_id': date.strftime('%Y%m%d'), 'start_time': '14:00', 'end_time': '12:00'}
        response = self.client.post(slot_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'employee': employee_id, 'day_id': date.strftime('%Y%m%d'), 'start_time': '11:00', 'end_time': '12:00'}
        response = self.client.post(slot_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Slot.objects.count(), 1)
        self.assertEqual(Slot.objects.get().employee, Employee.objects.get())
        self.assertEqual(Slot.objects.get().code, date.strftime('%Y%m%d') + '11')

        data = {'employee': employee_id, 'day_id': date.strftime('%Y%m%d'), 'start_time': '11:00', 'end_time': '12:00'}
        response = self.client.post(slot_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Slot.objects.count(), 1)

        data = {'employee': employee_id, 'day_id': date.strftime('%Y%m%d'), 'start_time': '13:00', 'end_time': '16:00'}
        response = self.client.post(slot_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Slot.objects.count(), 4)

        data = {'employee': employee_id, 'day_id': date.strftime('%Y%m%d'), 'start_time': '09:00', 'end_time': '17:00'}
        response = self.client.post(slot_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Slot.objects.count(), 8)

    def test_slot_create_candidate(self):
        url_list = reverse('candidates')
        data = {'first_name': 'John', 'last_name': 'Smith'}
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        candidate_id = Candidate.objects.get().id

        slot_list = self.build_url('slots', {'candidate_id': candidate_id})
        date = datetime.now() + timedelta(days=(7 - datetime.now().weekday() + 1))
        data = {'employee': candidate_id, 'day_id': date.strftime('%Y%m%d'), 'start_time': '11:00', 'end_time': '12:00'}
        response = self.client.post(slot_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Slot.objects.count(), 1)

    def test_slot_one_candidate_one_employee(self):
        url_list = reverse('candidates')
        data = {'first_name': 'John', 'last_name': 'Smith'}
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        candidate_id = Candidate.objects.get().id

        slot_list = self.build_url('slots', {'candidate_id': candidate_id})
        date = datetime.now() + timedelta(days=(7 - datetime.now().weekday() + 1))
        data = {'employee': candidate_id, 'day_id': date.strftime('%Y%m%d'), 'start_time': '11:00', 'end_time': '15:00'}
        response = self.client.post(slot_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url_list = reverse('employees')
        data = {'first_name': 'Jason', 'last_name': 'Ted', 'position': 'manager'}
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee_1 = Employee.objects.get().id

        slot_list = self.build_url('slots', {'employee_id': employee_1})
        data = {'employee': employee_1, 'day_id': date.strftime('%Y%m%d'), 'start_time': '10:00', 'end_time': '13:00'}
        response = self.client.post(slot_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        slots_url = self.build_url('slots', {'employee_ids': employee_1, 'candidate_id': candidate_id})
        response = self.client.get(slots_url, format='json')
        self.assertSequenceEqual(response.data, ['2018-09-11 11:00', '2018-09-11 12:00'])

        slots_url = self.build_url('slots', {'employee_ids': str(employee_1) + ',55', 'candidate_id': candidate_id})
        response = self.client.get(slots_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url_list = reverse('employees')
        data = {'first_name': 'Don', 'last_name': 'Donowan', 'position': 'vp'}
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee_2 = Employee.objects.last().id

        slots_url = self.build_url('slots', {'employee_ids': str(employee_1) + ',' + str(employee_2), 'candidate_id': candidate_id})
        response = self.client.get(slots_url, format='json')
        self.assertSequenceEqual(response.data, [])

        slot_list = self.build_url('slots', {'employee_id': employee_2})
        data = {'employee': employee_1, 'day_id': date.strftime('%Y%m%d'), 'start_time': '12:00', 'end_time': '13:00'}
        response = self.client.post(slot_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        slots_url = self.build_url('slots', {'employee_ids': str(employee_1) + ',' + str(employee_2),
                                             'candidate_id': candidate_id})
        response = self.client.get(slots_url, format='json')
        self.assertSequenceEqual(response.data, ['2018-09-11 12:00'])


