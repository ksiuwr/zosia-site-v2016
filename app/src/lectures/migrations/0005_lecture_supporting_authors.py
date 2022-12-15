# Generated by Django 3.2.16 on 2022-12-15 22:36

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lectures', '0004_remove_lecture_person_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecture',
            name='supporters_names',
            field=models.TextField(blank=True, default='', help_text="Write here the names of people that you'd like to present your lecture/workshop with. The organizers will then assign their accounts to your lecture/workshop.", max_length=500, verbose_name="Supporting authors' names"),
        ),
        migrations.AddField(
            model_name='lecture',
            name='supporting_authors',
            field=models.ManyToManyField(related_name='lectures_supporting', to=settings.AUTH_USER_MODEL, verbose_name='Supporting authors'),
        ),
        migrations.AlterField(
            model_name='lecture',
            name='description',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Authors description'),
        ),
        migrations.AlterField(
            model_name='lecture',
            name='duration',
            field=models.PositiveSmallIntegerField(choices=[(10, '10'), (15, '15'), (20, '20'), (30, '30'), (45, '45'), (60, '60'), (75, '75'), (90, '90'), (120, '120')], help_text="Please remember that organizers <u>ARE ALLOWED</u> to cut you off during your lecture/workshop when you're out of declared time!", verbose_name='Duration (in minutes)'),
        ),
        migrations.AlterField(
            model_name='lecture',
            name='events',
            field=models.TextField(blank=True, help_text="Are you planning any event after your lecture/workshop (e.g. pizza, drinks, games, recruitment)? <b>TELL US ABOUT IT!</b> Beware that organizers <u>WON'T ALLOW</u> you to arrange your event if you don't announce it here!", max_length=800, null=True, verbose_name='Additional events'),
        ),
        migrations.AlterField(
            model_name='lecture',
            name='requests',
            field=models.TextField(blank=True, help_text='Your requests, suggestions or comments intended for organizers', max_length=800, null=True, verbose_name='Requests or comments'),
        ),
    ]
