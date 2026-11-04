import sys,json,collections
from playwright.sync_api import sync_playwright
S=str(__import__('pathlib').Path(__file__).resolve().parent/'out');__import__('pathlib').Path(S).mkdir(exist_ok=True);res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':1100,'height':800})
    pg.on('pageerror',lambda e:errs.append('PAGEERROR '+str(e)))
    pg.route('**/*',lambda r:r.abort() if any(h in r.request.url for h in('supabase','jsdelivr','googleapis','gstatic')) else r.continue_())
    pg.goto('file://'+str(__import__('pathlib').Path(__file__).resolve().parent.parent/'index.html'));pg.wait_for_timeout(600)
    pg.evaluate("show('game');SV.tut=1;menu()");pg.wait_for_timeout(200)
    res['przyciski Hard w menu']=pg.locator('#ov .lv.hd').count()
    pg.screenshot(path=S+'/hard_menu.png')
    def kinds(hard,i,n=60):
        pg.evaluate(f"start({i},{'1' if hard else '0'})");c=collections.Counter()
        for _ in range(n):
            pg.evaluate("deck=prio(CATS[lvl].w.slice());seen=[];ask(5,5)")
            c[pg.evaluate("qm+':'+tyv")]+=1
        return dict(c)
    res['normal A1 (nowe slowka)']=kinds(0,0)
    pg.evaluate("SV.m={}")
    res['hard A1']=kinds(1,0)
    iB=pg.evaluate("CATS.findIndex(c=>c.l==='B1'&&c.w.some(w=>w[2]))")
    res['hard B1']=kinds(1,iB)
    # każdy typ hard: odpowiedz poprawnie i błędnie
    out=[]
    pg.evaluate("start(0,1)")
    for k in range(40):
        pg.evaluate("deck=prio(CATS[lvl].w.slice());seen=[];map[5][5]=4;ask(5,5)")
        kind=pg.evaluate("qm+':'+tyv")
        if kind.startswith('ty'):
            right=k%2==0
            pg.fill('#ti',pg.evaluate("cur[1]") if right else 'zzz');pg.press('#ti','Enter')
        elif kind=='sb':
            pg.evaluate("sbT.replace(/[.?!]+$/,'').split(' ').forEach(()=>{});sbc=[];sbs.forEach((_,i)=>{})")
            # ułóż poprawnie: indeksy wg kolejności słów
            pg.evaluate("(()=>{const t=n2(sbT).split(' ');const used=new Set();sbc=[];t.forEach(w=>{const j=sbs.findIndex((x,i)=>!used.has(i)&&n2(x)===w);used.add(j);sbc.push(j)})})()")
            pg.evaluate("ans(-1)");right=True
        pg.wait_for_timeout(30)
        out.append((kind,pg.evaluate("document.getElementById('fb').innerText.slice(0,14)"),pg.evaluate("hearts")))
        pg.evaluate("answered&&hide();state='play';hearts=3")
    res['odpowiedzi hard']=collections.Counter(o[0]+' '+o[1].split('\n')[0] for o in out)
    # A2: dystraktory najbliższe (podobne) vs A1 losowe
    # win w trybie hard zapisuje osobne gwiazdki
    pg.evaluate("start(0,1);got=CATS[0].w.slice(0,3);right=asked=5;win()")
    res['gwiazdki hard/normal']=pg.evaluate("({h:SV.h,s:SV.s})")
    res['karta win']=pg.inner_text('#ov')[:90]
    pg.evaluate("menu()");res['menu po wygranej']=pg.inner_text('#ov .lvr >> nth=0')
    pg.screenshot(path=S+'/hard_menu2.png')
    pg.evaluate("start(0,1)");pg.evaluate("hide()");pg.wait_for_timeout(300);pg.screenshot(path=S+'/hard_hud.png')
    res['HARD flaga']=pg.evaluate("HARD");res['errors']=errs
    br.close()
print(json.dumps(res,ensure_ascii=False,indent=1))
