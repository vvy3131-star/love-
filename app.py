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
    streamlit run app.py --server.enableStaticServing true

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
}

.date-text {
    font-size: 13px;
    opacity: 0.55;
    letter-spacing: 0.5px;
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
}

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
}
"""

JS_CONTENT = r"""/* ==========================================================================
   LOVE PAGE GENERATOR - CLIENT SIDE EFFECTS
   ========================================================================== */

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

            if (p.alpha <= 0.1 || p.alpha >= 0.95) p.twinkleDir *= -1;
            if (p.y < -10) { p.y = window.innerHeight + 10; p.x = rand(0, window.innerWidth); }
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

    var HEART_SVG = '<svg viewBox="0 0 32 29" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M23.6 0c-3 0-5.9 1.6-7.6 4.3C14.3 1.6 11.4 0 8.4 0 3.8 0 0 3.8 0 8.4c0 8.4 12 17.3 15.2 19.6.5.4 1.1.4 1.6 0C20 25.7 32 16.8 32 8.4 32 3.8 28.2 0 23.6 0z"/></svg>';

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

    var ytPlayer = null;
    var isPlaying = false;

    function loadYouTubeAPI(callback) {
        if (window.YT && window.YT.Player) { callback(); return; }
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
                        try { e.target.playVideo(); } catch (err) {}
                    },
                    onStateChange: function (e) {
                        isPlaying = e.data === YT.PlayerState.PLAYING;
                        updatePlayButton();
                    }
                }
            });
        });
    }

    var ICON_PLAY = '<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M8 5v14l11-7z"/></svg>';
    var ICON_PAUSE = '<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>';

    function updatePlayButton() {
        var btn = document.getElementById("play-pause-btn");
        if (btn) btn.innerHTML = isPlaying ? ICON_PAUSE : ICON_PLAY;
    }

    function bindMusicControls() {
        var playBtn = document.getElementById("play-pause-btn");
        var volumeSlider = document.getElementById("volume-slider");
        if (playBtn) {
            playBtn.innerHTML = ICON_PLAY;
            playBtn.addEventListener("click", function () {
                if (!ytPlayer) return;
                if (isPlaying) ytPlayer.pauseVideo();
                else ytPlayer.playVideo();
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

    function bindTapOverlay() {
        var overlay = document.getElementById("tap-overlay");
        if (!overlay) return;
        function dismiss() {
            overlay.classList.add("hidden");
            if (ytPlayer && ytPlayer.playVideo) ytPlayer.playVideo();
            document.removeEventListener("click", dismiss);
            document.removeEventListener("touchstart", dismiss);
        }
        overlay.addEventListener("click", dismiss);
    }

    function init() {
        new ParticleEngine("particle-canvas");
        startFloatingHearts();
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

    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600;700&family=Playfair+Display:ital,wght@1,600&family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet" />

    <style>
        {{ css_content | safe }}
    </style>
</head>
<body 
    class="{% if bg_image_data %}has-bg-image{% endif %}"
    {% if bg_image_data %}style="background-image: url('{{ bg_image_data }}');"{% endif %}
    data-heart-count="{{ heart_count }}"
    data-heart-speed="{{ heart_speed }}"
    data-youtube-id="{{ youtube_id }}"
    data-song-title="{{ song_title }}"
    data-primary-color="{{ primary_color }}"
    data-message="{{ message }}"
>
    <div class="bg-overlay"></div>
    <div class="aurora-light"></div>
    <canvas id="particle-canvas"></canvas>
    <div id="hearts-container"></div>

    <div id="tap-overlay" class="tap-overlay">
        <div class="pulse-heart">❤️</div>
        <p>Chạm vào bất kỳ đâu để bắt đầu</p>
    </div>

    <div class="center-wrapper">
        <div class="glass-card">
            {% if avatar_data %}
            <div class="avatar-ring">
                <img src="{{ avatar_data }}" alt="Avatar" />
            </div>
            {% endif %}

            <h1 class="main-message">{{ message }}</h1>

            {% if sub_message %}
            <p class="sub-text">{{ sub_message }}</p>
            {% endif %}

            {% if date_str %}
            <p class="date-text">🗓️ {{ date_str }}</p>
            {% endif %}
        </div>
    </div>

    <div class="music-bar">
        <button id="play-pause-btn" class="play-btn" aria-label="Play/Pause"></button>
        <div class="track-info">
            <span class="track-title">{{ song_title or 'Đang phát nhạc nền' }}</span>
        </div>
        <div class="volume-wrap">
            <input type="range" id="volume-slider" min="0" max="100" value="70" />
        </div>
    </div>

    <div id="yt-player"></div>

    <script>
        {{ js_content | safe }}
    </script>
</body>
</html>
"""


# ==============================================================================
# 2. XỬ LÝ STATIC FOLDER & CONFIG STREAMLIT AUTO-FIX
# ==============================================================================

def ensure_streamlit_config():
    """Tự động tạo file .streamlit/config.toml để bật enableStaticServing."""
    os.makedirs(".streamlit", exist_ok=True)
    config_path = os.path.join(".streamlit", "config.toml")
    
    need_write = True
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "enableStaticServing = true" in content:
                need_write = False
                
    if need_write:
        with open(config_path, "a", encoding="utf-8") as f:
            f.write("\n[server]\nenableStaticServing = true\n")

ensure_streamlit_config()

# Tạo thư mục static để phục vụ các file trang đã sinh
STATIC_DIR = os.path.join(os.getcwd(), "static")
os.makedirs(STATIC_DIR, exist_ok=True)


# ==============================================================================
# 3. TIỆN ÍCH PYTHON & YT-DLP SEARCH
# ==============================================================================

def search_youtube_id(song_name: str) -> tuple[str, str]:
    """Tìm kiếm tên bài hát trên YouTube lấy ID và tiêu đề chuẩn."""
    if not song_name.strip():
        return "", ""
    
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "default_search": "ytsearch1",
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{song_name}", download=False)
            if info and "entries" in info and len(info["entries"]) > 0:
                video = info["entries"][0]
                return video.get("id", ""), video.get("title", song_name)
    except Exception as e:
        st.warning(f"Không thể tra cứu nhạc tự động: {e}")
    return "", song_name

def file_to_base64(uploaded_file) -> str:
    """Chuyển đổi file tải lên thành Data URI dạng base64."""
    if uploaded_file is None:
        return ""
    bytes_data = uploaded_file.getvalue()
    mime_type = uploaded_file.type or "image/png"
    base64_str = base64.b64encode(bytes_data).decode("utf-8")
    return f"data:{mime_type};base64,{base64_str}"

def render_html_page(data: dict) -> str:
    """Sử dụng Jinja2 render HTML từ template."""
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    template = env.from_string(HTML_TEMPLATE)
    return template.render(
        css_content=CSS_CONTENT,
        js_content=JS_CONTENT,
        title=data.get("title", "Trang Tình Yêu"),
        message=data.get("message", "Anh Yêu Em"),
        sub_message=data.get("sub_message", ""),
        date_str=data.get("date_str", ""),
        primary_color=data.get("primary_color", "#ff4d6d"),
        heart_count=data.get("heart_count", 25),
        heart_speed=data.get("heart_speed", 8),
        youtube_id=data.get("youtube_id", ""),
        song_title=data.get("song_title", ""),
        avatar_data=data.get("avatar_data", ""),
        bg_image_data=data.get("bg_image_data", "")
    )


# ==============================================================================
# 4. GIAO DIỆN STREAMLIT MAIN APP
# ==============================================================================

st.set_page_config(
    page_title="Love Page Generator",
    page_icon="💖",
    layout="wide"
)

st.title("💖 Love Page Generator — Tạo Trang Tình Yêu")
st.caption("Tạo trang web tỏ tình / kỷ niệm 1 file HTML duy nhất dễ dàng chia sẻ.")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("⚙️ Cấu hình nội dung")
    
    title_input = st.text_input("Tiêu đề trang (SEO/Tab trình duyệt)", "Gửi Người Anh Yêu 💖")
    message_input = st.text_area("Lời nhắn chính (Xuất hiện nổi bật)", "Anh Yêu Em Nhiều Lắm!")
    sub_message_input = st.text_input("Lời nhắn phụ (Nhỏ phía dưới)", "Cùng nhau đi hết đoạn đường đời nhé...")
    
    use_date = st.checkbox("Hiển thị ngày kỷ niệm", True)
    date_str = ""
    if use_date:
        selected_date = st.date_input("Chọn ngày", datetime.now())
        date_str = selected_date.strftime("%d/%m/%Y")
        
    st.divider()
    st.subheader("🎨 Giao diện & Hiệu ứng")
    
    primary_color = st.color_picker("Màu chủ đạo", "#ff4d6d")
    heart_count = st.slider("Số lượng trái tim bay", 5, 60, 25)
    heart_speed = st.slider("Tốc độ bay (giây)", 3, 15, 8)
    
    st.divider()
    st.subheader("🖼️ Hình ảnh & 🎵 Nhạc nền")
    
    avatar_file = st.file_uploader("Tải lên ảnh đại diện / Avatar (hình tròn)", type=["png", "jpg", "jpeg", "webp"])
    bg_file = st.file_uploader("Tải lên ảnh nền trang web (tùy chọn)", type=["png", "jpg", "jpeg", "webp"])
    
    song_query = st.text_input("Tên bài hát / Nhạc nền (Tự tìm trên YouTube)", "Chắc Ai Đó Sẽ Về")

with col_right:
    st.subheader("👁️ Xem trước & Xuất bản")
    
    yt_id = ""
    song_title = ""
    if song_query.strip():
        with st.spinner("Đang tìm nhạc trên YouTube..."):
            yt_id, song_title = search_youtube_id(song_query)
            if yt_id:
                st.success(f"Đã tìm thấy bài hát: **{song_title}**")
            else:
                st.warning("Không tìm thấy bài hát phù hợp trên YouTube, trang sẽ chạy không nhạc.")

    avatar_data = file_to_base64(avatar_file)
    bg_image_data = file_to_base64(bg_file)

    render_data = {
        "title": title_input,
        "message": message_input,
        "sub_message": sub_message_input,
        "date_str": date_str,
        "primary_color": primary_color,
        "heart_count": heart_count,
        "heart_speed": heart_speed,
        "youtube_id": yt_id,
        "song_title": song_title or song_query,
        "avatar_data": avatar_data,
        "bg_image_data": bg_image_data
    }

    final_html = render_html_page(render_data)

    st.write("### Live Preview")
    components.html(final_html, height=500, scrolling=True)

    st.divider()
    
    # Xử lý sinh Link và Lưu File Tĩnh
    if st.button("🚀 Sinh Trang & Tạo Link Chia Sẻ", type="primary"):
        file_id = str(uuid.uuid4())[:8]
        filename = f"love_{file_id}.html"
        filepath = os.path.join(STATIC_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_html)
            
        st.success("Tạo trang web thành công!")
        
        # Đường dẫn tĩnh công khai
        local_url = f"/app/static/{filename}"
        alt_url = f"/static/{filename}"
        
        st.markdown(f"**🔗 Đường dẫn truy cập công khai:**")
        st.code(local_url, language="text")
        st.caption(f"Nếu trang web chạy trên reverse proxy, bạn cũng có thể mở qua đường dẫn: `{alt_url}`")
        
        # Tạo QR Code để quét
        qr = qrcode.QRCode(box_size=5, border=2)
        qr.add_data(local_url)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        
        buf = io.BytesIO()
        img_qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="Quét QR để mở trang", width=200)

    st.download_button(
        label="📥 Tải về file HTML duy nhất",
        data=final_html,
        file_name="love_page.html",
        mime="text/html"
    )
