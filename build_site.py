import json,os,shutil,sys,re
ROOT=os.path.dirname(os.path.abspath(__file__));SRC=ROOT+"/src";OUT=ROOT+"/website"
_ARGS=[a for a in sys.argv[1:] if not a.startswith("--")]
SITE=_ARGS[0].rstrip("/") if _ARGS else ""
FRESH="--fresh" in sys.argv
PH_TEL="+918296889214";PH_DISP="+91 82968 89214";WA="918296889214"
NAME="Bro Code Fashion"
TITLE="Bro Code Fashion | Men's casual wear, order on WhatsApp | Bengaluru"
DESC="Graphic tees and men's casual wear from Bro Code Fashion, Bengaluru. Choose your tee, confirm your order and send it on WhatsApp. Order anytime, replies 9 AM to 9 PM."
PRODUCTS=[
 ("scorpion","Scorpion Tee","Cream",["back"],"Cream tee with a distressed scorpion graphic across the back."),
 ("thisday","This Day Tee","Black and navy tie-dye",["back"],"Black and navy tie-dye tee with a bold slogan printed on the back."),
 ("balance","Balance Tee","Washed black with gold print",["front","back"],"Washed black tee with a small gold wordmark on the front and a gold line-art print on the back."),
 ("lablack","California Tee","Washed black",["back"],"Washed black tee with a large California back print."),
 ("mythic","Gothic Crest Tee","Black tie-dye",["front"],"Black tie-dye tee with a white gothic crest graphic on the chest."),
 ("labrown","Rust LA Tee","Cream and rust tie-dye",["back"],"Cream tee with rust tie-dye and a large LA California back print."),
 ("silence","Silence Tee","Acid-wash black",["front","back"],"Acid-wash black tee with a Silence wordmark on the front and a skull graphic on the back."),
 ("eagle","Eagle Tee","Black",["front","back"],"Black tee with a white eagle crest on the front and a larger winged graphic on the back."),
 ("spider","Neon Web Tee","Black and grey with neon pink",["front","back"],"Black and grey tee with a neon pink web graphic on the front and a spider on the back."),
 ("unreal","Crackle Tee","Black with white crackle print",["front","back"],"Black tee with an all-over white crackle print and a small wordmark on the chest."),
]
LBL={"front":"Front print","back":"Back print"}
prods=[dict(id=i,code="BCF-"+i.upper(),name=n,colour=c,desc=d,views=[dict(k=v,label=LBL[v]) for v in vs]) for i,n,c,vs,d in PRODUCTS]
CONFIG={"brand":NAME,"whatsapp":WA,"phone":PH_DISP,"instagram":"","email":"","currency":"₹",
 "sizes":["S","M","L","XL"],"ga4":"","metaPixel":"",
 "prices":{p["id"]:None for p in prods},"products":prods}
def cfgjs():
    j=json.dumps(CONFIG,indent=1,ensure_ascii=False)
    # keep prices block easy to find
    return ("/* ===== BRO CODE FASHION: STORE SETTINGS =====\n"
    " Edit the values below, then re-upload the site.\n"
    " prices : put a number for each tee (for example 799). Leave null to show 'Price on WhatsApp'.\n"
    " sizes  : sizes offered on every tee.\n"
    " instagram / email : add them here and they appear on the Contact section automatically.\n"
    " ga4 / metaPixel : paste your Google Analytics ID (G-XXXX) or Meta Pixel ID to switch tracking on.\n"
    "================================================== */\nwindow.BCF="+j+";\n")
