"""
LOVE PAGE GENERATOR v2 — 1 file duy nhất (app.py)
Chạy:  pip install streamlit jinja2 qrcode[pil] pillow yt-dlp
       streamlit run app.py
Link chia sẻ dạng  {domain}/?page=<id>  (không cần enableStaticServing).

Có gì mới ở trang kết quả:
  💌 Phong thư bí mật: chạm vào để mở -> nhạc bắt đầu, chữ hiện từng ký tự
  ✨ Sao lấp lánh + sao băng + trái tim được ghép từ các hạt sáng
  🌸 Cánh hoa rơi, tim bay, chạm đâu nổ tim/emoji đáng yêu đó
  💬 Lời nhắn dễ thương thỉnh thoảng bay lên
  🎁 Nút bất ngờ cuối trang: gấu bông + pháo tim
  ⚡ Vẫn giữ chế độ máy yếu (low-fx), tạm dừng khi tab ẩn
Sửa lỗi: bật autoescape cho Jinja2 (chống chèn mã HTML/JS từ ô nhập chữ),
chặn path traversal ở ?page=, viewer tự lấp đầy chiều cao màn hình.
"""
import base64, io, json, os, re, uuid
from datetime import datetime

import qrcode
import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Environment
import yt_dlp  # chỉ để TÌM video (lấy id/tiêu đề), không tải nhạc

