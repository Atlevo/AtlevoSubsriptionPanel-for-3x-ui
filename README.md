Вайбкодинг в чистом виде. Захотелось хоть как-то автоматизировать создание юзеров в 3x-ui (особенно когда у тебя много инбаундов).

🚀 Atlevo Subscription Panel for 3x-ui

Удобная и легкая веб-панель на базе Streamlit для управления пользователями и подписками в 3x-ui. Полностью автоматизирована и готова к работе через Docker.
✨ Основные возможности

    Управление клиентами: Просмотр лимитов трафика, сроков действия и UUID.

    Генератор ссылок: Удобное копирование ссылок на подписки.

    Безопасность: Авторизация использует те же учетные данные, что и ваша основная панель (через bcrypt).

    Docker-native: Изолированная среда, не засоряющая основную систему.

🛠 Быстрая установка (One-Line Install)

Просто запустите эту команду на сервере, где установлен 3x-ui:
Bash

wget -qO- https://raw.githubusercontent.com/Atlevo/AtlevoSubsriptionPanel-for-3x-ui/main/install.sh | bash

    Что сделает скрипт?

        Проверит наличие Docker и Docker Compose (и установит их, если нужно).

        Создаст рабочую директорию /root/sub-panel.

        Скачает все необходимые файлы из этого репозитория.

        Соберет и запустит контейнер на порту 8081.

⚙️ Ручная настройка

Если вы хотите развернуть панель вручную:

    Клонируйте репозиторий:
    Bash

    git clone https://github.com/Atlevo/AtlevoSubsriptionPanel-for-3x-ui.git
    cd AtlevoSubsriptionPanel-for-3x-ui

    Проверьте пути в docker-compose.yml:
    Убедитесь, что путь к вашей базе данных указан верно (по умолчанию /etc/x-ui/x-ui.db).

    Запустите:
    Bash

    docker-compose up -d --build

🔑 Вход в панель

    Адрес: http://IP_ВАШЕГО_СЕРВЕРА:8081

    Логин: Ваш логин от панели 3x-ui.

    Пароль: Ваш пароль от панели 3x-ui.

📂 Структура проекта
Файл	Описание
sub_manager.py	Ядро приложения на Streamlit
Dockerfile	Рецепт сборки Python-образа
docker-compose.yml	Конфигурация запуска и проброс портов
install.sh	Скрипт автоматической установки
⚠️ Важные замечания

    Права доступа: Для корректной работы Docker должен иметь доступ к базе данных. Если панель не видит данные, выполните:
    chmod 644 /etc/x-ui/x-ui.db

    Порты: Убедитесь, что порт 8081 открыт в вашем фаерволе (UFW/iptables).


🚀 Atlevo Subscription Panel for 3x-ui

Pure "Vibe Coding" in action. Created out of a desire to automate user management in 3x-ui, especially when dealing with a large number of inbounds.

This is a lightweight, web-based dashboard built with Streamlit to manage users and subscriptions. It's fully automated and ready to run via Docker.
✨ Key Features

    Client Management: View traffic limits, expiry dates, and UUIDs at a glance.

    Link Generator: Easy copying of subscription links for your users.

    Integrated Security: Uses your existing 3x-ui credentials for login (powered by bcrypt).

    Docker-native: Runs in an isolated environment without cluttering your main system.

🛠 One-Line Install

Run this command on the server where 3x-ui is installed:
Bash

wget -qO- https://raw.githubusercontent.com/Atlevo/AtlevoSubsriptionPanel-for-3x-ui/main/install.sh | bash

What does the script do?

    Checks for Docker and Docker Compose (installs them if missing).

    Creates the working directory: /root/sub-panel.

    Downloads all necessary files from this repository.

    Builds and starts the container on port 8081.

⚙️ Manual Setup

If you prefer to deploy the panel manually:

    Clone the repository:
    Bash

    git clone https://github.com/Atlevo/AtlevoSubsriptionPanel-for-3x-ui.git
    cd AtlevoSubsriptionPanel-for-3x-ui

    Verify paths in docker-compose.yml:
    Ensure the path to your database is correct (default is /etc/x-ui/x-ui.db).

    Launch:
    Bash

    docker-compose up -d --build

🔑 Accessing the Panel

    Address: http://YOUR_SERVER_IP:8081

    Username: Your 3x-ui login.

    Password: Your 3x-ui password.

📂 Project Structure
File	Description
sub_manager.py	Core application logic (Streamlit)
Dockerfile	Python build recipe
docker-compose.yml	Container configuration & port mapping
install.sh	Automated installation script
⚠️ Important Notes

    Database Permissions: For Docker to function correctly, it must have access to the database file. If the panel cannot read the data, run:
    chmod 644 /etc/x-ui/x-ui.db

    Firewall: Ensure port 8081 is open in your firewall (UFW/iptables).
