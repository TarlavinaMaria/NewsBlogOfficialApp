cd news_blog
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py loaddata base.json
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python3 manage.py shell