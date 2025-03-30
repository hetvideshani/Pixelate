from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.authentication import jwt_required

# Create your views here.
@api_view(['GET'])
@jwt_required
def get_courses(request):
    return Response({"data" : "good!"})
    