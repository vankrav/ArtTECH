# Быстрый старт - ArUco Detector

## Установка и запуск

### 1. Активация виртуального окружения
```bash
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

### 2. Переход в папку cv
```bash
cd cv
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Диагностика камеры
```bash
python camera_diagnostics.py
```

### 5. Тестирование камеры
```bash
python camera_test.py
```

### 6. Запуск детектора
```bash
python main.py
```

## Альтернативные способы запуска

### Через Makefile
```bash
make setup    # Установка пакета
make diagnose # Диагностика камеры
make run      # Запуск детектора
make markers  # Генерация тестовых маркеров
```

### Как установленный пакет
```bash
make setup
aruco-detector
```

## Управление программой

- **Q** - Выход
- **P** - Вывод информации о маркерах в консоль

## Генерация ArUco маркеров для тестирования

```bash
python generate_markers.py --start 0 --end 5
```

Маркеры будут сохранены в папке `markers/`

## Дополнительная информация

Смотрите `cv/README.md` для полной документации и примеров использования.
