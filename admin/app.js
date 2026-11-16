(function(){
'use strict';
var SUPABASE_URL='https://sfezhayjhmvidtjjwfba.supabase.co';
var SUPABASE_PUBLISHABLE_KEY='sb_publishable_uR4g6zZLbD1b7VqHIw-hMw_THVYuz1P';
var client=window.supabase.createClient(SUPABASE_URL,SUPABASE_PUBLISHABLE_KEY);
var $=function(s){return document.querySelector(s)};
var loginView=$('#login-view'),appView=$('#app-view'),notice=$('#notice'),profile=null;
function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function money(v){return v==null?'—':'₹'+Number(v).toLocaleString('en-IN')}
function date(v){return v?new Date(v).toLocaleString('en-IN',{dateStyle:'medium',timeStyle:'short'}):'—'}
function status(v){return '<span class="status '+esc(v)+'">'+esc(String(v||'—').replaceAll('_',' '))+'</span>'}
function message(t){notice.textContent=t;notice.hidden=false}
function clearMessage(){notice.hidden=true;notice.textContent=''}
function showLogin(){loginView.hidden=false;appView.hidden=true}
function showApp(){loginView.hidden=true;appView.hidden=false}
async function verifyAdmin(user){
 var r=await client.from('admin_users').select('user_id,full_name,role,is_active').eq('user_id',user.id).maybeSingle();
 if(r.error)throw r.error;
 if(!r.data||!r.data.is_active)throw new Error('This account is not an active Bro Code Fashion admin. Contact the owner.');
 profile=r.data;
 $('#admin-name').textContent=profile.full_name;
 $('#admin-role').textContent=profile.role;
 $('#avatar').textContent=(profile.full_name||'B').trim().charAt(0).toUpperCase();
}
async function enter(user){
 try{await verifyAdmin(user);showApp();clearMessage();await loadAll()}
 catch(e){await client.auth.signOut();showLogin();$('#login-error').textContent=e.message||'Admin access could not be verified.'}
}
$('#login-form').addEventListener('submit',async function(e){
 e.preventDefault();var f=e.currentTarget,btn=f.querySelector('button'),err=$('#login-error');
 btn.disabled=true;btn.textContent='Signing in…';err.textContent='';
 var r=await client.auth.signInWithPassword({email:f.elements.email.value.trim(),password:f.elements.password.value});
 btn.disabled=false;btn.innerHTML='Sign in <span>→</span>';
 if(r.error){err.textContent=r.error.message;return}
 await enter(r.data.user);
});
$('#sign-out').addEventListener('click',async function(){await client.auth.signOut();profile=null;showLogin()});
client.auth.onAuthStateChange(function(event,session){if(event==='SIGNED_OUT'){showLogin()}else if(event==='SIGNED_IN'&&session&&session.user){setTimeout(function(){if(!profile)enter(session.user)},0)}});
var pages=['overview','products','inventory','orders'];
function navigate(page){
 if(pages.indexOf(page)<0)return;
 pages.forEach(function(p){$('#page-'+p).hidden=p!==page});
 document.querySelectorAll('[data-page]').forEach(function(b){b.classList.toggle('active',b.dataset.page===page)});
 $('#page-title').textContent=page.charAt(0).toUpperCase()+page.slice(1);
}
document.querySelectorAll('[data-page]').forEach(function(b){b.addEventListener('click',function(){navigate(b.dataset.page)})});
document.querySelectorAll('[data-go]').forEach(function(b){b.addEventListener('click',function(){navigate(b.dataset.go)})});
$('#refresh').addEventListener('click',loadAll);
async function loadAll(){
 clearMessage();
 try{
  var results=await Promise.all([
   client.from('products').select('id,name,product_code,price_inr,status,is_featured,updated_at').order('created_at',{ascending:false}),
   client.from('product_variants').select('id,product_id,sku,size,color,is_active,price_override_inr'),
   client.from('inventory').select('variant_id,quantity,updated_at'),
   client.from('inventory_reservations').select('variant_id,quantity,status,expires_at').eq('status','active').gt('expires_at',new Date().toISOString()),
   client.from('orders').select('id,order_number,customer_name,phone,order_status,total_amount_inr,created_at,reservation_expires_at').order('created_at',{ascending:false}).limit(100)
  ]);
  results.forEach(function(r){if(r.error)throw r.error});
  var products=results[0].data||[],variants=results[1].data||[],stock=results[2].data||[],reservations=results[3].data||[],orders=results[4].data||[];
  var productById={};products.forEach(function(p){productById[p.id]=p});
  var stockByVariant={},reservedByVariant={};
  stock.forEach(function(s){stockByVariant[s.variant_id]=s.quantity});
  reservations.forEach(function(r){reservedByVariant[r.variant_id]=(reservedByVariant[r.variant_id]||0)+r.quantity});
  var active=products.filter(function(p){return p.status==='active'}).length;
  var low=variants.filter(function(v){return v.is_active&&productById[v.product_id]&&productById[v.product_id].status==='active'&&(stockByVariant[v.id]||0)-(reservedByVariant[v.id]||0)<=5}).length;
  $('#stat-products').textContent=active;
  $('#stat-low').textContent=low;
  $('#stat-pending').textContent=orders.filter(function(o){return o.order_status==='pending_whatsapp_confirmation'}).length;
  $('#stat-confirmed').textContent=orders.filter(function(o){return o.order_status==='confirmed'}).length;
  $('#today').textContent=new Date().toLocaleDateString('en-IN',{weekday:'short',day:'numeric',month:'short',year:'numeric'});
  renderOrders(orders.slice(0,6),'recent-orders');
  renderOrders(orders,'orders-table');
  renderProducts(products);
  renderInventory(variants,productById,stockByVariant,reservedByVariant);
 }catch(e){message('Could not load dashboard data: '+(e.message||'Unknown error'))}
}
function renderOrders(rows,target){
 var el=$('#'+target);
 if(!rows.length){el.innerHTML='<div class="empty-state">No orders yet. New WhatsApp requests will appear here.</div>';return}
 el.innerHTML='<table><thead><tr><th>ORDER</th><th>CUSTOMER</th><th>DATE</th><th>TOTAL</th><th>STATUS</th></tr></thead><tbody>'+rows.map(function(o){return '<tr><td><b>'+esc(o.order_number)+'</b></td><td>'+esc(o.customer_name)+'<br><small>'+esc(o.phone)+'</small></td><td>'+esc(date(o.created_at))+'</td><td>'+esc(money(o.total_amount_inr))+'</td><td>'+status(o.order_status)+'</td></tr>'}).join('')+'</tbody></table>';
}
function renderProducts(rows){
 var el=$('#products-table');
 if(!rows.length){el.innerHTML='<div class="empty-state">No products have been added yet.</div>';return}
 el.innerHTML='<table><thead><tr><th>PRODUCT</th><th>CODE</th><th>PRICE</th><th>STATUS</th><th>FEATURED</th></tr></thead><tbody>'+rows.map(function(p){return '<tr><td><b>'+esc(p.name)+'</b></td><td>'+esc(p.product_code)+'</td><td>'+esc(money(p.price_inr))+'</td><td>'+status(p.status)+'</td><td>'+(p.is_featured?'Yes':'No')+'</td></tr>'}).join('')+'</tbody></table>';
}
function renderInventory(variants,products,stock,reserved){
 var rows=variants.map(function(v){var p=products[v.product_id];if(!p)return null;var on=stock[v.id]||0,res=reserved[v.id]||0;return {p:p,v:v,on:on,res:res,available:on-res}}).filter(Boolean);
 var el=$('#inventory-table');
 if(!rows.length){el.innerHTML='<div class="empty-state">No product variants or stock records yet.</div>';return}
 el.innerHTML='<table><thead><tr><th>PRODUCT</th><th>SKU</th><th>SIZE / COLOR</th><th>ON HAND</th><th>RESERVED</th><th>AVAILABLE</th></tr></thead><tbody>'+rows.map(function(r){return '<tr><td><b>'+esc(r.p.name)+'</b></td><td>'+esc(r.v.sku)+'</td><td>'+esc(r.v.size)+' / '+esc(r.v.color)+'</td><td>'+r.on+'</td><td>'+r.res+'</td><td><b>'+r.available+'</b></td></tr>'}).join('')+'</tbody></table>';
}
client.auth.getSession().then(function(r){if(r.data.session)enter(r.data.session.user);else showLogin()});
})();