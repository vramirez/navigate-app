# Generated manually on 2025-10-19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0003_business_has_tv_screens'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessTypeKeyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_type', models.CharField(choices=[('coffee_shop', 'Cafetería'), ('restaurant', 'Restaurante'), ('pub', 'Pub/Bar'), ('bookstore', 'Librería')], max_length=50, verbose_name='Tipo de negocio')),
                ('keyword', models.CharField(max_length=100, verbose_name='Palabra clave')),
                ('weight', models.FloatField(default=0.15, help_text='Importancia de esta palabra clave en el matching (0.05 - 0.30)', verbose_name='Peso')),
                ('category', models.CharField(blank=True, max_length=50, help_text='Ej: bebidas, comida, deportes, eventos', verbose_name='Categoría')),
                ('is_active', models.BooleanField(default=True, help_text='Desactivar sin eliminar para mantener historial', verbose_name='Activa')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Palabra clave por tipo de negocio',
                'verbose_name_plural': 'Palabras clave por tipo de negocio',
                'ordering': ['business_type', 'category', 'keyword'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='businesstypekeyword',
            unique_together={('business_type', 'keyword')},
        ),
    ]
