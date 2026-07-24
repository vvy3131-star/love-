"""
==============================================================================
LOVE PAGE GENERATOR  —  PHIÊN BẢN GỘP 1 FILE DUY NHẤT (app.py)
------------------------------------------------------------------------------
Toàn bộ CSS, JavaScript và template HTML của "trang tình yêu" được nhúng
thẳng vào file Python này dưới dạng chuỗi (không cần thư mục templates/
hay static/css, static/js nữa). Chỉ cần duy nhất file app.py này +
requirements.txt là chạy được.

Cách chạy:
    pip install -r requirements.txt
    streamlit run app.py

------------------------------------------------------------------------------
GHI CHÚ SỬA LỖI "không tải được trang web kết quả":
    Bản trước dùng tính năng enableStaticServing của Streamlit để serve file
    tĩnh ở /app/static/... Vấn đề là Streamlit CHỈ đọc config.toml MỘT LẦN
    lúc khởi động server, trước khi app.py kịp chạy — nên việc tự ghi
    config.toml từ trong script luôn đến quá trễ, và trên nhiều nền tảng
    deploy (Streamlit Community Cloud, Render dùng buildpack mặc định...)
    bạn không thể tự thêm cờ --server.enableStaticServing được, khiến link
    luôn bị lỗi 404 / không tải được.

    => Đã chuyển sang cơ chế "xem trang qua query param" ngay trong chính
    app này: link chia sẻ có dạng {domain}/?page=<id>. Khi ai đó mở link,
    Streamlit chạy lại script, app.py phát hiện có tham số ?page=<id> trên
    URL và tự động hiển thị đúng trang tình yêu tương ứng (ẩn toàn bộ giao
    diện tạo trang / sidebar đi). Cách này chạy được ngay với
    "streamlit run app.py" thông thường, không cần cờ, không cần khởi động
    lại, và hoạt động trên mọi nền tảng deploy.

Tác giả: Senior Python Developer
==============================================================================
"""

import base64
import io
import json
import os
import re
import uuid
from datetime import datetime

import qrcode
import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Environment, select_autoescape

# yt_dlp chỉ dùng để TÌM video Youtube phù hợp với tên bài hát (lấy metadata
# / video id), KHÔNG tải bất kỳ file nhạc nào về máy.
import yt_dlp


# ==============================================================================
# 1. TÀI NGUYÊN NHÚNG SẴN: CSS + JAVASCRIPT + TEMPLATE HTML
#    (được nhúng thẳng vào biến Python thay vì đọc từ file rời)
# ==============================================================================

