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
var productForm=$('#product-form');
productForm.addEventListener('submit',async function(e){
 e.preventDefault();
 var form=e.currentTarget,btn=form.querySelector('button[type="submit"]'),out=$('#product-form-message');
 var data=new FormData(form);
 var name=String(data.get('name')||'').trim(),code=String(data.get('product_code')||'').trim().toUpperCase();
 var lines=String(data.get('variants')||'').split(/\r?\n/).map(function(x){return x.trim()}).filter(Boolean);

 var files=Array.from(form.elements.images.files||[]); if(files.some(function(f){return !['image/jpeg','image/png','image/webp'].includes(f.type)||f.size>5*1024*1024})){out.textContent='Each image must be JPEG, PNG or WebP and no larger than 5 MB.';return}
 var variants=[];
 for(var i=0;i<lines.length;i++){
  var parts=lines[i].split('|').map(function(x){return x.trim()});
  if(parts.length!==4||!parts[0]||!parts[1]||!parts[2]||!/^\\d+$/.test(parts[3])){out.textContent='Variant line '+(i+1)+' is invalid. Use: SKU | Size | Color | Stock';return}
  variants.push({sku:parts[0],size:parts[1],color:parts[2],quantity:Number(parts[3])});
 }
 if(!variants.length){out.textContent='Add at least one variant.';return}
 if(new Set(variants.map(function(v){return v.sku.toLowerCase()})).size!==variants.length){out.textContent='Each variant must have a unique SKU.';return}
 var priceRaw=String(data.get('price_inr')||'').trim();
 var price=priceRaw===''?null:Number(priceRaw);
 if(price!==null&&(!Number.isFinite(price)||price<0)){out.textContent='Enter a valid price.';return}
 btn.disabled=true;btn.textContent='Saving…';out.textContent='';
 var slug=name.toLowerCase().normalize('NFKD').replace(/[\\u0300-\\u036f]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
 try{
  var p=await client.from('products').insert({name:name,product_code:code,slug:slug,description:String(data.get('description')||'').trim()||null,price_inr:price,status:data.get('status'),is_featured:false,published_at:data.get('status')==='active'?new Date().toISOString():null}).select('id').single();
  if(p.error)throw p.error;
  var variantRows=variants.map(function(v){return {product_id:p.data.id,sku:v.sku,size:v.size,color:v.color,is_active:true}});
  var inserted=await client.from('product_variants').insert(variantRows).select('id,sku');
  if(inserted.error)throw new Error('Product saved, but variants could not be saved: '+inserted.error.message+' (Product code: '+code+')');
  var stockRows=inserted.data.map(function(v){var match=variants.find(function(x){return x.sku===v.sku});return {variant_id:v.id,quantity:match.quantity}});
  var stockResult=await client.from('inventory').insert(stockRows);
  if(stockResult.error)throw new Error('Product and variants saved, but opening stock could not be saved: '+stockResult.error.message);
  for(var imageIndex=0;imageIndex<files.length;imageIndex++){
   var file=files[imageIndex],extension=file.name.split('.').pop().toLowerCase().replace(/[^a-z0-9]/g,'')||'img';
   var path=p.data.id+'/'+String(imageIndex+1).padStart(2,'0')+'-'+Date.now()+'.'+extension;
   var uploaded=await client.storage.from('product-images').upload(path,file,{cacheControl:'3600',upsert:false,contentType:file.type});
   if(uploaded.error)throw new Error('Product and stock saved, but image upload failed: '+uploaded.error.message);
   var imageRow=await client.from('product_images').insert({product_id:p.data.id,storage_path:path,image_type:imageIndex===0?'front':'detail',alt_text:name+' product image '+(imageIndex+1),display_order:imageIndex});
   if(imageRow.error)throw new Error('Image uploaded but its product record could not be saved: '+imageRow.error.message);
  }
  out.textContent='Product saved with '+variants.length+' variant(s) and '+files.length+' image(s).';
  form.reset();await loadAll();
 }catch(err){out.textContent=err.message||'Could not save product.'}
 finally{btn.disabled=false;btn.textContent='Save product'}
});
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