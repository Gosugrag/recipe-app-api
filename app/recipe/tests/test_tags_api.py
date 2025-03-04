"""
Tests for Tags API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail URL."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_sample_user(email='user@example.com', password='testpass123'):
    """Create a sample user."""
    return get_user_model().objects.create_user(email, password)


class PublicTagsApiTests(TestCase):
    """Test the publicly available Tags API"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the private Tags API"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_sample_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags."""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test retrieving tags for authenticated user."""
        user2 = create_sample_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Fruit')
        tag = Tag.objects.create(user=self.user, name='Meat')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test partial updating a tag."""
        tag = Tag.objects.create(user=self.user, name='Vegan')

        payload = {'name': 'Not Vegan'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])
        self.assertEqual(tag.user, self.user)

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name='Vegan')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name='Fruit')
        tag2 = Tag.objects.create(user=self.user, name='Vegan')
        recipe = Recipe.objects.create(
            title='Apple Pie',
            time_minutes=10,
            price=Decimal('5.00'),
            description='Test recipe',
            link='http://test.com/recipe.pdf',
            user=self.user
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': True})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtering tags returns unique list."""
        tag = Tag.objects.create(user=self.user, name='Fruit')
        Tag.objects.create(user=self.user, name='Vegan')
        recipe1 = Recipe.objects.create(
            title='Apple Pie',
            time_minutes=10,
            price=Decimal('5.00'),
            description='Test recipe',
            link='http://test.com/recipe.pdf',
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Carrot Pie',
            time_minutes=10,
            price=Decimal('5.00'),
            description='Test recipe',
            link='http://test.com/recipe.pdf',
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': True})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
