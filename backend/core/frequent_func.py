from .supabase_client import supabase
from rest_framework_simplejwt.tokens import AccessToken


def user_exists(user_id):
    try:
        response = (
            supabase.table('users').select('*').eq('id', user_id).execute()
        )
        
        if len(response.data) < 1:
            return {"error": "user not found", "status": False}
        
        return {"data": response.data[0], "status": True}
        
    except Exception as e:
        return {"error": str(e), "status": False}


def course_exists(course_id):
    try:
        response = (
            supabase.table('courses').select('*').eq('id', course_id).execute()
        )
        
        if len(response.data) < 1:
            return {"error": "course not found", "status": False}
        
        return {"data": response.data[0], "status": True}
        
    except Exception as e:
        return {"error": str(e), "status": False}

def user_same_logged(user_id, cookies):
    access_token = cookies.get("access_token_django")

    if not access_token:
        return {"error": "Unauthorized: No access token found", "status":False}

    decoded_token = AccessToken(access_token) 
    user_id_from_token = str(decoded_token["user_id"])

    if user_id_from_token != str(user_id):  
        return {"error": "Unauthorized: User ID mismatch", "status": False}
    
    return {"data": decoded_token, "status": True}