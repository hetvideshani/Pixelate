import jwt
import os
from django.http import JsonResponse
from functools import wraps
from rest_framework_simplejwt.tokens import AccessToken
from core.supabase_client import supabase

# Middleware decorator for protected routes
def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            # Get token from cookies
            print("HEllo")
            token = request.COOKIES.get("access_token_django")
            if not token:
                return JsonResponse({"error": "Authentication required"}, status=401)

            # Decode token
            decoded_token = AccessToken(token)
            user_id = decoded_token["user_id"]

            # Check if user exists in Supabase
            response = supabase.table("users").select("*").eq("id", user_id).execute()
            if not response.data:
                return JsonResponse({"error": "User not found"}, status=401)

            # Attach user data to request
            request.user = response.data[0]
            return view_func(request, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return wrapper