CSS_CONTENT = r"""/* ==========================================================================
   LOVE PAGE GENERATOR - MAIN STYLESHEET
   Tác giả: Senior Python Developer
   Mô tả: Toàn bộ hiệu ứng nền, trái tim bay, glassmorphism, animation chữ,
          thanh điều khiển nhạc và responsive cho mọi thiết bị.
   ========================================================================== */

/* --------------------------------------------------------------------------
   1. CSS VARIABLES (được Jinja2 ghi đè giá trị màu chủ đạo lúc render)
   -------------------------------------------------------------------------- */
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

/* --------------------------------------------------------------------------
   2. RESET & BASE
   -------------------------------------------------------------------------- */
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

/* Nền ảnh do người dùng upload (nếu có), phủ blur + overlay hồng lãng mạn */
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

/* Ánh sáng lung linh - lớp glow chuyển động chậm phía sau */
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

/* --------------------------------------------------------------------------
   3. CANVAS PARTICLE LAYER (điều khiển bởi effects.js)
   -------------------------------------------------------------------------- */
#particle-canvas {
    position: fixed;
    inset: 0;
    z-index: 1;
    pointer-events: none;
}

/* --------------------------------------------------------------------------
   4. TRÁI TIM BAY (Floating Hearts)
   -------------------------------------------------------------------------- */
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
    0% {
        transform: translateY(0) translateX(0) rotate(0deg) scale(0.6);
        opacity: 0;
    }
    10% {
        opacity: 1;
    }
    50% {
        transform: translateY(-50vh) translateX(var(--drift, 30px)) rotate(180deg) scale(1);
    }
    100% {
        transform: translateY(-110vh) translateX(calc(var(--drift, 30px) * -1)) rotate(360deg) scale(0.5);
        opacity: 0;
    }
}

/* Sparkle lấp lánh khi chạm / click */
.sparkle {
    position: fixed;
    z-index: 5;
    width: 100px;
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

/* --------------------------------------------------------------------------
   5. TAP-TO-START OVERLAY (do trình duyệt chặn autoplay có âm thanh)
   -------------------------------------------------------------------------- */
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

/* --------------------------------------------------------------------------
   6. KHỐI NỘI DUNG TRUNG TÂM (glassmorphism card)
   -------------------------------------------------------------------------- */
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

/* Avatar tròn có viền glow */
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

/* Dòng chữ chính - hiệu ứng fade + scale + glow + con trỏ gõ chữ */
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
}

/* Con trỏ nhấp nháy cho hiệu ứng gõ chữ */
.main-message::after {
    content: '|';
    display: inline-block;
    margin-left: 3px;
    color: var(--primary-color);
    animation: blinkCursor 0.8s infinite;
}

.main-message.typing-done::after {
    display: none;
}

@keyframes blinkCursor {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}

@keyframes messageFadeScale {
    0% { opacity: 0; transform: scale(0.7); filter: blur(6px); }
    60% { opacity: 1; transform: scale(1.05); filter: blur(0); }
    100% { opacity: 1; transform: scale(1); }
}

@keyframes glowPulse {
    0%, 100% {
        text-shadow: 0 0 10px var(--glow-color), 0 0 24px var(--glow-color), 0 0 46px var(--shadow-color);
    }
    50% {
        text-shadow: 0 0 18px var(--glow-color), 0 0 40px var(--glow-color), 0 0 70px var(--shadow-color);
    }
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

/* --------------------------------------------------------------------------
   7. THANH ĐIỀU KHIỂN NHẠC (floating music bar)
   -------------------------------------------------------------------------- */
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

.music-bar button.play-btn:hover {
    transform: scale(1.08);
}

.music-bar button.play-btn:active {
    transform: scale(0.94);
}

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

.music-bar .track-marquee {
    display: inline-block;
    white-space: nowrap;
}

.music-bar .track-marquee.animate {
    animation: marquee 9s linear infinite;
}

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

/* --------------------------------------------------------------------------
   8. FOOTER / CHỮ KÝ
   -------------------------------------------------------------------------- */
.signature-footer {
    position: fixed;
    bottom: 6px;
    right: 12px;
    z-index: 30;
    font-size: 11px;
    opacity: 0.45;
    letter-spacing: 0.5px;
}

/* --------------------------------------------------------------------------
   9. RESPONSIVE - ĐIỆN THOẠI / TABLET / DESKTOP
   -------------------------------------------------------------------------- */

/* Điện thoại nhỏ */
@media (max-width: 480px) {
    .glass-card {
        padding: 34px 20px;
        border-radius: 24px;
        gap: 16px;
    }
    .avatar-ring {
        width: 90px;
        height: 90px;
    }
    .main-message {
        font-size: clamp(24px, 8vw, 36px);
    }
    .music-bar {
        min-width: unset;
        width: 90vw;
        padding: 10px 16px;
        bottom: 14px;
    }
    .tap-overlay .pulse-heart {
        font-size: 48px;
    }
}

/* Tablet */
@media (min-width: 481px) and (max-width: 900px) {
    .glass-card {
        padding: 42px 30px;
    }
    .avatar-ring {
        width: 105px;
        height: 105px;
    }
}

/* Desktop lớn */
@media (min-width: 1400px) {
    .center-wrapper {
        max-width: 760px;
    }
    .main-message {
        font-size: clamp(36px, 5vw, 64px);
    }
}

/* Màn hình thấp (landscape trên điện thoại) */
@media (max-height: 480px) and (orientation: landscape) {
    .glass-card {
        padding: 20px 26px;
        gap: 10px;
    }
    .avatar-ring {
        width: 64px;
        height: 64px;
    }
    .music-bar {
        bottom: 8px;
    }
}

/* Giảm hiệu ứng cho người dùng yêu cầu giảm chuyển động */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* --------------------------------------------------------------------------
   10. SCROLLBAR TÙY CHỈNH (đồng bộ theme hồng)
   -------------------------------------------------------------------------- */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: var(--primary-color);
    border-radius: 8px;
}
"""

