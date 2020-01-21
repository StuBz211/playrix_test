
## Тестовое задание
### на позицию Python Programmer

Для запуска необходим Python3 (программа проверялась на Python3.6)

Запуск 
```bash
python3 playerix.py -u <url> -t <github api token>
```

Доступные команды:
* **-u <адрес>** или **--url <адрес>**  - указание ссылки публичного репозитория (https://github.com/twbs/bootstrap)   
* **-df <дата>** или **--date_from <дата>** - дата начала, формат - (```2020-01-01```)
* **-dt <дата>** или **--date_to <дата>** - дата окончания, формат - (```2020-01-01```)
* **-b <имя ветки>** или **--branch <имя ветки>** - выбранное имя ветки, по умолчанию master (```master```)
* **-t <токен>** или **--token <токен>** - токен Api GitHub (```6b4db1a295a8a3376813febeefcc524640634f4d``` - не валидный токен)

Пример 1 
```bash
python3 playerix.py -u https://github.com/twbs/bootstrap -t 6b4db1a295a8a3376813febeefcc524640634f4d -df 2018-01-01 -dt 2020-01-01
```

Пример 2
```bash
python3 playerix.py --url https://github.com/twbs/bootstrap --token 6b4db1a295a8a3376813febeefcc524640634f4d --date_from 2018-01-01 --branch gh-pages
```


Для переодического выполнения программы можно использоваться **cron**
Для запуска редактирование необходимо ввести команду
```bash
crontab -e 
```
Для добавление задачи надо дописать строчку, к примеру:
```text
00 20 * * * /usr/bin/python3 /dir/to/playrix_text/playrix.py -u <url> -t <token>
```
скрипт будет выполнятся каждый день в 20:00,
подробнее [https://help.ubuntu.com/community/CronHowto]('https://help.ubuntu.com/community/CronHowto')


#### CI/DI 
Для CI/CD можно использовать например Jenkins - программа с открытым исходным кодом. 
Если уже используется GitLab в качестве репозитория, то гораздо проще будет использовать Gitlab-CI
