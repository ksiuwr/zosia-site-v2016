# -*- coding: utf-8 -*-
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from conferences.test_helpers import create_user, create_zosia


class UsersAPIViewTestCase(APITestCase):
    def setUp(self):
        super().setUp()

        self.zosia = create_zosia(active=True)

        self.normal_1 = create_user(0)
        self.normal_2 = create_user(1)
        self.staff_1 = create_user(2, is_staff=True)
        self.staff_2 = create_user(3, is_staff=True)

    def tearDown(self):
        self.client.force_authenticate(user=None)
        super().tearDown()


class UserListAPIViewTestCase(UsersAPIViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("users_api_list", kwargs={"version": "v1"})

    def test_user_cannot_get_all_users(self):
        self.client.force_authenticate(user=self.normal_1)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_get_all_users(self):
        self.client.force_authenticate(user=self.staff_2)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)


class SessionUserAPIViewTestCase(UsersAPIViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("users_api_me", kwargs={"version": "v1"})

    def test_user_can_get_their_info(self):
        self.client.force_authenticate(user=self.normal_2)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.normal_2.email, response.data["email"])
        self.assertEqual(self.normal_2.first_name, response.data["first_name"])
        self.assertEqual(self.normal_2.last_name, response.data["last_name"])

    def test_staff_can_get_their_info(self):
        self.client.force_authenticate(user=self.staff_1)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.staff_1.email, response.data["email"])
        self.assertEqual(self.staff_1.first_name, response.data["first_name"])
        self.assertEqual(self.staff_1.last_name, response.data["last_name"])

    def test_anonymous_cannot_get_their_info(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
