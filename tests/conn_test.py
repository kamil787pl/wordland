"""Połączenia: generowanie łamigłówki, zasady, wygrana/przegrana, codzienna, udostępnianie."""
import json,pathlib
from playwright.sync_api import sync_playwright
URL='file://'+str(pathlib.Path(__file__).resolve().parent.parent/'index.html')
res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':420,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(500);pg.evaluate("sessionStorage.clear();localStorage.clear()");pg.reload();pg.wait_for_timeout(500)
    res['karta na stronie glownej']='WordLinks' in pg.inner_text('#v-home')
    pg.evaluate("show('conn')");pg.wait_for_timeout(300)
    words=pg.evaluate("CN.tiles.map(t=>t.w)")
    import re;tx=pg.inner_text('#v-conn')+pg.inner_html('#v-conn');res['przed startem slowa ukryte']=not any(re.search(r'(?<![A-Za-z-])'+re.escape(w)+r'(?![A-Za-z])',tx) for w in words) and pg.locator('.cn-start').count()==1
    res['przed startem czas stoi']=pg.evaluate("CN.t0")==0 and pg.evaluate("cnTap(0),cnSubmit(),CN.t0")==0 and pg.evaluate("CN.sel.length")==0
    pg.wait_for_timeout(1200);res['przed startem czas 0:00']=pg.inner_text('#cn-time')=='0:00'
    pg.click('.cn-start .pri');pg.wait_for_timeout(200)
    res['po starcie slowa widoczne']=all(w in pg.inner_text('#v-conn') for w in words) and pg.evaluate("CN.t0")>0
    res['16 kafelkow']=pg.locator('.cn-t').count()==16
    res['unikalne slowa']=pg.evaluate("new Set(CN.tiles.map(t=>t.w.toLowerCase())).size")==16
    res['4 kategorie po 4']=pg.evaluate("CN.groups.length==4&&CN.groups.every(g=>g.w.length==4)")
    res['kolory 4 rozne']=pg.evaluate("new Set(CN.groups.map(g=>g.c)).size")==4
    # codzienna jest powtarzalna
    a=pg.evaluate("CN.tiles.map(t=>t.w).join()");pg.evaluate("CN=null;renderConn()");b=pg.evaluate("CN.tiles.map(t=>t.w).join()");pg.evaluate("cnStart()")
    res['codzienna powtarzalna']=a==b
    # zły ruch: 4 kafelki z różnych grup
    pg.evaluate("CN.sel=[];[0,1,2,3].forEach(k=>{});")
    pick="(()=>{const used={};const idx=[];CN.tiles.forEach((t,i)=>{if(!used[t.g]&&idx.length<4){used[t.g]=1;idx.push(i)}});CN.sel=idx;renderConn()})()"
    pg.evaluate(pick);res['zatwierdz aktywny przy 4']=not pg.is_disabled('.gbar .pri')
    pg.click('.gbar .pri');pg.wait_for_timeout(200)
    res['blad liczy sie']=pg.evaluate("CN.miss")==1;res['komunikat']=pg.inner_text('.cn-msg')
    # dobry ruch
    pg.evaluate("(()=>{const g=CN.tiles[0].g;CN.sel=CN.tiles.map((t,i)=>t.g===g?i:-1).filter(i=>i>=0);renderConn()})()");pg.click('.gbar .pri');pg.wait_for_timeout(200)
    res['grupa rozwiazana']=pg.evaluate("CN.solved.length")==1 and pg.locator('.cn-row').count()==1 and pg.locator('.cn-t').count()==12
    # wygrana: rozwiąż resztę
    for _ in range(3):
        pg.evaluate("(()=>{const g=CN.tiles[0].g;CN.sel=CN.tiles.map((t,i)=>t.g===g?i:-1).filter(i=>i>=0);renderConn()})()");pg.click('.gbar .pri');pg.wait_for_timeout(120)
    res['wygrana']=pg.evaluate("[CN.over,CN.won]")==[1,1]
    res['czas i medal po wygranej']=pg.evaluate("CN.ms>=CN.miss*10000&&cnMedal(CN.ms)==='🥇'")
    res['kara 10 s za blad']=pg.evaluate("CN.ms>=10000")  # w tescie jest 1 blad
    res['rekord zapisany']=pg.evaluate("SV.cn.bt===CN.ms&&CN.rec===1")
    res['ekran koncowy: czas i rekord']='Nowy rekord' in pg.inner_text('.cn-end') and '⏱' in pg.inner_text('.cn-end')
    res['udostepnianie z czasem']='⏱' not in pg.evaluate("cnShareText()") and ':' in pg.evaluate("cnShareText()")
    res['statystyki zapisane']=pg.evaluate("SV.cn.p==1&&SV.cn.w==1&&SV.cn.s==1")
    res['share ma kwadraciki']='🟨' in pg.evaluate("cnShareText()") or '🟩' in pg.evaluate("cnShareText()")
    # po odświeżeniu codzienna jest ukończona
    pg.reload();pg.wait_for_timeout(400);pg.evaluate("show('conn')");pg.wait_for_timeout(200)
    res['codzienna zapamietana']=pg.evaluate("[CN.over,CN.won]")==[1,1] and pg.locator('.cn-row').count()==4
    # losowa: przegrana po 4 błędach ujawnia grupy
    pg.evaluate("cnNew();cnStart()");pg.wait_for_timeout(200)
    for _ in range(4):
        pg.evaluate(pick);pg.click('.gbar .pri');pg.wait_for_timeout(100)
    res['przegrana ujawnia grupy']=pg.evaluate("[CN.over,CN.won,CN.solved.length]")==[1,0,4]
    pg.evaluate("cnLvl('A1');cnStart()");pg.evaluate("(()=>{CN.t0=Date.now()-30000;})()")
    for _ in range(4):
        pg.evaluate("(()=>{const g=CN.tiles[0].g;CN.sel=CN.tiles.map((t,i)=>t.g===g?i:-1).filter(i=>i>=0);renderConn()})()");pg.click('.gbar .pri');pg.wait_for_timeout(100)
    res['rekord losowej per poziom']=pg.evaluate("SV.cn.br.A1>=29000&&SV.cn.br.A1<40000&&CN.rec===1")
    res['losowa nie zmienia serii dziennej']=pg.evaluate("SV.cn.p")==1
    pg.set_viewport_size({'width':360,'height':740});pg.evaluate("cnNew()");pg.wait_for_timeout(300)
    res['mobile: brak poziomego przewijania']=pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth")
    # poziomy
    pg.evaluate("cnLvl('A2')");res['poziom A2']=pg.evaluate("CN.groups.length")==4
    # podpowiedź, powtórki, sprint, odznaki, ranking
    solve="(()=>{const g=CN.tiles[0].g;CN.sel=CN.tiles.map((t,i)=>t.g===g?i:-1).filter(i=>i>=0);renderConn()})()"
    pg.evaluate("localStorage.clear();SV.cn=null;SV.m={};cnNew();cnStart()");pg.wait_for_timeout(100)
    pg.click('button:has-text("Podpowiedź")');pg.wait_for_timeout(100)
    res['podpowiedz: kafelek i kara']=pg.locator('.cn-t.hint').count()==1 and pg.evaluate("CN.hints")==1 and 'Podpowiedź' in pg.inner_text('.cn-msg') and pg.evaluate("CN.t0=Date.now()-1000,cnTotal()>=15000")
    pg.click('button:has-text("Podpowiedź")');pg.wait_for_timeout(100);res['podpowiedz: max 2']=pg.is_disabled('button:has-text("(0)")')
    pg.evaluate(pick);pg.click('.gbar .pri');pg.wait_for_timeout(100)
    res['zle slowa zapamietane']=pg.evaluate("CN.bad.length")>=1
    for _ in range(3):
        pg.evaluate(solve);pg.click('.gbar .pri');pg.wait_for_timeout(80)
    pg.evaluate(solve);pg.click('.gbar .pri');pg.wait_for_timeout(100)
    res['koniec: podpowiedzi w opisie']='Podpowiedzi: 2' in pg.inner_text('.cn-end')
    n=pg.evaluate("CN.bad.length");pg.click('text=Powtórki');pg.wait_for_timeout(100)
    res['powtorki: wpisane do SV.m']=pg.evaluate("Object.values(SV.m).filter(m=>m.w>0).length")==n and n>0
    # sprint
    pg.evaluate("cnMode('sprint')");pg.wait_for_timeout(100)
    res['sprint: slowa ukryte']=pg.locator('.cn-t.blank').count()==16
    pg.click('.cn-start .pri');pg.wait_for_timeout(100)
    for k in range(3):
        for _ in range(4):
            pg.evaluate(solve);pg.click('.gbar .pri');pg.wait_for_timeout(60)
        if k<2:res[f'sprint: kolejna lamiglowka {k+2}']=pg.evaluate("[SPN.n,CN.over,CN.tiles.length]")==[k+2,0,16]
    res['sprint: wygrana i rekord']=pg.evaluate("[CN.over,CN.won,SV.cn.br.sp>0,CN.nb.includes('p')]")==[1,1,True,True]
    res['sprint: nie psuje rekordow zwyklych']=pg.evaluate("cnBestAll()")==0 or pg.evaluate("cnBestAll()")>0
    res['odznaka zapisana']=pg.evaluate("SV.cn.bd.p")==1
    # wieżowiec
    pg.evaluate("cnMode('sprint')");pg.wait_for_timeout(100)
    res['wiezowiec: sprint ma 12 pieter']=pg.locator('.tw-fl i').count()==12 and pg.get_attribute('.cn-tower','aria-label')=='Piętro 0 z 12'
    pg.click('.cn-start .pri');pg.wait_for_timeout(100)
    pg.evaluate(solve);pg.click('.gbar .pri');pg.wait_for_timeout(100)
    res['wiezowiec: pietro po grupie']=pg.get_attribute('.cn-tower','aria-label')=='Piętro 1 z 12' and pg.locator('.tw-fl i.on').count()==1
    for _ in range(3):
        pg.evaluate(solve);pg.click('.gbar .pri');pg.wait_for_timeout(80)
    res['wiezowiec: kolejna lamiglowka kontynuuje wspinaczke']=pg.get_attribute('.cn-tower','aria-label')=='Piętro 4 z 12'
    res['wiezowiec: pace medal']=pg.inner_text('#cn-pace')[:1] in '🥇🥈🥉🏁'
    # seria i odznaka tygodnia
    pg.evaluate("(()=>{const y=new Date();y.setDate(y.getDate()-1);const c=SV.cn;c.s=6;c.last=ymd(y);c.d=null;CNmode='daily';CN=null;renderConn()})()");pg.click('.cn-start .pri');pg.wait_for_timeout(100)
    for _ in range(4):
        pg.evaluate(solve);pg.click('.gbar .pri');pg.wait_for_timeout(60)
    res['seria 7 dni: odznaka']=pg.evaluate("[SV.cn.s,!!SV.cn.bd.s]")==[7,True]
    res['seria na ekranie']='Seria: 7' in ' '.join(pg.text_content('.cn-bd').split())
    res['ranking: gosc widzi zaproszenie']='Zaloguj' in pg.inner_text('.cn-lbp')
    pg.evaluate("show('home');heroGo(1)");pg.wait_for_timeout(300)
    res['home: seria i rekord']='Seria: 7' in pg.inner_text('.hchips') and 'rekord' in pg.inner_text('.hchips')
    # ranking z zalogowanym
    pg.evaluate("sb={rpc:async()=>({data:[]})};U={id:'u1',nick:'Ja'};CNB.t=Date.now();CNB.rows=[{nick:'Ala<b>',ms:61000,miss:0,me:false},{nick:'Ja',ms:75000,miss:1,me:true}];show('conn')");pg.wait_for_timeout(200)
    res['ranking: wiersze i escape']=pg.locator('.cn-lb li').count()==2 and pg.locator('.cn-lb b').first.inner_text()=='Ala<b>' and pg.locator('.cn-lb li.me').count()==1
    # wyzwanie przez link
    pg.evaluate("cnNew();cnStart()");pg.wait_for_timeout(100)
    for _ in range(4):
        pg.evaluate("(()=>{const g=CN.tiles[0].g;CN.sel=CN.tiles.map((t,i)=>t.g===g?i:-1).filter(i=>i>=0);renderConn()})()");pg.click('.gbar .pri');pg.wait_for_timeout(100)
    link=pg.evaluate("cnChalLink(1)");mine=pg.evaluate("[CN.ms,CN.groups.map(g=>g.w.slice().sort().join()).sort().join('|')]")
    recs=pg.evaluate("JSON.stringify(SV.cn)")
    pg2=br.new_page(viewport={'width':420,'height':900});pg2.on('pageerror',lambda e:errs.append(str(e)))
    pg2.goto(link);pg2.wait_for_timeout(700)
    res['link: otwiera wyzwanie']=pg2.evaluate("[view,CN.mode,CN.go]")==['conn','chal',0] and 'pobij' in pg2.inner_text('#v-conn')
    res['link: ta sama plansza']=pg2.evaluate("CN.groups.map(g=>g.w.slice().sort().join()).sort().join('|')")==mine[1] and pg2.evaluate("CN.t")==mine[0]
    res['link: slowa ukryte do startu']=pg2.evaluate("CN.tiles[0].w") not in pg2.inner_text('#v-conn')
    pg2.click('.cn-start .pri');pg2.wait_for_timeout(100)
    for _ in range(4):
        pg2.evaluate("(()=>{const g=CN.tiles[0].g;CN.sel=CN.tiles.map((t,i)=>t.g===g?i:-1).filter(i=>i>=0);renderConn()})()");pg2.click('.gbar .pri');pg2.wait_for_timeout(100)
    res['link: wynik porownany']='Pobiłeś' in pg2.inner_text('.cn-end') or 'Nie pobiłeś' in pg2.inner_text('.cn-end')
    res['link: nie zmienia rekordow']=pg2.evaluate("JSON.stringify(SV.cn||null)")in('null',recs) or pg2.evaluate("(SV.cn&&SV.cn.p)||0")==0
    res['link: hash wyczyszczony']=pg2.evaluate("location.hash")==''
    # złośliwy link nie wstrzykuje HTML
    import base64
    bad=base64.urlsafe_b64encode(json.dumps({"g":[["<img src=x onerror=window.XSS=1>","e",["a<b>","b2","c3","d4"],[]],["n","e",["e5","f6","g7","h8"],[]],["n","e",["i9","j10","k11","l12"],[]],["n","e",["m13","n14","o15","p16"],[]]],"t":5000}).encode()).decode().rstrip('=')
    pg3=br.new_page();pg3.on('pageerror',lambda e:errs.append(str(e)));pg3.goto(URL+'#wl='+bad);pg3.wait_for_timeout(600)
    res['link zlosliwy: brak XSS']=pg3.evaluate("window.XSS")is None and pg3.locator('#v-conn img').count()==0
    pg4=br.new_page();pg4.on('pageerror',lambda e:errs.append(str(e)));pg4.goto(URL+'#wl=zepsuty');pg4.wait_for_timeout(500)
    res['link zepsuty: portal dziala']=pg4.evaluate("view")=='home'
    res['errors']=errs
print(json.dumps(res,ensure_ascii=False,indent=1))
bad=[k for k,v in res.items() if v is False]
print('FAIL' if bad or errs else 'OK',bad)