# ============================ 1. TÀI NGUYÊN NHÚNG ============================
CSS_CONTENT = r''':root{--primary-color:#ff4d6d;--secondary-color:#ff8fa3;--accent-color:#ffd6e0;--glow-color:rgba(255,77,109,.75);--bg-dark:#2b0a18;--text-light:#fffafc;--heart-speed:8s}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{width:100%;height:100%;overflow:hidden;font-family:'Quicksand','Poppins',sans-serif;background:var(--bg-dark);color:var(--text-light)}
body{display:flex;align-items:center;justify-content:center;background:radial-gradient(circle at 50% 15%,var(--secondary-color) 0%,var(--bg-dark) 78%)}
body.has-bg-image{background-size:cover;background-position:center}
.bg-overlay{position:fixed;inset:0;z-index:0;background:linear-gradient(160deg,rgba(255,77,109,.5),rgba(43,10,24,.82) 60%,rgba(255,143,163,.5));pointer-events:none}
.aurora-light{position:fixed;inset:-20%;z-index:0;pointer-events:none;opacity:.5;filter:blur(40px);will-change:transform;
background:radial-gradient(circle at 20% 30%,var(--glow-color),transparent 35%),radial-gradient(circle at 80% 70%,var(--accent-color),transparent 40%),radial-gradient(circle at 50% 95%,var(--secondary-color),transparent 45%);animation:aur 20s ease-in-out infinite alternate}
@keyframes aur{to{transform:translate3d(4%,-3%,0) scale(1.08)}}
body.low-fx .aurora-light{animation:none;filter:blur(24px);opacity:.35}
#fx-canvas{position:fixed;inset:0;z-index:1;pointer-events:none;width:100%;height:100%}
#hearts-container,#petals,#notes{position:fixed;inset:0;overflow:hidden;pointer-events:none}
#hearts-container{z-index:2}#petals{z-index:3}#notes{z-index:6}
.heart{position:absolute;bottom:-60px;opacity:.85;will-change:transform,opacity;animation:floatUp linear 1 both}
.heart svg{width:100%;height:100%;display:block}
@keyframes floatUp{0%{transform:translate3d(0,0,0) rotate(-10deg) scale(.6);opacity:0}10%{opacity:1}50%{transform:translate3d(var(--drift),-55vh,0) rotate(12deg) scale(1)}100%{transform:translate3d(calc(var(--drift)*-1),-115vh,0) rotate(-12deg) scale(.6);opacity:0}}
.petal{position:absolute;top:-30px;width:14px;height:18px;border-radius:80% 0 80% 0;background:linear-gradient(135deg,#fff,var(--secondary-color));opacity:.85;will-change:transform;animation:fall linear 1 both}
@keyframes fall{0%{transform:translate3d(0,0,0) rotate(0)}50%{transform:translate3d(var(--sway),55vh,0) rotate(200deg)}100%{transform:translate3d(calc(var(--sway)*-.6),112vh,0) rotate(400deg);opacity:.2}}
.pop{position:fixed;z-index:60;pointer-events:none;font-size:var(--s,18px);will-change:transform,opacity;animation:pop 1.1s ease-out forwards}
@keyframes pop{0%{transform:translate(-50%,-50%) scale(0);opacity:1}100%{transform:translate(calc(-50% + var(--dx)),calc(-50% + var(--dy))) scale(1.2) rotate(var(--r));opacity:0}}
.note{position:absolute;padding:8px 14px;border-radius:18px 18px 18px 4px;background:rgba(255,255,255,.92);color:#b0214a;font-weight:700;font-size:14px;box-shadow:0 6px 18px rgba(0,0,0,.25);white-space:nowrap;animation:noteUp 6.5s ease-in-out forwards;will-change:transform,opacity}
@keyframes noteUp{0%{transform:translateY(20px) scale(.6);opacity:0}12%{opacity:1;transform:translateY(0) scale(1)}85%{opacity:1}100%{transform:translateY(-90px) scale(.95);opacity:0}}

/* ===== Phong thư bất ngờ ===== */
.envelope-stage{position:fixed;inset:0;z-index:50;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px;background:radial-gradient(circle at 50% 40%,#5a1230,#1d0610 75%);cursor:pointer;transition:opacity .9s ease .5s,visibility .9s ease .5s}
.envelope-stage.opened{opacity:0;visibility:hidden;pointer-events:none}
.env{position:relative;width:min(300px,78vw);aspect-ratio:3/2;animation:bob 3s ease-in-out infinite}
.env.open{animation:none}
@keyframes bob{50%{transform:translateY(-10px) rotate(-1.5deg)}}
.env-back,.env-front,.env-flap{position:absolute;inset:0;border-radius:10px}
.env-back{background:#ffb3c4;box-shadow:0 20px 50px rgba(0,0,0,.5)}
.env-letter{position:absolute;left:8%;right:8%;top:8%;bottom:8%;background:#fffaf5;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:40px;transition:transform .9s cubic-bezier(.3,1.3,.5,1) .55s;z-index:2}
.env.open .env-letter{transform:translateY(-70%) scale(1.05)}
.env-front{z-index:3;background:linear-gradient(135deg,transparent 49.5%,#ff8fa3 50%) left/50% 100% no-repeat,linear-gradient(225deg,transparent 49.5%,#ff8fa3 50%) right/50% 100% no-repeat,linear-gradient(to top,#ff7b98 55%,transparent 55.2%)}
.env-flap{z-index:4;clip-path:polygon(0 0,100% 0,50% 58%);background:linear-gradient(#ff6485,#ff4d6d);transform-origin:top;transition:transform .6s ease,z-index 0s .3s}
.env.open .env-flap{transform:rotateX(180deg);z-index:1}
.seal{position:absolute;z-index:5;left:50%;top:50%;width:62px;height:62px;margin:-46px 0 0 -31px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ff9aae,#c9184a);display:flex;align-items:center;justify-content:center;font-size:28px;box-shadow:0 4px 12px rgba(0,0,0,.4);animation:beat 1.1s infinite;transition:opacity .3s}
.env.open .seal{opacity:0;animation:none}
@keyframes beat{0%,100%{transform:scale(1)}25%{transform:scale(1.18)}45%{transform:scale(.95)}65%{transform:scale(1.1)}}
.env-hint{font-family:'Dancing Script',cursive;font-size:clamp(22px,5vw,30px);text-align:center;text-shadow:0 0 14px var(--glow-color);padding:0 20px}
.env-hint small{display:block;font-family:'Quicksand',sans-serif;font-size:13px;opacity:.6;margin-top:6px}

/* ===== Thẻ nội dung ===== */
.center-wrapper{position:relative;z-index:10;width:100%;max-width:640px;padding:20px;opacity:0;transform:scale(.88) translateY(30px);transition:opacity 1.2s ease,transform 1.2s cubic-bezier(.2,1.2,.4,1)}
body.revealed .center-wrapper{opacity:1;transform:none}
.glass-card{padding:44px 32px 36px;border-radius:34px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.35);box-shadow:0 10px 40px var(--glow-color),inset 0 1px 0 rgba(255,255,255,.3);backdrop-filter:blur(12px) saturate(130%);-webkit-backdrop-filter:blur(12px) saturate(130%);text-align:center;display:flex;flex-direction:column;align-items:center;gap:20px;position:relative}
body.low-fx .glass-card{backdrop-filter:none;background:rgba(43,10,24,.55)}
.glass-card::before,.glass-card::after{content:"🌸";position:absolute;font-size:30px;animation:wiggle 3s ease-in-out infinite}
.glass-card::before{top:-14px;left:-6px}.glass-card::after{content:"🎀";bottom:-12px;right:-4px;animation-delay:-1.5s}
@keyframes wiggle{50%{transform:rotate(14deg) scale(1.12)}}
.avatar-wrap{position:relative;cursor:pointer}
.avatar-ring{width:116px;height:116px;border-radius:50%;padding:4px;background:conic-gradient(var(--primary-color),#fff,var(--secondary-color),var(--primary-color));animation:spin 7s linear infinite;box-shadow:0 0 30px var(--glow-color)}
@keyframes spin{to{transform:rotate(360deg)}}
.avatar-ring img{width:100%;height:100%;border-radius:50%;object-fit:cover;border:3px solid var(--bg-dark);display:block;animation:spin 7s linear infinite reverse}
.avatar-wrap::after{content:"💗";position:absolute;right:-6px;bottom:2px;font-size:28px;animation:beat 1.2s infinite}
.main-message{font-family:'Dancing Script','Playfair Display',cursive;font-size:clamp(28px,6.4vw,50px);font-weight:700;line-height:1.35;min-height:1.4em;text-shadow:0 0 10px var(--glow-color),0 0 26px var(--glow-color);word-break:break-word;white-space:pre-wrap}
.main-message .ch{display:inline-block;animation:chIn .5s cubic-bezier(.3,1.6,.5,1) both}
@keyframes chIn{from{opacity:0;transform:translateY(14px) scale(.4) rotate(-12deg)}}
.main-message.done{animation:glow 3.4s ease-in-out infinite}
body.low-fx .main-message.done{animation:none}
@keyframes glow{50%{text-shadow:0 0 18px var(--glow-color),0 0 40px var(--glow-color)}}
.sub-text,.date-text{opacity:0;transition:opacity 1.4s ease}
.sub-text{font-size:14px;letter-spacing:.5px}.date-text{font-size:12px}
.main-message.done~.sub-text{opacity:.85}.main-message.done~.date-text{opacity:.55}
.hug-btn{border:0;cursor:pointer;font:700 15px 'Quicksand',sans-serif;color:#fff;padding:11px 24px;border-radius:999px;background:linear-gradient(135deg,var(--primary-color),var(--secondary-color));box-shadow:0 6px 20px var(--glow-color);opacity:0;pointer-events:none;transition:opacity 1s,transform .2s}
.main-message.done~.hug-btn{opacity:1;pointer-events:auto}
.hug-btn:active{transform:scale(.92)}
.surprise{position:fixed;inset:0;z-index:70;display:none;flex-direction:column;align-items:center;justify-content:center;gap:10px;background:rgba(43,10,24,.82);text-align:center;padding:24px;cursor:pointer}
.surprise.show{display:flex}
.surprise .big{font-size:clamp(90px,28vw,150px);animation:beat .9s infinite;filter:drop-shadow(0 0 30px var(--glow-color))}
.surprise p{font-family:'Dancing Script',cursive;font-size:clamp(26px,6vw,40px);text-shadow:0 0 16px var(--glow-color)}

/* ===== Nhạc ===== */
.music-bar{position:fixed;left:50%;bottom:22px;transform:translate(-50%,120px);z-index:40;display:flex;align-items:center;gap:12px;padding:10px 18px;min-width:270px;max-width:92vw;border-radius:999px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.35);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);box-shadow:0 6px 24px rgba(0,0,0,.35);transition:transform .9s cubic-bezier(.2,1.3,.4,1) 1.2s}
body.low-fx .music-bar{backdrop-filter:none;background:rgba(43,10,24,.65)}
body.revealed .music-bar{transform:translate(-50%,0)}
.play-btn{width:40px;height:40px;flex-shrink:0;border-radius:50%;border:0;background:var(--primary-color);color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 0 14px var(--glow-color)}
.track-info{flex:1;min-width:0;overflow:hidden}
.track-title{font-size:13px;font-weight:700;white-space:nowrap;display:block;overflow:hidden;text-overflow:ellipsis}
.track-marquee{display:inline-block;animation:mq 9s linear infinite}
@keyframes mq{to{transform:translateX(-50%)}}
.eq-bars{display:flex;align-items:flex-end;gap:2px;height:14px}
.eq-bars span{width:3px;background:var(--accent-color);border-radius:2px;animation:eq .9s ease-in-out infinite}
.eq-bars span:nth-child(2){animation-delay:.15s}.eq-bars span:nth-child(3){animation-delay:.3s}
@keyframes eq{0%,100%{height:4px}50%{height:14px}}
.paused .eq-bars span{animation-play-state:paused}
.volume-wrap{display:flex;align-items:center;gap:6px}
input[type=range]{-webkit-appearance:none;width:64px;height:4px;border-radius:4px;background:rgba(255,255,255,.35)}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:12px;height:12px;border-radius:50%;background:#fff}
.signature-footer{position:fixed;top:8px;right:12px;z-index:30;font-size:11px;opacity:.4}
@media(max-width:480px){.glass-card{padding:36px 20px 30px;border-radius:26px}.avatar-ring{width:92px;height:92px}.music-bar{min-width:0;width:92vw;bottom:12px}.volume-wrap input{width:48px}}
@media(max-height:480px) and (orientation:landscape){.glass-card{padding:18px 24px;gap:8px}.avatar-ring{width:60px;height:60px}.music-bar{bottom:6px}}
@media(prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}
'''

