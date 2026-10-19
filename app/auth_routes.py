from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user
from .extensions import oauth, db
from .models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")

@auth_bp.get("/login/<provider>")
def login_provider(provider):
    if provider not in {"google", "github"}:
        flash("Proveedor de acceso no permitido.", "error")
        return redirect(url_for("auth.login"))
    client = oauth.create_client(provider)
    if not client:
        flash(f"Configura las credenciales OAuth de {provider.title()} en .env.", "error")
        return redirect(url_for("auth.login"))
    callback = url_for("auth.callback", provider=provider, _external=True)
    return client.authorize_redirect(callback)

@auth_bp.get("/auth/callback/<provider>")
def callback(provider):
    if provider not in {"google", "github"}:
        return redirect(url_for("auth.login"))
    client = oauth.create_client(provider)
    if not client:
        return redirect(url_for("auth.login"))
    token = client.authorize_access_token()
    if provider == "google":
        profile = client.parse_id_token(token)
        email = profile.get("email")
        name = profile.get("name") or email
        avatar = profile.get("picture")
    else:
        profile = client.get("user").json()
        email = profile.get("email")
        if not email:
            emails = client.get("user/emails").json()
            primary = next((entry for entry in emails if entry.get("primary") and entry.get("verified")), None)
            email = primary.get("email") if primary else None
        name = profile.get("name") or profile.get("login") or email
        avatar = profile.get("avatar_url")
    if not email:
        flash("El proveedor no devolvió un correo verificado.", "error")
        return redirect(url_for("auth.login"))
    user = db.session.query(User).filter_by(email=email).first()
    if user is None:
        user = User(email=email, name=name, avatar_url=avatar, provider=provider)
        db.session.add(user)
    else:
        user.name, user.avatar_url, user.provider = name, avatar, provider
    db.session.commit()
    login_user(user, remember=False, fresh=True)
    return redirect(url_for("main.dashboard"))

@auth_bp.post("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
