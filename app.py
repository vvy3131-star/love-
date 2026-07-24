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

/* Dòng chữ chính - hiệu ứng fade + scale + glow */
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
       5. HIỆU ỨNG GÕ CHỮ (Typewriter) CHO DÒNG CHỮ CHÍNH - tuỳ chọn
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
        var messageEl = document.querySelector(".main-message");
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
<!--
    ==========================================================================
    LOVE PAGE GENERATOR - TEMPLATE TRANG TÌNH YÊU
    Template này được render bởi Jinja2 trong app.py.
    Toàn bộ CSS và JS được nhúng thẳng vào file (inline) để trang HTML
    xuất ra là MỘT FILE DUY NHẤT, độc lập, có thể chia sẻ mà không phụ
    thuộc vào file tĩnh nào khác.
    ==========================================================================
-->
<html lang="vi">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <meta name="theme-color" content="{{ primary_color }}" />

    <!-- SEO / chia sẻ mạng xã hội -->
    <title>{{ title }}</title>
    <meta name="description" content="{{ message }}" />
    <meta property="og:title" content="{{ title }}" />
    <meta property="og:description" content="{{ message }}" />
    <meta property="og:type" content="website" />
    {% if bg_image_data %}
    <meta property="og:image" content="{{ bg_image_data }}" />
    {% endif %}

    <!-- Google Fonts: chữ viết tay lãng mạn + font chính -->
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
        href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600;700&family=Playfair+Display:ital,wght@1,600&family=Poppins:wght@300;400;500;600;700&display=swap"
        rel="stylesheet"
    />

    <!-- Favicon trái tim (emoji data-uri, không cần file ngoài) -->
    <link
        rel="icon"
        href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>%E2%9D%A4%EF%B8%8F</text></svg>"
    />

    <style>
        /* ================= CSS ĐƯỢC NHÚNG TỪ static/css/style.css ================= */
        {{ css_content|safe }}

        /* ================= GHI ĐÈ BIẾN MÀU THEO NGƯỜI DÙNG CHỌN ================= */
        :root {
            --primary-color: {{ primary_color }};
            --secondary-color: {{ secondary_color }};
            --accent-color: {{ accent_color }};
            --glow-color: {{ glow_color }};
            --heart-speed: {{ heart_speed }}s;
        }

        {% if bg_image_data %}
        body {
            background-image: url('{{ bg_image_data }}');
        }
        {% endif %}
    </style>
</head>
<body
    class="{% if bg_image_data %}has-bg-image{% endif %}"
    data-heart-count="{{ heart_count }}"
    data-heart-speed="{{ heart_speed }}"
    data-youtube-id="{{ youtube_id }}"
    data-song-title="{{ song_title }}"
    data-primary-color="{{ primary_color }}"
    data-message="{{ message }}"
