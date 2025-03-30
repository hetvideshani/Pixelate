from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import bcrypt
from .models import User
from core.supabase_client import supabase
import uuid
import json  # Needed to parse JSON request body

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
