from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Инициализация авторизации
gauth = GoogleAuth()

# Пробуем загрузить сохранённый токен (если есть)
gauth.LoadCredentialsFile("credentials.json")

# Если токена нет или он устарел → запускаем авторизацию
if gauth.credentials is None or gauth.access_token_expired:
    gauth.LocalWebserverAuth()  # Откроет браузер (только 1 раз!)
    gauth.SaveCredentialsFile("credentials.json")  # Сохраняем токен
else:
    gauth.Authorize()  # Используем сохранённый токен

# Теперь можно работать с Google Drive
drive = GoogleDrive(gauth)

# Пример: выводим список файлов
file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file in file_list:
    print(f"Файл: {file['title']}, ID: {file['id']}")