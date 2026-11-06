import sys,json
from playwright.sync_api import sync_playwright
S=str(__import__('pathlib').Path(__file__).resolve().parent/'out');__import__('pathlib').Path(S).mkdir(exist_ok=True);res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':1100,'height':800})
    pg.on('pageerror',lambda e:errs.append('PAGEERROR '+str(e)))
    pg.route('**/*',lambda r:r.abort() if any(h in r.request.url for h in('supabase','jsdelivr','googleapis','gstatic')) else r.continue_())
    pg.goto('file://'+str(__import__('pathlib').Path(__file__).resolve().parent.parent/'index.html'));pg.wait_for_timeout(600)
    pg.evaluate("show('game')")
    res['plan']={n:pg.evaluate(f'plan({n})') for n in (5,9,10,12,16,17,24,30,60)}
    res['rozmiary kategorii']=pg.evaluate("CATS.map(c=>c.n+':'+c.w.length+' -> '+JSON.stringify(plan(c.w.length)))")
    # kategoria z >=12 słówkami => co najmniej 2 etapy
    i=pg.evaluate("CATS.findIndex(c=>plan(c.w.length).length>1)");res['idx wieloetapowej']=i
    pg.evaluate(f"start({i})");pg.wait_for_timeout(200)
    res['start']=pg.evaluate("({stage,needs,NEED,hearts,state})")
    def tp():  # postaw gracza przy fladze
        pg.evaluate("p.x=(MW-4)*T-6;p.y=hs[MW-4]*T-p.h-4;p.vx=0;p.vy=0")
    # za mało słówek: brak etapu
    tp();pg.wait_for_timeout(200);res['bez slowek']=pg.evaluate("state")
    # zbierz słówka etapu 1
    pg.evaluate("got=CATS[lvl].w.slice(0,NEED);score=NEED;seen=got.slice();hearts=2");tp();pg.wait_for_timeout(300)
    res['po fladze 1']={'state':pg.evaluate("state"),'karta':pg.inner_text('#ov')[:60]}
    pg.click('#ov button.g');pg.wait_for_timeout(300)
    res['etap 2']=pg.evaluate("({stage,NEED,hearts,state,got:got.length,cp:cp.got.length})")
    # porażka w etapie 2 => powrót do checkpointu
    pg.evaluate("got=got.concat(CATS[lvl].w.slice(NEED-1,NEED+1).filter(w=>!got.includes(w)));hearts=0;fail()")
    res['fail karta']=pg.inner_text('#ov')[:160]
    pg.click('#ov button.g');pg.wait_for_timeout(300)
    res['po retryStage']=pg.evaluate("({stage,NEED,hearts,got:got.length,state})")
    # ostatni etap => boss
    pg.evaluate("got=CATS[lvl].w.slice(0,NEED);score=NEED;seen=got.slice()");tp();pg.wait_for_timeout(300)
    res['po fladze ostatniej']={'state':pg.evaluate("state"),'karta':pg.inner_text('#ov')[:50]}
    # porażka w boss => retryBoss
    pg.evaluate("hearts=0;fail()");res['fail boss karta']=pg.inner_text('#ov')[:140]
    pg.click('#ov button.g');pg.wait_for_timeout(200);res['po retryBoss']=pg.evaluate("({state,hearts,bhp})")
    # pełny widok HUD
    pg.evaluate("start(%d)"%i);pg.wait_for_timeout(300);pg.evaluate("hide()");pg.screenshot(path=S+'/stage_hud.png')
    # mała kategoria => 1 etap jak dawniej
    j=pg.evaluate("CATS.push({n:'Mini',e:'🧪',l:'A1',w:[['a','aa'],['b','bb'],['c','cc'],['d','dd'],['e','ee']]})-1");pg.evaluate(f"start({j})");res['1 etap']=pg.evaluate("({needs,NEED})")
    # 300 klatek bez błędów
    pg.wait_for_timeout(1500)
    res['errors']=errs
    br.close()
print(json.dumps(res,ensure_ascii=False,indent=1))
