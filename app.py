"""
==============================================================================
LOVE PAGE GENERATOR  —  PHIÊN BẢN GỘP 1 FILE DUY NHẤT (app.py)
------------------------------------------------------------------------------
Toàn bộ CSS, JavaScript và template HTML của "trang tình yêu" được nhúng
thẳng vào file Python này dưới dạng chuỗi. Chỉ cần duy nhất file app.py 
này + requirements.txt là chạy được.

Cách chạy:
    pip install streamlit yt-dlp jinja2 qrcode
    streamlit run app.py
==============================================================================
"""

import json
import os
import re
import uuid
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Environment, select_autoescape
import yt_dlp

# ==============================================================================
# 1. TÀI NGUYÊN NHÚNG SẴN: CSS + JAVASCRIPT + TEMPLATE HTML
# ==============================================================================

CSS_CONTENT = r"""/* ==========================================================================
   LOVE PAGE GENERATOR - MAIN STYLESHEET
   ========================================================================== */

:root {
    --primary-color: #ff4d6d;
    --secondary-color: #ff8fa3;
    --accent-color: #ffd6e0;
    --glow-color: rgba(255, 77, 109, 0.75);
    --bg-dark: #2b0a18;
    --glass-bg: rgba(255, 255, 255, 0.12);
    --glass-border: rgba(255, 255, 255, 0.35);
    --text-light: #fffafc;
    --shadow-color: rgba(255, 77, 109, 0.45);
    --heart-speed: 8s;
    --transition-smooth: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
}

html, body {
    width: 100%;
    height: 100%;
    overflow-x: hidden;
    font-family: 'Poppins', 'Be Vietnam Pro', sans-serif;
    background-color: var(--bg-dark);
    color: var(--text-light);
    scroll-behavior: smooth;
}

body {
    position: relative;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: radial-gradient(circle at 50% 20%, var(--secondary-color) 0%, var(--bg-dark) 75%);
    overflow: hidden;
}

body.has-bg-image {
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.bg-overlay {
    position: fixed;
    inset: 0;
    z-index: 0;
    backdrop-filter: blur(6px) saturate(130%);
    -webkit-backdrop-filter: blur(6px) saturate(130%);
    background: linear-gradient(
        135deg,
        rgba(255, 77, 109, 0.55) 0%,
        rgba(43, 10, 24, 0.75) 60%,
        rgba(255, 143, 163, 0.55) 100%
    );
    pointer-events: none;
}

.aurora-light {
    position: fixed;
    inset: -20%;
    z-index: 0;
    background:
        radial-gradient(circle at 20% 30%, var(--glow-color) 0%, transparent 35%),
        radial-gradient(circle at 80% 70%, var(--accent-color) 0%, transparent 40%),
        radial-gradient(circle at 50% 90%, var(--secondary-color) 0%, transparent 45%);
    filter: blur(60px);
    opacity: 0.55;
    animation: auroraMove 18s ease-in-out infinite alternate;
    pointer-events: none;
}

@keyframes auroraMove {
    0%   { transform: translate(0, 0) scale(1); }
    50%  { transform: translate(-4%, 3%) scale(1.1); }
    100% { transform: translate(4%, -3%) scale(1.05); }
}

#particle-canvas {
    position: fixed;
    inset: 0;
    z-index: 1;
    pointer-events: none;
}

#hearts-container {
    position: fixed;
    inset: 0;
    z-index: 2;
    overflow: hidden;
    pointer-events: none;
}

.heart {
    position: absolute;
    bottom: -60px;
    color: var(--primary-color);
    opacity: 0.85;
    will-change: transform, opacity;
    animation-name: floatUp;
    animation-timing-function: ease-in;
    animation-iteration-count: 1;
    filter: drop-shadow(0 0 6px var(--glow-color));
}

.heart svg {
    width: 100%;
    height: 100%;
    display: block;
}

@keyframes floatUp {
    0% { transform: translateY(0) translateX(0) rotate(0deg) scale(0.6); opacity: 0; }
    10% { opacity: 1; }
    50% { transform: translateY(-50vh) translateX(var(--drift, 30px)) rotate(180deg) scale(1); }
    100% { transform: translateY(-110vh) translateX(calc(var(--drift, 30px) * -1)) rotate(360deg) scale(0.5); opacity: 0; }
}

.sparkle {
    position: fixed;
    z-index: 5;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: radial-gradient(circle, #fff 0%, var(--primary-color) 60%, transparent 100%);
    pointer-events: none;
    animation: sparklePop 0.9s ease-out forwards;
}

@keyframes sparklePop {
    0% { transform: scale(0) translate(0, 0); opacity: 1; }
    100% { transform: scale(1.6) translate(var(--sx, 20px), var(--sy, -20px)); opacity: 0; }
}

.tap-overlay {
    position: fixed;
    inset: 0;
    z-index: 50;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 18px;
    background: rgba(43, 10, 24, 0.92);
    backdrop-filter: blur(10px);
    cursor: pointer;
    text-align: center;
    padding: 20px;
    transition: opacity 0.6s ease, visibility 0.6s ease;
}

.tap-overlay.hidden {
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
}

.tap-overlay .pulse-heart {
    font-size: 64px;
    animation: pulseBeat 1.1s ease-in-out infinite;
}

.tap-overlay p {
    font-size: 18px;
    letter-spacing: 0.5px;
    color: var(--text-light);
    opacity: 0.9;
}

.tap-overlay span.small {
    font-size: 13px;
    opacity: 0.6;
}

@keyframes pulseBeat {
    0%, 100% { transform: scale(1); }
    25% { transform: scale(1.25); }
    40% { transform: scale(0.95); }
    60% { transform: scale(1.15); }
}

.center-wrapper {
    position: relative;
    z-index: 10;
    width: 100%;
    max-width: 640px;
    padding: 24px;
    display: flex;
    justify-content: center;
}

.glass-card {
    width: 100%;
    padding: 48px 36px;
    border-radius: 32px;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    box-shadow:
        0 8px 32px var(--shadow-color),
        inset 0 1px 0 rgba(255, 255, 255, 0.25);
    backdrop-filter: blur(18px) saturate(150%);
    -webkit-backdrop-filter: blur(18px) saturate(150%);
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 22px;
    animation: cardEntrance 1.2s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes cardEntrance {
    0% { opacity: 0; transform: translateY(40px) scale(0.92); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}

.avatar-ring {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    padding: 4px;
    background: conic-gradient(var(--primary-color), var(--accent-color), var(--secondary-color), var(--primary-color));
    animation: ringSpin 6s linear infinite;
    box-shadow: 0 0 30px var(--glow-color);
}

@keyframes ringSpin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.avatar-ring img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid var(--bg-dark);
    display: block;
}

.main-message {
    font-family: 'Dancing Script', 'Playfair Display', cursive, serif;
    font-size: clamp(28px, 6vw, 52px);
    font-weight: 700;
    line-height: 1.3;
    color: var(--text-light);
    text-shadow:
        0 0 10px var(--glow-color),
        0 0 24px var(--glow-color),
        0 0 46px var(--shadow-color);
    animation:
        messageFadeScale 1.4s ease-out both,
        glowPulse 2.6s ease-in-out infinite 1.4s;
    min-height: 60px; /* Tránh giật form khi gõ chữ */
}

/* Thêm nháy con trỏ gõ chữ */
.main-message::after {
    content: '|';
    animation: blink 1s step-end infinite;
}
.main-message.typing-done::after {
    display: none;
}

@keyframes blink {
    50% { opacity: 0; }
}

@keyframes messageFadeScale {
    0% { opacity: 0; transform: scale(0.7); filter: blur(6px); }
    60% { opacity: 1; transform: scale(1.05); filter: blur(0); }
    100% { opacity: 1; transform: scale(1); }
}

@keyframes glowPulse {
    0%, 100% { text-shadow: 0 0 10px var(--glow-color), 0 0 24px var(--glow-color), 0 0 46px var(--shadow-color); }
    50% { text-shadow: 0 0 18px var(--glow-color), 0 0 40px var(--glow-color), 0 0 70px var(--shadow-color); }
}

.sub-text {
    font-size: 15px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    opacity: 0.75;
    animation: fadeIn 1.8s ease-out 0.6s both;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 0.75; transform: translateY(0); }
}

.date-text {
    font-size: 13px;
    opacity: 0.55;
    letter-spacing: 0.5px;
    animation: fadeIn 1.8s ease-out 0.9s both;
}

.music-bar {
    position: fixed;
    left: 50%;
    bottom: 24px;
    transform: translateX(-50%);
    z-index: 40;
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 20px;
    min-width: 280px;
    max-width: 92vw;
    border-radius: 999px;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(16px) saturate(150%);
    -webkit-backdrop-filter: blur(16px) saturate(150%);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.35);
}

.music-bar button.play-btn {
    width: 42px;
    height: 42px;
    flex-shrink: 0;
    border-radius: 50%;
    border: none;
    background: var(--primary-color);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 0 14px var(--glow-color);
    transition: var(--transition-smooth);
}

.music-bar button.play-btn:hover { transform: scale(1.08); }
.music-bar button.play-btn:active { transform: scale(0.94); }

.music-bar .track-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.music-bar .track-title {
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.music-bar .track-marquee { display: inline-block; white-space: nowrap; }
.music-bar .track-marquee.animate { animation: marquee 9s linear infinite; }

@keyframes marquee {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

.music-bar .eq-bars {
    display: flex;
    align-items: flex-end;
    gap: 2px;
    height: 14px;
}

.music-bar .eq-bars span {
    width: 3px;
    background: var(--primary-color);
    border-radius: 2px;
    animation: eqBounce 0.9s ease-in-out infinite;
}

.music-bar .eq-bars span:nth-child(2) { animation-delay: 0.15s; }
.music-bar .eq-bars span:nth-child(3) { animation-delay: 0.3s; }

@keyframes eqBounce {
    0%, 100% { height: 4px; }
    50% { height: 14px; }
}

.music-bar .volume-wrap {
    display: flex;
    align-items: center;
    gap: 6px;
}

.music-bar input[type="range"] {
    -webkit-appearance: none;
    width: 70px;
    height: 4px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.35);
    outline: none;
}

.music-bar input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--text-light);
    cursor: pointer;
    box-shadow: 0 0 6px var(--glow-color);
}

.signature-footer {
    position: fixed;
    bottom: 6px;
    right: 12px;
    z-index: 30;
    font-size: 11px;
    opacity: 0.45;
    letter-spacing: 0.5px;
}

@media (max-width: 480px) {
    .glass-card { padding: 34px 20px; border-radius: 24px; gap: 16px; }
    .avatar-ring { width: 90px; height: 90px; }
    .main-message { font-size: clamp(24px, 8vw, 36px); }
    .music-bar { min-width: unset; width: 90vw; padding: 10px 16px; bottom: 14px; }
    .tap-overlay .pulse-heart { font-size: 48px; }
}

@media (min-width: 481px) and (max-width: 900px) {
    .glass-card { padding: 42px 30px; }
    .avatar-ring { width: 105px; height: 105px; }
}

@media (min-width: 1400px) {
    .center-wrapper { max-width: 760px; }
    .main-message { font-size: clamp(36px, 5vw, 64px); }
}

@media (max-height: 480px) and (orientation: landscape) {
    .glass-card { padding: 20px 26px; gap: 10px; }
    .avatar-ring { width: 64px; height: 64px; }
    .music-bar { bottom: 8px; }
}

@media (prefers-reduced-motion: reduce) {
    * { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }
}

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--primary-color); border-radius: 8px; }
"""

