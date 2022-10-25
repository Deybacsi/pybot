# Szuper ToDaMoon Binance python trading bot v0.1

Binance kereskedőrobot mozgóátlagok alapján. (Nem a hagyományos MA crossing method)

### Funkciók:
- TESZT mód Binance sandboxban, **JÁTÉKPÉNZZEL**
- Több kereskedési pár kezelése egyidejűleg
- Beállítható minimum profit
- Kicsi erőforrásigény
- Futtatható Windowson és linuxon is
- Könnyű beállítás

### Előnyei:
- Oldalazó trendnél (0.5%-1% profit beállítással) akár napi 1-2 tranzakció is **lehetséges**
- Oldalazásnál a beállított profit%/tranzakció **nagyjából** garantált (lásd lent)

### Hátrányai:
- Emelkedő, vagy zuhanó trendnél nem hatékony, vagy egyáltalán nem kereskedik
- A túl magasra állított profit %, vagy a nem oldalazó trend miatt ritka tranzakciók lehetnek, esetleg olyan vásárlások, amiknek az eladási feltételei soha nem teljesülnek (bentragadsz az adott coinban, amit drágán vettél)

**A fentiekből jól látszik, hogy ez a megoldás RIZIKÓS, úgyhogy a szokásos szöveg: ha élesben játszol, csak annyit kockáztass, amit nem sajnálsz elveszíteni.
Semmilyen felelősséget nem vállalok a veszteségeidért.**

## Jelenleg ajánlott test mode-ban futtatni!
## Éles használata csak saját felelősségre!

# Működés

A bot 3 mozgóátlagot (Moving Average=MA) - 7,25,99 figyel, és ezeknek az aktuális árhoz, és a beállított historikus adatokhoz viszonyított értékét.

Jelenleg csak a Binance tőzsdét támogatja, semmi mást nem.

Az általa használt MA indikátorok beállíthatóak a Binance felületén az alábbi módon:

![binance setup moving avergaes](docs/binance-MA-settings.png)

Így a tőzsdén közvetlenül is ellenőrizhető az aktuális állapot, amit a bot "lát".

Az alapelv viszonylag egyszerű:
- Ha az aktuális ár az MA-k **alatt** van, akkor **vesz**
- Ha az aktuális ár az MA-k **felett** van, akkor **elad**

Emellett megadható, hogy mennyit várjon az ár MA alá esése után a vásárlással, és MA fölé emelkedés után az eladással.

### Példa:

![binance price example](docs/binance-example.png)

A színes vonalak a mozgóátlagok. Ha beesik az árfolyam alájuk, az egy **lehetséges** vételi pozíciót jelez.

Mivel nem lenne szerencsés, ha egy-egy hirtelen leszúrás, vagy nagyon kis beesés egyből egy vételt generálna, így érdemes várni még egy kicsit. Hirtelen leszúrásnál lehetséges, hogy mire a bot eszmél (percenként néz árat), addigra az ár már teljesen máshol jár.
Emellett, ha az MA-k alá csak nagyon kicsivel esik az ár, és egyből veszünk, vagy fordított esetben eladunk, az rontja a későbbi profitunkat is. Érdemes a valamivel tartósabb kilengésekre várni, mert értelemszerűen minél olcsóbban szeretnénk venni, és minél drágábban eladni.

A képen látható `candlestobuy` beállítás szerint 3 gyertyányit várunk, mindháromnak az átlagok alatt kell zárnia, mire a következőnél *valahol* egy tényleges vásárlás fog történni. (Amikor a bot majd épp frissíti az árakat)

Párja a `candlestosell`, ami jelenleg szintén 3 gyertyányit vár, mire a következő feltétel megvizsgálásra kerül: az eladási ár magasabb legyen, mint a vételi. (`minprofit` beállítás)

A minimum profit szintet érdemes 0.1% fölé állítani, mivel ennyi a Binance alap tranzakciós díja. Kisebb értékkel kizárólag veszteségesen működik a bot.

A fenti példa egy ideális esetet mutat be.

### Zuhanó trendnél:
![binance bear trend example](docs/binance-example-bear.png)

A vétel után az ár tovább esik, majd oldalaz. Így az MA-k idővel ellaposodnak, és hiába lesz magasabb az ár náluk, mégis veszteséges lenne az eladás -> beragadtunk.

