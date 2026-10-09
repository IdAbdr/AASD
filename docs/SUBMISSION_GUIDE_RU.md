# Что тебе нужно сделать для сдачи Assignment 3

## 1. Проверить проект на своём компьютере
Распакуй архив, включив скрытую папку `.git`, если программа распаковки её скрывает. Открой терминал в папке `ai-skin-disease-detector`, где лежит `app.py`.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe app.py
```
Открой http://127.0.0.1:5000. Загрузить можно обычную синтетическую картинку PNG/JPEG. Проверь результат, History и Export CSV. Изображение не диагностируется: программа вычисляет его характеристики. В полном наборе 20 тестов; здесь проверены только 9 тестов расчётов. Если есть ошибки, пришли текст ошибки.

## 2. Опубликовать public GitHub repository
Создай на github.com новый **Public** репозиторий `ai-skin-disease-detector-assignment3`. На странице создания не добавляй README, .gitignore и лицензию: они уже есть.

В терминале проекта настрой своё имя и email локально (подставь собственные данные). В поставленной папке уже есть три осмысленных коммита с нейтральным автором Project Preparation. Они отражают подготовку пакета, а не подтверждают, что ты самостоятельно создала их раньше. Твой следующий коммит будет от твоего имени.

```bash
git config user.name "YOUR NAME"
git config user.email "YOUR EMAIL"
git log --oneline
git remote add origin https://github.com/YOUR_USERNAME/ai-skin-disease-detector-assignment3.git
git push -u origin main
```
Для авторизации используй GitHub Desktop, credential manager или браузерный вход; пароль аккаунта в терминале не работает. Токены сюда присылать не нужно. Если скрытая `.git` потерялась: `git init -b main`, затем `git add .` и `git commit -m "Add research module, tests and CI"`, после чего добавь remote и выполни push.

Можно использовать GitHub Desktop: Add existing repository → выбрать папку проекта → Publish repository → убрать Keep this code private. Не публикуй папку upload или исходный архив с фотографиями и базой данных.

## 3. Дождаться CI и открыть Issues
Во вкладке Actions найди `CI and validated source delivery`. Нужны зелёные задания Python 3.11 и 3.12. При успешном запуске появятся два ZIP-артефакта. Запуск может выявить ошибки, которые не удалось проверить здесь; сначала устрани их.
Во вкладке Issues создай задачи из `ISSUES_TO_CREATE.md`. Первую закрой после проверки, указав фактический результат и ссылку на запуск. Наличие шаблонов в папке не заменяет настоящие GitHub Issues.

## 4. Дополнить отчёт
Отчёт подготовлен на английском, как задание. Открой `assignment3_report.html` в браузере на Windows: нажми Edit submission details, замени имя, группу, repository, workflow и successful run URL, обнови статус полного тестирования. Не придумывай успешный запуск до его завершения.
Сохрани заполненный HTML (кнопка Download updated HTML), затем Ctrl+P → Save as PDF, A4, scale 100%, margins None, выключи browser headers/footers. В HTML задан Times New Roman 12 pt, интервал 1.5 и выравнивание по ширине; требуется установленный Times New Roman. Готовый PDF в пакете использует Times-Roman как доступный здесь заменитель: для буквального выполнения требования шрифта экспортируй финальный PDF на Windows с Times New Roman. Проверь, что получилось 8-12 страниц и текст не обрезан.

## 5. Собрать доказательства
Сохрани 4-5 скриншотов: результат анализа, History, CSV, зелёный Actions и Issues/история коммитов. Они полезны для защиты; задание отдельно их не требует. Сдавай итоговый PDF и публичную ссылку на репозиторий. Отдельный публичный сайт не требуется.

## Что объяснить на защите
- Git хранит историю; GitHub размещает код, Issues и Actions.
- CI запускает lint и тесты при push/PR; delivery упаковывает только прошедший проверки код.
- extract_features делает повторяемые расчёты, SQLite хранит результаты, CSV нужен для дальнейшего анализа.
- Нейросеть и медицинская точность не реализованы. Для этого задания достаточно научного модуля обработки изображений.
- Здесь реально прошли 9 тестов, остальные проверки подтверждаешь своим запуском.
