# Generated by Django 4.2 on 2023-04-08 01:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assigments_model', '0004_activity_id_num'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoticedOpenTimeActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('noticed', models.BooleanField()),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assigments_model.activity')),
            ],
        ),
        migrations.CreateModel(
            name='NoticedDeadlineActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('noticed', models.BooleanField()),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assigments_model.activity')),
            ],
        ),
    ]