WA_ICON='<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16.04 3C9.4 3 4 8.4 4 15.04c0 2.12.56 4.2 1.62 6.02L4 28l7.12-1.86a12.02 12.02 0 0 0 4.92 1.04C22.68 27.18 28 21.78 28 15.14 28 8.5 22.68 3 16.04 3Zm0 21.96c-1.7 0-3.36-.46-4.82-1.32l-.34-.2-4.22 1.1 1.12-4.1-.22-.36A9.9 9.9 0 0 1 6.1 15.04c0-5.46 4.46-9.9 9.94-9.9 5.46 0 9.9 4.44 9.9 9.9 0 5.46-4.44 9.92-9.9 9.92Zm5.44-7.42c-.3-.14-1.76-.86-2.04-.96-.28-.1-.48-.14-.68.14-.2.3-.78.96-.96 1.16-.18.2-.36.22-.66.08-.3-.16-1.26-.46-2.4-1.48-.88-.78-1.48-1.76-1.66-2.06-.18-.3-.02-.46.14-.6.14-.14.3-.36.46-.54.14-.18.2-.3.3-.5.1-.2.04-.38-.02-.54-.08-.14-.68-1.64-.94-2.24-.24-.58-.5-.5-.68-.5l-.58-.02c-.2 0-.52.08-.8.38-.28.3-1.06 1.04-1.06 2.54 0 1.5 1.1 2.94 1.24 3.14.16.2 2.16 3.3 5.24 4.62.74.32 1.3.5 1.76.64.74.24 1.4.2 1.94.12.6-.1 1.76-.72 2.02-1.42.24-.7.24-1.3.18-1.42-.08-.12-.28-.2-.58-.34Z"/></svg>'
DEFS=('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
'<linearGradient id="gAmC" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff7a14"/><stop offset=".5" stop-color="#ffd27a"/><stop offset="1" stop-color="#ff8a1a"/></linearGradient>'
'<linearGradient id="gAmT" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe9bd"/><stop offset=".5" stop-color="#fff8e6"/><stop offset="1" stop-color="#ffc46b"/></linearGradient>'
'<linearGradient id="gEmb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6b3510"/><stop offset=".5" stop-color="#2a1306"/><stop offset="1" stop-color="#7a3d12"/></linearGradient>'
'<linearGradient id="gGld" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#a06c14"/><stop offset=".3" stop-color="#ffe3a0"/><stop offset=".55" stop-color="#c9972f"/><stop offset=".8" stop-color="#f6d77f"/><stop offset="1" stop-color="#9a6a18"/></linearGradient>'
'<symbol id="hanger" viewBox="0 0 200 60"><path d="M100 30V17C100 5 116 3 116 14C116 21 108 23 100 30L22 52Q14 55 22 56H178Q186 55 178 52L100 30" fill="none" stroke="url(#gGld)" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></symbol>'
'<symbol id="g-kurta" viewBox="0 0 200 220"><path style="fill:url(#gEmb);stroke:#ffb13b" stroke-width="2" stroke-linejoin="round" d="M72 24Q100 46 128 24L152 38L176 78L154 92L150 80L156 206H44L50 80L46 92L24 78L48 38Z"/><path d="M100 36V132" fill="none" stroke="#ffb13b" stroke-width="1.6"/><circle cx="100" cy="54" r="2.4" fill="#ffb13b"/><circle cx="100" cy="72" r="2.4" fill="#ffb13b"/><circle cx="100" cy="90" r="2.4" fill="#ffb13b"/><path d="M62 160H138M62 170H138" fill="none" stroke="#ffb13b" stroke-width="1.2" opacity=".65"/></symbol>'
'<symbol id="g-anar" viewBox="0 0 200 220"><path style="fill:url(#gEmb);stroke:#ffb13b" stroke-width="2" stroke-linejoin="round" d="M78 22Q100 42 122 22L136 30L124 74L190 206H10L76 74L64 30Z"/><path d="M76 76Q100 86 124 76M100 84L68 206M100 84L132 206M100 84V206M16 190H184" fill="none" stroke="#ffb13b" stroke-width="1.4" opacity=".7"/></symbol>'
'<symbol id="mark" viewBox="0 0 260 280"><path d="M78 84L66 36L102 62L130 22L158 62L194 36L182 84Z" fill="url(#gAmC)"/><rect x="74" y="84" width="112" height="14" rx="4" fill="url(#gAmC)"/><circle cx="66" cy="33" r="6" fill="url(#gAmC)"/><circle cx="130" cy="17" r="6.5" fill="url(#gAmC)"/><circle cx="194" cy="33" r="6" fill="url(#gAmC)"/><text x="130" y="226" text-anchor="middle" font-family="Cinzel,serif" font-weight="700" font-size="104" fill="url(#gAmT)">BCF</text></symbol>'
'<symbol id="logo" viewBox="0 0 520 380"><path d="M208 84L196 36L232 62L260 22L288 62L324 36L312 84Z" fill="url(#gAmC)"/><rect x="204" y="84" width="112" height="14" rx="4" fill="url(#gAmC)"/><circle cx="196" cy="33" r="6" fill="url(#gAmC)"/><circle cx="260" cy="17" r="6.5" fill="url(#gAmC)"/><circle cx="324" cy="33" r="6" fill="url(#gAmC)"/>'
'<text x="260" y="262" text-anchor="middle" font-family="Cinzel,serif" font-weight="700" font-size="168" letter-spacing="2" fill="url(#gAmT)">BCF</text><path d="M30 240C170 192 340 140 492 112C352 170 200 216 52 250Z" fill="url(#gAmC)"/>'
'<text x="260" y="326" text-anchor="middle" font-family="Cinzel,serif" font-weight="700" font-size="52" letter-spacing="12" fill="url(#gAmT)">BRO CODE</text><text x="260" y="364" text-anchor="middle" font-family="Cinzel,serif" font-weight="700" font-size="24" letter-spacing="20" fill="url(#gAmC)">FASHION</text></symbol></defs></svg>')
MARK='<svg class="mark" viewBox="0 0 260 280" role="img" aria-label="Bro Code Fashion"><use href="#mark"/></svg>'
LOGO='<svg class="logo" viewBox="0 0 520 380" role="img" aria-label="Bro Code Fashion logo"><use href="#logo"/></svg>'
def garm(k): return '<div class="garm"><svg class="hg" viewBox="0 0 200 60" aria-hidden="true"><use href="#hanger"/></svg><svg class="gm" viewBox="0 0 200 220" aria-hidden="true"><use href="#g-%s"/></svg></div>'%k
def url(p): return (SITE+"/"+p) if SITE else p
def head(title,desc,path="",extra="",preview=False,depth=0):
    pre="../"*depth
    h='<!doctype html>\n<html lang="en-IN">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<meta name="claude:viewport-fit-sides" content="cover">\n'
    h+='<title>%s</title>\n<meta name="description" content="%s">\n<meta name="theme-color" content="#0a0605">\n'%(title,desc)
    if SITE: h+='<link rel="canonical" href="%s">\n'%(SITE+"/"+path)
    h+='<meta property="og:type" content="website">\n<meta property="og:site_name" content="Bro Code Fashion">\n<meta property="og:locale" content="en_IN">\n<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n<meta property="og:image" content="%s">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'%(title,desc,url("og-image.jpg"))
    if SITE: h+='<meta property="og:url" content="%s">\n'%(SITE+"/"+path)
    h+='<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="%s">\n<meta name="twitter:description" content="%s">\n<meta name="twitter:image" content="%s">\n'%(title,desc,url("og-image.jpg"))
    h+='<link rel="icon" href="favicon.svg" type="image/svg+xml">\n<link rel="icon" href="favicon.ico" sizes="32x32">\n<link rel="apple-touch-icon" href="apple-touch-icon.png">\n<link rel="manifest" href="site.webmanifest">\n'
    h+='<link rel="preload" href="assets/fonts/space-mono-700.woff2" as="font" type="font/woff2" crossorigin>\n<link rel="preload" href="assets/fonts/space-grotesk-400.woff2" as="font" type="font/woff2" crossorigin>\n'
    if preview: h+='<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Space+Grotesk:wght@400;500;700&family=Cinzel:wght@700&display=swap">\n'
    h+='<link rel="stylesheet" href="assets/css/app.css">\n'+extra+'</head>\n'
    return h
