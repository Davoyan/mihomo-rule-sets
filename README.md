Этот репозиторий для моих правил маршрутизации в различных приложениях и конфигах.

---
## Список IP адресов для маршрутизации внутри России.

Список ip подсетей, сгенерированный из баз [IPinfo](https://ipinfo.io/data) + [MaxMind](https://github.com/P3TERX/GeoLite.mmdb/).
А так же из AS российских компаний, операторов или компаний связанных с Россией. Обновляется раз в сутки.

Из чего формируется:

* В одной из двух баз страна подсети 🇷🇺 RU или 🇧🇾 BY.
* В названии AS в базе ipinfo есть [следующие ключевые слова](https://github.com/Davoyan/mihomo-rule-sets/blob/main/ip-for-ru/generate.py#L12), регистронезависимо
* В домене AS в базе ipinfo есть [следующие ключевые слова](https://github.com/Davoyan/mihomo-rule-sets/blob/main/ip-for-ru/generate.py#L16), регистронезависимо
* Домен AS в базе ipinfo полностью совпадает с значением из [списка](https://github.com/Davoyan/mihomo-rule-sets/blob/main/ip-for-ru/generate.py#L18), регистронезависимо

Подсети собираются и агрегируются, уменьшая конечный вес до ~1мб / ~40к строк. Что решает проблему с недостатком оперативной памяти на ios.

#### [ip-for-ru/lists](https://github.com/Davoyan/mihomo-rule-sets/tree/main/ip-for-ru/lists)
* `ips-for-ru-singbox.json` - json для Singbox
* `ips-for-ru-singbox.srs`  - srs для Singbox
* `ips-for-ru-snippet.json` - snippet для Remnawave
* `ips-for-ru.lst` - TXT файл с подсетями
* `ips-for-ru.mrs`- mrs для Mihomo
* `ips-for-ru.txt` - TXT файл с подсетями
* `ips-for-ru.yaml` - yaml для Clash/Mihomo

---
## Список доменов для маршрутизации внутри России.

Генерируется из уже готовых списоков, удаляя повторы.

Из чего формируется:
* category-ru и российские компании ([full](https://github.com/Davoyan/mihomo-rule-sets/blob/main/scripts/category-ru.py#L46)) из репозитория MetaCubeX
* itdoginfo список [outside](https://raw.githubusercontent.com/itdoginfo/allow-domains/main/Russia/outside-raw.lst)
* hydraponique списки [category-ru](https://raw.githubusercontent.com/hydraponique/roscomvpn-geosite/master/data/category-ru) и [whitelist](https://raw.githubusercontent.com/hydraponique/roscomvpn-geosite/master/data/whitelist)
* legacy [домены](https://github.com/Davoyan/mihomo-rule-sets/blob/main/domains/category-ru-legacy.txt) из репозитория hydraponique, перед чисткой доменов, которые резолвятся в RU ip

#### [rules](https://github.com/Davoyan/mihomo-rule-sets/tree/main/rules)
* `category-ru.lst` - TXT файл с доменами
* `category-ru.mrs` - mrs для Mihomo
* `category-ru.yaml` - yaml для Clash/Mihomo

---
## Шаблон Ultimate Mihomo Ru для Remnawave

Исчерпывающее описание вы можете прочитать в [коментариях](https://github.com/Davoyan/mihomo-rule-sets/blob/main/remnawave-templates/ultimate-mihomo-ru.yaml#L1) в шаблоне

Использует списки и правила из этого репозитория.

<details>
<summary>📖 Инструкция в картинках</summary>

### 1. Открываем панель, ищем редактор пользовательского конфига Mihomo
<img src="https://github.com/user-attachments/assets/4a21f2ae-e8a4-41d5-a0f4-989a7a4bf2d7" width="300"/>

### 2. Редактируем шаблон По умолчанию, что отдаётся пользователям подписки
<img src="https://github.com/user-attachments/assets/bc1cad1b-af2b-425f-959d-dcfeb9cdca69" width="400"/>

### 3. Открываем меню с готовыми шаблонами конфигураций
<img src="https://github.com/user-attachments/assets/9def91bf-65d3-4abd-a22e-9359d95a642b" width="500"/>

### 4. Загружаем шаблон
<img src="https://github.com/user-attachments/assets/4f75c3e7-3bb3-4b8c-a5f5-4921edcd465b" width="700"/>

### 5. Сохраняям, применяя изменения
<img src="https://github.com/user-attachments/assets/5218f05c-23b9-4f49-8e83-b0e12defb061" width="450"/>
</details>

---
## Donation
Если вы вдруг захотите меня поддержать.

- **TON: `UQAMcrN7fDEX5BV4Ui9LpJeQj_OfDttUiQKz-UsbiQrpCkgZ`**
- **BTC: `bc1qxl05dhaxp5s3vpu4njx4mrzqfccqlhgfsp5dyu`**
- **SOL (SPL): `3qT7wRUKXiTmpXvLuxT9J4STPZqEhWbVcn4NgZPyLMLi`**
- **ETH (ERC20): `0x90DF7F6eD4d7d0bD8cA6790c0712D21f0a4da55D`**
- **Tron(TRC20)/USDT: `TX8NzurextBLzRCnuQhxM6mzwNZ2LMbanE`**
