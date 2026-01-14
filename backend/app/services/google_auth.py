from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os
from app.core.config import settings


def get_google_flow():
    """Create and return Google OAuth flow"""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise ValueError("Google OAuth credentials not configured")
    
    redirect_uri = settings.GOOGLE_REDIRECT_URI or "http://localhost:3000/google/callback"
    
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
        redirect_uri=redirect_uri
    )
    
    return flow


def get_google_authorization_url():
    """Get Google OAuth authorization URL"""
    flow = get_google_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return authorization_url, state


def verify_google_token(token: str):
    """Verify Google ID token and return user info"""
    try:
        idinfo = id_token.verify_oauth2_token(
            token, Request(), settings.GOOGLE_CLIENT_ID
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        return {
            'email': idinfo['email'],
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture'),
            'google_id': idinfo['sub']
        }
    except ValueError as e:
        raise ValueError(f"Invalid token: {str(e)}")


def exchange_code_for_token(code: str):
    """Exchange authorization code for tokens"""
    flow = get_google_flow()
    flow.fetch_token(code=code)
    
    credentials = flow.credentials
    idinfo = id_token.verify_oauth2_token(
        credentials.id_token, Request(), settings.GOOGLE_CLIENT_ID
    )
    
    return {
        'email': idinfo['email'],
        'name': idinfo.get('name'),
        'picture': idinfo.get('picture'),
        'google_id': idinfo['sub']
    }

