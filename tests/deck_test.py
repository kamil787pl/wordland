"""WordDeck (etap 1): ekran startowy, zagranie karty zadaniem, tury, bot, koniec pojedynku, wyjscie."""
import pathlib
from playwright.sync_api import sync_playwright
URL='file://'+str(pathlib.Path(__file__).resolve().parent.parent/'index.html')
res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':1000,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(400);pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(400)
    res['katalog: 60 kart, zadania poprawne']=pg.evaluate("DKCARDS.length===60&&DKCARDS.every(c=>{const t=dkTask(c,'B1');return t.opts.length===4&&t.opts[t.ok]&&new Set(t.opts).size===4})")
    res['talie: 10 kart na kazdym poziomie']=pg.evaluate("['A1','A2','B1'].every(l=>dkDeck(l).length===10&&new Set(dkDeck(l).map(c=>c.id)).size===10)")
    pg.evaluate("show('deck')");pg.wait_for_timeout(300)
    res['start: opis, Start i Wyjscie']=pg.locator('.dk-start .dk-go').count()==1 and pg.locator('.dk-start .xit').count()==1
    pg.click('.dk-start .pri,.dk-start .dk-go');pg.wait_for_timeout(200)
    res['po starcie: 4 karty w rece, energia 3']=pg.locator('.dk-h').count()==4 and pg.evaluate("DK.en")==3
    # zagranie karty: bledna odpowiedz dwa razy -> potkniecie
    pg.evaluate("DK.hand[0]=DKCARDS.find(c=>c.cost===1&&c.t==='n');dkPlay(0)");pg.wait_for_timeout(100)
    res['zadanie: 3 odpowiedzi na A1']=pg.locator('.dk-opts button').count()==3
    pg.evaluate("dkAns(DK.task.t.ok)");pg.wait_for_timeout(1000)
    res['dobra odpowiedz: karta na polu z pelna moca']=pg.evaluate("DK.field[0][0]&&DK.field[0][0].mode==='full'&&DK.field[0][0].atk===DK.field[0][0].c.atk&&DK.en===2")
    pg.evaluate("DK.hand[0]=DKCARDS.find(c=>c.cost===1&&c.t==='n'&&c.id!==DK.field[0][0].c.id);dkPlay(0)");pg.wait_for_timeout(100)
    pg.evaluate("const t=DK.task.t;dkAns((t.ok+1)%t.opts.length)");pg.wait_for_timeout(100)
    res['pierwsza pomylka: druga szansa']=pg.evaluate("DK.task&&DK.task.t.tries===1&&!DK.task.t.done")
    pg.evaluate("const t=DK.task.t;dkAns(t.opts.map((_,k)=>k).find(k=>k!==t.ok&&!t.dis[k]))");pg.wait_for_timeout(1700)
    res['druga pomylka: karta potkniecia (moc 1)']=pg.evaluate("DK.field[0][1]&&DK.field[0][1].mode==='bad'&&DK.field[0][1].atk===1")
    res['za malo energii nie otwiera zadania']=pg.evaluate("DK.en=0;DK.hand[0]=DKCARDS.find(c=>c.cost===2);dkPlay(0);!DK.task")
    pg.evaluate("DK.en=2");pg.evaluate("dkEnd()");pg.wait_for_timeout(300)
    res['koniec tury: faza ataku/tura wroga']=pg.evaluate("DK.ph==='x'||DK.ph==='b'")
    pg.wait_for_function("DK.ph==='p'||DK.over",timeout=15000)
    res['tura 2: energia 4, bot zagral karte']=pg.evaluate("DK.turn===2&&DK.en===4&&DK.field[1].some(Boolean)")
    # symulacja do konca (zawsze dobre odpowiedzi)
    for i in range(12):
        if pg.evaluate("DK.over"):break
        pg.evaluate("""(()=>{for(let k=0;k<3;k++){if(DK.task)break;const i=DK.hand.findIndex(c=>c.cost<=DK.en);if(i<0||DK.field[0].indexOf(null)<0)break;dkPlay(i);if(DK.task){dkAns(DK.task.t.ok);dkPlace()}}dkEnd()})()""")
        pg.wait_for_function("DK.ph==='p'||DK.over",timeout=20000)
    res['pojedynek konczy sie wynikiem']=pg.evaluate("DK.over===1&&['w','l','d'].includes(DK.res)&&DK.turn<=8")
    res['ekran konca i Nowy pojedynek']=pg.locator('.dk-ov.end').count()==1 and 'Nowy pojedynek' in pg.inner_text('.gbar')
    res['statystyka zapisana lokalnie']=pg.evaluate("SV.deck&&SV.deck.g===1&&Object.keys(SV.deck.m).length>0")
    pg.click('.gbar .pri');pg.wait_for_timeout(200)
    res['nowy pojedynek: ekran startowy']=pg.locator('.dk-start').count()==1
    pg.click('.dk-start .xit');pg.wait_for_timeout(300)
    res['Wyjscie wraca na strone glowna']=pg.evaluate("view")=='home'
    for l in ['A1','A2','B1']:
        pg.evaluate("show('deck');dkLvl('%s')"%l);pg.wait_for_timeout(100)
        res['poziom '+l+': talia z kart <= poziomu']=pg.evaluate("DK.deck.concat(DK.hand).every(c=>c.lv<=DKL[DK.lvl])")
    pg.set_viewport_size({'width':390,'height':800});pg.evaluate("show('deck');dkLvl('A2');dkStart()");pg.wait_for_timeout(300)
    res['telefon: brak przewijania poziomego']=pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
    print({k:v for k,v in res.items() if v is not True});print('OK' if not errs else 'BLEDY',errs)