2 lehetőség van:

- Ha `minprofit` > 0 -> várunk addig, amíg az ár a vételi ár fölé visszamegy, hogy profitunk legyen
- Ha `minprofit` = 0 -> elad**hat**unk veszteséggel, és **ha mázlink van**, az oldalazásból elkezdünk profitálni megint, mint az alábbi képen.

    Látszik, hogy az ár még mindig nem érte el a kezdeti 19 282$-os szintet, de az esés utáni oldalazásnál csinált 2 sikeres tradet, amivel már pluszban vagyunk. (ez nem garantált, vagyis lehetséges további veszteség is, ha tovább esik az ár!)
    ![binance bear trend example with loss then profit](docs/btcusdt-orders-with-loss-then-profit.png)

Viszonylag jó taktika lehet olyan párokkal kereskedni, amiknek hiszünk a hosszútávú sikerében, így nem zavar, ha beragadunk egy magasabban árfolyamon. (Jelen esetben pl BTC-ben)

### Emelkedő trendnél
![binance bull trend example](docs/binance-example-bull.png)

Eladás után nincs vételi szignál, hiszen az ár sosem esik be az MA-k alá.

Amikor az oldalazás visszaáll, a bot folytatja a kereskedést.

Ilyen szituációknál viszont frusztráló lehet a rengeteg kihagyott lehetőség :)

## Felület

![trading bot gui](docs/gui.png)

Kicsit még szellős, sok az üres rész, a későbbiekben majd ez is fejlesztve lesz.

**Kilépés**: ESC

**Kereskedési párok váltása**: számbillentyűk 0-9 (10-nél több threadet elvben képes kezelni, de UI kijelzés nélkül)

Mivel a szálak számai a filenevek abc sorrendjéből adódnak, így a számozás hozzárendelhető direkt filenevekhez, az alábbi elnevezésekkel:

```
0-btcusdt.txt
1-ethudst.txt
2-akarmi.txt
3-harmas-thread.txt
...
```


# Telepítés

Első futtatás előtt nevezd át a `default_settings.txt`-t `settings.txt` névre, majd töltsd ki a megfelelő adatokkal. (Lásd lent)

A `pairs`-ben található `BTCUSDT.example` egy minta a kereskedési párok beállításához. Ezt lemásolva, átnevezve `valami.txt`-re hozhatod létre a párjaidat.

A file neve bármi lehet, de `.txt` kiterjesztése legyen. Más fileokat nem vesz figyelembe a bot.

Minden pár külön saját beállítás filet igényel.

## Linux:

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

Python letöltése: https://www.python.org/downloads/

Indítás után "Add python.exe to PATH"-hoz pipa, majd "Install now", és "Disable path length limit", Close

Win+R, szövegmezőbe `cmd` beír, majd enter

A megjelenő cmd ablakba: 

```
pip install python-binance
pip install windows-curses
```

A `pybot.py`-on duplaklikk a gyári windows cmd ablakban indítja a botot. Ha itt üres fekete képernyő fogad, akkor nagyobbra kell állítanod az ablak méretét. 


# settings.txt

A bot alapbeállításai.

Tartalma:

```
{
    "testmode": true,
    "apikey": "XXXXX",
    "apisecret": "XXXXX",
    "tapikey": "XXXXX",
    "tapisecret": "XXXXX"    
}
```

**testmode**:

- **true**: Binance sandbox használata, **JÁTÉKPÉNZZEL**

    Ez esetben a "**tapikey**" és "**tapisecret**" értékeket kell kitölteni.

    API key-t a https://testnet.binance.vision/key/generate oldalon lehet generáltatni, [Github account](https://github.com/signup) kell hozzá.

    Keygenerálás után a létrejövő Binance sandbox accountba minden kereskedhető coinból leoszt a rendszer egy szép adagot egyenlegként. Pl 1BTC, 10 ETH, 10 000 USDT, stbstb.

    Az egyenlegek, és egyéb adatok havonta resetelődnek az eredeti állapotra! Ezt a Binance automatikusan végzi, a botnak nincs rá hatása.