def ldjson():
    d={"@context":"https://schema.org","@type":"OnlineStore","name":NAME,"description":DESC,"telephone":PH_TEL,"areaServed":"IN",
       "address":{"@type":"PostalAddress","addressLocality":"Bengaluru","addressRegion":"Karnataka","addressCountry":"IN"},
       "image":url("og-image.jpg"),"logo":url("icon-512.png"),"contactPoint":{"@type":"ContactPoint","telephone":PH_TEL,"contactType":"customer service","availableLanguage":["English"]}}
    if SITE: d["url"]=SITE+"/"
    il={"@context":"https://schema.org","@type":"ItemList","name":"Bro Code Fashion tees","itemListElement":[{"@type":"ListItem","position":i+1,"name":p["name"],"image":url("assets/img/p-%s-%s-800.webp"%(p["id"],p["views"][0]["k"]))} for i,p in enumerate(prods)]}
    return '<script type="application/ld+json">%s</script>\n<script type="application/ld+json">%s</script>\n'%(json.dumps(d,ensure_ascii=False),json.dumps(il,ensure_ascii=False))
def card(p):
    v=p["views"];i=p["id"]
    def im(k,hid=False): return '<img src="assets/img/p-%s-%s-480.webp" srcset="assets/img/p-%s-%s-480.webp 480w, assets/img/p-%s-%s-800.webp 800w" sizes="(max-width:520px) 46vw,(max-width:1000px) 31vw,280px" alt="%s%s" width="480" height="600" loading="lazy" decoding="async">'%(i,k,i,k,i,k,p["name"]+" — "+LBL[k] if not hid else "", "" )
    tag="Front + back" if len(v)==2 else LBL[v[0]["k"]]
    imgs=im(v[0]["k"])+(im(v[1]["k"],True) if len(v)==2 else "")
    if len(v)==2: imgs=imgs.replace('alt=""','alt="" aria-hidden="true"')
    return ('<li><article class="pcard" data-r><button class="pimg" type="button" data-open="%s" aria-label="View %s"><span class="tag">%s</span>%s</button>'
            '<div class="pinfo"><h3>%s</h3><span class="c">%s</span><span class="price" data-price="%s">Price on WhatsApp</span><button class="btn" type="button" data-open="%s">Choose size</button></div></article></li>')%(i,p["name"],tag,imgs,p["name"],p["colour"],i,i)
