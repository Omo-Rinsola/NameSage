import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from core.security import create_access_token, create_refresh_token, decode_token
from crud.users import (
    create_or_update_user,
    save_refresh_token,
    get_refresh_token,
    revoke_refresh_token,
    get_user_by_id,
)
from dependencies import get_db
from utils.helpers import generate_id

router = APIRouter(prefix="/auth", tags=["Auth"])

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


# --- GET /auth/github ----------
# the login, the user (or CLI) hits this endpoint and gets redirected to GitHub

@router.get("/github")
def github_login(request: Request):
    # Read optional PKCE params sent by the CLI
    code_challenge = request.query_params.get("code_challenge", "")
    state = request.query_params.get("state", generate_id())

    params = (
        f"client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={BACKEND_URL}/auth/github/callback"
        f"&scope=read:user user:email"
        f"&state={state}"
    )

    if code_challenge:
        params += (
            f"&code_challenge={code_challenge}"
            f"&code_challenge_method=S256"
        )

    return RedirectResponse(f"https://github.com/login/oauth/authorize?{params}")

# __ GET /auth/github/callback -------
# GitHub redirects here after the user approves.


@router.get("/github/callback")
async def github_callback(
    request: Request,
    code: str,
    state: str = None,
    db: Session = Depends(get_db),
):
    code_verifier = request.query_params.get("code_verifier", None)

    # Step 1: Exchange the code for a GitHub access token
    token_url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": f"{BACKEND_URL}/auth/github/callback",
    }
    if code_verifier:
        payload["code_verifier"] = code_verifier

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            token_url,
            data=payload,
            headers={"Accept": "application/json"},
        )
        token_data = token_response.json()

    github_access_token = token_data.get("access_token")
    if not github_access_token:
        raise HTTPException(status_code=400, detail={
            "status": "error",
            "message": "Failed to get access token from GitHub"
        })

    # Step 2: Use the GitHub token to get the user's profile
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {github_access_token}"},
        )
        github_user = user_response.json()

    # Step 3: Create or update user in our database
    user = create_or_update_user(db, github_user)

    # Step 4: Issue our own tokens
    token_payload = {"sub": user.id, "role": user.role}
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    # Step 5: Save refresh token to DB so we can revoke it on logout
    save_refresh_token(db, user.id, refresh_token)

    # Step 6: Check if this came from CLI or browser
    # CLI sends a `cli=true` param so we know to return JSON
    is_cli = request.query_params.get("cli", "false") == "true"

    if is_cli:
        return JSONResponse({
            "status": "success",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "username": user.username,
            "role": user.role,
        })

    # Browser flow: redirect to frontend with tokens as query params
    # (web portal will pick these up and store in HTTP-only cookies)
    redirect_url = (
        f"{FRONTEND_URL}/auth/callback"
        f"?access_token={access_token}"
        f"&refresh_token={refresh_token}"
    )
    return RedirectResponse(redirect_url)


# ── POST /auth/refresh ────────────────────────────────────────────────────────
# When the access token expires (3 min), call this with the refresh token
# to get a brand new pair of tokens.

@router.post("/refresh")
def refresh_tokens(request: Request, db: Session = Depends(get_db)):
    body = None
    import asyncio

    async def get_body():
        return await request.json()

    try:
        import asyncio
        body = asyncio.get_event_loop().run_until_complete(get_body())
    except Exception:
        raise HTTPException(status_code=400, detail={
            "status": "error", "message": "Invalid request body"
        })

    refresh_token = body.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail={
            "status": "error", "message": "refresh_token is required"
        })

    # Check token exists in DB and isn't revoked
    db_token = get_refresh_token(db, refresh_token)
    if not db_token:
        raise HTTPException(status_code=401, detail={
            "status": "error", "message": "Invalid or expired refresh token"
        })

    # Decode the token to get user info
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail={
            "status": "error", "message": "Invalid token"
        })

    # Get fresh user data from DB
    user = get_user_by_id(db, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail={
            "status": "error", "message": "User not found or inactive"
        })

    # Invalidate the old refresh token immediately
    revoke_refresh_token(db, refresh_token)

    # Issue brand new tokens
    token_payload = {"sub": user.id, "role": user.role}
    new_access = create_access_token(token_payload)
    new_refresh = create_refresh_token(token_payload)
    save_refresh_token(db, user.id, new_refresh)

    return {
        "status": "success",
        "access_token": new_access,
        "refresh_token": new_refresh,
    }


# ----POST /auth/logout: Invalidates the refresh token. After this, the user must login again.

@router.post("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        refresh_token = body.get("refresh_token")
    except Exception:
        refresh_token = None

    if refresh_token:
        revoke_refresh_token(db, refresh_token)

    return {"status": "success", "message": "Logged out successfully"}