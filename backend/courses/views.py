from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.authentication import jwt_required
from core.supabase_client import supabase
import json
from core.serializers import CourseSerializer
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings  # Ensure JWT secret key is correctly set

# Create your views here.
@api_view(['GET'])
@jwt_required
def get_courses(request):
    try:
        response = (
            supabase.table('courses').select('*').execute()
        )
        
        if response.count is None:
            return Response({"data" : "no courses added!"})
        
        return Response({"data": response.data})
    except Exception as e:
        return Response({"error": str(e)})
    
    
@api_view(['POST'])
@jwt_required
def add_courses(request, user_id):
    try:
        print("Cookies Received:", request.COOKIES)

        access_token = request.COOKIES.get("access_token_django")

        if not access_token:
            return Response({"error": "Unauthorized: No access token found"}, status=401)

        decoded_token = AccessToken(access_token) 
        user_id_from_token = str(decoded_token["user_id"])

        if user_id_from_token != str(user_id):  
            return Response({"error": "Unauthorized: User ID mismatch"}, status=403)


        # Parse request data
        data = json.loads(request.body)
        print(data)

        # Validate course data
        course = CourseSerializer(data=data)
        if not course.is_valid():
            return Response({"error": course.errors}, status=400)

        # Check if the user already has a course with the same title
        check_course_exists = (
            supabase.table('courses')
            .select('id')
            .eq('title', course.validated_data['title'])
            .eq('user_id', str(user_id))  
            .execute()
        )

        if check_course_exists.data:
            return Response({"error": "Course with this title already exists for the user"}, status=409)

        course_data = course.validated_data
        course_data["user_id"] = str(user_id)

        response = (
            supabase.table('courses').insert(course_data).execute()
        )

        if not response.data:
            return Response({"error": "Course not added due to an unknown error"}, status=500)

        return Response({"data": response.data[0]}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['GET'])
def get_by_id(request, course_id):
    try:
        course = ( supabase.table('courses').select('*').eq('id', str(course_id)).execute() )
        
        if len(course.data) < 1:
            return Response({'data': 'no course found!'}, status=200)
        
        return Response({'data': course.data}, status=200)
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['PUT'])
@jwt_required    
def update_course(request, course_id, user_id):
    try:
        print("Cookies Received:", request.COOKIES)

        access_token = request.COOKIES.get("access_token_django")

        if not access_token:
            return Response({"error": "Unauthorized: No access token found"}, status=401)

        decoded_token = AccessToken(access_token) 
        user_id_from_token = str(decoded_token["user_id"])

        if user_id_from_token != str(user_id):  
            return Response({"error": "Unauthorized: User ID mismatch"}, status=403)

        course = (
            supabase.table('courses')
            .select('*')
            .eq('id', str(course_id))
            .eq('user_id', str(user_id))  
            .execute()
        )

        if len(course.data) < 1:
            return Response({'error': 'Course not found or not owned by the user'}, status=404)

        data = json.loads(request.body)
        serializer = CourseSerializer(data=data, partial=True) 

        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

        response = (
            supabase.table('courses')
            .update(serializer.validated_data)
            .eq('id', str(course_id))
            .execute()
        )

        if not response.data:
            return Response({"error": "Course update failed"}, status=500)

        return Response({"data": response.data[0]}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['DELETE'])
@jwt_required
def delete_course(request, course_id, user_id):
    try:
        print("Cookies Received:", request.COOKIES)

        access_token = request.COOKIES.get("access_token_django")

        if not access_token:
            return Response({"error": "Unauthorized: No access token found"}, status=401)

        decoded_token = AccessToken(access_token) 
        user_id_from_token = str(decoded_token["user_id"])

        if user_id_from_token != str(user_id):  
            return Response({"error": "Unauthorized: User ID mismatch"}, status=403)

        course = (
            supabase.table('courses')
            .select('*')
            .eq('id', str(course_id))
            .eq('user_id', str(user_id)) 
            .execute()
        )

        if len(course.data) < 1:
            return Response({'error': 'Course not found or not owned by the user'}, status=404)

        response = (
            supabase.table('courses')
            .delete()
            .eq('id', str(course_id))
            .execute()
        )

        if not response.data:
            return Response({"error": "Course deletion failed"}, status=500)

        return Response({"message": "Course deleted successfully"}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)