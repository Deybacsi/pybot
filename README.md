# Install

Első futtatás előtt nevezd át a `default_settings.txt`-t `settings.txt` névre.

## Linux:

Valamint:
```
pip install python-binance
```

### Raspberry pi:

Ha régi a raspbian:
Error : 
```
E: Repository 'http://raspbian.raspberrypi.org/raspbian buster InRelease' changed its 'Suite' value from 'stable' to 'oldstable'
N: This must be accepted explicitly before updates for this repository can be applied. See apt-secure(8) manpage for details.
```
Solution:
```
sudo apt-get update --allow-releaseinfo-change
sudo apt install python3-pip
pip3 install python-binance
```

## Windows

Python letöltése innen: https://www.python.org/downloads/

Indítás után "Add python.exe to PATH"-hoz pipa, majd "Install now", és "Disable path length limit", Close

Win+R, szövegmezőbe `cmd` beír, majd enter

A megjelenő cmd ablakba: 

```
pip install python-binance
pip install windows-curses
```

A `pybot.py`-on duplaklikk a gyári windows cmd ablakban indítja a botot. Ha itt üres fekete képernyő fogad, akkor nagyobbra kell venni az ablakméretet. 


# settings.txt

Beállítások:

```
{
    "testmode": true,
    "apikey": "XXXXX",
    "apisecret": "XXXXX",
    "tapikey": "XXXXX",
    "tapisecret": "XXXXX"    
}
```

## testmode:

**True**: Binance sandbox használata, JÁTÉKPÉNZZEL

Ez esetben a "**tapikey**" és "**tapisecret**" értékeket kell kitölteni.

API key-t a https://testnet.binance.vision/key/generate oldalon lehet generáltatni, Github account kell hozzá.

Keygenerálás után a létrejövő Binance sandbox accountba minden kereskedhető coinból leoszt a rendszer egy szép adagot egyenlegként. Pl 1BTC, 10 000 USDT, stb.
Az egyenlegek, és egyéb adatok havonta resetelődnek az eredeti állapotra.

**False**: VALÓS TRADING, VALÓS PÉNZZEL!

Az "**apikey**" és "**apisecret**" párost kell megadni.

API key generálás: https://www.binance.com/en/my/settings/api-management

A key restrictionsnél az *"Enable Spot & Margin Trading"* engedélyt meg kell adni. A létrehozott key alapállapotban 90 napig érvényes, utána kézzel meg kell hosszabbítani.

Ha beállítasz IP cím alapú korlátozást, akkor lehet korlátlan ideig érvényes keyt létrehozni.

# Kereskedési párok

A bot több párral is tud egyszerre kereskedni, ezeknek a beállításait a *pairs* folderben létrehozott `.txt` fileokban kell megadni.

A bot "thread" névvel jelöli a különböző beállított párokat.
Lehetséges ugyanolyan párokat létrehozni, különböző idő/profit beállításokkal. (Ugyanolyannal is lehet, mint egy már létező, de annak sok értelme nincs :D )

## pairs/x.txt

A file neve bármi lehet, csak annyi a lényeges, hogy .txt kiterjesztése legyen. Más fileokat nem vesz figyelembe a bot.

A file nevével fog a bot hivatkozni az adott kereskedési párunkra a felületen.

Tartalmuk:
```
{
    "asset1": "BTC",
    "asset2": "USDT",
    "quantity": 15,
    "candlestobuy": 3,
    "candlestosell": 3,
    "minprofit" : 0.5,
    "stopped": false
}
```

**asset1, asset2:**

A kereskedési pár nevei, értelemszerű.

**quantity:**

A "tőke" összege, amivel a bot gazdálkodhat.

A fenti példa alapján ez 15 USDT, vételi szándéknál ennyiért próbál meg majd BTC-t venni. Eladásnál értelemszerűen a 15 USDT-ért vett BTC-t próbálja meg mag eladni, drágábban.

**candlestobuy, candlestosell:**

Hány gyertyányi ideig legyen az ár a mozgóátlagok alatt (candlestobuy), vagy felett (candlestosell)

