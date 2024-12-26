"""
Test for the health check API
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


class HealthCheckTestCase(TestCase):
    """Tests for the health check API"""

    def test_healthcheck(self):
        """Test health check API"""
        client = APIClient()
        url = reverse('core:healthcheck')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
