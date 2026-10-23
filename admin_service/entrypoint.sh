#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py shell <<'PYEOF'
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ["DJANGO_SUPERUSER_USERNAME"]
password = os.environ["DJANGO_SUPERUSER_PASSWORD"]
email    = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

if User.objects.filter(username=username).exists():
    print(f"[entrypoint] Superuser '{username}' already exists, skipping.")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"[entrypoint] Superuser '{username}' created.")
PYEOF
fi

exec python manage.py runserver 0.0.0.0:8004