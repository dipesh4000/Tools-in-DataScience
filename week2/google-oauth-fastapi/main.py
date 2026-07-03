import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth

load_dotenv()

app = FastAPI(title="Google OAuth Demo")

# Session is needed to remember temporary OAuth state
# Authlib's FastAPI docs use SessionMiddleware to save temporary code/state
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET"),
    same_site="lax",
    https_only=False,  # Set True in production HTTPS
)

oauth = OAuth()

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    },
)

@app.get("/")
def home(request: Request):
    user = request.session.get("user")

    if user:
        return {
            "message": "You are logged in",
            "user": user,
            "logout": "/logout",
        }

    return {
        "message": "You are not logged in",
        "login": "/login",
    }

@app.get("/login")
async def login(request: Request):
    # This must exactly match Google Console redirect URI
    redirect_uri = request.url_for("auth_callback")

    # Sends browser to Google login/consent page
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def auth_callback(request: Request):
    # Authlib checks state and exchanges code for token
    token = await oauth.google.authorize_access_token(request)

    # For OpenID Connect, user info is available from the token/userinfo
    user = token.get("userinfo")

    if not user:
        return JSONResponse(
            {"error": "Could not fetch user info"},
            status_code=400,
        )

    # Store only safe, small identity data in session
    request.session["user"] = {
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
    }

    return RedirectResponse(url="/me")

@app.get("/me")
def me(request: Request):
    user = request.session.get("user")

    if not user:
        return JSONResponse(
            {"error": "Not logged in"},
            status_code=401,
        )

    return user

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "logged out"}