JS_CONTENT = r"""
(function () {
    "use strict";

    var body = document.body;
    var CONFIG = {
        heartCount: parseInt(body.getAttribute("data-heart-count") || "25", 10),
        heartSpeed: parseFloat(body.getAttribute("data-heart-speed") || "8"),
        youtubeId: body.getAttribute("data-youtube-id") || "",
        songTitle: body.getAttribute("data-song-title") || "",
        primaryColor: body.getAttribute("data-primary-color") || "#ff4d6d",
        message: body.getAttribute("data-message") || ""
    };

    function rand(min, max) { return Math.random() * (max - min) + min; }
    function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

    function ParticleEngine(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext("2d");
        this.particles = [];
        this.count = 70;
        this.resize();
        this.init();
        window.addEventListener("resize", this.resize.bind(this));
        this.loop = this.loop.bind(this);
        requestAnimationFrame(this.loop);
    }

    ParticleEngine.prototype.resize = function () {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    };

    ParticleEngine.prototype.init = function () {
        this.particles = [];
        for (var i = 0; i < this.count; i++) {
            this.particles.push({
                x: rand(0, window.innerWidth),
                y: rand(0, window.innerHeight),
                r: rand(0.6, 2.6),
                vx: rand(-0.15, 0.15),
                vy: rand(-0.25, -0.05),
                alpha: rand(0.15, 0.85),
                twinkleSpeed: rand(0.005, 0.02),
                twinkleDir: pick([1, -1])
            });
        }
    };

    ParticleEngine.prototype.loop = function () {
        if (!this.ctx) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        for (var i = 0; i < this.particles.length; i++) {
            var p = this.particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.alpha += p.twinkleSpeed * p.twinkleDir;

            if (p.alpha <= 0.1 || p.alpha >= 0.95) { p.twinkleDir *= -1; }
            if (p.y < -10) {
                p.y = window.innerHeight + 10;
                p.x = rand(0, window.innerWidth);
            }
            if (p.x < -10) p.x = window.innerWidth + 10;
            if (p.x > window.innerWidth + 10) p.x = -10;

            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            this.ctx.fillStyle = "rgba(255,255,255," + p.alpha.toFixed(2) + ")";
            this.ctx.shadowBlur = 6;
            this.ctx.shadowColor = CONFIG.primaryColor;
            this.ctx.fill();
        }
        requestAnimationFrame(this.loop);
    };

    var HEART_SVG =
        '<svg viewBox="0 0 32 29" xmlns="http://www.w3.org/2000/svg">' +
        '<path fill="currentColor" d="M23.6 0c-3 0-5.9 1.6-7.6 4.3C14.3 1.6 11.4 0 8.4 0 3.8 0 0 3.8 0 8.4c0 8.4 12 17.3 15.2 19.6.5.4 1.1.4 1.6 0C20 25.7 32 16.8 32 8.4 32 3.8 28.2 0 23.6 0z"/>' +
        "</svg>";

    function createHeart(container) {
        var heart = document.createElement("div");
        heart.className = "heart";
        var size = rand(14, 34);
        var left = rand(0, 100);
        var drift = rand(-60, 60);
        var duration = rand(CONFIG.heartSpeed * 0.7, CONFIG.heartSpeed * 1.3);
        var delay = rand(0, 2);

        heart.style.left = left + "vw";
        heart.style.width = size + "px";
        heart.style.height = size + "px";
        heart.style.setProperty("--drift", drift + "px");
        heart.style.animationDuration = duration + "s";
        heart.style.animationDelay = delay + "s";
        heart.innerHTML = HEART_SVG;

        if (Math.random() > 0.6) {
            heart.style.color = pick(["#ff8fa3", "#ffd6e0", "#ff4d6d", "#ffffff"]);
        }

        container.appendChild(heart);

        window.setTimeout(function () {
            if (heart.parentNode) heart.parentNode.removeChild(heart);
        }, (duration + delay) * 1000 + 500);
    }

    function startFloatingHearts() {
        var container = document.getElementById("hearts-container");
        if (!container) return;
        for (var i = 0; i < CONFIG.heartCount; i++) {
            window.setTimeout(function () { createHeart(container); }, rand(0, 4000));
        }
        var intervalMs = Math.max(250, 6000 / Math.max(CONFIG.heartCount, 1));
        window.setInterval(function () { createHeart(container); }, intervalMs);
    }

    function spawnSparkle(x, y) {
        var s = document.createElement("div");
        s.className = "sparkle";
        s.style.left = x + "px";
        s.style.top = y + "px";
        s.style.setProperty("--sx", rand(-30, 30) + "px");
        s.style.setProperty("--sy", rand(-40, -10) + "px");
        document.body.appendChild(s);
        window.setTimeout(function () {
            if (s.parentNode) s.parentNode.removeChild(s);
        }, 950);
    }

    function bindSparkleEvents() {
        document.addEventListener("click", function (e) {
            for (var i = 0; i < 3; i++) {
                spawnSparkle(e.clientX + rand(-8, 8), e.clientY + rand(-8, 8));
            }
        });
        document.addEventListener("touchstart", function (e) {
            var t = e.touches[0];
            if (!t) return;
            for (var i = 0; i < 3; i++) {
                spawnSparkle(t.clientX + rand(-8, 8), t.clientY + rand(-8, 8));
            }
        }, { passive: true });
    }

    function typewriterEffect(el, text, speed) {
        if (!el || !text) return;
        el.textContent = "";
        var i = 0;
        function typeNext() {
            if (i <= text.length) {
                el.textContent = text.slice(0, i);
                i++;
                window.setTimeout(typeNext, speed);
            } else {
                el.classList.add("typing-done");
            }
        }
        typeNext();
    }

    var ytPlayer = null;
    var isPlaying = false;

    function loadYouTubeAPI(callback) {
        if (window.YT && window.YT.Player) {
            callback();
            return;
        }
        var tag = document.createElement("script");
        tag.src = "https://www.youtube.com/iframe_api";
        document.head.appendChild(tag);
        window.onYouTubeIframeAPIReady = callback;
    }

    function initYouTubePlayer() {
        if (!CONFIG.youtubeId) return;
        loadYouTubeAPI(function () {
            ytPlayer = new YT.Player("yt-player", {
                height: "0",
                width: "0",
                videoId: CONFIG.youtubeId,
                playerVars: { autoplay: 1, controls: 0, loop: 1, playlist: CONFIG.youtubeId, playsinline: 1 },
                events: {
                    onReady: function (e) {
                        e.target.setVolume(70);
                        tryAutoPlay(e.target);
                    },
                    onStateChange: function (e) {
                        isPlaying = e.data === YT.PlayerState.PLAYING;
                        updatePlayButton();
                    }
                }
            });
        });
    }

    function tryAutoPlay(player) {
        try { player.playVideo(); } catch (err) { console.warn("Autoplay bị chặn:", err); }
    }

    function updatePlayButton() {
        var btn = document.getElementById("play-pause-btn");
        if (!btn) return;
        btn.innerHTML = isPlaying ? ICON_PAUSE : ICON_PLAY;
    }

    var ICON_PLAY = '<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M8 5v14l11-7z"/></svg>';
    var ICON_PAUSE = '<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>';

    function bindMusicControls() {
        var playBtn = document.getElementById("play-pause-btn");
        var volumeSlider = document.getElementById("volume-slider");

        if (playBtn) {
            playBtn.innerHTML = ICON_PLAY;
            playBtn.addEventListener("click", function () {
                if (!ytPlayer) return;
                if (isPlaying) { ytPlayer.pauseVideo(); } else { ytPlayer.playVideo(); }
            });
        }
        if (volumeSlider) {
            volumeSlider.addEventListener("input", function (e) {
                if (ytPlayer && ytPlayer.setVolume) { ytPlayer.setVolume(parseInt(e.target.value, 10)); }
            });
        }
    }

    function bindTapOverlay() {
        var overlay = document.getElementById("tap-overlay");
        if (!overlay) return;

        function dismiss() {
            overlay.classList.add("hidden");
            if (ytPlayer && ytPlayer.playVideo) { ytPlayer.playVideo(); }
            document.removeEventListener("click", dismiss);
            document.removeEventListener("touchstart", dismiss);
        }
        overlay.addEventListener("click", dismiss);
        window.setTimeout(function () {
            if (isPlaying) { overlay.classList.add("hidden"); }
        }, 1200);
    }

    function setupMarquee() {
        var title = document.querySelector(".track-title");
        if (!title || !CONFIG.songTitle) return;
        title.textContent = CONFIG.songTitle;
        if (CONFIG.songTitle.length > 22) {
            var marqueeInner = document.createElement("span");
            marqueeInner.className = "track-marquee animate";
            marqueeInner.textContent = CONFIG.songTitle + "   •   " + CONFIG.songTitle;
            title.innerHTML = "";
            title.appendChild(marqueeInner);
        }
    }

    function init() {
        new ParticleEngine("particle-canvas");
        startFloatingHearts();
        bindSparkleEvents();
        setupMarquee();
        bindMusicControls();
        bindTapOverlay();

        if (CONFIG.youtubeId) {
            initYouTubePlayer();
        } else {
            var bar = document.querySelector(".music-bar");
            if (bar) bar.style.display = "none";
            var overlay = document.getElementById("tap-overlay");
            if (overlay) overlay.classList.add("hidden");
        }

        var messageEl = document.querySelector(".main-message");
        if (messageEl) {
            // Hiệu ứng gõ chữ
            var textToType = messageEl.textContent.trim() || CONFIG.message;
            typewriterEffect(messageEl, textToType, 90);

            // Bổ sung lấp lánh định kỳ
            window.setInterval(function () {
                var rect = messageEl.getBoundingClientRect();
                spawnSparkle(
                    rect.left + rand(0, rect.width),
                    rect.top + rand(0, rect.height)
                );
            }, 1800);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <meta name="theme-color" content="{{ primary_color }}" />

    <title>{{ title }}</title>
    <meta name="description" content="{{ message }}" />
    <meta property="og:title" content="{{ title }}" />
    <meta property="og:description" content="{{ message }}" />
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600&family=Dancing+Script:wght@700&family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    
    <style>
        {{ css_content|safe }}
    </style>
</head>
<body class="{% if bg_image %}has-bg-image{% endif %}"
      style="{% if bg_image %}background-image: url('{{ bg_image }}');{% endif %}"
      data-heart-count="{{ heart_count }}"
      data-heart-speed="{{ heart_speed }}"
      data-youtube-id="{{ youtube_id }}"
      data-song-title="{{ song_title }}"
      data-primary-color="{{ primary_color }}"
      data-message="{{ message }}">

    <div class="bg-overlay"></div>
    <div class="aurora-light"></div>
    <canvas id="particle-canvas"></canvas>
    <div id="hearts-container"></div>

    <div class="center-wrapper">
        <div class="glass-card">
            {% if avatar %}
            <div class="avatar-ring">
                <img src="{{ avatar }}" alt="Avatar" />
            </div>
            {% endif %}
            
            <div class="main-message">{{ message }}</div>
            
            {% if sub_text %}
            <div class="sub-text">{{ sub_text }}</div>
            {% endif %}
            
            {% if date_text %}
            <div class="date-text">{{ date_text }}</div>
            {% endif %}
        </div>
    </div>

    {% if youtube_id %}
    <div id="tap-overlay" class="tap-overlay">
        <div class="pulse-heart">🤍</div>
        <p>Chạm vào màn hình để bắt đầu</p>
        <span class="small">(Bật âm thanh nhé)</span>
    </div>
    
    <div id="yt-player"></div>
    
    <div class="music-bar">
        <button id="play-pause-btn" class="play-btn"></button>
        <div class="track-info">
            <div class="track-title">{{ song_title }}</div>
            <div class="eq-bars">
                <span></span><span></span><span></span>
            </div>
        </div>
        <div class="volume-wrap">
            <input type="range" id="volume-slider" min="0" max="100" value="70">
        </div>
    </div>
    {% endif %}

    <div class="signature-footer">Created with Love Page Generator</div>

    <script>
        {{ js_content|safe }}
    </script>
</body>
</html>
"""

