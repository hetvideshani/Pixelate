from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.authentication import jwt_required
from core.supabase_client import supabase
from core.frequent_func import user_exists, user_same_logged, course_exists
import json
from core.serializers import FeedbackSerializer

@api_view(['POST'])
@jwt_required
def create_feedback(request, course_id, user_id):
    try:
        user = user_exists(user_id=user_id)
        course = course_exists(course_id)
        user_loggedin = user_same_logged(user_id, request.COOKIES)
        
        if not user["status"] or not course["status"] or not user_loggedin["status"]:
            if not user["status"]: return Response({"error": user["error"]}, status=404)
            elif not course["status"]: return Response({"error": course["error"]}, status=404)
            elif not user_loggedin["status"]: return Response({"error": user_loggedin["error"]}, status=403)
            
        data = json.loads(request.body)
        serializer = FeedbackSerializer(data=data, partial=True)
        
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

        course_data = serializer.validated_data
        course_data['user_id'] = str(user_id)
        course_data['course_id'] = str(course_id)
        
        response = (
            supabase.table('feedback').insert(course_data).execute()
        )
        
        if not response.data:
            return Response({"error": "Course not added due to an unknown error"}, status=500)
        
        return Response({"data": response.data[0]}, status=200)
        
    except Exception as e:
        return Response({"error": str(e)})
    
    
@api_view(['DELETE'])
@jwt_required
def delete_feedback(request, user_id, course_id):
    try:
        user = user_exists(user_id=user_id)
        course = course_exists(course_id)
        user_loggedin = user_same_logged(user_id, request.COOKIES)

        if not user["status"] or not course["status"] or not user_loggedin["status"]:
            if not user["status"]: return Response({"error": user["error"]}, status=404)
            elif not course["status"]: return Response({"error": course["error"]}, status=404)
            elif not user_loggedin["status"]: return Response({"error": user_loggedin["error"]}, status=403)

        response = (
            supabase.table('feedback')
            .delete()
            .eq('user_id', str(user_id))
            .eq('course_id', str(course_id))
            .execute()
        )

        if not response.data:
            return Response({"error": "Feedback not found or already deleted"}, status=404)

        return Response({"message": "Feedback deleted successfully"}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def get_course_feedback(request, course_id):
    try:
        course = course_exists(course_id)
        
        if not course["status"]:
            return Response({"error": course["error"]}, status=404)
        
        feedbacks = (
            supabase.table('feedback')
            .select('*')
            .eq('course_id', str(course_id))
            .execute()
        )

        if not feedbacks.data:
            return Response({"error": "No feedback found for this course"}, status=404)

        return Response({"data": feedbacks.data}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    

# TODO: implement like/dislike func