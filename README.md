# Социальная сеть

Этот проект - это небольшая социальная сеть, в которой вы сможете публиковать посты, находить себе друзей и переписываться с ними.

### Установка

У вас должен быть установлен `python3` и `pip`
1. Установите зависимости:
   ```sh
   pip3 install -r requirements.txt
   ```
2. Настройте сайт с помощью создания файла `.env`. Вот пример файла:
   ```
   EMAIL_HOST_USER="имя пользователя от email, откуда будет рассылаться рассылка"
   EMAIL_HOST_PASSWORD="пароль"

   P.S простите за такое маленькое кол-во настроек, в будущем их будет больше :)

### Запуск

1. Создайте БД:
   ```sh
   python3 manage.py migrate
   ```
2. Запустите сервер
   ```sh
   python3 manage.py runserver
   ```
