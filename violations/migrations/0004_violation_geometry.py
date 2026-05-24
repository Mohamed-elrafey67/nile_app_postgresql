from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('violations', '0003_auditlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='violation',
            name='geometry',
            field=models.JSONField(blank=True, null=True, verbose_name='هندسة القطعة (GeoJSON)'),
        ),
        migrations.AlterField(
            model_name='violation',
            name='latitude',
            field=models.FloatField(default=0, verbose_name='خط العرض'),
        ),
        migrations.AlterField(
            model_name='violation',
            name='longitude',
            field=models.FloatField(default=0, verbose_name='خط الطول'),
        ),
    ]