>

    <!-- ====================================================================
         LỚP NỀN: overlay hồng blur + ánh sáng lung linh (aurora)
         ==================================================================== -->
    <div class="bg-overlay"></div>
    <div class="aurora-light"></div>

    <!-- ====================================================================
         LỚP PARTICLE (canvas) - vẽ bằng JS
         ==================================================================== -->
    <canvas id="particle-canvas"></canvas>

    <!-- ====================================================================
         LỚP TRÁI TIM BAY LIÊN TỤC
         ==================================================================== -->
    <div id="hearts-container"></div>

    <!-- ====================================================================
         OVERLAY "CHẠM ĐỂ BẮT ĐẦU" (xử lý autoplay bị trình duyệt chặn)
         ==================================================================== -->
    {% if youtube_id %}
    <div class="tap-overlay" id="tap-overlay">
        <div class="pulse-heart">❤️</div>
        <p>Chạm vào màn hình để bắt đầu</p>
        <span class="small">{{ song_title }}</span>
    </div>
    {% endif %}

    <!-- ====================================================================
         NỘI DUNG TRUNG TÂM: avatar + dòng chữ + ngày tháng
         ==================================================================== -->
    <div class="center-wrapper">
        <div class="glass-card">

            {% if avatar_data %}
            <div class="avatar-ring">
                <img src="{{ avatar_data }}" alt="avatar" />
            </div>
            {% endif %}

            <div class="main-message">{{ message }}</div>

            <div class="sub-text">Được gửi bằng tất cả yêu thương</div>

            {% if generated_date %}
            <div class="date-text">{{ generated_date }}</div>
            {% endif %}
        </div>
    </div>

    <!-- ====================================================================
         THANH ĐIỀU KHIỂN NHẠC (chỉ hiện nếu có bài hát)
         ==================================================================== -->
    {% if youtube_id %}
    <div class="music-bar">
        <button id="play-pause-btn" class="play-btn" aria-label="Play/Pause"></button>

        <div class="track-info">
            <span class="track-title">{{ song_title }}</span>
        </div>

        <div class="eq-bars">
            <span></span><span></span><span></span>
        </div>

        <div class="volume-wrap">
            <svg viewBox="0 0 24 24" width="16" height="16">
                <path
                    fill="currentColor"
                    d="M3 10v4h4l5 5V5L7 10H3zm13.5 2c0-1.77-.77-3.29-2-4.2v8.4c1.23-.91 2-2.43 2-4.2z"
                />
            </svg>
            <input type="range" id="volume-slider" min="0" max="100" value="70" />
        </div>
    </div>

    <!-- Div ẩn chứa YouTube player (âm thanh, không hiện khung hình) -->
    <div id="yt-player" style="position:fixed; bottom:-200px; left:-200px; width:1px; height:1px; opacity:0;"></div>
    {% endif %}

    <!-- ====================================================================
         CHỮ KÝ CUỐI TRANG
         ==================================================================== -->
    <div class="signature-footer">💌 made with Love Page Generator</div>

    <!-- ====================================================================
         SCRIPT: nhúng toàn bộ static/js/effects.js
         ==================================================================== -->
    <script>
        {{ js_content|safe }}
    </script>