REEL=[("scorpion","Scorpion Tee"),("eagle","Eagle Tee"),("spider","Neon Web Tee"),("labrown","Rust LA Tee")]
def rowimgs(keys): return ''.join('<img src="assets/img/a-%s-520.webp" alt="" loading="lazy" width="320" height="256">'%k for k in keys*2)
def footer(depth=0):
    return ('<footer class="foot"><div class="w"><div class="fgrid"><div>'+LOGO+'<p>Men\'s casual wear from Bengaluru. Order anytime on WhatsApp. We reply 9 AM to 9 PM.</p></div>'
    '<div><p class="fh">Shop</p><a href="/#shop">The drop</a><a href="/#how">How to order</a><a href="/#collections">Collections</a><a href="/#faq">Questions</a></div>'
    '<div><p class="fh">Help</p><a href="/shipping-returns.html">Shipping &amp; returns</a><a href="/terms.html">Terms</a><a href="/privacy.html">Privacy</a></div>'
    '<div><p class="fh">Contact</p><a href="tel:%s">%s</a><a href="https://wa.me/%s" target="_blank" rel="noopener">WhatsApp</a><a href="/#contact">All contact details</a></div></div>'
    '<p class="giant" aria-hidden="true">BRO CODE</p><p class="legal">© 2026 Bro Code Fashion, Bengaluru. All rights reserved.</p></div></footer>')%(PH_TEL,PH_DISP,WA)
