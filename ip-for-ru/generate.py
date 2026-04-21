import ipaddress
import json
import csv
import maxminddb
from pathlib import Path

IPINFO_CSV = "ipinfo_lite.csv"
MAXMIND_MMDB = "maxmind.mmdb"

WANTED = {"RU", "BY"}

KEYWORDS_AS = ["yandex", "kaspersky", "VKontakte", "LLC VK", "Rostelecom", "GRCHC", "ru-center", "EdgeCenter LLC", 
               "Vimpelcom", "CDNvideo", "Sovkombank", "Sberbank", "Alfa-Bank", "Russian Agricultural Bank", "ngenix", "SERVICEPIPE", 
               "DDOS-GUARD", "Moscow city telephone network", "ALEF-BANK", "Ruform LLC", "Nauka-Svyaz"]
               
KEYWORDS_DOMAIN = ["yandex", "kaspersky", "beeline", "stormwall", "edgecenter", "ngenix", "servicepipe", "rutube"]

FULL_DOMAIN = ["ya.ru", "yandex.net", "reg.ru", "mail.ru", "cloud.ru", "megafon.ru", "beeline.ru", "corbina.net", "mts.ru", "net.ru",
               "t2.ru", "rt.ru", "rostelecom.ru", "rtcomm.ru", "ertelecom.ru", "curator.pro", "nic.ru", "nichost.ru", "edgecenter.ru", "ddos-guard.net", "kaspersky.com", "drweb.com", "drweb.ru", "avito.ru"
               "sputnik.ru", "ok.ru", "rambler.ru", "ozon.ru", "reg.ru", "tinkoff.ru", "tbank.ru", "vk.com", "vk.ru", "vkontakte.ru", "vk.company", "cdnvideo.com", "cdnvideo.ru"
               "vtb.ru", "vtb.com", "vtb.ge", "vtb-bank.by", "vtb.am", "rshb.ru", "cft.ru", "variti.io", "koronapay.com", "mid.ru", "gov.ru", "rfc-cfa.ru", "farline.net",
               "donsattv.ru", "mobile-win.ru", "crelcom.ru", "xn--80ahgneri.net", "crimea-com.net", "crimea-com.ru", "ardinvest.net", "redi.su",
               "miranda-media.ru", "realnet.ru", "d-group.online", "mageal.ru", "m3x.org", "liveproxy.ru", "meshnet.su", "mytrinet.ru",
               "bestline.su", "tkmotel.ru", "skymaxsib.ru", "crimea.com", "sevstar.net", "sevtelecom.ru", "ubsnet.ru", "komfort21vek.ru", "avanta-telecom.ru", "reconn.ru"
               "airee.ru", "rusety.ru", "1city.org", "naukanet.ru", "ekma.is", "ekma-is.ru", "ugletele.com", "lds.online"]


def iso_from_maxmind(record: dict) -> str | None:
    if not isinstance(record, dict):
        return None
    country = record.get("country")
    if isinstance(country, dict):
        iso = country.get("iso_code")
        if isinstance(iso, str) and iso:
            return iso
    return None


def ipinfo_matches(row: dict) -> bool:
    if row.get("country_code") in WANTED:
        return True

    as_name = (row.get("as_name") or "").casefold()
    as_domain = (row.get("as_domain") or "").casefold()

    for kw in KEYWORDS_AS:
        kw = kw.casefold()
        if kw in as_name:
            return True
            
    for kw in KEYWORDS_DOMAIN:
        kw = kw.casefold()
        if kw in as_domain:
            return True

    for kw in FULL_DOMAIN:
        kw = kw.casefold()
        if kw == as_domain:
            return True
            
    return False


def main() -> None:
    base = Path(__file__).resolve().parent

    v4: list[ipaddress.IPv4Network] = []
    v6: list[ipaddress.IPv6Network] = []

    # IPinfo CSV
    ipinfo_path = base / IPINFO_CSV
    if not ipinfo_path.exists():
        raise FileNotFoundError(f"File not found: {ipinfo_path}")

    with ipinfo_path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if not ipinfo_matches(row):
                continue

            net_s = row.get("network")
            if not net_s:
                continue

            net = ipaddress.ip_network(net_s, strict=False)
            if net.version == 4:
                v4.append(net)
            elif net.version == 6:
                v6.append(net)
            else:
                raise ValueError(f"Unknown IP version: {net.version}")

    # MaxMind MMDB
    mmdb_path = base / MAXMIND_MMDB
    if not mmdb_path.exists():
        raise FileNotFoundError(f"File not found: {mmdb_path}")

    with maxminddb.open_database(str(mmdb_path)) as reader:
        for network, record in reader:
            if iso_from_maxmind(record) not in WANTED:
                continue

            net = ipaddress.ip_network(network, strict=False)
            if net.version == 4:
                v4.append(net)
            elif net.version == 6:
                v6.append(net)
            else:
                raise ValueError(f"Unknown IP version: {net.version}")

    v4 = list(ipaddress.collapse_addresses(v4))
    v6 = list(ipaddress.collapse_addresses(v6))

    all_nets = [*map(str, v4), *map(str, v6)]
    
    listsdir = base / "lists"
    
    # txt lst
    (listsdir / "ips-for-ru.lst").write_text("\n".join(all_nets) + ("\n" if all_nets else ""), encoding="utf-8")
    (listsdir / "ips-for-ru.txt").write_text("\n".join(all_nets) + ("\n" if all_nets else ""), encoding="utf-8")

    # json snippet
    payload = [
        {
            "ip": all_nets,
            "outboundTag": "RU",
        }
    ]
    (listsdir / "ips-for-ru-snippet.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # json snippet blancer
    payload = [
        {
            "ip": all_nets,
            "balancerTag": "BAL-RU",
        }
    ]
    (listsdir / "ips-for-ru-snippet-balancer.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
  
    # json singbox
    payload = {
      "version": 2,
      "rules": [
        {
          "ip_cidr": all_nets,
        }
      ]
    }
    (listsdir / "ips-for-ru-singbox.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    
    # yaml
    yaml_file = listsdir / "ips-for-ru.yaml"
    with yaml_file.open("w", encoding="utf-8", newline="\n") as f:
        f.write("payload:\n")
        for net in all_nets:
            f.write(f"    - {net}\n")

    print(f"IPv4: {len(v4)}")
    print(f"IPv6: {len(v6)}")
    print(f"Total: {len(all_nets)}")


if __name__ == "__main__":
    main()
