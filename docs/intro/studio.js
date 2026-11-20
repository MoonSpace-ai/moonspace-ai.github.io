'use strict';
const FIELDS=['name','headline','about','doing','offer','workTitle','workStory','workUrl','seeking','question','availability','growth','witnessName','witness','contact','website','contactNote'];
const KEY='moonspace-intro-v1';
const empty=()=>Object.fromEntries([...FIELDS.map(k=>[k,'']),['witnessApproved',false]]);
const escapeHtml=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function safeUrl(value){try{const url=new URL(value);return ['https:','http:'].includes(url.protocol)?url.href:null;}catch{return null;}}
function normalize(value){if(!value||typeof value!=='object'||Array.isArray(value)||!FIELDS.some(key=>Object.prototype.hasOwnProperty.call(value,key)))throw new Error('草稿格式不正确');const clean=empty();for(const key of FIELDS){if(value[key]!==undefined&&typeof value[key]!=='string')throw new Error('草稿字段格式不正确');clean[key]=(value[key]||'').slice(0,2400);}clean.witnessApproved=value.witnessApproved===true;return clean;}
function groups(d){return [
 {title:'最近在做什么',body:d.doing},
 {title:'我能提供的帮助',body:d.offer},
 {title:d.workTitle||'一项具体的成果',body:d.workStory,url:d.workUrl},
 {title:'我正在寻找',body:d.seeking},
 {title:'我关心的问题',body:d.question},
 {title:'我的协作方式',body:d.availability},
 {title:'我最近的一次成长',body:d.growth},
 ...(d.witnessApproved&&d.witnessName.trim()&&d.witness.trim()?[{title:'伙伴见证',body:d.witness,by:d.witnessName,witness:true}]:[]),
 {title:'和我联系',body:[d.contact,d.contactNote].filter(Boolean).join('\n'),url:d.website}
 ].filter(g=>g.body?.trim()||safeUrl(g.url));}
