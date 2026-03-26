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
