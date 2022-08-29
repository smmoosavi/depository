# Depository

## development

```bash
export DJANGO_SETTINGS_MODULE=depository.settings.development
python manage.py loaddata depository/apps/structure/fixtures/initial_data.json
python manage.py loaddata depository/apps/accounting/fixtures/initial_data.json
python manage.py runserver
```