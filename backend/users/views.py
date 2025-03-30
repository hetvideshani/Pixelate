from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import bcrypt
from .models import User
from core.supabase_client import supabase
import uuid
import json  # Needed to parse JSON request body
import jwt
import datetime
from django.conf import settings
import os

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