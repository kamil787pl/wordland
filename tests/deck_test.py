"""WordDeck (etap 1): ekran startowy, zagranie karty zadaniem, tury, bot, koniec pojedynku, wyjscie."""
import pathlib
from playwright.sync_api import sync_playwright
URL='file://'+str(pathlib.Path(__file__).resolve().parent.parent/'index.html')
res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':1000,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(400);pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(400)
    res['katalog: 64 kosmiczne karty (4 zaklecia), unikalne nazwy i emoji, klasy 1-3']=pg.evaluate("DKCARDS.length===64&&DKCARDS.filter(dkIsSp).length===4&&new Set(DKCARDS.map(c=>c.w)).size===64&&new Set(DKCARDS.map(c=>c.emo)).size===64&&[1,2,3].every(l=>DKCARDS.some(c=>c.lv===l))&&DKCARDS.every(c=>['f','o','b','s'].includes(c.t)&&c.atk>=1&&c.hp>=1&&!c.pl)")
    res['zadania ze slowek calego portalu: poziom, unikalne odpowiedzi, dobra odpowiedz']=pg.evaluate("['A1','A2','B1'].every(l=>{dkNew(l);for(let i=0;i<40;i++){const T=dkTask(l),n=l==='A1'?3:4;if(T.opts.length!==n||new Set(T.opts).size!==n||!T.opts[T.ok]||!(T.opts[T.ok]===T.w[0]||T.opts[T.ok]===T.w[1])||!CATS.some(c=>c.l===l&&c.w.includes(T.w)))return false}return true})")
    res['rotacja slowek: duzo roznych, bez powtorki pod rzad']=pg.evaluate("(()=>{dkNew('A1');const a=[];for(let i=0;i<30;i++)a.push(dkTask('A1').w[1]);return new Set(a).size>=18&&a.every((x,i)=>i===0||x!==a[i-1])})()")
    res['zadania: rozne rodzaje (en->pl, pl->en, luka w zdaniu)']=pg.evaluate("(()=>{dkNew('B1');const m=new Set();for(let i=0;i<120;i++)m.add(dkTask('B1').cap);return m.size>=3})()")
    res['slowa wymagajace powtorki wracaja czesciej']=pg.evaluate("(()=>{dkNew('A1');const P=clPool('A1'),bad=P[0].w,k=bad[0]+'='+bad[1];P.slice(1).forEach(x=>SV.m[x.w[0]+'='+x.w[1]]={b:5,r:5,w:0});SV.m[k]={b:0,r:0,w:4};let n=0;for(let i=0;i<300;i++){DK.recent=[];if(dkPick().w[1]===bad[1])n++}return n>300/P.length*3})()")

    res['talie: 10 kart na kazdym poziomie']=pg.evaluate("['A1','A2','B1'].every(l=>dkDeck(l).length===10&&new Set(dkDeck(l).map(c=>c.id)).size===10)")
    res['pole: 4 miejsca na karty']=pg.evaluate("(()=>{dkNew('A1');return DK.field[0].length===4&&DK.field[1].length===4})()")
    res['losowanie: kto zaczyna bywa rozny']=pg.evaluate("(()=>{const f=new Set();for(let i=0;i<80;i++){dkNew('A1');f.add(DK.first)}return f.size===2})()")
    pg.evaluate("dkNew('A1');DK.first=0;show('deck')");pg.wait_for_timeout(300)
    res['start: opis, Start i Wyjscie']=pg.locator('.dk-start .dk-go').count()==1 and pg.locator('.dk-start .xit').count()==1
    pg.click('.dk-start .pri,.dk-start .dk-go');pg.wait_for_timeout(200)
    res['po starcie: 4 karty w rece, energia 3']=pg.locator('.dk-h').count()==4 and pg.evaluate("DK.en")==3
    # zagranie karty: bledna odpowiedz dwa razy -> potkniecie
    pg.evaluate("DK.hand[0]=DKCARDS.find(c=>c.cost===1&&c.t==='f');dkPlay(0)");pg.wait_for_timeout(100)
    res['zadanie: 3 odpowiedzi na A1']=pg.locator('.dk-opts button').count()==3
    pg.evaluate("dkAns(DK.task.t.ok)");pg.wait_for_timeout(1000)
    res['po dobrej odpowiedzi: wybor miejsca (4 pola, energia jeszcze nie zabrana)']=pg.evaluate("!!DK.place&&DK.place.mode==='full'&&DK.en===3")and pg.locator('.dk-slot.pick').count()==4
    res['podczas wyboru miejsca nie mozna grac ani konczyc tury']=pg.evaluate("(()=>{dkPlay(1);dkEnd();return !DK.task&&DK.ph==='p'&&!!DK.place})()")
    pg.locator('.dk-slot.pick').nth(2).click();pg.wait_for_timeout(200)
    res['karta stoi w wybranym miejscu (3), pelna moc, energia 2']=pg.evaluate("DK.field[0][2]&&!DK.field[0][0]&&DK.field[0][2].mode==='full'&&DK.field[0][2].atk===DK.field[0][2].c.atk&&DK.en===2&&!DK.place")
    pg.evaluate("DK.hand[0]=DKCARDS.find(c=>c.cost===1&&c.t==='f'&&c.id!==DK.field[0][2].c.id);dkPlay(0)");pg.wait_for_timeout(100)
    pg.evaluate("const t=DK.task.t;dkAns((t.ok+1)%t.opts.length)");pg.wait_for_timeout(100)
    res['pierwsza pomylka: druga szansa']=pg.evaluate("DK.task&&DK.task.t.tries===1&&!DK.task.t.done")
    pg.evaluate("const t=DK.task.t;dkAns(t.opts.map((_,k)=>k).find(k=>k!==t.ok&&!t.dis[k]))");pg.wait_for_timeout(1700)
    pg.evaluate("dkPut(1)")
    res['druga pomylka: karta potkniecia (moc 1) w miejscu 2']=pg.evaluate("DK.field[0][1]&&DK.field[0][1].mode==='bad'&&DK.field[0][1].atk===1")
    res['za malo energii nie otwiera zadania']=pg.evaluate("DK.en=0;DK.hand[0]=DKCARDS.find(c=>c.cost===2);dkPlay(0);!DK.task")
    pg.evaluate("DK.en=2");pg.evaluate("dkEnd()");pg.wait_for_timeout(300)
    res['koniec tury: faza ataku/tura wroga']=pg.evaluate("DK.ph==='x'||DK.ph==='b'")
    pg.wait_for_function("DK.ph==='p'||DK.over",timeout=15000)
    res['tura 2: energia 4, bot zagral karte']=pg.evaluate("DK.turn===2&&DK.en===4&&DK.field[1].some(Boolean)")
    # symulacja do konca (zawsze dobre odpowiedzi)
    for i in range(12):
        if pg.evaluate("DK.over"):break
        pg.evaluate("""(()=>{for(let k=0;k<3;k++){if(DK.task)break;const i=DK.hand.findIndex(c=>c.cost<=DK.en);if(i<0||DK.field[0].indexOf(null)<0)break;dkPlay(i);if(DK.task){dkAns(DK.task.t.ok);dkPlace();dkPut(DK.field[0].indexOf(null))}}dkEnd()})()""")
        pg.wait_for_function("DK.ph==='p'||DK.over",timeout=20000)
    res['pojedynek konczy sie wynikiem']=pg.evaluate("DK.over===1&&['w','l','d'].includes(DK.res)&&DK.turn<=8")
    res['koniec rundy: wynik bitwy i przycisk Nastepna runda']=pg.locator('.dk-ov.end').count()==1 and 'Następna runda' in pg.inner_text('.gbar') and not pg.evaluate("DK.sover")
    res['statystyka zapisana lokalnie']=pg.evaluate("SV.deck&&SV.deck.g===1&&Object.keys(SV.m).length>0")
    pg.click('.gbar .pri');pg.wait_for_timeout(200)
    res['nastepna runda: zaczyna druga strona, runda 2, wynik zachowany']=pg.evaluate("DK.ser.n===2&&!DK.over&&DK.turn===1&&DK.ser.w[0]+DK.ser.w[1]+DK.ser.d===1")
    pg.evaluate("dkLvl(DKlvl)");pg.wait_for_timeout(200)
    res['nowa bitwa: ekran startowy, wynik 0:0']=pg.locator('.dk-start').count()==1 and pg.evaluate("DK.ser.w[0]===0&&DK.ser.w[1]===0&&DK.ser.n===1")
    pg.click('.dk-start .xit');pg.wait_for_timeout(300)
    res['Wyjscie wraca na strone glowna']=pg.evaluate("view")=='home'
    pg.evaluate("show('deck');dkLvl('A1');DK.first=1;dkStart()");pg.wait_for_function("DK.ph==='p'",timeout=15000)
    res['zaczyna rywal: jego karta na polu, potem tura gracza (runda 1, energia 3)']=pg.evaluate("DK.turn===1&&DK.en===3&&DK.field[1].some(Boolean)&&DK.hand.length===4")
    pg.evaluate("dkEnd()");pg.wait_for_function("DK.turn===2&&DK.ph==='b'||DK.turn===2&&DK.ph==='x'||DK.turn===2",timeout=15000)
    res['po rundzie gracza zaczyna sie runda 2 od rywala']=pg.evaluate("DK.turn===2")
    for i in range(12):
        if pg.evaluate("DK.over"):break
        pg.wait_for_function("DK.ph==='p'||DK.over",timeout=20000)
        if pg.evaluate("DK.over"):break
        pg.evaluate("dkEnd()")
        pg.wait_for_function("DK.ph!=='x'&&DK.ph!=='b'||DK.over",timeout=20000)
    res['pojedynek z rywalem na starcie tez sie konczy']=pg.evaluate("DK.over===1&&DK.turn<=8")
    # --- nowe mechaniki
    ST="dkNew('B1');DK.first=0;DK.go=1;DK.turn=1;DK.ph='p';DK.en=6;const C=w=>DKCARDS.find(c=>c.w===w);"
    res['podglad przewagi: +1 / -1 / prosto w serca']=pg.evaluate("(()=>{"+ST+"DK.field[0][0]=dkInst(C('Rakieta'),'full');DK.field[1][0]=dkInst(C('Obcy'),'full');DK.field[0][1]=dkInst(C('Obcy'),'full');DK.field[1][1]=dkInst(C('Rakieta'),'full');DK.field[0][2]=dkInst(C('Zwiadowca'),'full');renderDeck();return document.querySelectorAll('.dk-row.p .adv.up').length===1&&document.querySelectorAll('.dk-row.p .adv.dn').length===1&&document.querySelectorAll('.dk-row.p .adv.open').length===1&&document.querySelectorAll('.dk-row.e .adv.dn').length===1})()")
    res['ruch karty: 1 energii, raz na turę, zamiana i puste pole']=pg.evaluate("(()=>{"+ST+"DK.field[0][0]=dkInst(C('Rakieta'),'full');DK.field[0][1]=dkInst(C('Zwiadowca'),'full');renderDeck();dkMove(0);const sel=DK.mv===0;dkMove(2);const a=DK.field[0][2]&&DK.field[0][2].c.w==='Rakieta'&&!DK.field[0][0]&&DK.en===5&&DK.moved;dkMove(1);dkMove(0);return sel&&a&&DK.mv==null&&DK.en===5})()")
    pg.evaluate("dkNew('B1');DK.first=0;DK.go=1;DK.turn=1;DK.ph='p';DK.en=6;DK.field[0][0]=dkInst(DKCARDS.find(c=>c.w==='Rakieta'),'full');renderDeck()")
    pg.locator('.dk-row.p .dk-m').first.click();pg.wait_for_timeout(100)
    res['ruch karty: klik w karte pokazuje pola docelowe']=pg.locator('.dk-slot.pick.mv').count()==3
    res['zaklecia: leczenie, wzmocnienie, zamrozenie, obrazenia']=pg.evaluate("(()=>{"+ST+"DK.hero[0]=10;dkCast(0,C('Nanoboty'),'full',0);const h=DK.hero[0]===14;DK.field[0][0]=dkInst(C('Rakieta'),'full');DK.field[0][1]=dkInst(C('Zwiadowca'),'full');const a0=DK.field[0][0].atk;dkCast(0,C('Wzmacniacz'),'full',0);const b=DK.field[0][0].atk===a0+2&&DK.field[0][1].atk===C('Zwiadowca').atk+2;DK.field[1][0]=dkInst(C('Obcy'),'full');DK.field[1][2]=dkInst(C('Gwiazdka'),'full');dkCast(0,C('Mgławica mrozu'),'full',0);const f=DK.field[1][0].frozen&&DK.field[1][2].frozen;dkCast(0,C('Burza słoneczna'),'half',0);return h&&b&&f&&DK.hero[1]===18})()")
    res['zaklecie z reki: dziala od razu, nie zajmuje pola, zabiera energie']=pg.evaluate("(()=>{"+ST+"DK.hand[0]=C('Burza słoneczna');dkPlay(0);dkAns(DK.task.t.ok);dkPlace();return DK.hero[1]===17&&!DK.place&&DK.en===3&&DK.field[0].every(x=>!x)&&DK.hand.length===3})()")
    res['seria 3 dobrych odpowiedzi: +1 energii']=pg.evaluate("(()=>{"+ST+"DK.streak=2;DK.hand[0]=C('Rakieta');dkPlay(0);dkAns(DK.task.t.ok);dkPlace();return DK.streak===0&&DK.en===7&&!!DK.place})()")
    res['pomylka zeruje serie']=pg.evaluate("(()=>{"+ST+"DK.streak=2;DK.hand[0]=C('Rakieta');dkPlay(0);const t=DK.task.t;const w=k=>t.opts.map((_,j)=>j).filter(j=>j!==t.ok&&!t.dis[j])[0];dkAns(w());dkAns(w());dkPlace();return DK.streak===0&&DK.st.bad===1&&Object.keys(DK.miss).length===1})()")
    res['trudne zadanie: wpisanie slowa, podpowiedz, druga szansa, bonus']=pg.evaluate("(()=>{"+ST+"DK.hand[0]=C('Rakieta');dkPlay(0);dkHard(1);const T=DK.task.t;dkTyp('zzz');const h=T.tries===1&&/liter/.test(T.hint)&&!T.done;dkTyp(' '+T.h.ok.toUpperCase()+' ');const half=T.done==='half';dkPlace();const m=DK.place&&DK.place.b===0&&DK.place.mode==='half';DK.place=null;DK.hand[0]=C('Zwiadowca');dkPlay(0);dkHard(1);dkTyp(DK.task.t.h.ok);dkPlace();return h&&half&&m&&DK.place.b===1&&DK.place.mode==='full'})()")
    res['trudne zadanie: bonus +1 moc i +1 tarcza na karcie']=pg.evaluate("(()=>{"+ST+"DK.hand[0]=C('Rakieta');dkPlay(0);dkHard(1);dkTyp(DK.task.t.h.ok);dkPlace();dkPut(0);const x=DK.field[0][0];return x.atk===C('Rakieta').atk+1&&x.hp===C('Rakieta').hp+1})()")
    pg.evaluate("dkNew('B1');DK.first=0;DK.go=1;DK.turn=1;DK.ph='p';DK.en=6;DK.hand[0]=DKCARDS.find(c=>c.w==='Rakieta');renderDeck();dkPlay(0);dkHard(1)");pg.wait_for_timeout(150)
    res['trudne zadanie: pole tekstowe w nakladce']=pg.locator('#dk-in').count()==1 and pg.locator('.dk-hint,.dk-typ').count()>=1
    res['plan bota (B1): stawia Flote naprzeciw Obcego gracza']=pg.evaluate("(()=>{"+ST+"DK.ben=6;DK.bhand=[C('Rakieta')];DK.field[0][2]=dkInst(C('Obcy'),'full');let ok=1;for(let i=0;i<25;i++){const p=dkPlan(1);if(!p||p.s!==2)ok=0}return !!ok})()")
    res['bot rzuca zaklecie zamiast wystawiac karte, gdy ma tylko je']=pg.evaluate("(()=>{"+ST+"DK.ben=6;DK.bhand=[C('Burza słoneczna')];const p=dkPlan(1);return p&&p.s===-1&&p.c.w==='Burza słoneczna'})()")
    pg.evaluate("dkNew('A2');DK.first=0;DK.go=1;DK.over=1;DK.ph='x';DK.hero=[5,0];DK.res='l';(()=>{const P=clPool('A2');DK.miss={a:P[0],b:P[1]}})();renderDeck()");pg.wait_for_timeout(150)
    res['koniec: lista bledow i Powtorz teraz']=pg.locator('.dk-miss li').count()==2 and pg.locator('.dk-ov.end .dk-go').count()==1
    pg.click('.dk-ov.end .dk-go');pg.wait_for_timeout(150)
    res['powtorka: pytania z odpowiedziami']=pg.locator('.dk-opts button').count()>=3
    pg.evaluate("dkDAns(DK.drill.t.ok)");pg.wait_for_timeout(900)
    pg.evaluate("dkDAns(DK.drill.t.ok)");pg.wait_for_timeout(900)
    res['powtorka: koniec i wynik 2/2']=pg.evaluate("DK.drill&&DK.drill.fin&&DK.drill.ok===2")
    pg.evaluate("dkDClose()");pg.wait_for_timeout(100)
    res['powtorka: zamkniecie czysci poprawione slowka']=pg.evaluate("!DK.drill&&Object.keys(DK.miss).length===0")
    pg.evaluate("""(()=>{dkNew('B1');DK.first=0;DK.go=1;DK.turn=1;DK.ph='x';const C=w=>DKCARDS.find(c=>c.w===w);window.__a=dkInst(C('Zwiadowca'),'full');window.__b=dkInst(C('Rakieta'),'full');window.__f=dkInst(C('Skaut'),'full');window.__g=dkInst(C('Łazik'),'full');window.__f.frozen=1;
      DK.field[0][0]=window.__a;DK.field[1][0]=window.__b;DK.field[0][1]=window.__f;DK.field[1][1]=window.__g;window.__done=0;dkCombat(()=>{window.__done=1})})()""")
    pg.wait_for_function("window.__done===1",timeout=15000)
    res['walka jednoczesna: obie karty dostaja obrazenia od siebie']=pg.evaluate("(()=>{const C=w=>DKCARDS.find(c=>c.w===w);return __a.hp===C('Zwiadowca').hp-C('Rakieta').atk&&__b.hp===C('Rakieta').hp-C('Zwiadowca').atk})()")
    res['zamrozona karta nie atakuje, a po walce sie odmraza']=pg.evaluate("__g.hp===__g.mhp&&!__f.frozen")
    res['bitwa do 3 wygranych: 3. wygrana konczy bitwe, przycisk Nowy pojedynek']=pg.evaluate("(()=>{dkNew('A1');DK.ser.w=[2,1];DK.hero=[5,0];dkFinish();return DK.sover==='w'&&DK.ser.w[0]===3})()") and 'Nowy pojedynek' in pg.inner_text('.gbar')
    res['podsumowanie bitwy: puchar, wynik, lista rund, statystyki']=pg.evaluate("(()=>{dkNew('A1');DK.ser.w=[2,1];DK.hero=[5,0];dkFinish();const o=document.querySelector('.dk-sum.win');return !!o&&!!o.querySelector('.dk-cup svg')&&o.querySelectorAll('.dk-rd').length===1&&o.querySelector('.dk-big b').textContent==='3'&&o.querySelectorAll('.dk-tiles>div').length===3})()")
    res['przegrana 3. runda rywala konczy bitwe porazka']=pg.evaluate("(()=>{dkNew('A1');DK.ser.w=[1,2];DK.hero=[0,5];dkFinish();return DK.sover==='l'})()")
    res['wygrana rundy (1:1 -> 2:1) nie konczy bitwy, kolejna runda zaczyna druga strona']=pg.evaluate("(()=>{dkNew('A1');DK.first=0;DK.ser.w=[1,1];DK.hero=[5,0];dkFinish();const f=DK.first;dkRound();return !DK.sover&&DK.ser.w[0]===2&&DK.first===1-f&&DK.ser.n===2})()")
    res['remis w sercach rozstrzyga sila ostatnich ciosow']=pg.evaluate("(()=>{dkNew('A1');DK.hero=[0,0];DK.def=[1,3];dkFinish();return DK.res==='w'})()")
    res['trudne zadanie: odpowiedz to slowo z bazy, nie z karty; pytanie nie zdradza odpowiedzi']=pg.evaluate("(()=>{dkNew('B1');for(let i=0;i<60;i++){const T=dkTask(i%2?'B1':'A2');const h=dkHardQ(T);if(h.ok!==T.w[1])return false;if(!h.gap&&h.q.toLowerCase().includes(h.ok.toLowerCase()))return false;if(h.gap&&!h.q.includes('___'))return false}return true})()")
    res['odpowiedzi zapisuja postep slowka we wspolnej bazie portalu']=pg.evaluate("(()=>{"+ST+"DK.hand[0]=C('Rakieta');dkPlay(0);const w=DK.task.t.w,k=w[0]+'='+w[1],r0=(SV.m[k]||{r:0}).r;dkAns(DK.task.t.ok);dkPlace();return SV.m[k].r===r0+1})()")
    pg.evaluate("dkNew('B1');DK.first=0;DK.go=1;DK.turn=1;DK.ph='p';DK.en=6;DK.hand[0]=DKCARDS.find(c=>c.w==='Rakieta');renderDeck();dkPlay(0)");pg.wait_for_timeout(150)
    res['nakladka pokazuje zagrywana karte (nazwa kosmiczna)']=pg.locator('.dk-tcw .dk-h.big strong').inner_text().lower()=='rakieta'
    res['kazda z 64 kart ma wlasna ikone SVG (nie emoji)']=pg.evaluate("DKCARDS.length===64&&DKCARDS.every(c=>DKIC[c.w]&&dkIc(c).startsWith('<svg'))")
    res['nakladka i reka renderuja ikone SVG']=pg.evaluate("document.querySelectorAll('.dk-tcw .dk-h.big .dart svg.dic').length===1")
    for l in ['A1','A2','B1']:
        pg.evaluate("show('deck');dkLvl('%s')"%l);pg.wait_for_timeout(100)
        res['poziom '+l+': talia z kart <= poziomu']=pg.evaluate("DK.deck.concat(DK.hand).every(c=>c.lv<=DKL[DK.lvl])")
    pg.set_viewport_size({'width':390,'height':800});pg.evaluate("show('deck');dkLvl('A2');dkStart()");pg.wait_for_timeout(300)
    res['telefon: brak przewijania poziomego']=pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
    print({k:v for k,v in res.items() if v is not True});print('OK' if not errs else 'BLEDY',errs)
