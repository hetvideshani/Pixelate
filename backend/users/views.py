from .models import User
from core.supabase_client import supabase
import uuid
import json  # Needed to parse JSON request body
import datetime
import bcrypt
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework_simplejwt.tokens import RefreshToken
from core.serializers import UserSerializer

class UserObject:
    """Converts a dictionary into an object-like structure to mimic Django's User model."""
    def __init__(self, user_dict):
        self.id = user_dict.get("id")  # Ensure the ID exists
        self.email = user_dict.get("email")
        self.full_name = user_dict.get("full_name")




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
    """Signs in the user and sets JWT access and refresh tokens in cookies."""
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"error": "Email and password are required"}, status=400)

        response = supabase.table("users").select("*").eq("email", email).execute()

        if not response or not response.data:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        user_dict = response.data[0]  

        if not bcrypt.checkpw(password.encode("utf-8"), user_dict["password_hash"].encode("utf-8")):
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        if not user_dict:
            return JsonResponse({"error": "Invalid credentials"}, status=401)
        
        user_serializer = UserSerializer(user_dict)

        # ✅ Manually generate JWT token with only user_id
        refresh = RefreshToken()
        refresh["user_id"] = str(user_dict["id"])  # Store only user_id

        # Create response and set cookies
        response = JsonResponse({
            "message": "Login successful",
            "user": user_serializer.data
        })
        response.set_cookie("access_token_django", str(refresh.access_token), httponly=True, samesite="Lax")

        return response
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)