@echo off
cd /d D:\nile_app_shapefile_updated\nile_app_postgresql
start /B python manage.py runserver 0.0.0.0:8002 --noreload
exit
