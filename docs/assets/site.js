const toggle=document.querySelector('.menu-toggle');
const nav=document.querySelector('.nav');
toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('is-open',open);toggle.textContent=open?'收起':'菜单';});
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&nav?.classList.contains('is-open')){nav.classList.remove('is-open');toggle.setAttribute('aria-expanded','false');toggle.textContent='菜单';toggle.focus();}});
document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{const status=document.getElementById(button.dataset.status);try{await navigator.clipboard.writeText(button.dataset.copy);status.textContent='已复制微信号，添加时备注「MoonSpace」。';}catch{status.textContent='请选中微信号复制：'+button.dataset.copy;}}));
const filters=document.querySelectorAll('[data-filter]');
filters.forEach(button=>button.addEventListener('click',()=>{let count=0;filters.forEach(item=>item.setAttribute('aria-pressed',String(item===button)));document.querySelectorAll('[data-kind]').forEach(card=>{const visible=button.dataset.filter==='all'||card.dataset.kind===button.dataset.filter;card.hidden=!visible;if(visible)count++;});document.getElementById('filter-status').textContent='显示'+count+'项'+(button.dataset.filter==='all'?'内容':button.textContent); }));

// Quiet, progressive motion: content is fully visible without JavaScript.
const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
const finePointer=matchMedia('(hover: hover) and (pointer: fine)');
const observer='IntersectionObserver' in window?new IntersectionObserver(entries=>entries.forEach(entry=>entry.target.classList.toggle('is-visible',entry.isIntersecting)),{threshold:.12}):null;
document.querySelectorAll('.community-collage>a,.discover-item').forEach(el=>observer?.observe(el));
const halo=document.querySelector('.pointer-halo');
const title=document.querySelector('.hero-title');
let glyphs=[];
if(title){
 title.querySelectorAll('[data-title-text],.title-bang').forEach(line=>{
  [...line.childNodes].filter(n=>n.nodeType===Node.TEXT_NODE).forEach(node=>{
   const fragment=document.createDocumentFragment();
   [...node.textContent].forEach(character=>{const span=document.createElement('span');span.className='title-glyph';span.textContent=character;fragment.append(span);});
   node.replaceWith(fragment);
  });
 });
 glyphs=[...title.querySelectorAll('.title-glyph')];
 title.addEventListener('pointermove',event=>{
  if(reducedMotion.matches||!finePointer.matches)return;
  glyphs.forEach(glyph=>{const rect=glyph.getBoundingClientRect();const distance=Math.hypot(event.clientX-rect.x-rect.width/2,event.clientY-rect.y-rect.height/2);glyph.style.setProperty('--glyph-opacity',String(.4+.6*Math.min(1,distance/115)));});
 });
 title.addEventListener('pointerleave',()=>glyphs.forEach(g=>g.style.removeProperty('--glyph-opacity')));
}
document.addEventListener('pointermove',event=>{
 if(!halo||!finePointer.matches||reducedMotion.matches)return;
 const link=!!event.target.closest('a,button,summary');const size=link?46:32;
 halo.classList.toggle('is-link',link);halo.style.translate=`${event.clientX-size/2}px ${event.clientY-size/2}px`;halo.style.opacity='1';
},{passive:true});
document.documentElement.addEventListener('pointerleave',()=>{if(halo)halo.style.opacity='0';});
document.addEventListener('pointerdown',event=>{
 if(reducedMotion.matches||!finePointer.matches||event.button!==0)return;
 const echo=document.createElement('span');echo.className='click-echo';echo.style.left=`${event.clientX-9}px`;echo.style.top=`${event.clientY-9}px`;echo.setAttribute('aria-hidden','true');document.body.append(echo);echo.addEventListener('animationend',()=>echo.remove(),{once:true});
});

// Original instrumental loop, synthesised locally. No download or autoplay.
const soundButton=document.querySelector('.sound-toggle');
let audioContext,masterGain,musicTimer,musicOn=false,audioBusy=false,nextBeat=0,beatIndex=0;
const chords=[[48,55,60,64],[45,52,57,60],[41,48,53,57],[43,50,55,59]];
const melody=[72,null,76,79,null,76,74,null,72,null,69,72,null,76,72,null,69,null,72,77,null,76,72,null,71,null,74,79,null,74,71,null];
const hz=note=>440*Math.pow(2,(note-69)/12);
function tone(note,start,duration,volume,type='sine'){
 const oscillator=audioContext.createOscillator(),gain=audioContext.createGain();
 oscillator.type=type;oscillator.frequency.value=hz(note);
 gain.gain.setValueAtTime(0,start);gain.gain.linearRampToValueAtTime(volume,start+.08);gain.gain.exponentialRampToValueAtTime(.0001,start+duration);
 oscillator.connect(gain);gain.connect(masterGain);oscillator.start(start);oscillator.stop(start+duration+.05);
}
function scheduleMusic(){
 if(!musicOn)return;
 while(nextBeat<audioContext.currentTime+.3){
  const step=beatIndex%32,chord=chords[Math.floor(step/8)];
  if(step%8===0)chord.forEach((note,index)=>tone(note,nextBeat+index*.08,4.8,.035));
  if(step%2===0)tone(chord[(step/2)%4]+12,nextBeat,1.65,.032,'triangle');
  if(melody[step]!==null)tone(melody[step],nextBeat+.04,1.8,.04);
  nextBeat+=.62;beatIndex++;
 }
}
function musicLabel(on){soundButton?.setAttribute('aria-pressed',String(on));soundButton?.setAttribute('aria-label',on?'关闭纯音乐':'开启纯音乐');if(soundButton)soundButton.querySelector('.sound-label').textContent=on?'关闭音乐':'开启音乐';}
async function stopMusic(){
 musicOn=false;clearInterval(musicTimer);musicLabel(false);
 const context=audioContext;audioContext=null;
 if(context){masterGain.gain.cancelScheduledValues(context.currentTime);masterGain.gain.setTargetAtTime(0,context.currentTime,.06);setTimeout(()=>context.close().catch(()=>{}),250);}
}
soundButton?.addEventListener('click',async()=>{
 if(audioBusy)return;
 if(musicOn){await stopMusic();return;}
 audioBusy=true;
 try{
  const Context=window.AudioContext||window.webkitAudioContext;if(!Context)throw new Error('Audio unavailable');
  audioContext=new Context();masterGain=audioContext.createGain();masterGain.gain.value=.32;masterGain.connect(audioContext.destination);await audioContext.resume();
  if(audioContext.state!=='running')throw new Error('Audio suspended');
  musicOn=true;musicLabel(true);beatIndex=0;nextBeat=audioContext.currentTime+.05;scheduleMusic();musicTimer=setInterval(scheduleMusic,120);
 }catch{await stopMusic();soundButton.querySelector('.sound-label').textContent='音乐暂不可用';}finally{audioBusy=false;}
});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&musicOn)stopMusic();});
window.addEventListener('pagehide',()=>{if(musicOn)stopMusic();});