def rel(s): return s.replace('href="/#','href="index.html#').replace('href="/','href="')
def index(preview=False):
    cards=''.join(card(p) for p in prods)
    reel_rows=''.join('<p class="row" data-step="%d" data-mode="cur"><span>0%d</span>%s</p>'%(i,i+1,n) for i,(k,n) in enumerate(REEL))
    reel_imgs=''.join('<img data-step="%d" src="assets/img/a-%s-960.webp" alt="%s styled in an amber-lit frame" loading="lazy" width="960" height="760">'%(i,k,n) for i,(k,n) in enumerate(REEL))
    reel_btn=''.join('<button type="button" data-step="%d" data-mode="cur" data-open="%s">Shop %s</button>'%(i,k,n) for i,(k,n) in enumerate(REEL))
    h=head("Bro Code Fashion" if preview else TITLE,DESC,"",ldjson(),preview)
    b='<body>\n<a class="skip" href="#shop">Skip to the shop</a>\n'+DEFS+'\n'
    b+='<div class="ann" role="region" aria-label="Ordering and reply hours"><span>Order anytime on WhatsApp</span><i>·</i><span data-status>Replies 9 AM – 9 PM</span></div>\n'
    b+='<div class="navwrap"><nav class="nav" id="top-nav" aria-label="Main"><a href="#top" aria-label="Bro Code Fashion home">'+MARK+'</a><a class="opt" href="#shop">Shop</a><a class="opt" href="#how">How to order</a><a class="opt" href="#collections">Collections</a><a class="opt" href="#contact">Contact</a><button class="bagbtn" type="button" data-bag aria-label="Open bag">Bag <b data-cart-count hidden>0</b></button></nav></div>\n'
    b+=('<header class="hero" id="top"><picture class="poster"><source media="(max-width:760px)" srcset="assets/img/poster-port.webp"><img src="assets/img/poster-land.webp" alt="" width="1600" height="900" fetchpriority="high"></picture>'
     '<video id="hv" muted loop playsinline preload="none" aria-hidden="true" tabindex="-1"></video><div class="shade"></div><div class="scan" aria-hidden="true"></div><canvas id="em" aria-hidden="true"></canvas>'
     '<div class="txt"><div class="w"><div class="in"><div><small>Dress the unconventional</small><h1>Wear the new code</h1></div><div class="r"><p>Graphic tees from Bengaluru. Pick your tee, confirm your order and send it on WhatsApp.</p><div class="cta"><a class="btn" href="#shop">Shop the drop</a><a class="btn ghost" data-wa="Hi Bro Code Fashion!" href="#" target="_blank" rel="noopener">Chat on WhatsApp</a></div></div></div></div></div></header>\n')
    b+='<section class="feat" aria-label="Highlights"><div><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3l6 4 6-4 3 5-4 2v11H7V10L3 8z"/></svg><b>Men\'s casual</b><span>Graphic tees, ready to order.</span></div><div><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l3 6 6 1-4.5 4.2L18 21l-6-3.2L6 21l1.5-6.8L3 10l6-1z"/></svg><b>Women\'s ethnic</b><span>Ask us on WhatsApp.</span></div><div><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H8l-4 4z"/></svg><b>Order on WhatsApp</b><span>Anytime. We reply 9 AM – 9 PM.</span></div></section>\n'
    b+='<div class="marq" aria-hidden="true"><div>'+''.join('<span>%s</span><i>✦</i>'%s for s in ["Order anytime on WhatsApp","Men's casual wear","Women's ethnic wear","Bengaluru","Replies 9 AM – 9 PM"]*2)+'</div></div>\n'
    b+='<main id="main">\n<section id="shop" class="sec w"><div class="shophd"><div><p class="k" data-r>The drop</p><h2 data-r>Pick your tee</h2></div><p class="lead" data-r style="--d:.1s;margin:0">Tap a tee, choose your size and add it to your bag. Send your order on WhatsApp. Nothing is charged on this website.</p></div><ul class="pgrid">'+cards+'</ul><noscript><p class="note">Ordering on this page needs JavaScript. You can also place your order directly on <a href="https://wa.me/'+WA+'">WhatsApp</a>.</p></noscript></section>\n'
    b+='<section id="reel" class="reel" data-scrub data-steps="4" aria-label="Look reel"><div class="stick"><div class="rl-list"><p class="k">Look reel</p><h2>Scroll. Drop. Repeat.</h2>'+reel_rows+'</div><div class="rl-view">'+reel_imgs+'<div class="scan" aria-hidden="true"></div><div class="rl-shop">'+reel_btn+'</div></div></div></section>\n'
    b+='<div class="rows" aria-hidden="true"><div class="trk">'+rowimgs(["thisday","unreal","lablack","mythic","silence"])+'</div><div class="trk rev">'+rowimgs(["spider","balance","labrown","eagle","scorpion"])+'</div></div>\n'
    b+=('<section id="how" class="sec w"><p class="k" data-r>How to order</p><h2 data-r>Four steps. No payment page.</h2><ol class="steps">'
     '<li data-r><b>Choose</b><p>Open a tee, pick your size and add it to your bag.</p></li><li data-r style="--d:.08s"><b>Review</b><p>Check your order summary and enter your delivery details.</p></li>'
     '<li data-r style="--d:.16s"><b>Confirm order</b><p>Tap Confirm order. WhatsApp opens with your full order already written.</p></li><li data-r style="--d:.24s"><b>Send on WhatsApp</b><p>Press send. We confirm availability, delivery and payment with you there.</p></li></ol>'
     '<p class="note" data-r>This website does not take payments. Prices, delivery charges and payment details are confirmed with you on WhatsApp before anything is charged.</p></section>\n')
    b+=('<section id="about" class="sec w about"><div data-r>'+LOGO+'<p class="k">The code</p><h2>Look sharp. Feel easy. Stand together.</h2></div><div class="abt" data-r style="--d:.12s"><p>Bro Code Fashion is a clothing label from Bengaluru. We make graphic tees and casual wear for men, and we are building towards traditional ethnic wear for women, an online store and more locations.</p>'
     '<ul class="code"><li><b>Casual, done right</b><span>Everyday pieces for men that work from morning to night.</span></li><li><b>Order your way</b><span>Choose online, confirm on WhatsApp, and talk to a real person about size, delivery and payment.</span></li><li><b>Built to grow</b><span>Starting from HSR Layout, Bengaluru, with an online store and more locations planned.</span></li></ul></div></section>\n')
    b+=('<section id="collections" class="sec w"><p class="k" data-r>Collections</p><h2 data-r>Two wardrobes. One label.</h2><div class="colls"><article class="cpan" data-r><img src="assets/img/a-scorpion-960.webp" alt="" loading="lazy" width="960" height="760"><div class="t"><small>For him</small><h3>Men\'s casual wear</h3><p>Graphic tees and relaxed everyday pieces. Tap through to the drop.</p><a class="btn sm" href="#shop">Shop men\'s tees</a></div></article>'
     '<article class="cpan w" data-r style="--d:.12s"><div class="garms" aria-hidden="true">'+garm("kurta")+garm("anar")+'</div><div class="t"><small>For her</small><h3>Women\'s ethnic wear</h3><p>Traditional silhouettes for festivals and every day. Tell us what you are looking for and we will get back to you on WhatsApp.</p><a class="btn sm wa" data-wa="Hi Bro Code Fashion, I would like to know about women\'s ethnic wear." href="#" target="_blank" rel="noopener">Ask on WhatsApp</a></div></article></div></section>\n')
    b+=('<section id="roadmap" class="sec w"><p class="k" data-r>Roadmap</p><h2 data-r>From one street to every city.</h2><ol class="road" data-prog><li data-r><small>Now</small><b>Order on WhatsApp</b><p>Pick your tees here, confirm on WhatsApp.</p></li><li data-r style="--d:.08s"><small>Soon</small><b>Online store</b><p>Full checkout and payments on this site.</p></li><li data-r style="--d:.16s"><small>Planned</small><b>More locations</b><p>New Bro Code stores beyond Bengaluru.</p></li><li data-r style="--d:.24s"><small>Planned</small><b>Delivery across India</b><p>One supply chain, every pin code.</p></li></ol></section>\n')
    faq=[("How do I place an order?","Open a tee, choose your size and add it to your bag. In checkout, enter your delivery details and tap Confirm order. WhatsApp opens with your full order, and you press send."),
         ("Do I pay on the website?","No. This website does not take payments. We confirm your order, the total and the payment details with you on WhatsApp."),
         ("What are your hours?","You can order any time. We reply on WhatsApp between 9 AM and 9 PM."),
         ("How much is delivery and when will it arrive?","We confirm delivery availability, charges and timing for your pincode on WhatsApp before you pay."),
         ("What if I am not sure about my size?","Message us on WhatsApp and we will help you choose before you order."),
         ("Can I return or exchange an item?","Return and exchange terms are shared on WhatsApp before you pay. See our Shipping &amp; returns page for details."),
         ("Is there a store I can visit?","We are based in HSR Layout, Bengaluru and are building towards a store. For now, orders are placed online and confirmed on WhatsApp.")]
    b+='<section id="faq" class="sec w faq"><div data-r><p class="k">Questions</p><h2>Good to know.</h2></div><div class="qa" data-r style="--d:.1s">'+''.join('<details%s><summary>%s</summary><p>%s</p></details>'%(' open' if i==0 else '',q,a) for i,(q,a) in enumerate(faq))+'</div></section>\n'
    b+=('<section id="contact" class="sec w contact"><div data-r><p class="k">Contact</p><h2>Say hello on WhatsApp.</h2><p class="lead">Questions about sizes, availability or an order? Message or call us.</p><div class="cta"><a class="btn wa" data-wa="Hi Bro Code Fashion!" href="#" target="_blank" rel="noopener">'+WA_ICON+'Chat on WhatsApp</a><a class="btn ghost" href="tel:'+PH_TEL+'">Call '+PH_DISP+'</a></div></div>'
     '<ul class="clist" data-r style="--d:.1s"><li><span>Call</span><a href="tel:'+PH_TEL+'">'+PH_DISP+'</a></li><li><span>WhatsApp</span><a href="https://wa.me/'+WA+'" target="_blank" rel="noopener">'+PH_DISP+'</a></li>'
     '<li data-contact="instagram" hidden><span>Instagram</span><a href="#"></a></li><li data-contact="email" hidden><span>Email</span><a href="#"></a></li>'
     '<li><span>Orders</span><b>Anytime</b></li><li><span>Replies</span><b>9 AM – 9 PM<small>We answer on WhatsApp and phone</small></b></li><li><span>Based in</span><b>HSR Layout, Bengaluru</b></li></ul></section>\n</main>\n')
    b+=rel(footer())
    b+='<aside aria-label="WhatsApp chat"><a class="fab" data-wa="Hi Bro Code Fashion!" href="#" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">'+WA_ICON+'</a></aside>\n'
    b+='<nav class="dock" aria-label="Quick actions"><a class="a" href="#shop">Shop</a><button class="b" type="button" data-bag>Bag <b data-cart-count hidden>0</b></button><a class="c" data-wa="Hi Bro Code Fashion!" href="#" target="_blank" rel="noopener">WhatsApp</a></nav>\n<aside aria-label="Notifications"><div class="toast" id="toast" role="status" aria-live="polite"></div></aside>\n'
    # dialogs
    b+=('<dialog id="pm" aria-labelledby="pm-name"><div class="pmg"><div class="pmimg"><img id="pm-img" src="" alt="" width="800" height="1000"><div class="thumbs" id="pm-thumbs"></div></div>'
     '<div class="pmi"><button class="x" type="button" data-close aria-label="Close">×</button><p class="k" style="margin:0">Bro Code Fashion</p><h2 id="pm-name"></h2><p class="sub" id="pm-sub"></p><p class="pp" id="pm-price"></p><p class="d" id="pm-desc"></p>'
     '<fieldset class="sizes"><legend>Size</legend><div class="sizes" id="pm-sizes" style="display:contents"></div></fieldset><p class="err" id="pm-err" role="alert"></p>'
     '<div class="qrow"><div class="qty" role="group" aria-label="Quantity"><button type="button" data-pq="-1" aria-label="Decrease">−</button><output id="pm-q">1</output><button type="button" data-pq="1" aria-label="Increase">+</button></div></div>'
     '<div class="row"><button class="btn" id="pm-add" type="button">Add to bag</button><a class="btn ghost" id="pm-ask" href="#" target="_blank" rel="noopener">Ask on WhatsApp</a></div><p class="tiny">Not sure about your size? Ask us on WhatsApp before you order.</p></div></div></dialog>\n')
    b+=('<dialog id="bag" aria-labelledby="bag-h"><div class="dh"><h2 id="bag-h">Your bag</h2><button class="x" type="button" data-close aria-label="Close bag">×</button></div><div class="bagbody"><ul class="lines" id="bag-lines"></ul></div>'
     '<div class="bagfoot"><div class="tot"><span>Total</span><span id="bag-total"></span></div><p class="tiny">Delivery charges and payment are confirmed on WhatsApp.</p><button class="btn" id="bag-go" type="button">Checkout</button></div></dialog>\n')
    b+=('<dialog id="co" aria-labelledby="co-h"><div class="dh"><h2 id="co-h">Checkout</h2><button class="x" type="button" data-close aria-label="Close checkout">×</button></div>'
     '<div id="co-form-view"><div class="cogrid"><form id="co-form" novalidate><h3 style="margin-bottom:16px">Delivery details</h3>'
     '<div class="fld"><label for="f-name">Full name</label><input id="f-name" name="name" autocomplete="name" required aria-describedby="e-name"><span class="err" id="e-name" role="alert"></span></div>'
     '<div class="fld"><label for="f-phone">Mobile number</label><input id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="10-digit mobile number" required aria-describedby="e-phone"><span class="err" id="e-phone" role="alert"></span></div>'
     '<div class="fld"><label for="f-address">Delivery address</label><textarea id="f-address" name="address" autocomplete="street-address" required aria-describedby="e-address"></textarea><span class="err" id="e-address" role="alert"></span></div>'
     '<div class="f2"><div class="fld"><label for="f-city">City</label><input id="f-city" name="city" autocomplete="address-level2" required aria-describedby="e-city"><span class="err" id="e-city" role="alert"></span></div><div class="fld"><label for="f-pin">Pincode</label><input id="f-pin" name="pincode" inputmode="numeric" maxlength="6" autocomplete="postal-code" required aria-describedby="e-pincode"><span class="err" id="e-pincode" role="alert"></span></div></div>'
     '<div class="fld"><label for="f-notes">Notes (optional)</label><textarea id="f-notes" name="notes" placeholder="Anything we should know?"></textarea></div>'
     '<button class="btn wa confirm" type="submit">'+WA_ICON+'Confirm order</button><p class="tiny" style="margin-top:12px">Tapping Confirm order opens WhatsApp with your full order summary and details written out. Press send in WhatsApp to place your order. No payment is taken on this website.</p></form>'
     '<aside class="sum" aria-label="Order summary"><h3>Order summary</h3><ul class="lines" id="co-lines"></ul><div class="tot" style="margin-top:14px"><span>Total</span><span id="co-total"></span></div><p class="tiny" style="margin-top:10px">Delivery charges and payment are confirmed with you on WhatsApp.</p></aside></div></div>'
     '<div id="co-done" class="done" hidden><div class="ok" aria-hidden="true">✓</div><h2 style="margin:0">Your order is ready to send</h2><p class="lead" style="margin:0">WhatsApp should have opened with your order written out. Press <b>send</b> there to place it. We will confirm availability, delivery and payment with you, 9 AM to 9 PM.</p>'
     '<p class="k" style="margin:0">Order ID: <span id="done-id"></span></p><pre id="done-msg"></pre><div class="row"><a class="btn wa" id="done-open" href="#" target="_blank" rel="noopener">'+WA_ICON+'Open WhatsApp</a><button class="btn ghost" type="button" id="done-copy">Copy order message</button><button class="btn ghost" type="button" id="done-more">Keep shopping</button></div><p class="tiny">WhatsApp did not open? Tap Open WhatsApp, or copy the message and send it to '+PH_DISP+'.</p></div></dialog>\n')
    b+='<script src="assets/js/config.js"></script>\n<script src="assets/js/app.js" defer></script>\n</body>\n</html>\n'
    return h+b
