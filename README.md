#Скрипт для расчета арбитражных сделок
Этот скрипт помогает осуществлять арбитражную торговлю на бирже криптовалюты [btc-e.com](https://btc-e.com)

##Системные требования
Скрипт написан на python 2.7. Скачать python можно на [официальном сайте](https://www.python.org/downloads/).  
Требуется "чистый" доступ в интернет, без прокси.  
Испытывался на WinXP, Win7, XUbubtu 14.xx

##Как этим пользоваться
Настройки скрипта прописываются в файле `config.py`.

Прописываем список валют которые **могут** участвовать в обмене в перменной `tradeSequence`.  
Стартовая валюта указывается в `startCurrency`.  
Количество обменов в цикле: `tradeLength`. Рекомендуемое значение: 3.  
Начальную сумма указывается в `startAmount`.
```python
tradeSequence = 'usd', 'nvc', 'btc', 'nmc'
startCurrency = 'usd'
tradeLength = 3
startAmount = 7.25
```

Запускаем `arbitrage.py` в Win или `python arbitrage.py` в Linux

Скрипт подключается к бирже, подкачивает условия торговли, состояние стаканов и предлагает результаты кругового обмена результат которого превышает начальную сумму.  
Цифрой выбираете предложенный вариант и скрипт показывает детализацию.