Jelen esetben 15 perces gyertyákkal dolgozik, vagyis egy candlestobuy=3 azt jelenti, hogy az árnak 3*15=45 percig az MA-k alatt kell lennie, hogy a bot vásároljon.

Az értelme az, hogy tartós árfolyam esésnél (trendnél) vásároljon a bot, és ne egy-egy hirtelen leszúrásnál.

Ugyanez fordítva eladásnál, 3*15 percig az MA-k fölött tartózkodó árnál a bot elad, HA:

**minprofit:**

A minimum profit, amit keresni szeretnénk egy tranzakción, százalékban.

A 0.5 fél százalékot jelent. A bot addig nem ad el, amíg ez nem teljesül.

Hátránya: a buy order után "beragadhatunk", ha lefelé tartó trend van, és az aktuális ár sosem éri el a megadott profitszintet. Megoldást lásd a `.trades` fileoknál.

**stopped** - jelenleg not implemented
Hogy ne kelljen fileokat törölgetni/moveolni, itt kikapcsolható (lesz) az adott kereskedési szál. 

## pairs/x.trades

A `.txt` konfig fileokban megadott párokkal eddig végzett tranzakciók adatai (majdnem) JSON formátumban, lefele időrendben. 
A bot ezekből dolgozik, és tudja, hogy éppen venni vagy eladni kell, valamint ezek adataiból számolja a profit %-okat. Kézzel szerkesztésük nem ajánlott, ha nem tudod mit csinálsz.
Ha a file nem létezik, a bot létrehozza, és a kereskedés folyamán szépen feltölti adatokkal.
Hasznos lehet majd jövőbeni összesített statisztikákhoz, stb.
Egy esetleges fent említett zuhanó trend árfolyam beragadásnál a legutolsó BUY ordert kitörölve a bot "elfelejti" azt, és így nem akar majd sell-el próbálkozni. Újraindítás után megint venni akar majd.

## debug.log, candledata.log

Szemét, debug fileok

# Tudnivalók

**Kilépés**: ESC

**Kereskedési párok váltása**: számbillentyűk 0-9 (10-nél több threadet elvben képes kezelni, de UI kijelzés nélkül)

Bármelyik file (`.txt` vagy `.trades`) szerkesztése után érdemes a botot újraindítani. (Bár a `.trades`-eket beolvassa percenként)

Mivel ez még eléggé work in progress verzió, így a bot megáll, ha

- fileok hiányoznak
- settings.txt rossz
- nincs elég egyenleged (vételnél asset2, eladásnál asset1)
- nincs internetkapcsolat (néha a Binance sandbox api endpoint is szarakodik) 
- az ablakméret nem elég nagy, bár ez javarészt már javítva lett (ha addwstr errorral száll el, akkor nagyobbra kell venni az ablakot)
- egyéb hibák :)

A test modeban az árfolyam **nem tükrözi** a valós piaci adatokat, mivel rengetegen rángatják a sandboxon belül az árakat fel/le.
Így a test tradek és tranzakciók csak nagyjából lesznek egálban az aktuális valósággal. Emellett mivel hihetetlen nagy kilengések is vannak az árban, a gyertyák esetlegesen extrém low/high értékei felül vannak írva, és maximálva vannak akt ár +- 0.1%-ban. Erre azért volt szükség, mert pl BTC esetén voltak olyan gyertyák, amiknél a low 18k a high pedig 90k volt, ezzel eléggé tönkretéve a chartot, és lehetetlenné téve a tesztelést.

Egyelőre csak linuxon lett tesztelve a bot, windowson **elvileg** ugyanúgy működnie kell.

## Linux scriptek

### start_screen_linux.sh

Screen-el háttérbe rakja a botot, hogy ssh-n keresztül futtatva ne álljon le, ha az ssh kapcsolat megszakad.

### list_screen.sh

Kilistázza az aktuális futó screen sessionöket

### switch_to_screen.sh

Átvált a háttérben futó screen sessionre. 


