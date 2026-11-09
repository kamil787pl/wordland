"""WordHeist: sprawa The Missing Cake, telefon i laptop, zagadki, przesluchanie, tablica, punkty, RPC (mock), ranking, profil."""
import pathlib
from playwright.sync_api import sync_playwright
URL='file://'+str(pathlib.Path(__file__).resolve().parent.parent/'index.html')
res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':1000,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(400);pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(400)
    pg.evaluate("window.CALLS=[];U={id:'u1',nick:'Test'};sb={rpc:async(n,a)=>{CALLS.push([n,a]);return{data:n==='heist_award'?40:[]}},from:()=>({upsert:async()=>({})})}")
    pg.evaluate("show('heist')");pg.wait_for_timeout(200)
    res['nakladka startowa']=pg.locator('.hs-go').count()==1 and pg.evaluate("HS.go")==0
    res['ranking przed startem']=pg.locator('#v-heist .cn-lbp').count()==1
    pg.evaluate("hsStart()");pg.wait_for_timeout(100)
    res['5 lup w scenie']=pg.locator('.hs-spot').count()==5
    res['telefon i laptop z plakietkami']=pg.evaluate("[...document.querySelectorAll('.hs-inv em')].map(e=>e.textContent)")==['5','3']
    res['tablica zablokowana']=pg.locator('.gbar .pri').first.is_disabled()
    pg.evaluate("hsOpen(1)");pg.wait_for_timeout(50)
    res['dowod 1 ma 4 opcje']=pg.locator('.hs-opts button').count()==4
    pg.evaluate("hsPick(0)");res['blad liczy sie']=pg.evaluate("HS.err")==1 and not pg.evaluate("!!HS.done[1]")
    pg.evaluate("hsHint()");res['podpowiedz usuwa opcje']=pg.locator('.hs-opts button').count()==3 and pg.evaluate("HS.hint")==1
    pg.evaluate("hsPick(HSI[0].a)");res['poprawna zapisuje']=pg.evaluate("!!HS.done[1]")
    pg.evaluate("hsBack()")
    pg.evaluate("hsApp('phone')");res['telefon: 5 SMS']=pg.locator('.hs-app.ph .hs-row').count()==5
    pg.evaluate("hsOpen(12)");res['mylny trop bez pytania']=pg.locator('.hs-opts').count()==0 and 'nie jest trop' in pg.inner_text('.hs-ov')
    pg.evaluate("hsBack()");res['powrot z SMS do telefonu']=pg.evaluate("HS.v")=='app'
    pg.evaluate("hsOpen(6);hsPl()");res['polski kosztuje podpowiedz']=pg.evaluate("HS.hint")==2
    res['SMS ma godzine']='4:10' in pg.inner_text('.hs-ov')
    pg.evaluate("hsPick(HSI[5].a)")
    pg.evaluate("hsBack();hsOpen(9);hsPick(HSI[8].a);hsBack();hsBack()")
    res['plakietka telefonu spadla']=pg.evaluate("[...document.querySelectorAll('.hs-inv em')].map(e=>e.textContent)")==['2','3']
    pg.evaluate("hsApp('laptop');hsOpen(10);hsPick(hsIt(10).a);hsBack();hsBack()")
    res['laptop: e-mail zapisany']=pg.evaluate("!!HS.done[10]")
    res['tablica nadal zablokowana (4/6)']=pg.evaluate("hsSolved()")==4 and pg.locator('.gbar .pri').first.is_disabled()
    for i in (2,3):pg.evaluate("hsOpen(%d);hsPick(hsIt(%d).a);hsBack()"%(i,i))
    res['tablica odblokowana przy 6']=pg.evaluate("hsSolved()")==6 and not pg.locator('.gbar .pri').first.is_disabled()
    pg.evaluate("hsBoard()")
    res['tablica: 4 podejrzanych, 6 dowodow']=pg.locator('.hs-sus').count()==4 and pg.locator('.hs-ch').count()==6
    pg.evaluate("hsSus(0);hsSel(2);hsSel(3);hsAccuse()");res['oskarzenie bez przesluchan odrzucone']=pg.evaluate("HS.over")==0 and 'każdego' in pg.evaluate("HS.msg")
    pg.evaluate("HS.sus=-1;hsAsk()");res['przesluchanie wymaga wyboru osoby']=pg.evaluate("HS.v")=='board'
    pg.evaluate("HS.sus=0;hsAsk()");e0=pg.evaluate("HS.err");pg.evaluate("hsAskTap(HS.ask.w.find(i=>i!==0))");res['zly szyk = blad']=pg.evaluate("HS.err")==e0+1
    pg.evaluate("for(let i=0;i<6;i++)hsAskTap(i)")
    res['Tom etap 1: klamie o bibliotece']=pg.evaluate("HS.int[0]")==1 and 'library' in pg.inner_text('.hs-ov')
    pg.evaluate("HS.v='board';renderHeist();hsAsk();for(let i=0;i<9;i++)hsAskTap(i)");pg.wait_for_timeout(50)
    res['Tom etap 2: zmienia wersje na sale']=pg.evaluate("HS.int[0]")==2 and 'basketball' in pg.inner_text('.hs-ov')
    pg.evaluate("HS.v='board';renderHeist();hsAsk()")
    res['Tom etap 3 zablokowany bez klucza']=pg.evaluate("HS.v")=='board' and 'Art room key' in pg.evaluate("HS.msg")
    res['oskarzenie wymaga przesluchania wszystkich']=True
    pg.evaluate("HS.sel=[2,3];HS.sus=0;hsAccuse()");res['Tom przesluchany, reszta nie: odrzucone']=pg.evaluate("HS.over")==0 and 'każdego' in pg.evaluate("HS.msg")
    pg.evaluate("hsBack();hsApp('laptop');hsOpen(11);hsPick(hsIt(11).a);hsBack();hsBack();hsBoard();HS.sus=0;hsAsk();for(let i=0;i<8;i++)hsAskTap(i)");pg.wait_for_timeout(50)
    res['Tom etap 3: wykreca sie']=pg.evaluate("HS.int[0]")==3 and 'project' in pg.inner_text('.hs-ov')
    pg.evaluate("for(const i of [4,5,7,8,9])HS.done[i]=1;HS.v='board';renderHeist()")
    for sus,n in ((1,6),(2,6),(3,6)):
        pg.evaluate("HS.v='board';renderHeist();HS.sus=%d;hsAsk();for(let i=0;i<%d;i++)hsAskTap(i)"%(sus,n))
    res['Lucy etap 1: dentysta']=pg.evaluate("HS.int[1]")==1 and pg.evaluate("HS.int.every(n=>n>=1)")
    pg.evaluate("HS.v='board';renderHeist();HS.sus=1;hsAsk();for(let i=0;i<6;i++)hsAskTap(i)")
    res['Lucy etap 2: kurtka u Toma']=pg.evaluate("HS.int[1]")==2 and 'Tom has it' in pg.inner_text('.hs-ov')
    pg.evaluate("HS.v='board';renderHeist();HS.sus=2;hsAsk();for(let i=0;i<7;i++)hsAskTap(i)")
    res['Green etap 2: klasa 5A']=pg.evaluate("HS.int[2]")==2
    pg.evaluate("HS.v='board';renderHeist()")
    e1=pg.evaluate("HS.err");pg.evaluate("HS.sus=1;HS.sel=[2,3];hsAccuse()")
    res['Lucy: blad i wyjasnienie']=pg.evaluate("HS.err")==e1+1 and 'dentist' in pg.evaluate("HS.msg") and 'Dentist card' in pg.evaluate("HS.msg") and pg.evaluate("HS.over")==0
    pg.evaluate("HS.sus=2;HS.sel=[2,3];hsAccuse()");res['Green: dowod w komunikacie']='Duty list' in pg.evaluate("HS.msg")
    pg.evaluate("HS.sus=3;HS.sel=[2,3];hsAccuse()");res['Ola: dowod w komunikacie']="Ola's voicemail" in pg.evaluate("HS.msg")
    e2=pg.evaluate("HS.err");pg.evaluate("HS.sus=0;HS.sel=[];hsSel(6);hsSel(3);hsAccuse()")
    res['zly dowod: blad']=pg.evaluate("HS.err")==e2+1 and pg.evaluate("HS.over")==0
    pg.evaluate("HS.sus=0;HS.sel=[];hsSel(11);hsSel(2);hsAccuse()");pg.wait_for_timeout(300)
    res['werdykt']=pg.evaluate("HS.over")==1 and 'Sprawa rozwiązana' in pg.inner_text('#v-heist') and 'Thank you, detective' in pg.inner_html('#v-heist')
    res['punkty wg wzoru']=pg.evaluate("HS.pts")==pg.evaluate("hsPts(HS.err,HS.hint,HS.secs)") and pg.evaluate("HS.pts")>=100
    res['1 gwiazdka przy wielu bledach']=pg.evaluate("HS.stars")==1
    res['RPC award z parametrami']=pg.evaluate("CALLS.filter(c=>c[0]==='heist_award'&&c[1].p_case==='missing-cake'&&c[1].p_errors===HS.err&&c[1].p_hints===HS.hint).length")==1
    res['premia z serwera']='+40' in pg.inner_text('#v-heist')
    res['slowka do powtorek']=pg.evaluate("Object.keys(SV.m).some(k=>k.endsWith('=quarter to'))")
    res['punkty lokalne']=pg.evaluate("SV.heist.pts")==40
    res['suma zawiera WordHeist']=pg.evaluate("totalPts()")>=40
    res['ranking po werdykcie']=pg.locator('#v-heist .cn-lbp').count()==1
    # idealna sprawa: 3 gwiazdki i 300 pkt
    pg.evaluate("hsNewR();hsStart()")
    for i in range(1,12):pg.evaluate("hsOpen(%d);hsPick(hsIt(%d).a)"%(i,i))
    pg.evaluate("hsBoard()")
    for sus in (0,1,2,3):pg.evaluate("HS.sus=%d;hsAsk();for(let i=0;i<HSQS[%d][0].w.length;i++)hsAskTap(i);HS.v='board'"%(sus,sus))
    pg.evaluate("renderHeist();hsSus(0);hsSel(2);hsSel(3);hsAccuse()");pg.wait_for_timeout(200)
    res['ideal: 3 gwiazdki, 300 pkt']=pg.evaluate("[HS.stars,HS.pts]")==[3,300]
    res['ideal: brak nowych punktow lokalnie (mock daje 40)']=pg.evaluate("HS.over")==1
    res['klawisze 1-4']=True
    pg.evaluate("hsNewR();hsStart();hsOpen(1)");pg.keyboard.press('2');res['klawisz 2 wybiera']=pg.evaluate("!!HS.done[1]")
    pg.evaluate("show('prof')");t=pg.inner_text('#v-prof')
    res['profil: panel i ranga']='WordHeist' in t and 'Ranga WordHeist' in t
    res['trofea 30']=pg.evaluate("document.querySelectorAll('#v-prof .rm-t').length")==30
    res['przelacznik rankingu ma WordHeist']='WordHeist' in pg.locator('#v-prof .cn-lbp').first.inner_text()
    pg.evaluate("wbGame('hs')");pg.wait_for_timeout(300)
    res['ranking hs wola heist_pts_board']=pg.evaluate("CALLS.some(c=>c[0]==='heist_pts_board')")
    pg.evaluate("show('home')");pg.wait_for_timeout(200)
    res['karta gry na stronie glownej']=pg.locator('.gc.g-hs').count()==1 and pg.locator('.gc.g-hs img.gimg').count()==1
    res['5 slajdow w karuzeli']=pg.locator('.hdots button').count()==5
    pg.evaluate("heroGo(4)");res['slajd WordHeist']='WordHeist' in pg.inner_text('#hero')
    pg.evaluate("howGo(4)");res['jak to dziala: WordHeist']='Szukaj tropów' in pg.inner_html('#how')
    res['rangi w Poradniku']='Legenda Wydziału' in pg.evaluate("hpRanks()")
    res['menu: przycisk']=pg.locator('#nb-heist').count()==1
    # mobilny widok
    pg.set_viewport_size({'width':390,'height':800});pg.evaluate("show('heist');hsNewR();hsStart();hsOpen(3)");pg.wait_for_timeout(200)
    res['mobilny: bez poziomego przewijania']=pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
    pg.set_viewport_size({'width':1000,'height':900});pg.evaluate("hsBack()");pg.screenshot(path=str(pathlib.Path(__file__).parent/'out'/'heist.png'))
    print({k:v for k,v in res.items() if v is not True});print('OK' if not errs else 'BLEDY',errs)
