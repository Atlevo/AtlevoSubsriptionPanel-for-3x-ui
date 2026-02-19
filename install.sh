#!/bin/bash

# Цвета для красоты в терминале
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}>>> Запуск установки Atlevo Subscription Panel...${NC}"

# 1. Проверка Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker не найден. Устанавливаем...${NC}"
    curl -fsSL https://get.docker.com | sh
fi

# 2. Проверка Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose не найден. Устанавливаем...${NC}"
    apt update && apt install docker-compose -y
fi

# 3. Подготовка папки проекта
mkdir -p /root/sub-panel
cd /root/sub-panel

# 4. Скачивание файлов из твоего GitHub
echo -e "${GREEN}>>> Загрузка файлов из репозитория Atlevo...${NC}"
REPO_URL="https://raw.githubusercontent.com/Atlevo/AtlevoSubsriptionPanel-for-3x-ui/main"

curl -sL "$REPO_URL/sub_manager.py" -o sub_manager.py
curl -sL "$REPO_URL/Dockerfile" -o Dockerfile
curl -sL "$REPO_URL/docker-compose.yml" -o docker-compose.yml
curl -sL "$REPO_URL/requirements.txt" -o requirements.txt

# 5. Сборка и запуск контейнера
echo -e "${GREEN}>>> Сборка Docker-образа и запуск...${NC}"
docker-compose up -d --build

# 6. Финальная проверка
if [ $? -eq 0 ]; then
    IP=$(curl -s ifconfig.me)
    echo -e "${GREEN}==============================================${NC}"
    echo -e "${GREEN}Установка успешно завершена!${NC}"
    echo -e "Панель доступна по адресу: ${YELLOW}http://$IP:8081${NC}"
    echo -e "Используйте логин/пароль от вашей панели 3x-ui."
    echo -e "${GREEN}==============================================${NC}"
else
    echo -e "\033[0;31mПроизошла ошибка при запуске Docker-контейнера.\033[0m"
fi