JS_CONTENT = r"""/* ==========================================================================
   LOVE PAGE GENERATOR - CLIENT SIDE EFFECTS
   File này chạy trong trang HTML đã tạo (được nhúng trực tiếp vào <script>).
   Toàn bộ config (số lượng tim, tốc độ, youtube id...) được đọc từ
   thuộc tính data-* gắn trên thẻ <body> do Jinja2 render ra.
   ========================================================================== */

(function () {
    "use strict";

    /* ----------------------------------------------------------------------
       0. ĐỌC CẤU HÌNH TỪ BODY DATA ATTRIBUTES
       ---------------------------------------------------------------------- */
    var body = document.body;
    var CONFIG = {
        heartCount: parseInt(body.getAttribute("data-heart-count") || "25", 10),
        heartSpeed: parseFloat(body.getAttribute("data-heart-speed") || "8"),
        youtubeId: body.getAttribute("data-youtube-id") || "",
        songTitle: body.getAttribute("data-song-title") || "",
        primaryColor: body.getAttribute("data-primary-color") || "#ff4d6d",
        message: body.getAttribute("data-message") || ""
    };

    /* ----------------------------------------------------------------------
       1. HÀM TIỆN ÍCH NGẪU NHIÊN
       ---------------------------------------------------------------------- */
    function rand(min, max) {
        return Math.random() * (max - min) + min;
    }

    function pick(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    }

    /* ----------------------------------------------------------------------
       2. CANVAS PARTICLE ENGINE (ánh sáng lung linh bay nhẹ nhàng)
       ---------------------------------------------------------------------- */
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

            if (p.alpha <= 0.1 || p.alpha >= 0.95) {
                p.twinkleDir *= -1;
            }
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

    /* ----------------------------------------------------------------------
       3. TRÁI TIM BAY LIÊN TỤC (Floating Hearts)
       ---------------------------------------------------------------------- */
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

        // Đôi khi đổi màu tim cho sinh động
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

        // Tạo lượt tim ban đầu
        for (var i = 0; i < CONFIG.heartCount; i++) {
            window.setTimeout(function () {
                createHeart(container);
            }, rand(0, 4000));
        }

        // Sinh tim liên tục theo chu kỳ
        var intervalMs = Math.max(250, 6000 / Math.max(CONFIG.heartCount, 1));
        window.setInterval(function () {
            createHeart(container);
        }, intervalMs);
    }

    /* ----------------------------------------------------------------------
       4. SPARKLE LẤP LÁNH KHI CHẠM / CLICK MÀN HÌNH
       ---------------------------------------------------------------------- */
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
        document.addEventListener(
            "touchstart",
            function (e) {
                var t = e.touches[0];
                if (!t) return;
                for (var i = 0; i < 3; i++) {
                    spawnSparkle(t.clientX + rand(-8, 8), t.clientY + rand(-8, 8));
                }
            },
            { passive: true }
        );
    }

    /* ----------------------------------------------------------------------
       5. HIỆU ỨNG GÕ CHỮ (Typewriter) CHO DÒNG CHỮ CHÍNH
       ---------------------------------------------------------------------- */
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

    /* ----------------------------------------------------------------------
       6. ĐIỀU KHIỂN NHẠC QUA YOUTUBE IFRAME API
       ---------------------------------------------------------------------- */
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
                playerVars: {
                    autoplay: 1,
                    controls: 0,
                    loop: 1,
                    playlist: CONFIG.youtubeId,
                    playsinline: 1
                },
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
        try {
            player.playVideo();
        } catch (err) {
            console.warn("Autoplay bị chặn, chờ người dùng tương tác:", err);
        }
    }

    function updatePlayButton() {
        var btn = document.getElementById("play-pause-btn");
        if (!btn) return;
        btn.innerHTML = isPlaying ? ICON_PAUSE : ICON_PLAY;
    }

    var ICON_PLAY =
        '<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M8 5v14l11-7z"/></svg>';
    var ICON_PAUSE =
        '<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>';

    function bindMusicControls() {
        var playBtn = document.getElementById("play-pause-btn");
        var volumeSlider = document.getElementById("volume-slider");

        if (playBtn) {
            playBtn.innerHTML = ICON_PLAY;
            playBtn.addEventListener("click", function () {
                if (!ytPlayer) return;
                if (isPlaying) {
                    ytPlayer.pauseVideo();
                } else {
                    ytPlayer.playVideo();
                }
            });
        }

        if (volumeSlider) {
            volumeSlider.addEventListener("input", function (e) {
                if (ytPlayer && ytPlayer.setVolume) {
                    ytPlayer.setVolume(parseInt(e.target.value, 10));
                }
            });
        }
    }

    /* ----------------------------------------------------------------------
       7. OVERLAY "CHẠM ĐỂ BẮT ĐẦU" - xử lý chính sách chặn autoplay có âm thanh
       ---------------------------------------------------------------------- */
    function bindTapOverlay() {
        var overlay = document.getElementById("tap-overlay");
        if (!overlay) return;

        function dismiss() {
            overlay.classList.add("hidden");
            if (ytPlayer && ytPlayer.playVideo) {
                ytPlayer.playVideo();
            }
            document.removeEventListener("click", dismiss);
            document.removeEventListener("touchstart", dismiss);
        }

        overlay.addEventListener("click", dismiss);

        // Nếu nhạc tự phát thành công thì tự ẩn overlay sau 1.2s
        window.setTimeout(function () {
            if (isPlaying) {
                overlay.classList.add("hidden");
            }
        }, 1200);
    }

    /* ----------------------------------------------------------------------
       8. MARQUEE TÊN BÀI HÁT NẾU QUÁ DÀI
       ---------------------------------------------------------------------- */
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

    /* ----------------------------------------------------------------------
       9. KHỞI TẠO TOÀN BỘ KHI TRANG SẴN SÀNG
       ---------------------------------------------------------------------- */
    function init() {
        new ParticleEngine("particle-canvas");
        startFloatingHearts();
        bindSparkleEvents();
        setupMarquee();
        bindMusicControls();
        bindTapOverlay();

        // Kích hoạt hiệu ứng gõ chữ cho thông điệp chính
        var messageEl = document.querySelector(".main-message");
        if (messageEl && CONFIG.message) {
            typewriterEffect(messageEl, CONFIG.message, 80);
        }

        if (CONFIG.youtubeId) {
            initYouTubePlayer();
        } else {
            // Không có nhạc -> ẩn luôn thanh điều khiển nhạc
            var bar = document.querySelector(".music-bar");
            if (bar) bar.style.display = "none";
            var overlay = document.getElementById("tap-overlay");
            if (overlay) overlay.classList.add("hidden");
        }

        // Hiệu ứng chữ lấp lánh nhẹ định kỳ (glow đã xử lý ở CSS,
        // đây chỉ là bổ sung random spark quanh chữ)
        if (messageEl) {
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
    <meta property="og:type" content="website" />

    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&family=Dancing+Script:wght@600;700&family=Playfair+Display:ital,wght@0,600;1,400&family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet" />

    <style>
{{ css_content }}
    </style>
</head>
<body
    data-heart-count="{{ heart_count }}"
    data-heart-speed="{{ heart_speed }}"
    data-youtube-id="{{ youtube_id }}"
    data-song-title="{{ song_title }}"
    data-primary-color="{{ primary_color }}"
    data-message="{{ message }}"
    {% if bg_image_base64 %}
    class="has-bg-image"
    style="background-image: url('{{ bg_image_base64 }}');"
    {% endif %}
>

    <div class="bg-overlay"></div>
    <div class="aurora-light"></div>

    <canvas id="particle-canvas"></canvas>

    <div id="hearts-container"></div>

    <div id="tap-overlay" class="tap-overlay">
        <div class="pulse-heart">💖</div>
        <p>Chạm vào màn hình để bắt đầu...</p>
        <span class="small">Lưu ý: Mở âm lượng thiết bị để nghe nhạc nền nhé</span>
    </div>

    <main class="center-wrapper">
        <article class="glass-card">
            {% if avatar_base64 %}
            <div class="avatar-ring">
                <img src="{{ avatar_base64 }}" alt="Avatar" />
            </div>
            {% endif %}

            <h1 class="main-message">{{ message }}</h1>

            {% if sub_text %}
            <p class="sub-text">{{ sub_text }}</p>
            {% endif %}

            {% if date_text %}
            <p class="date-text">🗓 {{ date_text }}</p>
            {% endif %}
        </article>
    </main>

    {% if youtube_id %}
    <div class="music-bar">
        <button id="play-pause-btn" class="play-btn" aria-label="Play/Pause"></button>
        <div class="track-info">
            <span class="track-title">{{ song_title or "Đang phát nhạc..." }}</span>
        </div>
        <div class="eq-bars">
            <span></span>
            <span></span>
            <span></span>
        </div>
        <div class="volume-wrap">
            <input id="volume-slider" type="range" min="0" max="100" value="70" aria-label="Âm lượng" />
        </div>
    </div>

    <div id="yt-player" style="position: absolute; width: 0; height: 0; opacity: 0; pointer-events: none;"></div>
    {% endif %}

    <footer class="signature-footer">
        Crafted with ❤️
    </footer>

    <script>
{{ js_content }}
    </script>
</body>
</html>
"""


