
# Online databáze přístupových údajů
Autoři: Jakub Asszonyi, Matěj Vopálka, Vojta Hynek, Vojtěch Váňa


# Popis projektu.
bla bla bla


# Instalace projektu
Seznam použitých externích knihoven je v sourboru `requirements.txt`
Pro nainstalování potřebných knihoven použijte příkaz
```sh
pip install -r requirements.txt
```

## Instalace podpisové autority
Je zapotřebí soubor CA.py. 
Je využit jako knihovna pro ověřování v klientské i serverové části a zároveň slouží jak nástroj pro vygenerování klíčů, podepsání souborů a ověření podpisů pro kryptografické protokolu DSA (Digital Signature Algorithm).
Podpisová autorita může být samostatná entita, nebo může být součástí serveru, kdy uživatel věří vývojáři aplikace. Při obou případech se podpisová autorita nasadí příkazem
```sh
python3 CA.py −−generate
```
který vygeneruje pár klíčů `private_key.pem` a `public_key.pem`.
Privátní klíč je zašifrovaný heslem, které uživatel zadá při vygenerování a musí ho používat při podepisování.

## Instalace serveru
Je zapotřebí vygenerovat pár klíčů pro RSA příkazem 
```sh
python3 RSA_server.py
```
jehož výstupem jsou soubory `private_key_RSA.pem` sloužící jako soukromý klíč DSA a `public_key_RSA.pem` sloužící jako veřejný klíč DSA

Následně je třeba podepsat veřejný klíč RSA podpisovou autoritou.
Podpis je realizován příkazem
```sh
python3 CA.py −−sign public_key_RSA.pem
```
a výstupem je soubor `hash.sig`, který v případě samostatné podpisové autority musí být přesunut na server. Slouží jako podpis, kterým klient verifikuje identitu serveru.




## Instalace klienta
Pro instalaci klienta je jen zapotřebí vložit všechny potřebné soubory do příslušného adresáře, ze kterého poté budete Klienta spouštět.


## Spuštění Serveru

Pro spuštění serveru proveďte tento příkaz:
```sh
python3 Server_main.py
```
Toto zapne server. V terminálu se vypisuje pár základních informací o akcích které momentálně zpracovává.
Server umožňuje připojení více klientů současně, takže je tam také vypsáno klient a uživatel se připojit k serveru.


## Spuštění klienta
Spuštění klienta zadejte tento příkaz:
```sh
python3 Client.py
```

### Registrace nového uživatele
Spuštěním klienta a projitím registrací v podobě zadávání informací v příkazovém řádku se vytvoří identita klienta.
Tím se vytvoří pár klíčů DSA pro ověření uživatelského zařízení. 
Tento pár klíčů je pouze na zařízení využitém při registraci, ze kterého se stává podpisová autorita pro konkrétního uživatele a musí podepsat všechny ostatní podpisové veřejné klíče už pro konkrétní zařízení. 

Soukromý klíč je uložen jako `private_key_<username>.pem`.
Pro každé další první přihlášení z nového zařízení si musí uživatel vytvořit pár klíčů
pomocí pomocného nástroje příkazem 
```sh
python3 App_client_gen_dsa_tool.py
```
který vygeneruje pár klíčů `private_key_DSA_<username>.pem`, který je zašifrovaný heslem, které uživatel zadá a `public_key_DSA_<username>.pem`.
`public_key_DSA_<username>.pem` musí uživatel podepsat soukromým klíčem `private_key_<username>.pem` pomocí dalšího pomocného nástroje 
```sh
python3 App_client_sign_user.py
```
na původním zařízení na kterém se registroval a podpis obsažený v souboru `hash_<username>_verify.sig` přenést zpět na zařízení, které registroval.

### Uživatelské rozhraní aplikace
Po přihlášení je uživatel v přikazovém okně naší aplikace, lze poznat podle příkazového ukazatele
```sh
KryPi> 
```

Pro nápovědu a vypsání dostupných příkazu zadejte
```sh
KryPi> help

Documented commands (type help <topic>):
========================================
add  delete  edit  end  get  help  list  show
```

Pro podrobnější informace o funkčnosti konkrétní příkazu
Pro nápovědu a vypsání dostupných příkazu zadejte
```sh
KryPi> help add
Add a new entry
add [title]
```


Po dokončení uprav uknočíte relaci příkazem

```sj
KryPi> end
```
čímž se vaše data uloží na server. (Pokud někdy v průběhu úprav či registrace dojte k chybě, či přerušení spojení nebudou provedeny žádné změny.)


















