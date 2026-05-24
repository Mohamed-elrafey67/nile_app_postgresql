$proc = Start-Process -NoNewWindow -FilePath python -ArgumentList "manage.py runserver 0.0.0.0:8000 --noreload" -PassThru
$proc.Id | Out-File -FilePath D:\nile_app_shapefile_updated\nile_app\server_pid.txt
# Keep running so bash tool doesn't kill the child
while ($true) { Start-Sleep 10 }