- **false**: VALÓS TRADING, **VALÓS PÉNZZEL!**

    Az "**apikey**" és "**apisecret**" párost kell megadni.

    API key generálás: https://www.binance.com/en/my/settings/api-management

    A key restrictionsnél az *"Enable Spot & Margin Trading"* engedélyt meg kell adni, különben a bot nem tud kereskedni.
    
    MÁS ENGEDÉLY NEM SZÜKSÉGES! Sőt, ajánlott semmi mást nem engedélyezni.
    
    A létrehozott key alapállapotban **90 napig érvényes**, utána kézzel meg kell majd ezen az oldalon hosszabbítani.

    Ha beállítasz IP cím alapú korlátozást, akkor lehet korlátlan ideig érvényes keyt létrehozni. Ehhez értelemszerűen fix IP kell, szóval saját szerver, VPS, stb.

# Kereskedési párok

A bot több párral is tud egyszerre kereskedni, ezeknek a beállításait a `pairs` folderben létrehozott `.txt` fileokban kell megadni.

A bot "thread" névvel jelöli a különböző beállított párokat.
Lehetséges ugyanolyan párokat létrehozni, különböző idő/profit beállításokkal. (Teljesen ugyanolyannal is lehet, mint egy már létező, de annak sok értelme nincs :D )

A beállítható párok száma **elvben** végtelen, de ennek határt szabnak a számítógépben lévő memória, az internetkapcsolat, és többek között a Binance API query limitjei is. Talán query/IP limit is van.

Emellett az adatok lekérése láthatóen nem túl gyors, így 20-50-100 párnál a bot működése jelentősen belassulhat. Mire lehúzza az árakat, azok már rég elvavultak, így múltbeli adatokkal dolgozik, ami veszteséget okozhat.

A Binance sandbox a teszteléshez **nem biztosít minden párat**, csak kb 20-at. Ezek megtalálhatók a `testmode-binance-pairs.txt`-ben.

## pairs/x.txt

A file neve bármi lehet, csak annyi a lényeges, hogy .txt kiterjesztése legyen. Más fileokat nem vesz figyelembe a bot. (pl a `BTCUSDT.example`-t sem, ami mintaként használható)

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

A fenti példa alapján ez 15 USDT, vételi szándéknál ennyiért próbál meg majd BTC-t venni. Eladásnál értelemszerűen a 15 USDT-ért vett BTC-t próbálja meg majd eladni, drágábban.

Nem érdemes a Binance által engedett minimális order szintre állítani. Pl ha veszel 10 USDT-ért ETH-t, ebből lejön a trading fee, vagyis kapsz 9.9$-nyi eth-t. Az eladáshoz viszont min 10$-nyi ETH kellene, az order beragadt. (A számok most csak példa jellegűek voltak, nézz utána a minimum összegeknek)

**candlestobuy, candlestosell:**

Hány gyertyányi ideig legyen az ár a mozgóátlagok alatt (candlestobuy), vagy felett (candlestosell)

Jelen esetben 15 perces gyertyákkal dolgozik, vagyis egy candlestobuy=3 azt jelenti, hogy az árnak 3*15=45 percig az MA-k alatt kell lennie, hogy a bot vásároljon.

Ugyanez fordítva eladásnál, 3*15 percig az MA-k fölött tartózkodó árnál a bot elad, HA:

**minprofit:**

A minimum profit, amit keresni szeretnénk egy tranzakción, **százalékban**.

A `0.5` fél százalékot jelent. A bot **addig nem ad el**, amíg ez nem teljesül. 

### Ebből a %-ból levonásra kerül a trading fee! Alapesetben ez 2*0.1%! (1 buy + 1 sell order)

Vagyis a 0.5% beállítás nagyjából 0.3%-ot jelent majd. Emellett előfordult már olyan eset, amikor ez a % azért nem teljesül, mert mire "beér" a tőzsdére a sell market order, az ár beesik. Ez főképp teszt környezetben gyakori, a hirtelen fel/le mozgások miatt.

![buy order with profit](docs/ethusdt-orders-with-profit.png)

Természetesen a tényleges profitunk lehet magasabb is, ha az ár nagyobbat ugrik felfelé, mint a beállított érték.

![buy order with profit](docs/btcusdt-orders-with-profit.png)


