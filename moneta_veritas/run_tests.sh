#!/bin/bash
# run_tests.sh

echo "=== Запуск тестов проекта Moneta Veritas ==="
echo ""

# Установка coverage, если не установлен
pip install coverage > /dev/null 2>&1 || echo "Coverage уже установлен"

echo "1. Запуск тестов приложения catalog..."
python manage.py test catalog.tests -v 2

echo ""
echo "2. Запуск тестов приложения usercollections..."
python manage.py test usercollections.tests -v 2

echo ""
echo "3. Запуск тестов приложения homepage..."
python manage.py test homepage.tests -v 2

echo ""
echo "4. Запуск всех тестов с coverage..."
coverage run --source='.' manage.py test

echo ""
echo "5. Генерация отчета о покрытии..."
coverage report

echo ""
echo "6. Создание HTML отчета..."
coverage html
echo "HTML отчет создан в папке htmlcov/"

echo ""
echo "=== Тестирование завершено ==="