# ==============================================================================
# 2. LOGIC BACKEND & GIAO DIỆN APP STREAMLIT
# ==============================================================================

DB_FILE = "love_pages.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def get_youtube_info(url):
    if not url: return "", ""
    try:
        # Thử lấy ID đơn giản qua regex trước cho nhanh
        match = re.search(r"(?:v=|youtu\.be/)([^&]+)", url)
        yt_id = match.group(1) if match else ""
        
        # Nếu muốn lấy chính xác tên bài hát, dùng yt_dlp
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('id', yt_id), info.get('title', 'Tình ca gửi người ấy 💖')
    except Exception:
        # Nếu lỗi vẫn trả về ID lấy được từ regex
        return yt_id, "Nhạc nền lãng mạn 🎵"

def render_love_page(page_id):
    """Render trang HTML full màn hình khi người dùng truy cập link chia sẻ"""
    db = load_db()
    if page_id not in db:
        st.error("Trang này không tồn tại hoặc đã bị xóa!")
        return
    
    data = db[page_id]
    env = Environment(autoescape=select_autoescape(['html', 'xml']))
    template = env.from_string(HTML_TEMPLATE)
    
    html_output = template.render(
        css_content=CSS_CONTENT,
        js_content=JS_CONTENT,
        title=data.get("title", "For You"),
        message=data.get("message", "Anh yêu em!"),
        sub_text=data.get("sub_text", ""),
        date_text=data.get("date_text", ""),
        primary_color=data.get("primary_color", "#ff4d6d"),
        heart_count=data.get("heart_count", 25),
        heart_speed=data.get("heart_speed", 8),
        youtube_id=data.get("youtube_id", ""),
        song_title=data.get("song_title", ""),
        bg_image=data.get("bg_image", ""),
        avatar=data.get("avatar", "")
    )
    
    # Ẩn giao diện mặc định của Streamlit và ép FullScreen
    st.markdown("""
        <style>
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stApp {margin-top: -80px;}
            iframe {border: none; width: 100vw; height: 100vh;}
        </style>
    """, unsafe_allow_html=True)
    
    components.html(html_output, height=1000, scrolling=True)

