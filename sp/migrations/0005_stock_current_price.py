# Generated by Django 4.1.9 on 2023-05-24 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sp', '0004_alter_stocktransaction_transaction_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='current_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]