"""
Serializers for recipe API
"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe model"""

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('id',)
