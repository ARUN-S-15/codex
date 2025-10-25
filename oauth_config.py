# oauth_config.py - OAuth configuration for Google and GitHub
import os
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()

def init_oauth(app):
    """Initialize OAuth with Google and GitHub providers"""
    oauth = OAuth(app)
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        google = oauth.register(
            name='google',
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
        print("✅ Google OAuth enabled")
    else:
        google = None
        # OAuth optional - username/password login works great for learning platforms
    
    # GitHub OAuth Configuration
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
    
    if GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET:
        github = oauth.register(
            name='github',
            client_id=GITHUB_CLIENT_ID,
            client_secret=GITHUB_CLIENT_SECRET,
            access_token_url='https://github.com/login/oauth/access_token',
            access_token_params=None,
            authorize_url='https://github.com/login/oauth/authorize',
            authorize_params=None,
            api_base_url='https://api.github.com/',
            client_kwargs={'scope': 'user:email'},
        )
        print("✅ GitHub OAuth enabled")
    else:
        github = None
        # OAuth optional - username/password login works great for learning platforms
    
    return oauth, google, github
