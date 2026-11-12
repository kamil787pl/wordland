"""WordDeck: punkty, rangi, RPC deck_award/deck_my_points, ranking, profil, widocznosc w portalu."""
import pathlib
from playwright.sync_api import sync_playwright
URL='file://'+str(pathlib.Path(__file__).resolve().parent.parent/'index.html')
res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':1000,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(400);pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(400)
    res['menu: przycisk WordDeck']=pg.locator('#nb-deck').count()==1
    pg.evaluate("show('home')");pg.wait_for_timeout(200)
    res['home: karta WordDeck z obrazkiem 5:3']=pg.locator('#v-home .gc.g-dk img.gimg').count()==1 and pg.evaluate("GAMES.find(g=>g.k==='dk').img")=='assets/card-dk.webp'
    res['karuzela: 6 slajdow, slajd 6 to WordDeck']=pg.locator('#hero .hdots button').count()==6 and (pg.evaluate("heroGo(5);document.querySelector('#hero h2').textContent")=='WordDeck')
    res['Jak to dziala: zakladka WordDeck']=pg.evaluate("howGo(5);document.querySelector('#how').textContent.includes('Zagrywaj karty')")
    pg.evaluate("window.CALLS=[];U={id:'u1',nick:'Test'};sb={rpc:async(n,a)=>{CALLS.push([n,a]);return{data:n==='deck_award'?120:n==='deck_my_points'?777:[]}},from:()=>({upsert:async()=>({})})}")
    res['rangi: 6 stopni od Kadeta']=pg.evaluate("DKRK.length===6&&DKRK[0][1]==='Kadet'")
    pg.evaluate("show('deck');dkNew('A2');DK.st={first:8,half:2,bad:0};DK.ser={w:[2,0],n:2,d:0,h:[]};DK.hero=[6,1];DK.def=[0,0];DK.miss={};dkFinish()");pg.wait_for_timeout(400)
    res['koniec bitwy: RPC deck_award z poziomem i rundami']=pg.evaluate("CALLS.filter(c=>c[0]==='deck_award'&&c[1].p_level==='A2'&&c[1].p_rounds_won===3&&c[1].p_rounds_lost===0&&c[1].p_acc===90).length")==1
    res['punkty z serwera w SV i na ekranie']=pg.evaluate("SV.deck.pts")==120 and '+120' in pg.inner_text('#v-deck')
    res['suma zawiera WordDeck']=pg.evaluate("totalPts()")>=120
    res['ranking pod plansza']=pg.locator('#v-deck .cn-lbp').count()==1
    pg.evaluate("dkNew('A1');DK.st={first:1,half:0,bad:0};DK.ser={w:[2,2],n:4,d:0,h:[]};DK.hero=[3,5];DK.def=[0,0];DK.miss={};dkFinish()");pg.wait_for_timeout(300)
    res['runda bez konca bitwy nie nagradza']=pg.evaluate("CALLS.filter(c=>c[0]==='deck_award').length")==2
    pg.evaluate("dkSync()");pg.wait_for_timeout(200)
    res['sync: deck_my_points']=pg.evaluate("SV.deck.pts")==777
    pg.evaluate("show('prof');profTab('dk')");pg.wait_for_timeout(300)
    res['profil: panel WordDeck + ranga']=pg.evaluate("(()=>{const e=document.querySelector('#v-prof .ptab[data-t=dk]');return !e.hidden&&!!e.querySelector('.gpn.g-dk')&&!!e.querySelector('.rkp')})()")
    pg.evaluate("sb={rpc:async(n,a)=>{CALLS.push([n,a]);return{data:null,error:{message:'x'}}}}");pg.evaluate("SV.deck.pts=0;SV.deck.pd=null;dkNew('B1');DK.st={first:10,half:0,bad:0};DK.ser={w:[2,0],n:3,d:0,h:[]};DK.hero=[8,0];DK.def=[0,0];DK.miss={};dkFinish()");pg.wait_for_timeout(300)
    res['blad RPC: wynik lokalny wg wzoru (B1: 500*(.5+.3+.2)=500)']=pg.evaluate("SV.deck.pts")==500
    res['ranking: przelacznik gry ma WordDeck']='WordDeck' in pg.evaluate("(show('home'),document.querySelector('#v-home .bb .cn-seg').textContent)")
    print({k:v for k,v in res.items() if v is not True});print('OK' if not errs else 'BLEDY',errs)
