

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        # Keep your existing dependencies
        ('accounts', '0004_auto_20250415_1820'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- First handle first_name column
            DECLARE @sql NVARCHAR(MAX) = '';
            SELECT @sql = @sql + 'ALTER TABLE accounts_customuser DROP CONSTRAINT ' + name + ';' 
            FROM sys.default_constraints 
            WHERE parent_object_id = OBJECT_ID('accounts_customuser') 
            AND parent_column_id = COLUMNPROPERTY(OBJECT_ID('accounts_customuser'), 'first_name', 'ColumnId');
            EXEC sp_executesql @sql;
            ALTER TABLE accounts_customuser DROP COLUMN first_name;
            
            -- Then handle last_name column
            SET @sql = '';
            SELECT @sql = @sql + 'ALTER TABLE accounts_customuser DROP CONSTRAINT ' + name + ';' 
            FROM sys.default_constraints 
            WHERE parent_object_id = OBJECT_ID('accounts_customuser') 
            AND parent_column_id = COLUMNPROPERTY(OBJECT_ID('accounts_customuser'), 'last_name', 'ColumnId');
            EXEC sp_executesql @sql;
            ALTER TABLE accounts_customuser DROP COLUMN last_name;
            """,
            reverse_sql="""
            ALTER TABLE accounts_customuser ADD first_name NVARCHAR(150) NULL;
            ALTER TABLE accounts_customuser ADD last_name NVARCHAR(150) NULL;
            """
        ),
    ]