JS_CONTENT = r'''(function(){"use strict";
var B=document.body,C={n:parseInt(B.dataset.heartCount||"20",10),sp:parseFloat(B.dataset.heartSpeed||"8"),yt:B.dataset.youtubeId||"",song:B.dataset.songTitle||"",msg:B.dataset.message||""};
function weak(){try{if(matchMedia("(prefers-reduced-motion: reduce)").matches)return true;var c=navigator.hardwareConcurrency||4,m=navigator.deviceMemory||4,n=navigator.connection;if(c<=4&&m<=4)return true;if(n&&(n.saveData||/2g/.test(n.effectiveType||"")))return true;if(innerWidth<=480&&c<=6)return true}catch(e){}return false}
var LOW=weak();if(LOW)B.classList.add("low-fx");
var MAXH=LOW?9:24,MAXP=LOW?5:14,STARS=LOW?16:46,vis=!document.hidden;
document.addEventListener("visibilitychange",function(){vis=!document.hidden});
var R=function(a,b){return Math.random()*(b-a)+a},P=function(a){return a[Math.floor(Math.random()*a.length)]};
var $=function(id){return document.getElementById(id)};

/* ---- Canvas: sao lấp lánh, sao băng, trái tim thành hình từ các hạt ---- */
var cv=$("fx-canvas"),cx=cv.getContext("2d"),dpr=Math.min(devicePixelRatio||1,1.5),W,H,stars=[],shoot=null,hp=[],hform=0;
function size(){W=innerWidth;H=innerHeight;cv.width=W*dpr;cv.height=H*dpr;cx.setTransform(dpr,0,0,dpr,0,0);buildHeart()}
function buildHeart(){hp=[];var n=LOW?36:72,s=Math.min(W,H)*(W<H?.021:.017),cy=H*(W<H?.2:.5);
 for(var i=0;i<n;i++){var t=i/n*Math.PI*2,x=16*Math.pow(Math.sin(t),3),y=-(13*Math.cos(t)-5*Math.cos(2*t)-2*Math.cos(3*t)-Math.cos(4*t));
  hp.push({tx:W/2+x*s,ty:cy+y*s,x:R(0,W),y:R(0,H),r:R(1.4,2.6),ph:R(0,6.28)})}}
for(var i=0;i<STARS;i++)stars.push({x:R(0,1),y:R(0,1),r:R(.6,1.8),a:R(.2,.9),d:R(.004,.012)*P([1,-1])});
var last=0;function loop(t){requestAnimationFrame(loop);if(!vis||t-last<33)return;last=t;cx.clearRect(0,0,W,H);
 for(var i=0;i<stars.length;i++){var s=stars[i];s.a+=s.d;if(s.a<.15||s.a>.95)s.d*=-1;cx.fillStyle="rgba(255,255,255,"+s.a.toFixed(2)+")";cx.beginPath();cx.arc(s.x*W,s.y*H,s.r,0,6.3);cx.fill()}
 if(hform>0){for(var j=0;j<hp.length;j++){var p=hp[j];p.x+=(p.tx-p.x)*.06;p.y+=(p.ty-p.y)*.06;var tw=.55+.45*Math.sin(t/300+p.ph);cx.fillStyle="rgba(255,214,224,"+tw.toFixed(2)+")";cx.beginPath();cx.arc(p.x,p.y,p.r,0,6.3);cx.fill()}}
 if(!LOW){if(!shoot&&Math.random()<.008)shoot={x:R(.2,1)*W,y:R(0,.4)*H,l:0};
  if(shoot){shoot.x-=11;shoot.y+=5;shoot.l++;var g=cx.createLinearGradient(shoot.x,shoot.y,shoot.x+80,shoot.y-36);g.addColorStop(0,"rgba(255,255,255,.95)");g.addColorStop(1,"rgba(255,255,255,0)");cx.strokeStyle=g;cx.lineWidth=2;cx.beginPath();cx.moveTo(shoot.x,shoot.y);cx.lineTo(shoot.x+80,shoot.y-36);cx.stroke();if(shoot.l>70)shoot=null}}}
size();var rt;addEventListener("resize",function(){clearTimeout(rt);rt=setTimeout(size,200)});requestAnimationFrame(loop);

/* ---- Tim bay, cánh hoa rơi ---- */
var SVG='<svg viewBox="0 0 32 29"><path fill="currentColor" d="M23.6 0c-3 0-5.9 1.6-7.6 4.3C14.3 1.6 11.4 0 8.4 0 3.8 0 0 3.8 0 8.4c0 8.4 12 17.3 15.2 19.6.5.4 1.1.4 1.6 0C20 25.7 32 16.8 32 8.4 32 3.8 28.2 0 23.6 0z"/></svg>',live=0,livep=0;
function heart(){if(live>=MAXH)return;var h=document.createElement("div"),s=R(14,32),d=R(C.sp*.8,C.sp*1.25);h.className="heart";h.style.cssText="left:"+R(0,100)+"vw;width:"+s+"px;height:"+s+"px;--drift:"+R(-50,50)+"px;animation-duration:"+d+"s;color:"+(Math.random()>.45?P(["#ff8fa3","#ffd6e0","#fff","#ff4d6d"]):"var(--primary-color)");h.innerHTML=SVG;$("hearts-container").appendChild(h);live++;setTimeout(function(){h.remove();live--},d*1000+300)}
function petal(){if(livep>=MAXP)return;var e=document.createElement("div"),d=R(7,12);e.className="petal";e.style.cssText="left:"+R(0,100)+"vw;--sway:"+R(-60,60)+"px;animation-duration:"+d+"s;transform:scale("+R(.7,1.3)+")";$("petals").appendChild(e);livep++;setTimeout(function(){e.remove();livep--},d*1000+200)}
function ambient(){for(var i=0;i<Math.min(C.n,LOW?10:30);i++)setTimeout(heart,R(0,3500));
 setInterval(function(){if(vis){heart();if(Math.random()>.5)petal()}},LOW?1000:Math.max(380,6000/Math.max(C.n,1)))}

/* ---- Nổ tim / emoji khi chạm ---- */
var EM=["💖","💗","💕","🌸","✨","💝","🧸","🫶"],lp=0,np=0;
function burst(x,y,n,big){if(np>(LOW?14:40))return;n=LOW?Math.ceil(n/2):n;for(var i=0;i<n;i++){var e=document.createElement("div"),a=R(0,6.28),r=R(40,big?190:90);e.className="pop";e.textContent=P(EM);e.style.cssText="left:"+x+"px;top:"+y+"px;--dx:"+Math.cos(a)*r+"px;--dy:"+(Math.sin(a)*r-30)+"px;--r:"+R(-60,60)+"deg;--s:"+R(14,big?34:24)+"px";document.body.appendChild(e);np++;setTimeout(function(el){el.remove();np--}.bind(null,e),1150)}}
document.addEventListener("pointerdown",function(e){var t=performance.now();if(t-lp<120)return;lp=t;burst(e.clientX,e.clientY,6,false)});
var tl=0;document.addEventListener("pointermove",function(e){if(LOW||e.pointerType==="touch")return;var t=performance.now();if(t-tl<110)return;tl=t;burst(e.clientX,e.clientY,1,false)});

/* ---- Lời nhắn đáng yêu bay lên ---- */
var NOTES=["Nhớ bạn nhiều lắm 🥺","Hôm nay bạn cười chưa? 😊","Cảm ơn vì đã xuất hiện 💗","Ôm một cái nè 🤗","Bạn là điều dễ thương nhất 🧸","Thương bạn nhiều hơn hôm qua 💕","Đừng quên uống nước nha 💧","Có mình ở đây rồi 🫶"];
function note(){if(!vis)return;var n=document.createElement("div");n.className="note";n.textContent=P(NOTES);n.style.left=R(6,Math.max(10,(innerWidth<500?45:70)))+"vw";n.style.top=R(14,innerHeight<500?50:70)+"vh";$("notes").appendChild(n);setTimeout(function(){n.remove()},6600)}

/* ---- Nhạc YouTube ---- */
var yp=null,playing=!1,IP='<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M8 5v14l11-7z"/></svg>',IPA='<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>';
function ui(){var b=$("play-pause-btn");if(b)b.innerHTML=playing?IPA:IP;var m=document.querySelector(".music-bar");if(m)m.classList.toggle("paused",!playing)}
function initYT(){if(!C.yt)return;function mk(){yp=new YT.Player("yt-player",{height:"0",width:"0",videoId:C.yt,playerVars:{controls:0,loop:1,playlist:C.yt,playsinline:1},events:{onReady:function(e){e.target.setVolume(70);if(started)e.target.playVideo()},onStateChange:function(e){playing=e.data===1;ui()}}})}
 if(window.YT&&YT.Player)mk();else{var s=document.createElement("script");s.src="https://www.youtube.com/iframe_api";document.head.appendChild(s);window.onYouTubeIframeAPIReady=mk}}
function music(){var b=$("play-pause-btn"),v=$("volume-slider");ui();if(b)b.onclick=function(){if(!yp)return;playing?yp.pauseVideo():yp.playVideo()};if(v)v.oninput=function(e){yp&&yp.setVolume(+e.target.value)};
 var t=document.querySelector(".track-title");if(t&&C.song){t.textContent=C.song;if(C.song.length>22){t.innerHTML='<span class="track-marquee">'+C.song+" &nbsp;•&nbsp; "+C.song+" &nbsp;•&nbsp; </span>"}}else if(!C.yt){var m=document.querySelector(".music-bar");if(m)m.style.display="none"}}

/* ---- Chữ hiện từng ký tự ---- */
function type(done){var el=$("main-message"),ch=Array.from(C.msg),i=0;el.textContent="";(function step(){if(i>=ch.length){el.classList.add("done");done&&done();return}var s=document.createElement("span");s.className="ch";s.textContent=ch[i]===" "?"\u00a0":ch[i];el.appendChild(s);i++;setTimeout(step,ch[i-1]==="\n"?400:Math.max(40,Math.min(110,2600/ch.length)))})()}

/* ---- Mở phong thư ---- */
var started=false;
function open(){if(started)return;started=true;var env=$("env"),st=$("envelope-stage");env.classList.add("open");
 var r=env.getBoundingClientRect();burst(r.left+r.width/2,r.top+r.height/2,14,true);
 if(yp&&yp.playVideo)yp.playVideo();
 setTimeout(function(){st.classList.add("opened");B.classList.add("revealed");hform=1;ambient();
  type(function(){burst(innerWidth/2,innerHeight*.4,16,true);setInterval(note,LOW?9000:5200);setTimeout(note,800)})},1500)}

/* ---- Bất ngờ cuối: bấm nút ---- */
function bindSurprise(){var b=$("hug-btn"),s=$("surprise");if(!b||!s)return;
 b.onclick=function(e){e.stopPropagation();s.classList.add("show");for(var i=0;i<5;i++)setTimeout(function(){burst(R(.15,.85)*innerWidth,R(.2,.7)*innerHeight,12,true)},i*260)};
 s.onclick=function(){s.classList.remove("show")}}
var av=document.querySelector(".avatar-wrap");if(av)av.addEventListener("click",function(e){burst(e.clientX,e.clientY,12,true)});

function init(){music();initYT();bindSurprise();var s=$("envelope-stage");s.addEventListener("click",open)}
document.readyState==="loading"?document.addEventListener("DOMContentLoaded",init):init();
})();
'''

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
<meta name="theme-color" content="{{ primary_color }}" />
<title>{{ title }}</title>
<meta name="description" content="{{ message }}" />
<meta property="og:title" content="{{ title }}" />
<meta property="og:description" content="{{ message }}" />
<meta property="og:type" content="website" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600;700&family=Quicksand:wght@500;700&display=swap" rel="stylesheet" />
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>%E2%9D%A4%EF%B8%8F</text></svg>" />
<style>
{{ css_content|safe }}
:root{--primary-color:{{ primary_color }};--secondary-color:{{ secondary_color }};--accent-color:{{ accent_color }};--glow-color:{{ glow_color }};--heart-speed:{{ heart_speed }}s}
{% if bg_image_data %}body{background-image:url('{{ bg_image_data }}')}{% endif %}
</style>
</head>
<body class="{% if bg_image_data %}has-bg-image{% endif %}" data-heart-count="{{ heart_count }}" data-heart-speed="{{ heart_speed }}" data-youtube-id="{{ youtube_id }}" data-song-title="{{ song_title }}" data-message="{{ message }}">
<div class="bg-overlay"></div>
<div class="aurora-light"></div>
<canvas id="fx-canvas"></canvas>
<div id="hearts-container"></div>
<div id="petals"></div>
<div id="notes"></div>

