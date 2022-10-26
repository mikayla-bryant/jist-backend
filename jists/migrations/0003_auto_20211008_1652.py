# Generated by Django 3.2.7 on 2021-10-08 20:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jists', '0002_auto_20211004_1840'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jist',
            name='topic',
        ),
        migrations.AddField(
            model_name='topic',
            name='jists',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jists.jist'),
        ),
    ]
