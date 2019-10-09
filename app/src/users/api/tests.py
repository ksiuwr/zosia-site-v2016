# -*- coding: utf-8 -*-
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from conferences.test_helpers import create_user, create_zosia


class UsersViewSetTestCase(APITestCase):
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


class UserViewSetListTestCase(UsersViewSetTestCase):
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
        super().tearDown()


class UserViewSetDetailTestCase(UsersViewSetTestCase):
    def setUp(self):
        super().setUp()
        self.url_n1 = reverse("users_api_detail", kwargs={"version": "v1", "pk": self.normal_1.pk})
        self.url_n2 = reverse("users_api_detail", kwargs={"version": "v1", "pk": self.normal_2.pk})
        self.url_s1 = reverse("users_api_detail", kwargs={"version": "v1", "pk": self.staff_1.pk})
        self.url_s2 = reverse("users_api_detail", kwargs={"version": "v1", "pk": self.staff_2.pk})

    def test_user_cannot_get_normal_user(self):
        self.client.force_authenticate(user=self.normal_1)

        response = self.client.get(self.url_n2)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_get_staff_user(self):
        self.client.force_authenticate(user=self.normal_2)

        response = self.client.get(self.url_s1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_get_normal_user(self):
        self.client.force_authenticate(user=self.staff_2)

        response = self.client.get(self.url_n1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "lennon@thebeatles.com")

    def test_staff_can_get_staff_user(self):
        self.client.force_authenticate(user=self.staff_1)

        response = self.client.get(self.url_s2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "harrison@thebeatles.com")


class SessionUserAPIViewTestCase(UsersViewSetTestCase):
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