</body>
</html>
"""


# ==============================================================================
# 2. CẤU HÌNH ĐƯỜNG DẪN
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(BASE_DIR, "static", "pages")
INDEX_JSON_PATH = os.path.join(PAGES_DIR, "_index.json")

# Đảm bảo thư mục lưu trang đã tạo luôn tồn tại (nơi lưu file .html gốc,
# dùng để "xem trước" trong app và để route ?page=<id> đọc lại khi chia sẻ).
os.makedirs(PAGES_DIR, exist_ok=True)

MAX_IMAGE_DIMENSION = 1600      # giới hạn cạnh lớn nhất của ảnh nền
MAX_AVATAR_DIMENSION = 500      # giới hạn cạnh lớn nhất của avatar
JPEG_QUALITY = 82                # chất lượng nén ảnh khi convert sang JPEG


# ==============================================================================
# 3. XỬ LÝ MÀU SẮC (sinh màu phụ / glow từ màu chủ đạo người dùng chọn)
# ==============================================================================
def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*[max(0, min(255, int(c))) for c in rgb])


def adjust_color(hex_color: str, amount: int) -> str:
    """Làm sáng (amount > 0) hoặc làm tối (amount < 0) một màu HEX."""
    r, g, b = hex_to_rgb(hex_color)
    r = r + amount if amount >= 0 else r * (1 + amount / 255)
    g = g + amount if amount >= 0 else g * (1 + amount / 255)
    b = b + amount if amount >= 0 else b * (1 + amount / 255)
    return rgb_to_hex((r, g, b))


def hex_to_rgba_string(hex_color: str, alpha: float) -> str:
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r}, {g}, {b}, {alpha})"


# ==============================================================================
# 4. XỬ LÝ YOUTUBE (nhận diện link / tìm kiếm theo tên bài hát)
# ==============================================================================
YOUTUBE_URL_PATTERN = re.compile(
    r"(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([A-Za-z0-9_-]{11})"
)


def is_youtube_url(text: str) -> bool:
    if not text:
        return False
    return bool(YOUTUBE_URL_PATTERN.search(text))


def extract_youtube_id_from_url(url: str):
    match = YOUTUBE_URL_PATTERN.search(url)
    if match:
        return match.group(1)
    return None


def search_youtube_by_song_name(song_name: str):
    """
    Dùng yt_dlp để tìm video Youtube khớp nhất với tên bài hát.
    Trả về tuple (video_id, video_title) hoặc (None, None) nếu không tìm thấy.
    Chỉ lấy metadata (skip_download=True), không tải bất kỳ file nào.
    """
    if not song_name or not song_name.strip():
        return None, None

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
        "default_search": "ytsearch1",
        "extract_flat": "in_playlist",
        "socket_timeout": 12,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(song_name, download=False)

            if result and "entries" in result and len(result["entries"]) > 0:
                entry = result["entries"][0]
                video_id = entry.get("id")
                title = entry.get("title", song_name)
                return video_id, title

            if result and result.get("id"):
                return result.get("id"), result.get("title", song_name)

    except Exception as exc:  # noqa: BLE001 - cần bắt mọi lỗi mạng / parsing
        st.session_state["last_youtube_error"] = str(exc)
        return None, None

    return None, None


def resolve_youtube_id(song_name: str, youtube_link: str):
    """
    Quyết định video Youtube nào sẽ được dùng, theo thứ tự ưu tiên:
      1) Nếu người dùng nhập link Youtube hợp lệ -> dùng luôn link đó.
      2) Nếu không, thử tìm kiếm theo tên bài hát.
    Trả về (video_id, hiển_thị_tên_bài_hát).
    """
    if youtube_link and is_youtube_url(youtube_link):
        video_id = extract_youtube_id_from_url(youtube_link)
        display_title = song_name.strip() if song_name else "Nhạc nền"
        return video_id, display_title

    if song_name and song_name.strip():
        video_id, title = search_youtube_by_song_name(song_name.strip())
        return video_id, (title or song_name.strip())

    return None, ""


# ==============================================================================
# 5. XỬ LÝ ẢNH UPLOAD (nén + chuyển sang base64 data URI để nhúng vào HTML)
# ==============================================================================
def uploaded_image_to_data_uri(uploaded_file, max_dimension: int) -> str:
    """
    Nhận một UploadedFile từ st.file_uploader, resize cho vừa max_dimension,
    nén sang JPEG và encode base64 thành data URI để nhúng trực tiếp vào HTML
    (giúp trang chia sẻ là 1 file HTML độc lập, không phụ thuộc ảnh ngoài).
    """
    if uploaded_file is None:
        return ""

    try:
        from PIL import Image

        image = Image.open(uploaded_file)

        if image.mode in ("RGBA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image.convert("RGBA"), mask=image.convert("RGBA").split()[-1])
            image = background
        else:
            image = image.convert("RGB")

        image.thumbnail((max_dimension, max_dimension), Image.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"

    except Exception as exc:  # noqa: BLE001
        st.warning(f"⚠️ Không thể xử lý ảnh đã upload: {exc}")
        return ""


# ==============================================================================
# 6. RENDER TRANG HTML BẰNG JINJA2 (render thẳng từ chuỗi HTML_TEMPLATE)
# ==============================================================================
def render_love_page(
    message: str,
    primary_color: str,
    bg_image_data: str,
    avatar_data: str,
    youtube_id: str,
    song_title: str,
    heart_count: int,
    heart_speed: float,
) -> str:
    """Render toàn bộ file HTML hoàn chỉnh (đã nhúng sẵn CSS + JS)."""

    env = Environment(autoescape=select_autoescape(disabled_extensions=("html",), default=False))
    template = env.from_string(HTML_TEMPLATE)

    secondary_color = adjust_color(primary_color, 40)
    accent_color = adjust_color(primary_color, 90)
    glow_color = hex_to_rgba_string(primary_color, 0.75)

    html_output = template.render(
        title="Trang Tình Yêu Của Bạn",
        message=message,
        primary_color=primary_color,
        secondary_color=secondary_color,
        accent_color=accent_color,
        glow_color=glow_color,
        bg_image_data=bg_image_data,
        avatar_data=avatar_data,
        youtube_id=youtube_id or "",
        song_title=song_title or "",
        heart_count=heart_count,
        heart_speed=heart_speed,
        generated_date=datetime.now().strftime("%d/%m/%Y"),
        css_content=CSS_CONTENT,
        js_content=JS_CONTENT,
    )
    return html_output


# ==============================================================================
# 7. LƯU TRANG ĐÃ TẠO + GHI INDEX
# ==============================================================================
def save_generated_page(html_content: str) -> str:
    """Lưu file HTML vào static/pages/<id>.html, trả về page_id."""
    page_id = uuid.uuid4().hex[:8]
    file_path = os.path.join(PAGES_DIR, f"{page_id}.html")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    _append_to_index(page_id)
    return page_id


def _append_to_index(page_id: str):
    """Ghi lại lịch sử các trang đã tạo (phục vụ tab Thống kê)."""
    index_data = []
    if os.path.exists(INDEX_JSON_PATH):
        try:
            with open(INDEX_JSON_PATH, "r", encoding="utf-8") as f:
                index_data = json.load(f)
        except Exception:  # noqa: BLE001
            index_data = []

    index_data.append(
        {
            "id": page_id,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
    )

    with open(INDEX_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)


def load_index():
    if not os.path.exists(INDEX_JSON_PATH):
        return []
    try:
        with open(INDEX_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return []


# ==============================================================================
# 8. XÁC ĐỊNH DOMAIN HIỆN TẠI ĐỂ SINH LINK CHIA SẺ
# ==============================================================================
def get_base_url() -> str:
    """
    Tự động nhận diện domain đang chạy ứng dụng để sinh link chia sẻ đúng:
      - Nếu có biến môi trường / secrets PUBLIC_BASE_URL -> ưu tiên dùng
        (khi bạn deploy sau một domain riêng, ví dụ domain.com).
      - Nếu chạy trên Streamlit Cloud / Render -> tự lấy Host từ header.
      - Nếu chạy local -> mặc định http://localhost:8501
    """
    try:
        custom_url = st.secrets.get("PUBLIC_BASE_URL", "")
        if custom_url:
            return custom_url.rstrip("/")
    except Exception:  # noqa: BLE001
        pass

    env_url = os.environ.get("PUBLIC_BASE_URL", "")
    if env_url:
        return env_url.rstrip("/")

    host = None
    try:
        headers = st.context.headers  # type: ignore[attr-defined]
        if headers:
            host = headers.get("Host") or headers.get("host")
    except Exception:  # noqa: BLE001
        host = None

    if host:
        is_https = (
            "streamlit.app" in host
            or "onrender.com" in host
            or "herokuapp.com" in host
            or os.environ.get("RENDER") is not None
        )
        scheme = "https" if is_https else "http"
        return f"{scheme}://{host}"

    return "http://localhost:8501"


def build_share_url(page_id: str) -> str:
    """
    Sinh link chia sẻ dạng {domain}/?page=<id>. Khi ai đó mở link này,
    Streamlit chạy lại app.py, hàm main() phát hiện query param "page"
    và tự hiển thị đúng trang tình yêu đó (xem render_page_viewer()).
    """
    base_url = get_base_url()
    return f"{base_url}/?page={page_id}"


# ==============================================================================
# 9. TẠO QR CODE
# ==============================================================================
def generate_qr_code_bytes(url: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#ff4d6d", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


# ==============================================================================
# 10. ROUTE XEM TRANG CHIA SẺ (?page=<id>)
# ==============================================================================
def render_page_viewer(page_id: str):
    """
    Được gọi khi URL có dạng .../?page=<id>. Đọc lại file HTML đã lưu
    trong static/pages/<id>.html và hiển thị TOÀN MÀN HÌNH, ẩn hết sidebar
    và giao diện tạo trang của Streamlit đi — đây chính là "trang tình yêu"
    mà người nhận link sẽ thấy.
    """
    file_path = os.path.join(PAGES_DIR, f"{page_id}.html")

    if not os.path.exists(file_path):
        st.error(
            "💔 Không tìm thấy trang này. Link có thể đã sai hoặc trang đã bị xoá."
        )
        st.caption(f"Mã trang: `{page_id}`")
        st.stop()

    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Ẩn toàn bộ khung Streamlit (header, menu, padding mặc định, footer)
    # để trang tình yêu hiển thị full màn hình, giống một trang web bình
    # thường chứ không phải nằm lồng trong app Streamlit.
    st.markdown(
        """
        <style>
            #MainMenu {visibility: hidden;}
            header[data-testid="stHeader"] {display: none;}
            footer {visibility: hidden;}
            .block-container {
                padding: 0 !important;
                margin: 0 !important;
                max-width: 100% !important;
            }
            iframe {
                display: block;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    components.html(html_content, height=1000, scrolling=True)


# ==============================================================================
# 11. GIAO DIỆN STREAMLIT
# ==============================================================================
def setup_page_config():
    st.set_page_config(
        page_title="Love Page Generator",
        page_icon="❤️",
        layout="centered",
        initial_sidebar_state="expanded",
    )


def render_sidebar():
    """Vẽ toàn bộ form nhập liệu ở sidebar, trả về dict chứa các giá trị input."""

    with st.sidebar:
        st.markdown(
            "<div style='text-align:center; font-size:52px;'>❤️</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h2 style='text-align:center; margin-top:-10px;'>Love Page Generator</h2>",
            unsafe_allow_html=True,
        )
        st.caption("Tạo trang HTML tình yêu chỉ trong vài giây 💌")

        st.divider()

        song_name = st.text_input(
            "🎵 Tên bài hát",
            placeholder="Ví dụ: Perfect - Ed Sheeran",
            help="Ứng dụng sẽ tự tìm bài hát này trên YouTube.",
        )

        youtube_link = st.text_input(
            "🔗 Link YouTube (nếu có)",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Nếu bạn đã có sẵn link YouTube, dán vào đây để dùng chính xác video này.",
        )

        message = st.text_area(
            "💬 Dòng chữ muốn hiện",
            value="Anh yêu em ❤️",
            height=90,
            help="Dòng chữ chính sẽ hiển thị nổi bật ở giữa trang.",
        )

        bg_image_file = st.file_uploader(
            "🖼️ Ảnh nền (không bắt buộc)",
            type=["jpg", "jpeg", "png", "webp"],
        )

        avatar_file = st.file_uploader(
            "🙂 Avatar (không bắt buộc)",
            type=["jpg", "jpeg", "png", "webp"],
        )

        primary_color = st.color_picker("🎨 Màu chủ đạo", value="#ff4d6d")

        heart_speed = st.slider(
            "💨 Tốc độ trái tim (giây/vòng bay)",
            min_value=3,
            max_value=15,
            value=8,
            help="Giá trị càng nhỏ, trái tim bay càng nhanh.",
        )

        heart_count = st.slider(
            "💗 Số lượng trái tim",
            min_value=10,
            max_value=100,
            value=30,
            step=5,
        )

        st.divider()

        submitted = st.button("❤️ Tạo trang", use_container_width=True, type="primary")

    return {
        "song_name": song_name,
        "youtube_link": youtube_link,
        "message": message,
        "bg_image_file": bg_image_file,
        "avatar_file": avatar_file,
        "primary_color": primary_color,
        "heart_speed": heart_speed,
        "heart_count": heart_count,
        "submitted": submitted,
    }


def handle_generation(inputs: dict):
    """Xử lý toàn bộ pipeline tạo trang khi người dùng bấm nút '❤️ Tạo trang'."""

    if not inputs["message"] or not inputs["message"].strip():
        st.error("⚠️ Vui lòng nhập dòng chữ muốn hiển thị trước khi tạo trang.")
        return

    progress_bar = st.progress(0, text="🚀 Bắt đầu tạo trang...")

    try:
        progress_bar.progress(15, text="🎵 Đang tìm bài hát trên YouTube...")
        youtube_id, song_title = resolve_youtube_id(
            inputs["song_name"], inputs["youtube_link"]
        )
        if inputs["song_name"] and not youtube_id and not inputs["youtube_link"]:
            st.warning(
                "⚠️ Không tìm thấy bài hát trên YouTube, trang sẽ được tạo mà không có nhạc nền."
            )

        progress_bar.progress(40, text="🖼️ Đang xử lý hình ảnh...")
        bg_image_data = uploaded_image_to_data_uri(
            inputs["bg_image_file"], MAX_IMAGE_DIMENSION
        )
        avatar_data = uploaded_image_to_data_uri(
            inputs["avatar_file"], MAX_AVATAR_DIMENSION
        )

        progress_bar.progress(65, text="🧩 Đang dựng giao diện trang tình yêu...")
        html_content = render_love_page(
            message=inputs["message"].strip(),
            primary_color=inputs["primary_color"],
            bg_image_data=bg_image_data,
            avatar_data=avatar_data,
            youtube_id=youtube_id or "",
            song_title=song_title,
            heart_count=inputs["heart_count"],
            heart_speed=inputs["heart_speed"],
        )

        progress_bar.progress(85, text="💾 Đang lưu trang lên server...")
        page_id = save_generated_page(html_content)
        share_url = build_share_url(page_id)

        progress_bar.progress(97, text="📱 Đang tạo mã QR...")
        qr_bytes = generate_qr_code_bytes(share_url)

        progress_bar.progress(100, text="✅ Hoàn tất!")

        result = {
            "page_id": page_id,
            "share_url": share_url,
            "qr_bytes": qr_bytes,
            "message": inputs["message"].strip(),
            "has_music": bool(youtube_id),
            "created_at": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
        }
        st.session_state["last_result"] = result
        st.session_state.setdefault("history", [])
        st.session_state["history"].insert(0, result)

    except Exception as exc:  # noqa: BLE001
        progress_bar.empty()
        st.error("❌ Đã có lỗi xảy ra trong quá trình tạo trang.")
        st.exception(exc)


def render_copy_button(url: str):
    """Nút Copy Link dùng JS clipboard API, nhúng qua components.html."""
    safe_url = json.dumps(url)  # escape an toàn để nhúng vào JS string
    components.html(
        f"""
        <div style="display:flex; gap:8px; align-items:center; font-family:sans-serif;">
            <button id="copy-btn" style="
                background:#ff4d6d; color:white; border:none; padding:8px 16px;
                border-radius:8px; cursor:pointer; font-size:14px; font-weight:600;">
                📋 Copy Link
            </button>
            <span id="copy-status" style="font-size:13px; color:#888;"></span>
        </div>
        <script>
            const btn = document.getElementById("copy-btn");
            const status = document.getElementById("copy-status");
            btn.addEventListener("click", async () => {{
                try {{
                    await navigator.clipboard.writeText({safe_url});
                    status.textContent = "Đã sao chép ✔";
                    setTimeout(() => status.textContent = "", 2000);
                }} catch (err) {{
                    status.textContent = "Không thể copy tự động, hãy copy thủ công.";
                }}
            }});
        </script>
        """,
        height=45,
    )


def render_result_section():
    """Hiển thị kết quả trang vừa tạo (nếu có) - link, QR, copy, preview."""

    result = st.session_state.get("last_result")
    if not result:
        return

    st.success("✅ Thành công! Trang tình yêu của bạn đã sẵn sàng.")

    st.markdown("#### 🔗 Link chia sẻ")
    st.code(result["share_url"], language="text")
    render_copy_button(result["share_url"])

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 📱 Mã QR")
        st.image(result["qr_bytes"], width=200)
        st.download_button(
            "⬇️ Tải mã QR",
            data=result["qr_bytes"],
            file_name=f"qr_{result['page_id']}.png",
            mime="image/png",
            use_container_width=True,
        )

    with col2:
        st.markdown("#### ℹ️ Thông tin")
        st.write(f"**Mã trang:** `{result['page_id']}`")
        st.write(f"**Tạo lúc:** {result['created_at']}")
        st.write(f"**Có nhạc nền:** {'Có 🎵' if result['has_music'] else 'Không'}")

    with st.expander("👀 Xem trước trang tình yêu"):
        page_path = os.path.join(PAGES_DIR, f"{result['page_id']}.html")
        if os.path.exists(page_path):
            with open(page_path, "r", encoding="utf-8") as f:
                preview_html = f.read()
            components.html(preview_html, height=650, scrolling=True)
        else:
            st.info("Không tìm thấy file xem trước.")


def render_history_tab():
    """Tab '📊 Thống kê': liệt kê toàn bộ trang đã từng tạo trên server."""
    entries = load_index()
    if not entries:
        st.info("Chưa có trang nào được tạo. Hãy sang tab 'Tạo trang' để bắt đầu!")
        return

    base_url = get_base_url()
    st.metric("Tổng số trang đã tạo", len(entries))
    st.divider()

    for entry in reversed(entries):
        page_id = entry.get("id", "")
        created_at = entry.get("created_at", "")
        share_url = f"{base_url}/?page={page_id}"

        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Mã trang:** `{page_id}`")
                st.write(f"🕒 Tạo lúc: {created_at}")
                st.write(f"🔗 [{share_url}]({share_url})")
            with col2:
                file_path = os.path.join(PAGES_DIR, f"{page_id}.html")
                exists = os.path.exists(file_path)
                st.write("✅ Còn tồn tại" if exists else "❌ Đã bị xoá")


def render_intro():
    st.title("💕 Love Page Generator")
    st.write(
        "Nhập thông tin ở thanh bên trái, sau đó bấm **❤️ Tạo trang** để tạo "
        "ra một trang HTML tình yêu lung linh: nền hồng blur, trái tim bay, "
        "particle, nhạc tự phát và dòng chữ toả sáng — rồi chia sẻ link cho "
        "người ấy!"
    )
    st.info(
        "💡 Mẹo: bạn có thể nhập tên bài hát (VD: *Perfect - Ed Sheeran*) để "
        "ứng dụng tự tìm trên YouTube, hoặc dán thẳng link YouTube nếu đã có."
    )


# ==============================================================================
# 12. MAIN
# ==============================================================================
def main():
    # ----------------------------------------------------------------------
    # Kiểm tra URL có tham số ?page=<id> không (đây là link chia sẻ mà
    # người khác mở ra). Phải đọc query params TRƯỚC set_page_config vì
    # 2 chế độ (xem trang / tạo trang) cần layout khác nhau.
    # ----------------------------------------------------------------------
    shared_page_id = st.query_params.get("page")

    if shared_page_id:
        st.set_page_config(
            page_title="💌 Trang Tình Yêu",
            page_icon="❤️",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
        render_page_viewer(shared_page_id)
        return

    setup_page_config()

    tab_create, tab_stats = st.tabs(["💌 Tạo trang", "📊 Thống kê"])

    with tab_create:
        render_intro()
        inputs = render_sidebar()

        if inputs["submitted"]:
            handle_generation(inputs)

        render_result_section()

    with tab_stats:
        render_history_tab()

    st.divider()
    st.caption(
        "Made with ❤️ using Streamlit · Jinja2 · yt-dlp · qrcode · Pillow — 1 file app.py duy nhất"
    )


if __name__ == "__main__":
    main()