<!-- Phong thư: chạm để mở (cũng là lần chạm cho phép phát nhạc) -->
<div class="envelope-stage" id="envelope-stage">
  <div class="env" id="env">
    <div class="env-back"></div>
    <div class="env-letter">💌</div>
    <div class="env-front"></div>
    <div class="env-flap"></div>
    <div class="seal">❤️</div>
  </div>
  <div class="env-hint">Có một điều bất ngờ dành cho bạn<small>Chạm vào phong thư để mở</small></div>
</div>

<div class="center-wrapper">
  <div class="glass-card">
    {% if avatar_data %}<div class="avatar-wrap"><div class="avatar-ring"><img src="{{ avatar_data }}" alt="avatar" /></div></div>{% endif %}
    <div class="main-message" id="main-message"></div>
    <div class="sub-text">Được gửi bằng tất cả yêu thương</div>
    {% if generated_date %}<div class="date-text">{{ generated_date }}</div>{% endif %}
    <button class="hug-btn" id="hug-btn" type="button">Bấm vào đây nhé 🎁</button>
  </div>
</div>

<div class="surprise" id="surprise">
  <div class="big">🧸</div>
  <p>Gửi bạn một cái ôm thật chặt!</p>
  <p style="font-size:16px;opacity:.7;font-family:Quicksand,sans-serif">Chạm để đóng</p>
