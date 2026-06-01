Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "python manage.py runserver 0.0.0.0:8002 --noreload", 0, False
