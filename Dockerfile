FROM python:3.11

ENV DJANGO_SUPERUSER_PASSWORD
ENV DJANGO_SUPERUSER_EMAIL
ENV DJANGO_SECRET_KEY

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements/requirements.txt
RUN python3 manage.py makemigrations && python3 manage.py migrate
RUN python3 manage.py createsuperuser --noinput --email DJANGO_SUPERUSER_EMAIL

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "hanbaiki_fyi.wsgi:application"]