</div>

{% if youtube_id %}
<div class="music-bar paused">
  <button id="play-pause-btn" class="play-btn" aria-label="Phát / tạm dừng"></button>
  <div class="track-info"><span class="track-title">{{ song_title }}</span></div>
  <div class="eq-bars"><span></span><span></span><span></span></div>
  <div class="volume-wrap">
    <svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M3 10v4h4l5 5V5L7 10H3zm13.5 2c0-1.77-.77-3.29-2-4.2v8.4c1.23-.91 2-2.43 2-4.2z"/></svg>
    <input type="range" id="volume-slider" min="0" max="100" value="70" aria-label="Âm lượng" />
  </div>
</div>
<div id="yt-player" style="position:fixed;bottom:-200px;left:-200px;width:1px;height:1px;opacity:0"></div>
{% endif %}

<div class="signature-footer">💌 made with Love Page Generator</div>
<script>
{{ js_content|safe }}
</script>
</body>
</html>
'''

# ============================ 2. ĐƯỜNG DẪN ============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(BASE_DIR, "static", "pages")
INDEX_JSON_PATH = os.path.join(PAGES_DIR, "_index.json")
os.makedirs(PAGES_DIR, exist_ok=True)
MAX_IMAGE_DIMENSION, MAX_AVATAR_DIMENSION, JPEG_QUALITY = 1600, 500, 82
PAGE_ID_RE = re.compile(r"^[a-f0-9]{8}$")


# ============================ 3. MÀU SẮC ============================
def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*[max(0, min(255, int(c))) for c in rgb])


def adjust_color(h, amount):
    return rgb_to_hex([c + amount if amount >= 0 else c * (1 + amount / 255) for c in hex_to_rgb(h)])


def hex_to_rgba_string(h, a):
    r, g, b = hex_to_rgb(h)
    return f"rgba({r}, {g}, {b}, {a})"


# ============================ 4. YOUTUBE ============================
YT_RE = re.compile(r"(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([A-Za-z0-9_-]{11})")


def search_youtube_by_song_name(name):
    if not name or not name.strip():
        return None, None
    opts = {"quiet": True, "no_warnings": True, "skip_download": True, "noplaylist": True,
            "default_search": "ytsearch1", "extract_flat": "in_playlist", "socket_timeout": 12}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            res = ydl.extract_info(name, download=False)
            if res and res.get("entries"):
                e = res["entries"][0]
                return e.get("id"), e.get("title", name)
            if res and res.get("id"):
                return res["id"], res.get("title", name)
    except Exception as exc:  # noqa: BLE001
        st.session_state["last_youtube_error"] = str(exc)
    return None, None


def resolve_youtube_id(song_name, youtube_link):
    m = YT_RE.search(youtube_link or "")
    if m:
        return m.group(1), (song_name.strip() if song_name else "Nhạc nền")
    if song_name and song_name.strip():
        vid, title = search_youtube_by_song_name(song_name.strip())
        return vid, (title or song_name.strip())
    return None, ""


# ============================ 5. ẢNH UPLOAD ============================
def uploaded_image_to_data_uri(f, max_dim):
    if f is None:
        return ""
    try:
        from PIL import Image
        img = Image.open(f)
        if img.mode in ("RGBA", "P"):
            rgba = img.convert("RGBA")
            bg = Image.new("RGB", rgba.size, (255, 255, 255))
            bg.paste(rgba, mask=rgba.split()[-1])
            img = bg
        else:
            img = img.convert("RGB")
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception as exc:  # noqa: BLE001
        st.warning(f"⚠️ Không thể xử lý ảnh đã upload: {exc}")
        return ""


# ============================ 6. RENDER HTML ============================
def render_love_page(message, primary_color, bg_image_data, avatar_data,
                     youtube_id, song_title, heart_count, heart_speed):
    env = Environment(autoescape=True)  # BẬT autoescape: chống XSS từ message/song_title
    return env.from_string(HTML_TEMPLATE).render(
        title="Gửi bạn một điều bất ngờ 💌",
        message=message,
        primary_color=primary_color,
        secondary_color=adjust_color(primary_color, 40),
        accent_color=adjust_color(primary_color, 90),
        glow_color=hex_to_rgba_string(primary_color, 0.75),
        bg_image_data=bg_image_data, avatar_data=avatar_data,
        youtube_id=youtube_id or "", song_title=song_title or "",
        heart_count=heart_count, heart_speed=heart_speed,
        generated_date=datetime.now().strftime("%d/%m/%Y"),
        css_content=CSS_CONTENT, js_content=JS_CONTENT,
    )


# ============================ 7. LƯU TRANG + INDEX ============================
def load_index():
    try:
        with open(INDEX_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return []


def save_generated_page(html):
    page_id = uuid.uuid4().hex[:8]
    with open(os.path.join(PAGES_DIR, f"{page_id}.html"), "w", encoding="utf-8") as f:
        f.write(html)
    idx = load_index()
    idx.append({"id": page_id, "created_at": datetime.now().isoformat(timespec="seconds")})
    with open(INDEX_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)
    return page_id


# ============================ 8. LINK CHIA SẺ + QR ============================
def get_base_url():
    try:
        u = st.secrets.get("PUBLIC_BASE_URL", "")
        if u:
            return u.rstrip("/")
    except Exception:  # noqa: BLE001
        pass
    u = os.environ.get("PUBLIC_BASE_URL", "")
    if u:
        return u.rstrip("/")
    try:
        h = st.context.headers
        host = h.get("Host") or h.get("host")
    except Exception:  # noqa: BLE001
        host = None
    if host:
        https = any(k in host for k in ("streamlit.app", "onrender.com", "herokuapp.com")) or os.environ.get("RENDER")
        return f"{'https' if https else 'http'}://{host}"
    return "http://localhost:8501"


def build_share_url(page_id):
    return f"{get_base_url()}/?page={page_id}"


def generate_qr_code_bytes(url):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=3)
    qr.add_data(url)
    qr.make(fit=True)
    buf = io.BytesIO()
    qr.make_image(fill_color="#ff4d6d", back_color="white").save(buf, format="PNG")
    return buf.getvalue()


# ============================ 9. VIEWER ?page=<id> ============================
def render_page_viewer(page_id):
    path = os.path.join(PAGES_DIR, f"{page_id}.html")
    if not PAGE_ID_RE.match(page_id or "") or not os.path.exists(path):
        st.error("💔 Không tìm thấy trang này. Link có thể đã sai hoặc trang đã bị xoá.")
        st.stop()
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    st.markdown(
        """<style>
        #MainMenu,footer{visibility:hidden}
        header[data-testid="stHeader"]{display:none}
        .block-container{padding:0!important;margin:0!important;max-width:100%!important}
        iframe{display:block;border:0;width:100vw;height:100vh!important;position:fixed;inset:0}
        </style>""",
        unsafe_allow_html=True,
    )
    components.html(html, height=900, scrolling=False)


# ============================ 10. GIAO DIỆN STREAMLIT ============================
def render_sidebar():
    with st.sidebar:
        st.markdown("<div style='text-align:center;font-size:52px;'>❤️</div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;margin-top:-10px;'>Love Page Generator</h2>", unsafe_allow_html=True)
        st.caption("Tạo trang tình yêu bất ngờ trong vài giây 💌")
        st.divider()
        song_name = st.text_input("🎵 Tên bài hát", placeholder="Ví dụ: Perfect - Ed Sheeran")
        youtube_link = st.text_input("🔗 Link YouTube (nếu có)", placeholder="https://www.youtube.com/watch?v=...")
        message = st.text_area("💬 Dòng chữ muốn hiện", value="Anh yêu em ❤️", height=90,
                               max_chars=200, help="Có thể xuống dòng. Chữ sẽ hiện từng ký tự rất dễ thương.")
        bg_image_file = st.file_uploader("🖼️ Ảnh nền (không bắt buộc)", type=["jpg", "jpeg", "png", "webp"])
        avatar_file = st.file_uploader("🙂 Avatar (không bắt buộc)", type=["jpg", "jpeg", "png", "webp"])
        primary_color = st.color_picker("🎨 Màu chủ đạo", value="#ff4d6d")
        heart_speed = st.slider("💨 Tốc độ trái tim (giây/vòng bay)", 3, 15, 8)
        heart_count = st.slider("💗 Số lượng trái tim", 10, 60, 20, step=5,
                                help="Trang tự giảm hiệu ứng trên máy yếu.")
        st.divider()
        submitted = st.button("❤️ Tạo trang", use_container_width=True, type="primary")
    return dict(song_name=song_name, youtube_link=youtube_link, message=message,
                bg_image_file=bg_image_file, avatar_file=avatar_file, primary_color=primary_color,
                heart_speed=heart_speed, heart_count=heart_count, submitted=submitted)


def handle_generation(inp):
    if not inp["message"] or not inp["message"].strip():
        st.error("⚠️ Vui lòng nhập dòng chữ muốn hiển thị trước khi tạo trang.")
        return
    bar = st.progress(0, text="🚀 Bắt đầu tạo trang...")
    try:
        bar.progress(15, text="🎵 Đang tìm bài hát trên YouTube...")
        yt_id, song_title = resolve_youtube_id(inp["song_name"], inp["youtube_link"])
        if inp["song_name"] and not yt_id and not inp["youtube_link"]:
            st.warning("⚠️ Không tìm thấy bài hát trên YouTube, trang sẽ được tạo mà không có nhạc nền.")
        bar.progress(40, text="🖼️ Đang xử lý hình ảnh...")
        bg = uploaded_image_to_data_uri(inp["bg_image_file"], MAX_IMAGE_DIMENSION)
        av = uploaded_image_to_data_uri(inp["avatar_file"], MAX_AVATAR_DIMENSION)
        bar.progress(65, text="🧩 Đang dựng trang tình yêu...")
        html = render_love_page(inp["message"].strip(), inp["primary_color"], bg, av,
                                yt_id or "", song_title, inp["heart_count"], inp["heart_speed"])
        bar.progress(85, text="💾 Đang lưu trang...")
        page_id = save_generated_page(html)
        url = build_share_url(page_id)
        bar.progress(97, text="📱 Đang tạo mã QR...")
        qr = generate_qr_code_bytes(url)
        bar.progress(100, text="✅ Hoàn tất!")
        result = {"page_id": page_id, "share_url": url, "qr_bytes": qr, "has_music": bool(yt_id),
                  "created_at": datetime.now().strftime("%H:%M:%S %d/%m/%Y")}
        st.session_state["last_result"] = result
    except Exception as exc:  # noqa: BLE001
        bar.empty()
        st.error("❌ Đã có lỗi xảy ra trong quá trình tạo trang.")
        st.exception(exc)


def render_copy_button(url):
    components.html(f"""
    <div style="display:flex;gap:8px;align-items:center;font-family:sans-serif">
      <button id="b" style="background:#ff4d6d;color:#fff;border:0;padding:8px 16px;border-radius:8px;cursor:pointer;font-weight:600">📋 Copy Link</button>
      <span id="s" style="font-size:13px;color:#888"></span></div>
    <script>
      b.onclick=async()=>{{try{{await navigator.clipboard.writeText({json.dumps(url)});s.textContent="Đã sao chép ✔"}}
      catch(e){{s.textContent="Hãy copy thủ công."}}setTimeout(()=>s.textContent="",2000)}}
    </script>""", height=45)


def render_result_section():
    r = st.session_state.get("last_result")
    if not r:
        return
    st.success("✅ Thành công! Trang tình yêu của bạn đã sẵn sàng.")
    st.markdown("#### 🔗 Link chia sẻ")
    st.code(r["share_url"], language="text")
    render_copy_button(r["share_url"])
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📱 Mã QR")
        st.image(r["qr_bytes"], width=200)
        st.download_button("⬇️ Tải mã QR", r["qr_bytes"], f"qr_{r['page_id']}.png", "image/png", use_container_width=True)
    with c2:
        st.markdown("#### ℹ️ Thông tin")
        st.write(f"**Mã trang:** `{r['page_id']}`")
        st.write(f"**Tạo lúc:** {r['created_at']}")
        st.write(f"**Có nhạc nền:** {'Có 🎵' if r['has_music'] else 'Không'}")
    with st.expander("👀 Xem trước (chạm phong thư để mở)"):
        p = os.path.join(PAGES_DIR, f"{r['page_id']}.html")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                components.html(f.read(), height=650, scrolling=False)


def render_history_tab():
    entries = load_index()
    if not entries:
        st.info("Chưa có trang nào được tạo. Hãy sang tab 'Tạo trang' để bắt đầu!")
        return
    base = get_base_url()
    st.metric("Tổng số trang đã tạo", len(entries))
    st.divider()
    for e in reversed(entries):
        pid = e.get("id", "")
        url = f"{base}/?page={pid}"
        with st.container(border=True):
            a, b = st.columns([3, 1])
            with a:
                st.write(f"**Mã trang:** `{pid}`")
                st.write(f"🕒 Tạo lúc: {e.get('created_at', '')}")
                st.write(f"🔗 [{url}]({url})")
            with b:
                ok = os.path.exists(os.path.join(PAGES_DIR, f"{pid}.html"))
                st.write("✅ Còn tồn tại" if ok else "❌ Đã bị xoá")


def render_intro():
    st.title("💕 Love Page Generator")
    st.write("Nhập thông tin ở thanh bên trái rồi bấm **❤️ Tạo trang**. Người nhận sẽ thấy một "
             "**phong thư bí mật**; chạm vào là nhạc vang lên, chữ hiện từng nét, sao lấp lánh, "
             "tim ghép thành hình và một món quà bất ngờ ở cuối 🎁")
    st.info("💡 Nhập tên bài hát để tự tìm trên YouTube, hoặc dán thẳng link nếu đã có.")


# ============================ 11. MAIN ============================
def main():
    page_id = st.query_params.get("page")
    if page_id:
        st.set_page_config(page_title="💌 Gửi bạn một điều bất ngờ", page_icon="❤️",
                           layout="wide", initial_sidebar_state="collapsed")
        render_page_viewer(page_id)
        return
    st.set_page_config(page_title="Love Page Generator", page_icon="❤️",
                       layout="centered", initial_sidebar_state="expanded")
    tab_create, tab_stats = st.tabs(["💌 Tạo trang", "📊 Thống kê"])
    with tab_create:
        render_intro()
        inp = render_sidebar()
        if inp["submitted"]:
            handle_generation(inp)
        render_result_section()
    with tab_stats:
        render_history_tab()
    st.divider()
    st.caption("Made with ❤️ using Streamlit · Jinja2 · yt-dlp · qrcode · Pillow")


if __name__ == "__main__":
    main()
