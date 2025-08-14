from django.db import migrations


def drop_quantity_column(apps, schema_editor):
    # Safely drop the column only if it exists (works on MySQL/MariaDB)
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'core_car'
              AND COLUMN_NAME = 'quantity'
            """
        )
        exists = cursor.fetchone()[0]
        if exists:
            cursor.execute("ALTER TABLE core_car DROP COLUMN quantity")


def add_quantity_column(apps, schema_editor):
    # Reverse: re-add the column if it doesn't exist
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'core_car'
              AND COLUMN_NAME = 'quantity'
            """
        )
        exists = cursor.fetchone()[0]
        if not exists:
            cursor.execute("ALTER TABLE core_car ADD COLUMN quantity int NOT NULL DEFAULT 1")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(drop_quantity_column, add_quantity_column),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name='car',
                    name='quantity',
                ),
            ],
        ),
    ]