def policy(slug,title,desc,body):
    h=head(title+" | Bro Code Fashion",desc,slug,"",False)
    h=h.replace('<meta name="viewport"','<meta name="robots" content="index,follow">\n<meta name="viewport"',1)
    return (h+'<body>\n'+DEFS+'\n<div class="w"><header class="phead"><a href="index.html" aria-label="Bro Code Fashion home">'+MARK+'</a><a href="index.html">← Back to the shop</a></header>\n<main class="page" id="main"><h1>'+title+'</h1><p class="upd">Last updated 4 November 2026</p>'+body+'</main></div>\n'+rel(footer())+'\n</body>\n</html>\n')
PRIV=('<p>This page explains what Bro Code Fashion does with the details you enter on this website.</p><h2>What we collect</h2><ul><li>When you check out, you type your name, mobile number, delivery address, city, pincode and optional notes.</li><li>Your bag and these details are kept in your own browser so you do not have to retype them. They are not stored on any server by this website.</li></ul>'
 '<h2>How we use it</h2><p>Your details are used to write the WhatsApp order message that you send to us. We use them to confirm your order, arrange payment and delivery, and reply to your questions.</p><h2>WhatsApp</h2><p>When you send your order, WhatsApp (Meta) handles the message under its own privacy policy. Messages go to our business number '+PH_DISP+'.</p>'
 '<h2>Cookies and tracking</h2><p>This website does not set tracking cookies. If we switch on analytics later (for example Google Analytics or Meta Pixel), we will update this page.</p><h2>Your choices</h2><ul><li>Clear your browser data to remove the bag and saved details from your device.</li><li>Message us on WhatsApp if you want us to delete the details in an order conversation.</li></ul><h2>Contact</h2><p>Bro Code Fashion, Bengaluru. Call or WhatsApp '+PH_DISP+'.</p>')
