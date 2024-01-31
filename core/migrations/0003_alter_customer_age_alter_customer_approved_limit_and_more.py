# Generated by Django 5.0.1 on 2024-01-31 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_loan_emis_paid_on_time_alter_loan_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='age',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customer',
            name='approved_limit',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customer',
            name='monthly_salary',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customer',
            name='phone_number',
            field=models.CharField(default=1, max_length=12),
            preserve_default=False,
        ),
    ]