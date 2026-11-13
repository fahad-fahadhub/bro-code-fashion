import os
CHROME={'executable_path':'/usr/bin/google-chrome'} if os.path.exists('/usr/bin/google-chrome') else {}
import asyncio,urllib.parse,sys
from playwright.async_api import async_playwright
S=os.path.join(os.path.dirname(os.path.abspath(__file__)),"out")+os.sep;os.makedirs(S,exist_ok=True)
BASE=os.environ.get("BASE","http://localhost:8123/index.html")
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(**CHROME,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
        ctx=await b.new_context(viewport={'width':1366,'height':820});pg=await ctx.new_page()
        errs=[];pg.on('pageerror',lambda e:errs.append('PAGEERR '+str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
        pg.on('requestfailed',lambda r:errs.append('FAIL '+r.url[-60:]))
        await pg.add_init_script("window.__open=[];window.open=function(u){window.__open.push(u);return {}}")
        await pg.goto(BASE);await pg.wait_for_timeout(2500)
        await pg.screenshot(path=S+'t-hero.png')
        print('overflowX',await pg.evaluate('document.documentElement.scrollWidth>innerWidth'),'video',await pg.evaluate('[document.getElementById("hv").currentSrc.slice(-20),document.getElementById("hv").readyState]'))
        await pg.evaluate('BCF.prices.scorpion=799;BCF.prices.balance=899')
        # product flow
        await pg.evaluate('document.getElementById("shop").scrollIntoView()');await pg.wait_for_timeout(1500)
        await pg.screenshot(path=S+'t-shop.png')
        await pg.click('[data-open="scorpion"].pimg');await pg.wait_for_timeout(400)
        await pg.click('#pm-add');print('err msg:',await pg.inner_text('#pm-err'))
        await pg.click('#pm-sizes label:nth-child(3)');await pg.click('[data-pq="1"]');await pg.wait_for_timeout(200)
        await pg.screenshot(path=S+'t-modal.png')
        await pg.click('#pm-add');await pg.wait_for_timeout(500)
        # add second product (no price case: uses price 899 set) and a third without price
        await pg.click('#bag [data-close]');await pg.click('[data-open="silence"].pimg');await pg.click('#pm-sizes label:nth-child(2)');await pg.click('#pm-add');await pg.wait_for_timeout(500)
        await pg.screenshot(path=S+'t-bag.png')
        print('bag total:',await pg.inner_text('#bag-total'))
        await pg.click('#bag-go');await pg.wait_for_timeout(500)
        await pg.click('#co .confirm');await pg.wait_for_timeout(300)
        print('errors shown:',[await pg.inner_text('#e-'+k) for k in('name','phone','address','city','pincode')])
        await pg.fill('#f-name','Test Customer');await pg.fill('#f-phone','+91 98765 43210');await pg.fill('#f-address','12, 3rd Cross, 5th Main, HSR Layout Sector 2');await pg.fill('#f-city','Bengaluru');await pg.fill('#f-pin','560102');await pg.fill('#f-notes','Please call before delivery')
        await pg.screenshot(path=S+'t-checkout.png')
        await pg.click('#co .confirm');await pg.wait_for_timeout(500)
        u=await pg.evaluate('window.__open[0]');print('WA url starts:',u[:60]);print(urllib.parse.unquote(u.split('text=')[1]))
        print('cart after:',await pg.evaluate('JSON.parse(localStorage.getItem("bcf_cart_v1")).length'))
        await pg.screenshot(path=S+'t-done.png')
        print('errors:',errs[:6])
        await b.close()
asyncio.run(main())
