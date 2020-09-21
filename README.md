LoggerBotLogging
============================

Клиентская часть LoggerBot.

Сервер  -- https://github.com/WesBAn/LoggerBotLoggingServer

Установка
------------
    git clone https://github.com/den-bibik/LoggerBotLogging.git
    pip install -r requirements.txt

    export LOGGER_TOKEN=<LOGGER_TOKEN>
    
    LOGGER_TOKEN=md5 -s $user$password

len(LOGGER_TOKEN) должна быть равна 32
 
Пример
------------

    from bot_logging import RemoteLogger
    
    logger_name = ""
    logger = RemoteLogger(logger_name, user_name, user_host)
    
    logger.info("Hello World")
    
 Структура
 ------------
 ![structure image](structure.jpg)
 
 Основной класс RemoteLogger добавляет в стандартный Logger ProducerHandler. ProducerHandler и ConsumerThread сделаны по принципу Producer/Consumer паттерна. ProducerHandler посылает записи лолов в ConsumerThread через общую переменныу queue. ConsumerThread получает батч записей из queue и посылает их на сервер. ConsumerThread завершается тогда когда завершается последний Producer.
 
 ### Документация
```
source venv/bin/activate
export PYTHONPATH=`pwd`
python3 -m pydoc -p port bot_logging
```
По полученной ссылке можно посмотреть документацию

### Тестирование
Для тестирования используется стандартный фреймворк pytest
```
source venv/bin/activate
export PYTHONPATH=`pwd`
python -m unittest tests/test.py 
```

### Сборка колеса
```
source venv/bin/activate
python3 setup.py bdist_wheel