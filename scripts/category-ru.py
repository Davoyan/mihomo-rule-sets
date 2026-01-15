import requests
import sys
from pathlib import Path

def remove_overlaps(domains: set[str]) -> list[str]:
    sorted_domains = sorted(domains, key=lambda d: d.count("."))
    result = set()

    for domain in sorted_domains:
        parts = domain.split(".")
        skip = False
        for i in range(1, len(parts)):
            parent = ".".join(parts[i:])
            if parent in result:
                skip = True
                break
        if not skip:
            result.add(domain)

    return list(result)


def main():
    base = Path(__file__).parent

    ru_urls = [
        "https://raw.githubusercontent.com/hydraponique/roscomvpn-geosite/master/data/category-ru",
        "https://raw.githubusercontent.com/itdoginfo/allow-domains/main/Russia/outside-raw.lst",
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ru.list",
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/drweb.list",
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/mailru.list",
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/mailru-group.list",
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/avito.list",
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/yandex.list",
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/kaspersky.list"
    ]

    ru_domains = set([
        "2ip.ru", "yandex", "emias.info", "boosty.to", "donationalerts.com", "memealerts.com",
        "mycdn.me", "ozonusercontent.com", "mradx.net", "mvk.com", "userapi.com",
        "vk-apps.com", "vk-cdn.me", "vk-cdn.net", "vk-portal.net", "vk.cc", "vk.com",
        "vk.company", "vk.design", "vk.link", "vk.me", "vk.team", "vkcache.com", "vkgo.app",
        "vklive.app", "vkmessenger.app", "vkmessenger.com", "vkuser.net", "vkuseraudio.com",
        "vkuseraudio.net", "vkuserlive.net", "vkuservideo.com", "vkuservideo.net",
        "5post.market", "chizhik.club", "okolo.app", "perekrestok.com",
        "x5.ai", "x5.com", "x5.digital", "x5.group", "x5.media", "x5.team", "x5.tech", "x5static.net",
        "yandex.fi", "yastatic.net", "naydex.net", "yandex.fr", "yandex-bank.net", "yandex.aero",
        "yandex.az", "yandex.by", "yandex.cloud", "yandex.jobs", "yandex.com", "yandexwebcache.org",
        "yandexcom.net", "yandexcloud.net", "yandexadexchange.net", "yandex.kg", "yandex.de",
        "yandex.ee", "yandex.eu", "rostaxi.org", "yandex.uz", "yandex.kz", "yandex.lt",
        "yandex.lv", "yandex.md", "yandex.net", "yandex.org", "yandex.pl", "yandex.st",
        "yandex.sx", "yandex.tj", "yandex.tm", "yandex.ua", "yandex.com.ua", "yandex.com.tr",
        "yandex.com.ge", "yandex.com.am", "yandex.co.il", "yandex-images.clstorage.net"
    ])

    for url in ru_urls:
        print("Скачиваю:", url)
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"\n❌ Ошибка при скачивании {url}: {e}")
            sys.exit(1)
            return

        for line in resp.text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            for prefix in ("domain:", "host:", "full:"):
                if line.startswith(prefix):
                    line = line[len(prefix):]

            if line.startswith("+."):
                line = line[2:]

            ru_domains.add(line.strip())

    ru_domains_filtered = sorted(remove_overlaps(ru_domains))

    current_dir = Path(__file__).resolve().parent
    
    output_path = current_dir.parent / "rules" / "category-ru.yaml"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with output_path.open("w", encoding="utf-8") as f:
        f.write("payload:\n")
        for d in ru_domains_filtered:
            f.write(f"    - +.{d}\n")
            
    lst_path = current_dir.parent / "rules" / "category-ru.lst"
    with lst_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(ru_domains_filtered) + "\n")
        
    print(f"РУ доменов: {len(ru_domains_filtered)}")
    print("Готово! Финальный конфиг ->", output_path)


if __name__ == "__main__":
    main()
