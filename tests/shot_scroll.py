import os
CHROME={'executable_path':'/usr/bin/google-chrome'} if os.path.exists('/usr/bin/google-chrome') else {}
import asyncio,sys
from playwright.async_api import async_playwright
from PIL import Image
S=os.path.join(os.path.dirname(os.path.abspath(__file__)),"out")+os.sep;os.makedirs(S,exist_ok=True)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(**CHROME,args=['--no-sandbox'])
        for name,vw,vh,n in [('d',1366,820,14),('m',390,800,12)]:
            pg=await b.new_page(viewport={'width':vw,'height':vh});errs=[]
            pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
            await pg.goto('http://localhost:8123/index.html');await pg.wait_for_timeout(2500)
            H=await pg.evaluate('document.documentElement.scrollHeight');shots=[]
            for i in range(n):
                await pg.evaluate('window.scrollTo(0,%d)'%int((H-vh)*i/(n-1)));await pg.wait_for_timeout(1500)
                path='/tmp/bcf_s%d.png'%i;await pg.screenshot(path=path);shots.append(path)
            print(name,'H',H,'overflow',await pg.evaluate('document.documentElement.scrollWidth>innerWidth'),errs[:3],'fonts',await pg.evaluate('[...document.fonts].filter(f=>f.status=="loaded").map(f=>f.family+f.weight).join(",")'))
            cols=5 if name=='d' else 6;w=400 if name=='d' else 210
            ims=[Image.open(s).convert('RGB') for s in shots];h=int(ims[0].height*w/ims[0].width);rows=(len(ims)+cols-1)//cols
            sh=Image.new('RGB',(w*cols,h*rows))
            for i,im in enumerate(ims):sh.paste(im.resize((w,h)),((i%cols)*w,(i//cols)*h))
            sh.save(S+'full-%s.jpg'%name,quality=80);await pg.close()
        await b.close()
asyncio.run(main())
