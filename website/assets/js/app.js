(function(){'use strict';
var C=window.BCF,D=document,H=D.documentElement;
function $(s,r){return (r||D).querySelector(s)}function $$(s,r){return [].slice.call((r||D).querySelectorAll(s))}
var RM=matchMedia('(prefers-reduced-motion: reduce)').matches;if(RM)H.classList.add('rm');
var store={get:function(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}},set:function(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
var P={};C.products.forEach(function(p){P[p.id]=p});
var cart=(store.get('bcf_cart_v1')||[]).filter(function(l){return P[l.id]&&l.qty>0});
function price(id){var v=C.prices&&C.prices[id];return typeof v==='number'?v:null}
function money(n){return C.currency+Number(n).toLocaleString('en-IN')}
function sizesOf(p){return p.sizes||C.sizes}
function img(id,v,w){return 'assets/img/p-'+id+'-'+v+'-'+w+'.webp'}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function wa(text){return 'https://wa.me/'+C.whatsapp+'?text='+encodeURIComponent(text)}
function track(ev,data){try{if(window.gtag)gtag('event',ev,data||{});if(window.fbq)fbq('trackCustom',ev,data||{})}catch(e){}}
/* ---------- analytics (only when IDs are filled in config.js) */
if(C.ga4){var s=D.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+C.ga4;D.head.appendChild(s);window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag('js',new Date());gtag('config',C.ga4)}
if(C.metaPixel){!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src='https://connect.facebook.net/en_US/fbevents.js';s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,D,'script');fbq('init',C.metaPixel);fbq('track','PageView')}
/* ---------- cart */
function save(){store.set('bcf_cart_v1',cart)}
function count(){return cart.reduce(function(a,l){return a+l.qty},0)}
function totals(){var amt=0,unknown=false;cart.forEach(function(l){var p=price(l.id);if(p===null)unknown=true;else amt+=p*l.qty});return{amt:amt,unknown:unknown}}
function addLine(id,size,qty){var f=cart.filter(function(l){return l.id===id&&l.size===size})[0];if(f)f.qty=Math.min(20,f.qty+qty);else cart.push({id:id,size:size,qty:qty});save();render();track('add_to_cart',{item:id,size:size})}
function setQty(i,q){if(q<=0)cart.splice(i,1);else cart[i].qty=Math.min(20,q);save();render()}
function totalLine(){var t=totals();if(!cart.length)return '';if(t.unknown&&t.amt===0)return 'Price confirmed on WhatsApp';return money(t.amt)+(t.unknown?' + items priced on WhatsApp':'')}
function lineHTML(l,i,editable){var p=P[l.id],pr=price(l.id);return '<li class="ln"><img src="'+img(l.id,p.views[0].k,480)+'" alt="" width="64" height="80"><div class="li"><b>'+esc(p.name)+'</b><span>Size '+esc(l.size)+'</span>'+(editable?'<div class="qty" role="group" aria-label="Quantity for '+esc(p.name)+' size '+esc(l.size)+'"><button type="button" data-q="-1" data-i="'+i+'" aria-label="Decrease">−</button><output>'+l.qty+'</output><button type="button" data-q="1" data-i="'+i+'" aria-label="Increase">+</button></div>':'<span>Qty '+l.qty+'</span>')+'</div><div class="lp">'+(pr===null?'<small>Price on WhatsApp</small>':money(pr*l.qty))+(editable?'<button type="button" class="rmv" data-rm="'+i+'" aria-label="Remove '+esc(p.name)+'">Remove</button>':'')+'</div></li>'}
function render(){
  var n=count();$$('[data-cart-count]').forEach(function(e){e.textContent=n;e.hidden=!n});
  var bl=$('#bag-lines'),ck=$('#co-lines');
  if(bl){bl.innerHTML=cart.length?cart.map(function(l,i){return lineHTML(l,i,true)}).join(''):'<li class="empty">Your bag is empty. Pick a tee from the drop.</li>';$('#bag-total').textContent=totalLine();$('#bag-go').disabled=!cart.length}
  if(ck){ck.innerHTML=cart.map(function(l,i){return lineHTML(l,i,true)}).join('');$('#co-total').textContent=totalLine()}
}
/* ---------- dialogs */
var lastFocus=null;
function open(d){lastFocus=D.activeElement;if(!d.open){d.showModal?d.showModal():d.setAttribute('open','')}H.classList.add('lock')}
function close(d){if(d.open){d.close?d.close():d.removeAttribute('open')}if(!$$('dialog[open]').length){H.classList.remove('lock');if(lastFocus&&lastFocus.focus)try{lastFocus.focus()}catch(e){}}}
$$('dialog').forEach(function(d){d.addEventListener('click',function(e){if(e.target===d)close(d)});d.addEventListener('close',function(){if(!$$('dialog[open]').length)H.classList.remove('lock')});$$('[data-close]',d).forEach(function(b){b.addEventListener('click',function(){close(d)})})});
/* ---------- product modal */
var pm=$('#pm'),cur=null,curSize=null,curView=0,curQty=1;
function openProduct(id){cur=P[id];if(!cur)return;curSize=null;curView=0;curQty=1;paintProduct();open(pm);track('view_item',{item:id})}
function paintProduct(){var p=cur,pr=price(p.id);
  $('#pm-img').src=img(p.id,p.views[curView].k,800);$('#pm-img').alt=p.name+' — '+p.views[curView].label;
  $('#pm-thumbs').innerHTML=p.views.map(function(v,i){return '<button type="button" class="'+(i===curView?'on':'')+'" data-v="'+i+'" aria-label="Show '+esc(v.label)+'"><img src="'+img(p.id,v.k,480)+'" alt="" width="64" height="80"></button>'}).join('');
  $('#pm-name').textContent=p.name;$('#pm-sub').textContent=p.colour;$('#pm-desc').textContent=p.desc;
  $('#pm-price').innerHTML=pr===null?'Price on WhatsApp':money(pr);
  $('#pm-sizes').innerHTML=sizesOf(p).map(function(s){return '<label><input type="radio" name="size" value="'+esc(s)+'"'+(s===curSize?' checked':'')+'><span>'+esc(s)+'</span></label>'}).join('');
  $('#pm-q').textContent=curQty;$('#pm-err').textContent='';
  $('#pm-ask').href=wa('Hi Bro Code Fashion, I am interested in the '+p.name+' ('+p.code+'). Is it available?')}
pm.addEventListener('click',function(e){var t=e.target.closest('[data-v]');if(t){curView=+t.dataset.v;paintProduct();return}
  if(e.target.closest('[data-pq]')){curQty=Math.max(1,Math.min(20,curQty+(+e.target.closest('[data-pq]').dataset.pq)));$('#pm-q').textContent=curQty}});
pm.addEventListener('change',function(e){if(e.target.name==='size'){curSize=e.target.value;$('#pm-err').textContent=''}});
$('#pm-add').addEventListener('click',function(){if(!curSize){$('#pm-err').textContent='Please choose a size.';return}addLine(cur.id,curSize,curQty);close(pm);toast(cur.name+' added to bag');openBag()});
$$('[data-open]').forEach(function(b){b.addEventListener('click',function(e){e.preventDefault();openProduct(b.dataset.open)})});
/* ---------- bag */
var bag=$('#bag');function openBag(){render();open(bag);track('view_cart')}
$$('[data-bag]').forEach(function(b){b.addEventListener('click',openBag)});
bag.addEventListener('click',function(e){var q=e.target.closest('[data-q]'),r=e.target.closest('[data-rm]');if(q){var i=+q.dataset.i;setQty(i,cart[i].qty+(+q.dataset.q))}if(r)setQty(+r.dataset.rm,0)});
$('#bag-go').addEventListener('click',function(){close(bag);openCheckout()});
/* ---------- checkout */
var co=$('#co'),form=$('#co-form');
function openCheckout(){if(!cart.length)return;$('#co-form-view').hidden=false;$('#co-done').hidden=true;render();var s=store.get('bcf_cust');if(s)['name','phone','address','city','pincode'].forEach(function(k){if(s[k]&&!form.elements[k].value)form.elements[k].value=s[k]});open(co);track('begin_checkout',{value:totals().amt})}
co.addEventListener('click',function(e){var q=e.target.closest('[data-q]'),r=e.target.closest('[data-rm]');if(q){var i=+q.dataset.i;setQty(i,cart[i].qty+(+q.dataset.q))}if(r)setQty(+r.dataset.rm,0);if(!cart.length&&!$('#co-form-view').hidden){close(co)}});
function normPhone(v){var d=String(v).replace(/\D/g,'');if(d.length===12&&d.indexOf('91')===0)d=d.slice(2);if(d.length===11&&d[0]==='0')d=d.slice(1);return d}
var rules={name:function(v){return v.trim().length>=2||'Enter your full name'},phone:function(v){return /^[6-9]\d{9}$/.test(normPhone(v))||'Enter a valid 10-digit mobile number'},address:function(v){return v.trim().length>=8||'Enter your full delivery address'},city:function(v){return v.trim().length>=2||'Enter your city'},pincode:function(v){return /^\d{6}$/.test(v.trim())||'Enter a 6-digit pincode'}};
function validate(){var ok=true,first=null;Object.keys(rules).forEach(function(k){var el=form.elements[k],r=rules[k](el.value),er=$('#e-'+k);if(r===true){er.textContent='';el.removeAttribute('aria-invalid')}else{er.textContent=r;el.setAttribute('aria-invalid','true');ok=false;if(!first)first=el}});if(first)first.focus();return ok}
form.addEventListener('input',function(e){var n=e.target.name,er=n&&$('#e-'+n);if(er&&er.textContent){er.textContent='';e.target.removeAttribute('aria-invalid')}});
function orderId(){var d=new Date(),p=function(n){return ('0'+n).slice(-2)};return 'BCF-'+p(d.getDate())+p(d.getMonth()+1)+'-'+Math.random().toString(36).slice(2,6).toUpperCase()}
function buildMessage(id,c){var t=totals(),L=[];
  L.push('*New order — Bro Code Fashion*','Order ID: '+id,'Placed: '+new Date().toLocaleString('en-IN',{dateStyle:'medium',timeStyle:'short',timeZone:'Asia/Kolkata'}),'','*Items*');
  cart.forEach(function(l,i){var p=P[l.id],pr=price(l.id);L.push((i+1)+') '+p.name+' ['+p.code+'] — Size '+l.size+' × '+l.qty+' — '+(pr===null?'price to be confirmed':money(pr*l.qty)))});
  L.push('','*Total:* '+(t.unknown?(t.amt?money(t.amt)+' + items priced on WhatsApp':'to be confirmed on WhatsApp'):money(t.amt)),'Delivery charges and payment: to be confirmed on WhatsApp','','*Customer details*','Name: '+c.name,'Phone: +91 '+c.phone,'Address: '+c.address,'City: '+c.city,'Pincode: '+c.pincode);
  if(c.notes)L.push('Notes: '+c.notes);
  L.push('','Please confirm availability, delivery charges and payment details. Thank you!');return L.join('\n')}
form.addEventListener('submit',function(e){e.preventDefault();if(!cart.length||!validate())return;
  var c={name:form.elements.name.value.trim(),phone:normPhone(form.elements.phone.value),address:form.elements.address.value.trim(),city:form.elements.city.value.trim(),pincode:form.elements.pincode.value.trim(),notes:form.elements.notes.value.trim()};
  store.set('bcf_cust',c);var id=orderId(),msg=buildMessage(id,c),url=wa(msg);
  store.set('bcf_last',{id:id,msg:msg,at:Date.now()});track('generate_lead',{order_id:id,value:totals().amt});
  $('#done-id').textContent=id;$('#done-msg').textContent=msg;$('#done-open').href=url;$('#co-form-view').hidden=true;$('#co-done').hidden=false;
  cart.length=0;save();render();co.scrollTop=0;var w=null;try{w=window.open(url,'_blank','noopener')}catch(x){}if(!w){/* popup blocked: the visible button below opens WhatsApp */}});
$('#done-copy').addEventListener('click',function(){var t=$('#done-msg').textContent,b=this;(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){b.textContent='Copied'},function(){var r=D.createRange();r.selectNodeContents($('#done-msg'));var s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent='Select and copy the text'});setTimeout(function(){b.textContent='Copy order message'},2500)});
$('#done-more').addEventListener('click',function(){close(co);D.getElementById('shop').scrollIntoView({behavior:RM?'auto':'smooth'})});
/* ---------- toast */
var tt;function toast(m){var t=$('#toast');t.textContent=m;t.classList.add('on');clearTimeout(tt);tt=setTimeout(function(){t.classList.remove('on')},2400)}
/* ---------- general enquiry links */
$$('[data-wa]').forEach(function(a){a.href=wa(a.dataset.wa||'Hi Bro Code Fashion!')});
/* ---------- reply status (IST) */
function istHour(){return +new Intl.DateTimeFormat('en-GB',{hour:'numeric',hour12:false,timeZone:'Asia/Kolkata'}).format(new Date())%24}
(function(){var h=istHour(),on=h>=9&&h<21;$$('[data-status]').forEach(function(e){e.textContent=on?'Replying now on WhatsApp':'Replies resume 9 AM';e.classList.toggle('on',on)})})();
/* ---------- hero video (after first paint, skipped for reduced motion / data saver) */
(function(){var v=$('#hv'),c=navigator.connection;if(!v||RM||(c&&c.saveData))return;
  function go(){var m=matchMedia('(max-width:760px)').matches;v.src=m?'assets/video/hero-720.mp4':'assets/video/hero-1080.mp4';v.addEventListener('playing',function(){v.classList.add('on')},{once:true});var p=v.play();if(p&&p.catch)p.catch(function(){})}
  if('requestIdleCallback' in window)requestIdleCallback(go,{timeout:1800});else setTimeout(go,900);
  D.addEventListener('visibilitychange',function(){if(D.hidden)v.pause();else if(v.src)v.play().catch(function(){})})})();
/* ---------- reveal / scrub / float */
var rv=$$('[data-r]');if(RM||!('IntersectionObserver' in window)){rv.forEach(function(e){e.classList.add('in')})}else{var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}})},{threshold:.1,rootMargin:'0px 0px -6% 0px'});rv.forEach(function(e){io.observe(e)})}
var sc=$$('[data-scrub]'),pg=$$('[data-prog]'),px=$$('[data-speed]'),tk=false;
function tick(){var vh=innerHeight,y=scrollY;
  sc.forEach(function(e){var r=e.getBoundingClientRect(),p=Math.min(1,Math.max(0,-r.top/Math.max(1,r.height-vh)));e.style.setProperty('--p',p.toFixed(4));var n=+e.dataset.steps;if(n){var i=Math.min(n-1,Math.floor(p*n));$$('[data-step]',e).forEach(function(s){var k=+s.dataset.step;if(s.dataset.mode==='cur')s.classList.toggle('cur',k===i);else s.classList.toggle('on',k<=i)})}});
  pg.forEach(function(e){var r=e.getBoundingClientRect();e.style.setProperty('--p',Math.min(1,Math.max(0,(vh*.72-r.top)/r.height)).toFixed(3))});
  if(!RM)px.forEach(function(e){if(y<vh*1.4)e.style.transform='translate3d(0,'+(y*parseFloat(e.dataset.speed)).toFixed(1)+'px,0)'});
  tk=false}