TERMS=('<p>By using this website and placing an order with Bro Code Fashion you agree to these terms.</p><h2>Orders</h2><p>Choosing items and tapping Confirm order prepares a WhatsApp message. An order is placed when you send that message, and it is confirmed only when we reply and confirm availability, the total and payment details with you on WhatsApp.</p>'
 '<h2>Prices and availability</h2><p>Prices and availability are confirmed on WhatsApp. We may decline or adjust an order if an item is unavailable or a price shown was wrong.</p><h2>Payment</h2><p>This website does not take payments. Payment details and methods are shared with you on WhatsApp.</p>'
 '<h2>Delivery</h2><p>Delivery availability, charges and timing depend on your pincode and are confirmed on WhatsApp. See Shipping &amp; returns.</p><h2>Product images</h2><p>Product photos are for illustration. Colours and prints may look slightly different on different screens.</p>'
 '<h2>Our content</h2><p>The Bro Code Fashion name, logo, designs and photos belong to Bro Code Fashion. Please do not copy them without permission.</p><h2>Governing law</h2><p>These terms are governed by the laws of India.</p><h2>Contact</h2><p>Call or WhatsApp '+PH_DISP+'.</p>')
SHIP=('<h2>Delivery</h2><p>We confirm whether we can deliver to your pincode, the delivery charge and the expected time on WhatsApp before you pay. Delivery details for your order are repeated in your WhatsApp conversation.</p><h2>Order hours</h2><p>You can place an order at any time. We reply on WhatsApp between 9 AM and 9 PM.</p>'
 '<h2>Returns and exchanges</h2><p>Return and exchange terms are shared on WhatsApp before you pay, so you know exactly what applies to your order.</p><h2>Damaged or wrong items</h2><p>If your item arrives damaged or is not what you ordered, message us on WhatsApp as soon as possible with photos and your order ID, and we will help.</p><h2>Contact</h2><p>Call or WhatsApp '+PH_DISP+'.</p>')
