# Depository

## development

```bash
export DJANGO_SETTINGS_MODULE=depository.settings.development
python manage.py loaddata depository/apps/structure/fixtures/initial_data.json
python manage.py loaddata depository/apps/accounting/fixtures/initial_data.json
python manage.py runserver
```

## deploy

```bash
cd ansible
ansible-playbook server_playbook.yml -i hosts --private-key ~/.ssh/depository_id_rsa
# verbose:
# ansible-playbook server_playbook.yml -i hosts -vvv --private-key ~/.ssh/depository_id_rsa
```