function rq(){if(!tk){tk=true;requestAnimationFrame(tick)}}
addEventListener('scroll',rq,{passive:true});addEventListener('resize',rq);tick();
/* ---------- embers */
(function(){var cv=$('#em');if(!cv)return;var ctx=cv.getContext('2d'),W,Hh,Dp,Pt=[];
  function rs(){Dp=Math.min(devicePixelRatio||1,2);var r=cv.getBoundingClientRect();W=cv.width=Math.round(r.width*Dp);Hh=cv.height=Math.round(r.height*Dp);Pt=[];var n=innerWidth<760?28:60;for(var i=0;i<n;i++)Pt.push({x:Math.random(),y:Math.random(),s:Math.random()*2+.6,v:Math.random()*.00006+.00002})}
  rs();addEventListener('resize',rs);var vis=true;if('IntersectionObserver' in window)new IntersectionObserver(function(e){vis=e[0].isIntersecting}).observe(cv);
  function dr(t){ctx.clearRect(0,0,W,Hh);Pt.forEach(function(p){var y=((p.y-t*p.v)%1+1)%1,x=p.x+Math.sin(t*.0004+p.s*9)*.015;ctx.globalAlpha=.2+.55*(1-y);ctx.fillStyle='#ffc46b';ctx.beginPath();ctx.arc(x*W,y*Hh,p.s*Dp,0,7);ctx.fill()})}
  function lp(t){if(vis)dr(t);requestAnimationFrame(lp)}if(RM)dr(4000);else requestAnimationFrame(lp)})();
/* ---------- prices + optional contact rows from config.js */
$$('[data-price]').forEach(function(e){var p=price(e.dataset.price);e.textContent=p===null?'Price on WhatsApp':money(p)});
$$('[data-contact]').forEach(function(li){var k=li.dataset.contact,v=C[k];if(!v)return;var a=$('a',li);a.textContent=k==='instagram'?'@'+v.replace(/^@/,''):v;a.href=k==='instagram'?'https://instagram.com/'+v.replace(/^@/,''):'mailto:'+v;if(k==='instagram'){a.target='_blank';a.rel='noopener'}li.hidden=false});
render();
})();