function sectionsHtml(d){const list=groups(d);return list.length?list.map(g=>`<section class="profile-section${g.witness?' witness':''}"><h3>${escapeHtml(g.title)}</h3>${g.body?`<p>${escapeHtml(g.body)}</p>`:''}${safeUrl(g.url)?`<a href="${escapeHtml(safeUrl(g.url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(safeUrl(g.url))}</a>`:''}${g.by?`<p class="sub-label">见证人：${escapeHtml(g.by)} · 由作者录入，见证人已确认</p>`:''}</section>`).join(''):'<p class="empty-message">写下正在做的事、作品和期待，它们会在这里连成一份介绍。</p>';}
function markdown(d){const text=v=>String(v||'').replace(/[<>]/g,c=>c==='<'?'&lt;':'&gt;').replace(/[\\`*_{}\[\]]/g,'\\$&');return [`# ${text(d.name)}`,d.headline?text(d.headline):'',d.about?text(d.about):'',...groups(d).map(g=>`## ${text(g.title)}\n\n${text(g.body)}${safeUrl(g.url)?'\n\n'+safeUrl(g.url):''}${g.by?'\n\n见证人：'+text(g.by)+'（由作者录入，见证人已确认）':''}`),'---','由本人整理 · 使用 MoonSpace 个人说明书工坊制作','https://moonspace-ai.github.io/intro/'].filter(Boolean).join('\n\n')+'\n';}
function progress(d){return [!!d.name.trim(),!!(d.doing.trim()||d.offer.trim()),!!(d.workTitle.trim()&&(d.workStory.trim()||safeUrl(d.workUrl))),!!(d.seeking.trim()||d.question.trim()),!!d.growth.trim(),!!(d.contact.trim()||safeUrl(d.website))].filter(Boolean).length;}
if(typeof module!=='undefined'&&module.exports)module.exports={normalize,safeUrl,sectionsHtml,markdown,groups,progress};
if(typeof document!=='undefined'){
 const form=document.getElementById('profile-form'),status=document.getElementById('status');
 let data=empty(),step=0,timer;
 const inform=message=>{status.textContent=message;};
 try{const raw=localStorage.getItem(KEY);if(raw){const saved=JSON.parse(raw);data=normalize(saved.profile||saved);inform('已恢复这个浏览器里的草稿。');}}catch{inform('当前浏览器无法读取本地草稿。请用下载备份保存内容。');}
 for(const key of FIELDS)form.elements[key].value=data[key];form.elements.witnessApproved.checked=data.witnessApproved;
 function render(){
  document.getElementById('progress').textContent=`已填写 ${progress(data)} / 6 项`;
  document.getElementById('preview-name').textContent=data.name||'你的名字';
  document.getElementById('monogram').textContent=[...(data.name.trim()||'你')][0];
  document.getElementById('preview-headline').textContent=data.headline||'一句话，让别人认识你。';
  document.getElementById('preview-about').textContent=data.about||'你写下的介绍，会从这里开始。';
  document.getElementById('preview-sections').innerHTML=sectionsHtml(data);
  document.getElementById('preview-date').textContent=new Date().toLocaleDateString('zh-CN');
 }
 function save(){try{localStorage.setItem(KEY,JSON.stringify({version:1,profile:data,updatedAt:new Date().toISOString()}));inform('已保存在当前浏览器，尚未公开。');}catch{inform('本地保存不可用，请下载草稿备份。');}}
 function setStep(n){step=Math.max(0,Math.min(5,n));document.querySelectorAll('[data-step]').forEach((tab,index)=>{const active=index===step;tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1;});document.querySelectorAll('[data-panel]').forEach((panel,index)=>panel.hidden=index!==step);document.getElementById('panel').setAttribute('aria-labelledby',`tab-${step}`);document.getElementById('previous').disabled=step===0;document.getElementById('next').textContent=step===5?'检查说明书':'下一项';document.getElementById('step-count').textContent=`${step+1} / 6`;}
 form.addEventListener('submit',e=>e.preventDefault());
 form.addEventListener('input',()=>{for(const key of FIELDS)data[key]=form.elements[key].value;data.witnessApproved=form.elements.witnessApproved.checked;render();clearTimeout(timer);timer=setTimeout(save,250);});
 document.querySelectorAll('[data-step]').forEach(tab=>{tab.addEventListener('click',()=>setStep(Number(tab.dataset.step)));tab.addEventListener('keydown',e=>{if(['ArrowRight','ArrowLeft','Home','End'].includes(e.key)){e.preventDefault();setStep(e.key==='Home'?0:e.key==='End'?5:step+(e.key==='ArrowRight'?1:-1));document.getElementById(`tab-${step}`).focus();}});});
 document.getElementById('previous').addEventListener('click',()=>setStep(step-1));
 document.getElementById('next').addEventListener('click',()=>{if(step<5)setStep(step+1);else{document.getElementById('preview').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});inform('请检查预览中的作品、见证和联系方式，再导出。');}});
 function download(content,type,extension){const url=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=url;a.download=`${(data.name||'MoonSpace').replace(/[\\/:*?"<>|]/g,'').slice(0,45)}-个人说明书.${extension}`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 function validate(){if(!data.name.trim()){setStep(0);form.elements.name.focus();inform('先填写名字或昵称，再导出说明书。');return false;}for(const [field,index] of [['workUrl',2],['website',5]])if(data[field].trim()&&!safeUrl(data[field])){setStep(index);form.elements[field].focus();inform('请填写完整的 http 或 https 链接，也可以先留空。');return false;}return true;}
 document.getElementById('backup').addEventListener('click',()=>{download(JSON.stringify({version:1,profile:data,updatedAt:new Date().toISOString()},null,2),'application/json;charset=utf-8','json');inform('草稿备份已下载。它包含填写内容，请由你自行保管。');});
 document.getElementById('restore').addEventListener('change',async event=>{const file=event.target.files[0];if(!file)return;try{if(file.size>200000)throw new Error('草稿文件过大');const raw=JSON.parse(await file.text());const imported=normalize(raw.profile||raw);if(FIELDS.some(key=>data[key].trim())&&!confirm('导入会替换当前浏览器中的草稿。是否继续？'))return;data=imported;for(const key of FIELDS)form.elements[key].value=data[key];form.elements.witnessApproved.checked=data.witnessApproved;render();save();setStep(0);inform('草稿已导入并保存在当前浏览器。');}catch(error){inform('导入失败：'+(error.message||'请检查 JSON 草稿文件'));}finally{event.target.value='';}});
 document.getElementById('clear').addEventListener('click',()=>{if(!confirm('清空当前草稿？如需保留，请先下载备份。'))return;clearTimeout(timer);data=empty();for(const key of FIELDS)form.elements[key].value='';form.elements.witnessApproved.checked=false;try{localStorage.removeItem(KEY);}catch{}render();setStep(0);inform('当前浏览器中的草稿已清空。');});
 document.getElementById('export-md').addEventListener('click',()=>{if(validate()){download(markdown(data),'text/markdown;charset=utf-8','md');inform('Markdown 已下载，可以继续编辑或交给社区整理。');}});
 document.getElementById('copy-md').addEventListener('click',async()=>{if(!validate())return;try{await navigator.clipboard.writeText(markdown(data));inform('已复制 Markdown 文字。');}catch{inform('浏览器未允许复制，请使用导出 Markdown。');}});
 document.getElementById('export-html').addEventListener('click',async()=>{
  if(!validate())return;
  const snapshot=normalize(data);const button=document.getElementById('export-html');button.disabled=true;
  try{const response=await fetch(new URL('studio.css',location.href));if(!response.ok)throw new Error('样式加载失败');let css=await response.text();css=css.replace(/@font-face\{[^}]*\}/g,'').replace(/--hand:MoonHand,'KaiTi',cursive/g,"--hand:'KaiTi','STKaiti',serif");
   const article=`<article class="profile-paper"><div class="paper-top"><span class="paper-tag">个人说明书</span><span>${escapeHtml(new Date().toLocaleDateString('zh-CN'))}</span></div><div class="identity"><div class="monogram">${escapeHtml([...snapshot.name.trim()][0])}</div><div><h1 style="font-size:32px;margin:0">${escapeHtml(snapshot.name)}</h1><p>${escapeHtml(snapshot.headline)}</p></div></div>${snapshot.about?`<p class="about-text">${escapeHtml(snapshot.about)}</p>`:''}${sectionsHtml(snapshot)}<div class="paper-footer">由本人整理 · 使用 <a href="https://moonspace-ai.github.io/intro/">MoonSpace 个人说明书工坊</a>制作</div></article>`;
   const html=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escapeHtml(snapshot.name)}的个人说明书</title><style>${css}\nmain{max-width:850px;padding:35px 20px}.profile-paper{box-shadow:none}</style></head><body><main>${article}</main></body></html>`;
   download(html,'text/html;charset=utf-8','html');inform('独立网页已下载，可离线打开；需要发布后才会有在线链接。');
  }catch{inform('网页导出失败，请重试，或先导出 Markdown 和草稿备份。');}finally{button.disabled=false;}
 });
 render();setStep(0);
}