Hátránya: a buy order után "beragadhatunk", ha lefelé tartó trend van, és az aktuális ár sosem éri el a megadott profitszintet. Megoldást lásd a `.trades` fileoknál. Lehet, hogy sokáig nem lesz eladás, viszont "garantált(abb)" a profit.

Lehetséges a `minprofit` értékét nullára is állítani, így a nagyobb esések után, amikor az MA-k "kisimulnak", a bot eladja majd amit vett, valószínűleg veszteséggel.

![buy order with loss](docs/btcusdt-orders-with-loss.png)

Előnye: Ha sokáig tartó lefelé trend van, nem ragad be a megvett coinunk, várva a profitra. Az esés utáni esetleges oldalazásnál az első sell valószínűleg veszteséges, viszont utána ugyanúgy kereskedik tovább a bot. Remélhetőleg az így keletkezett veszteséget a további tradek kiegyenlítik.

**stopped** - jelenleg not implemented

Hogy ne kelljen fileokat törölgetni/moveolni, itt kikapcsolható (lesz) az adott kereskedési szál. 

## pairs/x.trades

Ezeket a fileokat a bot létrehozza, és a kereskedés folyamán szépen feltölti adatokkal.

A `.txt` konfig fileokban megadott párokkal eddig végzett tranzakciók adatait tartalmazzák (majdnem) JSON formátumban, lefele időrendben. 

A bot ezekből dolgozik, és tudja, hogy éppen venni vagy eladni kell, valamint ezek adataiból számolja a profit %-okat. Kézzel szerkesztésük nem ajánlott.



Hasznos lehet majd jövőbeni összesített statisztikákhoz is, stb.
Egy esetleges fent említett zuhanó trend árfolyam beragadásnál a legutolsó BUY ordert "kézzel" kitörölve a bot "elfelejti" azt, és így nem vár az eladási feltételekre, hanem a következő lehetőségnél megint vesz majd. 

## debug.log, candledata.log

Szemét, debug fileok.

# Tudnivalók

Bármelyik file (`.txt` vagy `.trades`) szerkesztése után érdemes a botot újraindítani. (Bár a `.trades`-eket beolvassa percenként)

Mivel ez még eléggé work in progress verzió, így a bot megáll, ha

- fileok hiányoznak
- settings.txt rossz
- nincs elég egyenleged (vételnél asset2, eladásnál asset1. ne a minimum limitekkel kereskedj élesben)
- nincs internetkapcsolat (néha a Binance sandbox api endpoint is szarakodik) 
- az ablakméret nem elég nagy, bár ez javarészt már javítva lett (ha addwstr errorral száll el, akkor nagyobbra kell venni az ablakot) legegyszerűbb teljes méretűre állítani, az biztosan elég
- egyéb hibák :)

A test modeban az árfolyam **nem tükrözi pontosan** a valós piaci adatokat, mivel rengetegen rángatják a sandboxon belül az árakat fel/le.
Így a test tradek és tranzakciók csak nagyjából lesznek egálban az aktuális valósággal. Emellett mivel hihetetlen nagy kilengések is vannak az árban, a gyertyák esetlegesen extrém low/high értékei a lekérdezés után felül vannak írva, és maximálva vannak **aktuális ár +- 0.1%**-ban. Erre azért volt szükség, mert pl BTC esetén voltak olyan gyertyák, amiknél a low 18k a high pedig 90k volt, ezzel eléggé tönkretéve a chartot, és lehetetlenné téve a tesztelést.

Egyelőre csak linuxon lett hosszabban tesztelve a bot, windowson **elvileg** ugyanúgy működnie kell.

## Linux scriptek

Linuxon lehetséges a botot a háttérben futtatni, ha távoli gépre van felrakva.

### start_screen_linux.sh

Screen-el háttérbe rakja a botot, hogy ssh-n keresztül futtatva ne álljon le, ha az ssh kapcsolat megszakad.

### list_screen.sh

Kilistázza az aktuális futó screen sessionöket.

### switch_to_screen.sh

Átvált arra a screen sessionre, ahol a bot fut.

A screen sessiönből kilépéshez: ctrl-a, majd ctrl-d

ESC megnyomásával a bot kilép, és így a screen session is véget ér!





[def]: docs/binance-example-l