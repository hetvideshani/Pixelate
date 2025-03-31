from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
import bcrypt
from .models import Quiz
from core.supabase_client import supabase
import uuid
import json  # Needed to parse JSON request body
import datetime
import bcrypt
import jwt
from django.conf import settings
import os
import random
import smtplib
from email.mime.text import MIMEText
from django.core.cache import cache

@csrf_exempt
@require_POST
def addquiz(request):
    try:
        data = json.loads(request.body)
        print(data) 
        
        course_id = data['course_id']
        question_text = data['question_text']
        options = data['options']
        correct_answer = data['correct_answer']
        explanation = data.get('explanation', '')
        
        # Create a new Quiz instance
        quiz = Quiz(
            id = uuid.uuid4(),
            course_id = course_id,
            question_text = question_text,
            options = options,
            correct_answer = correct_answer,
            explanation = explanation
        )
        
        # Save the Quiz instance to the database
        response = supabase.table("quiz_questions").insert(
            {
                "id": str(quiz.id),
                "course_id": course_id,
                "question_text": question_text,
                "options": options,
                "correct_answer": correct_answer,
                "explanation": explanation
            }
        ).execute()
        
        if response.data:
            return JsonResponse({"message": "Quiz question added successfully"}, status=201)
        else :
            return JsonResponse({"error": "Failed to add quiz question"}, status=500)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_GET
def getquizquestions(request):
    try:
        data = json.loads(request.body)
        print(data) 
        
        course_id = data['course_id']
        
        if not course_id:
            return JsonResponse({"error": "Missing course_id parameter"}, status=400)
        
        # Retrieve quiz questions from the database
        response = supabase.table("quiz_questions").select("*").eq("course_id", course_id).execute()
        
        if len(response.data) > 0:
            return JsonResponse({"data": response.data}, status=200)
        else:
            return JsonResponse({"data": "No quiz questions found for this course"}, status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_POST
def updatequizquestion(request):
    try:
        data = json.loads(request.body)
        print(data) 
        
        id = data['id']
        question_text = data['question_text']
        options = data['options']
        correct_answer = data['correct_answer']
        explanation = data.get('explanation', '')
        
        # Update the Quiz instance in the database
        response = supabase.table("quiz_questions").update(
            {
                "question_text": question_text,
                "options": options,
                "correct_answer": correct_answer,
                "explanation": explanation
            }
        ).eq("id", id).execute()
        
        if response.data:
            return JsonResponse({"message": "Quiz question updated successfully"}, status=200)
        else:
            return JsonResponse({"error": "Failed to update quiz question"}, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_POST
def deletequizquestion(request):
    try:
        data = json.loads(request.body)
        print(data) 
        id = data['id']
        
        # Delete the Quiz instance from the database
        response = supabase.table("quiz_questions").delete().eq("id", id).execute()
        
        if response.data:
            return JsonResponse({"message": "Quiz question deleted successfully"}, status=200)
        else:
            return JsonResponse({"error": "Failed to delete quiz question"}, status=500)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)