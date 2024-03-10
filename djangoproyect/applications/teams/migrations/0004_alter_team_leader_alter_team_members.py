# Generated by Django 4.2.10 on 2024-03-04 13:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teams', '0003_team_members_delete_teammembership'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='leader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leading_teams', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(related_name='teams', to=settings.AUTH_USER_MODEL),
        ),
    ]