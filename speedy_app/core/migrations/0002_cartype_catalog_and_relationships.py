from django.db import migrations, models
import django.db.models.deletion


def seed_initial_cartypes(apps, schema_editor):
    CarType = apps.get_model('core', 'CarType')
    defaults = [
        ("SEDAN", "Sedan", 4),
        ("SUV", "SUV", 6),
        ("VAN", "Van", 8),
        ("SPRINTER", "Sprinter", 12),
        ("BUS", "Bus", 20),
    ]
    for code, name, cap in defaults:
        CarType.objects.get_or_create(code=code, defaults={"name": name, "max_capacity": cap})


def backfill_cartype_and_rates(apps, schema_editor):
    Car = apps.get_model('core', 'Car')
    CarType = apps.get_model('core', 'CarType')
    Rate = apps.get_model('core', 'Rate')

    # Map Car.type to CarType by code
    for car in Car.objects.all():
        if getattr(car, 'type', None):
            ct = CarType.objects.filter(code=car.type).first()
            if ct and not getattr(car, 'car_type_id', None):
                car.car_type_id = ct.id
                car.save(update_fields=['car_type'])

    # Prefer Rate.car_type; if null, derive from linked car
    for rate in Rate.objects.all():
        if getattr(rate, 'car_type_id', None):
            continue
        if getattr(rate, 'car_id', None):
            car = Car.objects.filter(id=rate.car_id).first()
            if car and getattr(car, 'car_type_id', None):
                rate.car_type_id = car.car_type_id
                rate.save(update_fields=['car_type'])


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        """
                        -- Drop FK on core_booking(car_id_id) if present
                        SET @fk_name := (
                          SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking'
                            AND COLUMN_NAME='car_id_id' AND REFERENCED_TABLE_NAME='core_car' LIMIT 1
                        );
                        SET @sql := IF(@fk_name IS NOT NULL, CONCAT('ALTER TABLE core_booking DROP FOREIGN KEY ', @fk_name), 'SELECT 1');
                        PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

                        -- Drop FK on core_booking(car_type_id) if present
                        SET @fk_name := (
                          SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking'
                            AND COLUMN_NAME='car_type_id' AND REFERENCED_TABLE_NAME='core_car' LIMIT 1
                        );
                        SET @sql := IF(@fk_name IS NOT NULL, CONCAT('ALTER TABLE core_booking DROP FOREIGN KEY ', @fk_name), 'SELECT 1');
                        PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
                        """
                    ),
                    reverse_sql=("SELECT 1"),
                ),
                migrations.RunSQL(
                    sql=(
                        """
                        CREATE TABLE IF NOT EXISTS `core_cartype` (
                          `id` bigint AUTO_INCREMENT PRIMARY KEY,
                          `code` varchar(20) NOT NULL UNIQUE,
                          `name` varchar(50) NOT NULL,
                          `description` longtext NULL,
                          `image` varchar(100) NULL,
                          `max_capacity` int NOT NULL DEFAULT 1
                        ) ENGINE=InnoDB;
                        """
                    ),
                    reverse_sql=("DROP TABLE IF EXISTS `core_cartype`;")
                ),
                # Ensure booking column rename happens safely
                migrations.RunSQL(
                    sql=(
                        """
                        SET @has_old := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking' AND COLUMN_NAME='car_type_id'
                        );
                        SET @has_new := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking' AND COLUMN_NAME='car_id'
                        );
                        SET @sql := IF(@has_old > 0 AND @has_new = 0,
                          'ALTER TABLE core_booking CHANGE COLUMN car_type_id car_id bigint NULL',
                          'SELECT 1');
                        PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
                        """
                    ),
                    reverse_sql=(
                        """
                        SET @has_new := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking' AND COLUMN_NAME='car_id'
                        );
                        SET @has_old := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking' AND COLUMN_NAME='car_type_id'
                        );
                        SET @sql := IF(@has_new > 0 AND @has_old = 0,
                          'ALTER TABLE core_booking CHANGE COLUMN car_id car_type_id bigint NULL',
                          'SELECT 1');
                        PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
                        """
                    ),
                ),
                # Ensure foreign key columns exist before state operations
                migrations.RunSQL(
                    sql=(
                        """
                        -- Add core_car.car_type_id if missing
                        SET @exists := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_car' AND COLUMN_NAME='car_type_id'
                        );
                        SET @sql := IF(@exists = 0,
                          'ALTER TABLE core_car ADD COLUMN car_type_id bigint NULL',
                          'SELECT 1');
                        PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

                        -- Add core_rate.car_type_id if missing
                        SET @exists := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_rate' AND COLUMN_NAME='car_type_id'
                        );
                        SET @sql := IF(@exists = 0,
                          'ALTER TABLE core_rate ADD COLUMN car_type_id bigint NULL',
                          'SELECT 1');
                        PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

                        -- Add core_booking.car_type_id if missing
                        SET @exists := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking' AND COLUMN_NAME='car_type_id'
                        );
                        SET @sql := IF(@exists = 0,
                          'ALTER TABLE core_booking ADD COLUMN car_type_id bigint NULL',
                          'SELECT 1');
                        PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
                        """
                    ),
                    reverse_sql=(
                        """
                        -- Best-effort reverse: drop columns if exist
                        SET @exists := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking' AND COLUMN_NAME='car_type_id'
                        );
                        SET @sql := IF(@exists = 1,'ALTER TABLE core_booking DROP COLUMN car_type_id','SELECT 1');
                        PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

                        SET @exists := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_rate' AND COLUMN_NAME='car_type_id'
                        );
                        SET @sql := IF(@exists = 1,'ALTER TABLE core_rate DROP COLUMN car_type_id','SELECT 1');
                        PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

                        SET @exists := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_car' AND COLUMN_NAME='car_type_id'
                        );
                        SET @sql := IF(@exists = 1,'ALTER TABLE core_car DROP COLUMN car_type_id','SELECT 1');
                        PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
                        """
                    ),
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name='CarType',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('code', models.CharField(max_length=20, unique=True)),
                        ('name', models.CharField(max_length=50)),
                        ('description', models.TextField(blank=True, null=True)),
                        ('image', models.ImageField(blank=True, null=True, upload_to='car_types/')),
                        ('max_capacity', models.PositiveIntegerField(default=1)),
                    ],
                    options={
                        'verbose_name': 'Car Type',
                        'verbose_name_plural': 'Car Types',
                    },
                ),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        """
                        -- Normalize booking car_id column name
                        SET @has_wrong := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking' AND COLUMN_NAME='car_id_id'
                        );
                        SET @has_target := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking' AND COLUMN_NAME='car_id'
                        );
                        SET @sql := IF(@has_wrong > 0 AND @has_target = 0,
                          'ALTER TABLE core_booking CHANGE COLUMN car_id_id car_id bigint NULL',
                          'SELECT 1');
                        PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

                        SET @has_old := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking' AND COLUMN_NAME='car_type_id'
                        );
                        SET @has_target := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking' AND COLUMN_NAME='car_id'
                        );
                        SET @sql := IF(@has_old > 0 AND @has_target = 0,
                          'ALTER TABLE core_booking CHANGE COLUMN car_type_id car_id bigint NULL',
                          'SELECT 1');
                        PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

                        -- If both exist, drop the redundant car_id_id
                        SET @has_wrong := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking' AND COLUMN_NAME='car_id_id'
                        );
                        SET @has_target := (
                          SELECT COUNT(*) FROM information_schema.COLUMNS
                          WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='core_booking' AND COLUMN_NAME='car_id'
                        );
                        SET @sql := IF(@has_wrong > 0 AND @has_target > 0,
                          'ALTER TABLE core_booking DROP COLUMN car_id_id',
                          'SELECT 1');
                        PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
                        """
                    ),
                    reverse_sql=("SELECT 1"),
                ),
            ],
            state_operations=[
                migrations.RenameField(model_name='booking', old_name='car_type', new_name='car_id'),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='car',
                    name='car_type',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cars', to='core.cartype'),
                ),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='rate',
                    name='car_type',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rates', to='core.cartype'),
                ),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='rate',
                    name='car',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rates', to='core.car'),
                ),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='booking',
                    name='car_id',
                    field=models.ForeignKey(db_column='car_id', on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='core.car'),
                ),
            ],
        ),
        migrations.RunPython(seed_initial_cartypes, migrations.RunPython.noop),
        migrations.RunPython(backfill_cartype_and_rates, migrations.RunPython.noop),
    ]


