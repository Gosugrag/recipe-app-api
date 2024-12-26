"""
Core views for app
"""
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def health_check(request):
    """Returns successful response"""
    return Response({'healthy': True})
