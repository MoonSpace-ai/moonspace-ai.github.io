const toggle=document.querySelector('.menu-toggle');
const nav=document.querySelector('.nav');
toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('is-open',open);toggle.textContent=open?'收起':'菜单';});
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&nav?.classList.contains('is-open')){nav.classList.remove('is-open');toggle.setAttribute('aria-expanded','false');toggle.textContent='菜单';toggle.focus();}});
document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{const status=document.getElementById(button.dataset.status);try{await navigator.clipboard.writeText(button.dataset.copy);status.textContent='已复制微信号，添加时备注「MoonSpace」。';}catch{status.textContent='请选中微信号复制：'+button.dataset.copy;}}));
const filters=document.querySelectorAll('[data-filter]');
filters.forEach(button=>button.addEventListener('click',()=>{let count=0;filters.forEach(item=>item.setAttribute('aria-pressed',String(item===button)));document.querySelectorAll('[data-kind]').forEach(card=>{const visible=button.dataset.filter==='all'||card.dataset.kind===button.dataset.filter;card.hidden=!visible;if(visible)count++;});document.getElementById('filter-status').textContent='显示'+count+'项'+(button.dataset.filter==='all'?'内容':button.textContent); }));
