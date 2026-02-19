#!/bin/bash

# Цвета для терминала
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}>>> Начинаем установку Atlevo Subscription Panel...${NC}"

# 1. Проверка на root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Ошибка: Запустите скрипт от имени root (sudo -i)${NC}"
  exit 1
fi

# 2. Установка зависимостей (Docker и Docker Compose)
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker не найден. Устанавливаем...${NC}"
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}Docker Compose не найден. Устанавливаем...${NC}"
    apt update && apt install docker-compose -y
fi

# 3. Создание структуры папок
mkdir -p /root/sub-panel
cd /root/sub-panel

# 4. Скачивание файлов напрямую из твоего GitHub (Raw ссылки)
echo -e "${GREEN}>>> Скачивание компонентов панели...${NC}"
BASE_URL="https://raw.githubusercontent.com/Atlevo/AtlevoSubsriptionPanel-for-3x-ui/main"

curl -sL "$BASE_URL/sub_manager.py" -o sub_manager.py
curl -sL "$BASE_URL/Dockerfile" -o Dockerfile
curl -sL "$BASE_URL/docker-compose.yml" -o docker-compose.yml
curl -sL "$BASE_URL/requirements.txt" -o requirements.txt

# 5. Сборка и запуск контейнера
echo -e "${GREEN}>>> Сборка и запуск в Docker...${NC}"
if docker compose version &> /dev/null; then
    docker compose up -d --build
else
    docker-compose up -d --build
fi

# 6. Итог
if [ $? -eq 0 ]; then
    IP=$(curl -s ifconfig.me)
    echo -e "${GREEN}==============================================${NC}"
    echo -e "Установка завершена! Панель работает в фоне."
    echo -e "Адрес: ${YELLOW}http://$IP:8081${NC}"
    echo -e "Логин/Пароль: ваши данные от 3x-ui"
    echo -e "${GREEN}==============================================${NC}"
else
    echo -e "${RED}Ошибка запуска. Проверьте логи командой: docker ps${NC}"
fi
