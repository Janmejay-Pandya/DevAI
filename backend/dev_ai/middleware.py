from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        try:
            # Extract token from query string, adjust based on your client implementation
            query_string = scope["query_string"].decode("utf8")
            token = dict(qc.split("=") for qc in query_string.split("&")).get("token")

            if token:
                access_token = AccessToken(token)
                user_id = access_token["user_id"]
                user = await database_sync_to_async(User.objects.get)(id=user_id)
                scope["user"] = user
            else:
                scope["user"] = AnonymousUser()
        except Exception:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