def write(p,s):
    os.makedirs(os.path.dirname(p),exist_ok=True);open(p,"w").write(s)
def build(out,preview):
    write(out+"/index.html",index(preview))
    for slug,t,d,b in(("privacy.html","Privacy policy","How Bro Code Fashion handles the details you enter at checkout.",PRIV),("terms.html","Terms of use","Terms for ordering from Bro Code Fashion.",TERMS),("shipping-returns.html","Shipping and returns","Delivery, returns and exchanges at Bro Code Fashion.",SHIP)):
        write(out+"/"+slug,policy(slug,t,d,b))
    write(out+"/404.html",head("Page not found | Bro Code Fashion","This page could not be found.","404.html").replace('<meta name="viewport"','<meta name="robots" content="noindex">\n<meta name="viewport"',1)+'<body>\n'+DEFS+'<div class="w"><header class="phead"><a href="index.html">'+MARK+'</a></header><main class="page"><h1>Page not found</h1><p>That page does not exist. <a href="index.html">Go back to the shop</a>.</p></main></div></body></html>\n')
    shutil.copytree(ROOT+"/assets",out+"/assets",dirs_exist_ok=True)
    for f in os.listdir(ROOT+"/static"): shutil.copy(ROOT+"/static/"+f,out+"/"+f)
    os.makedirs(out+"/assets/css",exist_ok=True);os.makedirs(out+"/assets/js",exist_ok=True)
    shutil.copy(SRC+"/app.css",out+"/assets/css/app.css");shutil.copy(SRC+"/app.js",out+"/assets/js/app.js");write(out+"/assets/js/config.js",cfgjs())
    write(out+"/site.webmanifest",json.dumps({"name":"Bro Code Fashion","short_name":"Bro Code","start_url":"/","display":"standalone","background_color":"#0a0605","theme_color":"#0a0605","icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icon-512.png","sizes":"512x512","type":"image/png"}]},indent=1))
    write(out+"/robots.txt","User-agent: *\nAllow: /\n"+("Sitemap: %s/sitemap.xml\n"%SITE if SITE else ""))
    if SITE: write(out+"/sitemap.xml",'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>%s/%s</loc></url>\n'%(SITE,p) for p in ("","privacy.html","terms.html","shipping-returns.html"))+'</urlset>\n')
    write(out+"/_headers","/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n/assets/*\n  Cache-Control: public, max-age=604800\n/index.html\n  Cache-Control: no-cache\n")
def carry_over():
    """Keep what the owner edited in the last build's config.js: prices, sizes, Instagram, email and analytics IDs."""
    p=OUT+"/assets/js/config.js"
    if FRESH or not os.path.exists(p): return
    try:
        t=open(p,encoding="utf8").read();j=json.loads(t[t.index("window.BCF=")+11:].strip().rstrip(";"))
    except Exception as e:
        print("note: could not read the earlier config.js, using defaults:",e);return
    for k in ("instagram","email","ga4","metaPixel","sizes"):
        if k in j: CONFIG[k]=j[k]
    for pid,v in (j.get("prices") or {}).items():
        if pid in CONFIG["prices"]: CONFIG["prices"][pid]=v
    print("kept the settings from the earlier website/assets/js/config.js (use --fresh to reset them)")
carry_over()
if os.path.exists(OUT): shutil.rmtree(OUT)
build(OUT,False)
print("built",SITE or "(no domain yet)","->",OUT)