# ==============================================================================
# 2. BỘ LƯU TRỮ TRANG ĐÃ TẠO VÀO FILE JSON
#    (Mỗi khi người dùng bấm tạo trang, dữ liệu sẽ ghi vào pages_db.json.
#    Khi link dạng ?page=<id> được mở, app sẽ đọc từ DB này để render)
# ==============================================================================

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages_db.json")


def load_db() -> dict:
    """Tải danh sách các trang đã lưu từ file JSON."""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_page_to_db(page_id: str, data: dict):
    """Lưu dữ liệu trang mới vào file JSON."""
    db = load_db()
    db[page_id] = data
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Lỗi khi lưu dữ liệu trang: {e}")


def get_page_from_db(page_id: str) -> dict:
    """Lấy dữ liệu 1 trang theo ID."""
    db = load_db()
    return db.get(page_id)


# ==============================================================================
# 3. CÁC HÀM TIỆN ÍCH PYTHON
# ==============================================================================

def image_to_base64(file_bytes, mime_type: str) -> str:
    """Chuyển đổi file ảnh bytes sang chuỗi Data URI Base64."""
    if not file_bytes:
        return ""
    encoded = base64.b64encode(file_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def search_youtube_video_id(song_query: str) -> tuple:
    """
    Tìm kiếm ID video Youtube từ tên bài hát thông qua yt_dlp.
    Hàm CHỈ lấy metadata (ID và tiêu đề), KHÔNG tải nhạc.
    Trả về tuple: (video_id, title)
    """
    if not song_query or not song_query.strip():
        return "", ""

    query = song_query.strip()
    # Nếu người dùng dán nguyên link Youtube -> tách lấy video ID luôn
    yt_url_match = re.search(
        r"(?:v=|\/([0-9A-Za-z_-]{11}).*[\?&]v=|^youtu\.be\/|\/embed\/|\/v\/)([:_a-zA-Z0-9-]{11})",
        query,
    )
    if yt_url_match:
        vid_id = yt_url_match.group(1) or yt_url_match.group(2)
        if vid_id:
            return vid_id, "Youtube Track"

    # Nếu truyền tên bài hát -> Dùng yt_dlp search 1 kết quả duy nhất
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "default_search": "ytsearch1",
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if "entries" in info and len(info["entries"]) > 0:
                first_match = info["entries"][0]
                vid_id = first_match.get("id", "")
                title = first_match.get("title", query)
                return vid_id, title
    except Exception as err:
        st.warning(f"Lỗi khi tìm bài hát trên Youtube: {err}")

    return "", query


def generate_qr_code_base64(url: str) -> str:
    """Tạo ảnh QR Code cho đường dẫn URL dạng chuỗi Base64."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#ff4d6d", back_color="white")

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def hex_to_rgba(hex_code: str, alpha: float = 0.75) -> str:
    """Chuyển mã màu HEX (ví dụ #ff4d6d) sang dạng RGBA để làm bóng đổ glow."""
    hex_code = hex_code.lstrip("#")
    if len(hex_code) == 6:
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
    return f"rgba(255, 77, 109, {alpha})"


def render_html_page(params: dict) -> str:
    """Sử dụng Jinja2 render mẫu HTML_TEMPLATE với các tham số truyền vào."""
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    template = env.from_string(HTML_TEMPLATE)

    # Tính toán màu glow tương ứng với màu chính
    primary_color = params.get("primary_color", "#ff4d6d")
    glow_color = hex_to_rgba(primary_color, 0.75)
    shadow_color = hex_to_rgba(primary_color, 0.45)

    # Đưa màu động vào CSS
    custom_css = CSS_CONTENT.replace("#ff4d6d", primary_color)

    rendered = template.render(
        title=params.get("title", "Gửi Người Tôi Yêu ❤️"),
        message=params.get("message", "Anh Yêu Em ❤️"),
        sub_text=params.get("sub_text", ""),
        date_text=params.get("date_text", ""),
        primary_color=primary_color,
        glow_color=glow_color,
        shadow_color=shadow_color,
        heart_count=params.get("heart_count", 25),
        heart_speed=params.get("heart_speed", 8),
        youtube_id=params.get("youtube_id", ""),
        song_title=params.get("song_title", ""),
        avatar_base64=params.get("avatar_base64", ""),
        bg_image_base64=params.get("bg_image_base64", ""),
        css_content=custom_css,
        js_content=JS_CONTENT,
    )
    return rendered


# ==============================================================================
# 4. GIAO DIỆN CHÍNH (STREAMLIT APP)
# ==============================================================================

def main():
    st.set_page_config(
        page_title="Love Page Generator",
        page_icon="💖",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    # --------------------------------------------------------------------------
    # CHẾ ĐỘ 1: XEM TRANG TÌNH YÊU TRỰC TIẾP QUA QUERY PARAMETER ?page=<id>
    # (Tự động kích hoạt khi ai đó bấm vào link chia sẻ. Khi đó app hiển thị
    # nguyên trang HTML kết quả full màn hình, không hiển thị Streamlit UI)
    # --------------------------------------------------------------------------
    query_params = st.query_params
    page_id = query_params.get("page")

    if page_id:
        page_data = get_page_from_db(page_id)
        if page_data:
            full_html = render_html_page(page_data)
            # Dùng Streamlit Components render toàn bộ trang HTML độc lập
            components.html(full_html, height=1000, scrolling=True)

            # CSS ẩn giao diện thừa của Streamlit (header, footer, padding)
            st.markdown(
                """
                <style>
                    header {visibility: hidden !important;}
                    footer {visibility: hidden !important;}
                    #MainMenu {visibility: hidden !important;}
                    .block-container {
                        padding: 0 !important;
                        margin: 0 !important;
                        max-width: 100% !important;
                    }
                    iframe {
                        position: fixed !important;
                        top: 0 !important;
                        left: 0 !important;
                        width: 100vw !important;
                        height: 100vh !important;
                        border: none !important;
                        z-index: 999999 !important;
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )
            return
        else:
            st.error("❌ Trang tình yêu này không tồn tại hoặc đã bị xóa!")
            st.info("Hãy tự tạo một trang mới bên dưới nhé 👇")

    # --------------------------------------------------------------------------
    # CHẾ ĐỘ 2: BẢNG ĐIỀU KHIỂN TẠO TRANG TÌNH YÊU (Giao diện Streamlit)
    # --------------------------------------------------------------------------
    st.title("💖 Love Page Generator")
    st.caption("Tạo trang web tình yêu lãng mạn, nhúng nhạc Youtube & hiệu ứng lung linh")

    st.markdown("---")

    # Sidebar - Cấu hình tham số
    st.sidebar.header("🎨 Tùy chỉnh Giao diện")

    primary_color = st.sidebar.color_picker(
        "Màu chủ đạo (Theme Color)", value="#FF4D6D"
    )
    heart_count = st.sidebar.slider(
        "Số lượng trái tim bay", min_value=5, max_value=60, value=25, step=5
    )
    heart_speed = st.sidebar.slider(
        "Tốc độ bay của tim (giây)", min_value=3, max_value=15, value=8, step=1
    )

    st.sidebar.markdown("---")
    st.sidebar.header("🎵 Nhạc nền Youtube")
    song_input = st.sidebar.text_input(
        "Tên bài hát hoặc Link Youtube",
        value="Thắc Mắc - Thịnh Suy",
        help="Nhập tên bài hát (ví dụ: 'Cho Cùng Nhau Trốn Chạy') hoặc dán link Youtube trực tiếp.",
    )

    # Form nhập nội dung chính ở giữa
    st.subheader("📝 Nội dung trang")

    title = st.text_input("Tiêu đề trang (SEO / Tab browser)", value="Gửi Người Tôi Yêu ❤️")
    message = st.text_input(
        "Dòng chữ chính (Hiển thị nổi bật nhất)",
        value="Anh Yêu Em Rất Nhiều ❤️",
    )
    sub_text = st.text_area(
        "Dòng chữ phụ / Lời nhắn lãng mạn",
        value="Cảm ơn em đã xuất hiện và làm cho mỗi ngày của anh trở nên thật đặc biệt.",
        height=100,
    )
    date_text = st.text_input(
        "Ngày kỷ niệm (Không bắt buộc)",
        value=datetime.now().strftime("%d/%m/%Y"),
    )

    col1, col2 = st.columns(2)
    with col1:
        avatar_file = st.file_uploader(
            "📷 Ảnh đại diện (Avatar tròn)", type=["png", "jpg", "jpeg", "webp", "gif"]
        )
    with col2:
        bg_file = st.file_uploader(
            "🖼️ Ảnh nền trang (Background)", type=["png", "jpg", "jpeg", "webp"]
        )

    st.markdown("---")

    # Xử lý khi người dùng bấm Nút TẠO TRANG
    if st.button("🚀 TẠO TRANG TÌNH YÊU", type="primary", use_container_width=True):
        with st.spinner("⏳ Đang xử lý tài nguyên và tạo trang..."):
            # 1. Tìm nhạc Youtube
            yt_id = ""
            yt_title = ""
            if song_input.strip():
                yt_id, yt_title = search_youtube_video_id(song_input)

            # 2. Xử lý Base64 cho ảnh đại diện
            avatar_b64 = ""
            if avatar_file is not None:
                avatar_bytes = avatar_file.read()
                avatar_b64 = image_to_base64(avatar_bytes, avatar_file.type)

            # 3. Xử lý Base64 cho ảnh nền
            bg_b64 = ""
            if bg_file is not None:
                bg_bytes = bg_file.read()
                bg_b64 = image_to_base64(bg_bytes, bg_file.type)

            # 4. Gom tham số
            page_params = {
                "title": title,
                "message": message,
                "sub_text": sub_text,
                "date_text": date_text,
                "primary_color": primary_color,
                "heart_count": heart_count,
                "heart_speed": heart_speed,
                "youtube_id": yt_id,
                "song_title": yt_title or song_input,
                "avatar_base64": avatar_b64,
                "bg_image_base64": bg_b64,
            }

            # 5. Lưu vào database JSON
            new_id = uuid.uuid4().hex[:8]
            save_page_to_db(new_id, page_params)

            # 6. Tạo đường dẫn chia sẻ (Dạng ?page=<id>)
            # Tự động lấy domain hiện tại (hoặc localhost)
            server_url = st.get_option("browser.serverAddress") or "localhost"
            server_port = st.get_option("browser.serverPort") or 8501
            share_url = f"http://{server_url}:{server_port}/?page={new_id}"

            st.session_state["created_page_id"] = new_id
            st.session_state["created_share_url"] = share_url
            st.session_state["created_params"] = page_params

            st.success("🎉 Đã tạo trang tình yêu thành công!")

    # Hiển thị kết quả sau khi tạo thành công
    if "created_page_id" in st.session_state:
        page_id = st.session_state["created_page_id"]
        share_url = st.session_state["created_share_url"]
        params = st.session_state["created_params"]

        st.markdown("### 🔗 Link Chia Sẻ Trang")
        st.code(share_url, language="text")

        # QR Code để quét trên điện thoại
        col_qr, col_info = st.columns([1, 2])
        with col_qr:
            qr_b64 = generate_qr_code_base64(share_url)
            st.image(qr_b64, caption="Quét QR bằng camera điện thoại", width=180)

        with col_info:
            st.info(
                "💡 **Hướng dẫn:**\n\n"
                "• Bấm vào nút bên dưới để mở xem thử trang kết quả ngay lập tức.\n"
                "• Hoặc copy đường link/mã QR ở trên để gửi qua Zalo, Messenger cho người ấy!"
            )
            st.link_button(
                "👉 MỞ TRANG KẾT QUẢ NGAY",
                url=f"/?page={page_id}",
                type="primary",
                use_container_width=True,
            )

        st.markdown("---")

        # Nút Tải về file HTML Độc lập (Chạy offile không cần máy chủ)
        st.subheader("💾 Tải File HTML Độc Lập")
        st.caption(
            "Bạn cũng có thể tải về 1 file HTML duy nhất chứa toàn bộ hình ảnh, nhạc, CSS/JS "
            "để mở trực tiếp trên máy tính hoặc gửi file cho người ấy."
        )
        single_file_html = render_html_page(params)
        st.download_button(
            label="📥 Tải file index.html độc lập",
            data=single_file_html,
            file_name=f"love_page_{page_id}.html",
            mime="text/html",
            use_container_width=True,
        )

        # Xem trước giao diện trong khung Preview
        st.markdown("---")
        st.subheader("👁️ Xem Trước Giao Diện (Preview)")
        components.html(single_file_html, height=650, scrolling=True)


if __name__ == "__main__":
    main()
