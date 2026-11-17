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
   client.from('products').select('id,name,product_code,description,price_inr,status,is_featured,updated_at,product_images(id,storage_path,image_type,alt_text,display_order)').order('created_at',{ascending:false}),
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
  renderProducts(products,variants,stockByVariant);
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
  if(parts.length!==4||!parts[0]||!parts[1]||!parts[2]||!/^\d+$/.test(parts[3])){out.textContent='Variant line '+(i+1)+' is invalid. Use: SKU | Size | Color | Stock';return}
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
function renderProducts(rows,variants,stock){
 var el=$('#products-table');
 if(!rows.length){el.innerHTML='<div class="empty-state">No products have been added yet.</div>';return}
 var grouped={};(variants||[]).forEach(function(v){(grouped[v.product_id]||(grouped[v.product_id]=[])).push(v)});
 var viewMap={SCORPION:['back'],THISDAY:['back'],BALANCE:['front','back'],LABLACK:['back'],MYTHIC:['front'],LABROWN:['back'],SILENCE:['front','back'],EAGLE:['front','back'],SPIDER:['front','back'],UNREAL:['front','back']};
 el.innerHTML='<div class="admin-product-grid">'+rows.map(function(p){
  var code=(p.product_code||'').replace('BCF-',''),key=code.toLowerCase(),views=viewMap[code]||['front'],stored=(p.product_images||[]).slice().sort(function(a,b){return a.display_order-b.display_order}),gallery=stored.length?stored.map(function(im){var url=client.storage.from('product-images').getPublicUrl(im.storage_path).data.publicUrl;return '<img class="admin-product-thumb" src="'+esc(url)+'" alt="'+esc(im.alt_text||p.name)+'" loading="lazy">'}).join(''):views.map(function(view){return '<img class="admin-product-thumb" src="../assets/img/p-'+key+'-'+view+'-800.webp" alt="'+esc(p.name)+' '+view+'" loading="lazy" onerror="this.style.display=\'none\'">'}).join('');
  var vv=grouped[p.id]||[],sizes=vv.map(function(v){return v.size+' / '+v.color+' — '+v.sku+' — stock '+Number(stock[v.id]||0)+(v.is_active?'':' (inactive)')}).join('<br>');
  var on=vv.reduce(function(n,v){return n+Number(stock[v.id]||0)},0);
  return '<article class="admin-product-card"><div class="admin-product-gallery">'+gallery+'</div><div class="admin-product-info"><div class="admin-product-title"><b>'+esc(p.name)+'</b>'+status(p.status)+'</div><small>'+esc(p.product_code)+'</small><p>'+esc(p.description||'No description')+'</p><div class="admin-product-meta"><span>'+esc(money(p.price_inr))+'</span><span>Sizes: '+esc(sizes||'None')+'</span><span>Opening stock: '+on+'</span></div><div class="admin-product-actions"><button class="text-button" data-edit-product="'+p.id+'">Edit details</button><button class="text-button" data-toggle-product="'+p.id+'">'+(p.status==='active'?'Unpublish':'Publish')+'</button></div></div></article>';
 }).join('')+'</div>';
 el.querySelectorAll('[data-toggle-product]').forEach(function(b){b.addEventListener('click',async function(){var p=rows.find(function(x){return x.id===b.dataset.toggleProduct});if(!p)return;var next=p.status==='active'?'draft':'active';var r=await client.from('products').update({status:next,published_at:next==='active'?new Date().toISOString():null}).eq('id',p.id);if(r.error){message(r.error.message);return}await loadAll()})});
 el.querySelectorAll('[data-edit-product]').forEach(function(b){b.addEventListener('click',function(){var p=rows.find(function(x){return x.id===b.dataset.editProduct});if(p)openProductEditor(p,grouped[p.id]||[],stock)})});
}
function openProductEditor(product,variants,stock){
 var old=document.getElementById('product-editor');if(old)old.remove();
 var stockById={};stock.forEach(function(x){stockById[x.variant_id]=Number(x.quantity)||0});
 var imgs=(product.product_images||[]).slice().sort(function(a,b){return a.display_order-b.display_order});
 var modal=document.createElement('div');modal.id='product-editor';modal.className='editor-backdrop';
 modal.innerHTML='<section class="editor-panel" role="dialog" aria-modal="true" aria-labelledby="editor-title"><header class="editor-head"><div><p class="eyebrow">CATALOGUE MANAGEMENT</p><h2 id="editor-title">Edit product</h2></div><button type="button" class="icon-button" data-editor-close aria-label="Close">×</button></header><form id="editor-form" class="product-form"><div class="form-grid"><label>Product name<input name="name" required maxlength="120"></label><label>Product code<input name="product_code" readonly></label><label>Price (INR)<input name="price_inr" type="number" min="0" step="0.01" placeholder="Leave blank for WhatsApp"></label><label>Visibility<select name="status"><option value="draft">Draft</option><option value="active">Published</option></select></label></div><label>Description<textarea name="description" rows="3"></textarea></label><div><b>Current product images</b><div class="editor-images" id="editor-images"></div></div><label>Add images <span class="muted">(JPEG, PNG or WebP · max 5 MB each)</span><input name="new_images" type="file" accept="image/jpeg,image/png,image/webp" multiple></label><label>Variants and stock <span class="muted">(one per line: SKU | Size | Color | Stock)</span><textarea name="variants" rows="7" required></textarea></label><p class="form-help">Keep a line to retain a variant. Remove a line to deactivate it; variants with order history are retained, not deleted.</p><div class="form-actions"><button class="primary form-submit" type="submit">Save changes</button><button class="text-button" type="button" data-editor-close>Cancel</button><span id="editor-message" role="status"></span></div></form></section>';
 document.body.appendChild(modal);
 var f=modal.querySelector('#editor-form'),msg=modal.querySelector('#editor-message');
 f.elements.name.value=product.name||'';f.elements.product_code.value=product.product_code||'';f.elements.price_inr.value=product.price_inr==null?'':product.price_inr;f.elements.status.value=product.status;f.elements.description.value=product.description||'';
 f.elements.variants.value=variants.filter(function(v){return v.is_active}).map(function(v){return [v.sku,v.size,v.color,stockById[v.id]||0].join(' | ')}).join('\n');
 var imageBox=modal.querySelector('#editor-images');
 if(!imgs.length)imageBox.innerHTML='<p class="muted">No uploaded images yet. Existing storefront artwork remains available as fallback.</p>';
 else imageBox.innerHTML=imgs.map(function(im){var url=client.storage.from('product-images').getPublicUrl(im.storage_path).data.publicUrl;return '<figure><img src="'+esc(url)+'" alt="'+esc(im.alt_text||product.name)+'"><figcaption>'+esc(im.image_type)+' <button type="button" class="text-button danger-text" data-remove-image="'+im.id+'">Remove</button></figcaption></figure>'}).join('');
 modal.querySelectorAll('[data-editor-close]').forEach(function(x){x.addEventListener('click',function(){modal.remove()})});
 modal.addEventListener('click',function(e){if(e.target===modal)modal.remove()});
 imageBox.querySelectorAll('[data-remove-image]').forEach(function(btn){btn.addEventListener('click',async function(){if(!confirm('Remove this image from the product?'))return;btn.disabled=true;var im=imgs.find(function(x){return x.id===btn.dataset.removeImage});var del=await client.from('product_images').delete().eq('id',im.id);if(del.error){msg.textContent='Could not remove image: '+del.error.message;btn.disabled=false;return}var fileDel=await client.storage.from('product-images').remove([im.storage_path]);if(fileDel.error){msg.textContent='Image record removed, but storage cleanup failed: '+fileDel.error.message;return}imgs=imgs.filter(function(x){return x.id!==im.id});btn.closest('figure').remove();if(!imgs.length)imageBox.innerHTML='<p class="muted">No uploaded images yet.</p>'})})});
 f.addEventListener('submit',async function(e){
  e.preventDefault();var submit=f.querySelector('[type="submit"]');submit.disabled=true;submit.textContent='Saving…';msg.textContent='';
  try{
   var name=f.elements.name.value.trim(),priceText=f.elements.price_inr.value.trim(),price=priceText===''?null:Number(priceText);
   if(price!==null&&(!Number.isFinite(price)||price<0))throw new Error('Enter a valid non-negative price.');
   var lines=f.elements.variants.value.split(/\r?\n/).map(function(x){return x.trim()}).filter(Boolean),parsed=[];
   lines.forEach(function(line,i){var z=line.split('|').map(function(x){return x.trim()});if(z.length!==4||!z[0]||!['S','M','L','XL'].includes(z[1].toUpperCase())||!z[2]||!/^\d+$/.test(z[3]))throw new Error('Variant line '+(i+1)+' is invalid. Use SKU | S/M/L/XL | Color | Stock');parsed.push({sku:z[0],size:z[1].toUpperCase(),color:z[2],quantity:Number(z[3])})});
   if(!parsed.length)throw new Error('At least one active variant is required.');
   if(new Set(parsed.map(function(x){return x.sku.toLowerCase()})).size!==parsed.length)throw new Error('Variant SKUs must be unique.');
   var files=Array.from(f.elements.new_images.files||[]);if(files.some(function(x){return !['image/jpeg','image/png','image/webp'].includes(x.type)||x.size>5*1024*1024}))throw new Error('Each image must be JPEG, PNG or WebP and no larger than 5 MB.');
   var up=await client.from('products').update({name:name,slug:name.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,''),description:f.elements.description.value.trim()||null,price_inr:price,status:f.elements.status.value,published_at:f.elements.status.value==='active'?(product.published_at||new Date().toISOString()):null,updated_at:new Date().toISOString()}).eq('id',product.id);
   if(up.error)throw up.error;
   var existingBySku={};variants.forEach(function(v){existingBySku[v.sku.toLowerCase()]=v});
   var keep={};
   for(var i=0;i<parsed.length;i++){
    var v=parsed[i],old=existingBySku[v.sku.toLowerCase()],variantId;
    if(old){variantId=old.id;var vu=await client.from('product_variants').update({size:v.size,color:v.color,is_active:true}).eq('id',old.id);if(vu.error)throw new Error('Variant '+v.sku+' update failed: '+vu.error.message)}
    else{var vi=await client.from('product_variants').insert({product_id:product.id,sku:v.sku,size:v.size,color:v.color,is_active:true}).select('id').single();if(vi.error)throw new Error('Could not add variant '+v.sku+': '+vi.error.message);variantId=vi.data.id}
    keep[variantId]=true;var previous=old?Number(stockById[variantId]||0):0;var si=await client.from('inventory').upsert({variant_id:variantId,quantity:v.quantity,updated_at:new Date().toISOString()},{onConflict:'variant_id'});if(si.error)throw new Error('Stock update failed for '+v.sku+': '+si.error.message);var delta=v.quantity-previous;if(delta!==0){var mv=await client.from('inventory_movements').insert({variant_id:variantId,quantity_change:delta,movement_type:old?'adjustment':'initial_stock',reason:'Admin product editor stock update',performed_by:(await client.auth.getUser()).data.user.id});if(mv.error)throw new Error('Stock saved but inventory history could not be recorded for '+v.sku+': '+mv.error.message)}
   }
   for(var j=0;j<variants.length;j++){if(!keep[variants[j].id]&&variants[j].is_active){var off=await client.from('product_variants').update({is_active:false}).eq('id',variants[j].id);if(off.error)throw new Error('Could not deactivate removed variant '+variants[j].sku+': '+off.error.message)}}
   for(var k=0;k<files.length;k++){var file=files[k],ext=file.name.split('.').pop().toLowerCase().replace(/[^a-z0-9]/g,'')||'img',path=product.id+'/'+Date.now()+'-'+k+'.'+ext;var put=await client.storage.from('product-images').upload(path,file,{cacheControl:'3600',upsert:false,contentType:file.type});if(put.error)throw new Error('Image upload failed: '+put.error.message);var rec=await client.from('product_images').insert({product_id:product.id,storage_path:path,image_type:imgs.length===0&&k===0?'front':'detail',alt_text:name+' product image '+(imgs.length+k+1),display_order:imgs.length+k});if(rec.error)throw new Error('Image uploaded but image record failed: '+rec.error.message)}
   msg.textContent='Saved. Product, variants, stock and images are updated in Supabase.';await loadAll();setTimeout(function(){modal.remove()},700);
  }catch(err){msg.textContent=err.message||'Could not save changes.'}
  finally{submit.disabled=false;submit.textContent='Save changes'}
 });
}

function renderInventory(variants,products,stock,reserved){
 var rows=variants.map(function(v){var p=products[v.product_id];if(!p)return null;var on=stock[v.id]||0,res=reserved[v.id]||0;return {p:p,v:v,on:on,res:res,available:on-res}}).filter(Boolean);
 var el=$('#inventory-table');
 if(!rows.length){el.innerHTML='<div class="empty-state">No product variants or stock records yet.</div>';return}
 el.innerHTML='<table><thead><tr><th>PRODUCT</th><th>SKU</th><th>SIZE / COLOR</th><th>ON HAND</th><th>RESERVED</th><th>AVAILABLE</th></tr></thead><tbody>'+rows.map(function(r){return '<tr><td><b>'+esc(r.p.name)+'</b></td><td>'+esc(r.v.sku)+'</td><td>'+esc(r.v.size)+' / '+esc(r.v.color)+'</td><td>'+r.on+'</td><td>'+r.res+'</td><td><b>'+r.available+'</b></td></tr>'}).join('')+'</tbody></table>';
}
client.auth.getSession().then(function(r){if(r.data.session)enter(r.data.session.user);else showLogin()});
})();