def main():
    st.set_page_config(page_title="Love Page Generator", layout="centered", page_icon="💖")
    
    # Kiểm tra xem có query parameter ?page=id hay không
    params = st.query_params
    if "page" in params:
        render_love_page(params["page"])
        return

    # GIAO DIỆN TẠO TRANG
    st.title("💖 Love Page Generator")
    st.write("Tạo một trang web tỏ tình / kỷ niệm siêu lãng mạn chỉ trong vài thao tác!")

    with st.form("create_form"):
        title = st.text_input("Tiêu đề trang (Tab Browser)", "Gửi người tôi yêu ❤️")
        message = st.text_area("Lời nhắn chính (Có hiệu ứng gõ chữ)", "Anh yêu em nhiều lắm!")
        sub_text = st.text_input("Dòng chữ phụ (Ví dụ: Forever & Always)", "Mãi mãi bên nhau")
        date_text = st.text_input("Ngày kỷ niệm", datetime.now().strftime("%d/%m/%Y"))
        
        yt_url = st.text_input("Link Youtube (Nhạc nền - Tuỳ chọn)", "")
        avatar = st.text_input("Link ảnh đại diện (Tuỳ chọn)", "")
        bg_image = st.text_input("Link ảnh nền (Tuỳ chọn)", "")
        
        col1, col2 = st.columns(2)
        with col1:
            primary_color = st.color_picker("Màu chủ đạo", "#ff4d6d")
            heart_count = st.slider("Số lượng tim bay", 10, 80, 25)
        with col2:
            heart_speed = st.slider("Tốc độ tim bay (giây)", 3.0, 15.0, 8.0)
        
        submitted = st.form_submit_button("Tạo Trang Ngay! ✨")

        if submitted:
            with st.spinner("Đang chuẩn bị điều kỳ diệu..."):
                page_id = str(uuid.uuid4())[:8]
                yt_id, yt_title = get_youtube_info(yt_url)
                
                db = load_db()
                db[page_id] = {
                    "title": title,
                    "message": message,
                    "sub_text": sub_text,
                    "date_text": date_text,
                    "youtube_id": yt_id,
                    "song_title": yt_title,
                    "avatar": avatar,
                    "bg_image": bg_image,
                    "primary_color": primary_color,
                    "heart_count": heart_count,
                    "heart_speed": heart_speed
                }
                save_db(db)
                
                # Tạo link chia sẻ
                # Trong môi trường Local sẽ lấy link localhost, 
                # khi Deploy (VD: Streamlit Cloud) nó sẽ cần domain thực
                share_url = f"/?page={page_id}"
                
                st.success("Tạo trang thành công! 🎉")
                st.info("Hãy copy phần đuôi link bên dưới và dán vào phía sau đường dẫn trang web của bạn (hoặc bấm thẳng vào link nếu bạn đang chạy local).")
                st.markdown(f"**Link của bạn:** [Bấm vào đây để xem]({share_url})")
                st.code(f"?page={page_id}", language="text")

if __name__ == "__main__":
    main()
