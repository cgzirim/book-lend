# Generated by Django 5.1.1 on 2024-09-24 19:47

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100)),
                ('author', models.CharField(max_length=255)),
                ('published_date', models.DateField()),
                ('publisher', models.CharField(max_length=50)),
                ('category', models.CharField(max_length=50)),
                ('is_available', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-updated_at', '-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BorrowedBook',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('borrowed_date', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.DateTimeField()),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_v1.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at', '-created_at'],
                'abstract': False,
            },
        ),
    ]
