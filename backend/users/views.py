from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
import bcrypt
from .models import User
from core.supabase_client import supabase
import uuid
import json  # Needed to parse JSON request body
import jwt
import datetime
from django.conf import settings
import os
import random
import smtplib
from email.mime.text import MIMEText
from django.core.cache import cache

@csrf_exempt  # Disable CSRF for this view
@require_POST
def signup(request):
    """Registers a new user in Supabase"""
    try:
        # Ensure data is parsed correctly from JSON
        data = json.loads(request.body.decode("utf-8"))
        print(data)  # Debugging: Print the received data

        full_name = data.get("full_name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "student")
        preferred_language = data.get("preferred_language", "en")

        if not full_name or not email or not password:
            return JsonResponse({"error": "All fields are required"}, status=400)

        # Hash password
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        user = User(
            id=uuid.uuid4(),
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            role=role,
            preferred_language=preferred_language
        )

        # Store user in Supabase
        response = supabase.table("users").insert({
            "id": str(user.id),
            "full_name": full_name,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "preferred_language": preferred_language
        }).execute()

        if response and response.data:
            return JsonResponse({"message": "User registered successfully", "user": response.data}, status=201)
        else:
            return JsonResponse({"error": "Failed to register user"}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_POST
def signin(request):
    """Signs in the user and sets JWT token in cookies."""
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"error": "Email and password are required"}, status=400)

        response = supabase.table("users").select("*").eq("email", email).execute()

        if not response or not response.data:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        user = response.data[0]  

        if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        # Generate JWT token
        token_payload = {
            "id": user["id"],
            "email": user["email"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        }
        token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm="HS256")

        # Set token in an HTTP-only cookie
        res = JsonResponse({"message": "Login successful"}, status=200)
        res.set_cookie("token", token, httponly=True, samesite="Lax", secure=False)

        return res

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
@require_GET
def getuserprofile(request):
    """Get user profile"""
    try:
        token = request.COOKIES.get("token")
        
        if not token:
            return JsonResponse({"error": "Token not found"}, status=401)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload["id"]
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not response or not response.data:
            return JsonResponse({"error": "User not found"}, status=404)
        
        user = response.data[0]
        return JsonResponse({"user": user}, status=200)
    
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token expired"}, status=401)
    
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_POST
def updateuserprofile(request):
    """Update user profile"""
    try:
        token = request.COOKIES.get("token")
        
        if not token:
            return JsonResponse({"error": "Token not found"}, status=401)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload["id"]
        
        data = json.loads(request.body)
        full_name = data.get("full_name")
        email = data.get("email")
        preferred_language = data.get("preferred_language")
        
        if not full_name and not preferred_language and not email:
            return JsonResponse({"error": "At least one field is required"}, status=400)
        
        response = supabase.table("users").update({
            "full_name": full_name,
            "email": email,
            "preferred_language": preferred_language
        }).eq("id", user_id).execute()
        
        if not response or not response.data:
            return JsonResponse({"error": "Failed to update user profile"}, status=500)
        
        return JsonResponse({"message": "User profile updated successfully"}, status=200)
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
@require_POST
def sendverificationcode(request):
    """Send verification code to the user's email"""
    try:
        token = request.COOKIES.get("token")
        
        if not token:
            return JsonResponse({"error": "Token not found"}, status=401)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload["id"]
        user_email = payload["email"]
        
        verification_code = str(random.randint(100000, 999999))
        
        cache.set(f"verification_code:{user_id}", verification_code, timeout=300) 
        message = MIMEText(f"Your verification code is: {verification_code}")
        message["Subject"] = "Verification Code"
        message["From"] = settings.EMAIL_HOST_USER
        message["To"] = user_email
        
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(settings.EMAIL_HOST_USER, user_email, message.as_string())
        server.quit()
        
        return JsonResponse({"message": "Verification code sent successfully"}, status=200)
    
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token expired"}, status=401)
    
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
@require_POST
def changepassword(request):
    """Change user's password"""
    try:
        token = request.COOKIES.get("token")
        
        if not token:
            return JsonResponse({"error": "Token not found"}, status=401)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload["id"]
        user_email = payload["email"]
        
        data = json.loads(request.body)
        verificationcode = data.get("verificationcode")
        password = data.get("password")
        
        if not verificationcode or not password:
            return JsonResponse({"error": "All fields are required"}, status=400)
        
        verification_code_from_cache = cache.get(f"verification_code:{user_email}")
        
        if not verification_code_from_cache :
            return JsonResponse({"error": "Verification code not found or expired"}, status=401)
        
        if verificationcode!= verification_code_from_cache:
            return JsonResponse({"error": "Invalid verification code"}, status=401)
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        
        response = supabase.table("users").update({
            "password_hash": password_hash
        }).eq("id", user_id).execute()
        
        if not response or not response.data:
            return JsonResponse({"error": "Failed to change password"}, status=500)
        
        cache.delete(f"verification_code:{user_email}")
        
        return JsonResponse({"message": "Password changed successfully"}, status=200)
    
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token expired"}, status=401)
    
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)