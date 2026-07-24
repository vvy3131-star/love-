<!DOCTYPE html>
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
    <meta name="theme-color" content="#ff4d6d" />

    <!-- SEO / chia sẻ mạng xã hội -->
    <title>Test</title>
    <meta name="description" content="Anh yêu em ❤️" />
    <meta property="og:title" content="Test" />
    <meta property="og:description" content="Anh yêu em ❤️" />
    <meta property="og:type" content="website" />
    

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
        /* ==========================================================================
   LOVE PAGE GENERATOR - MAIN STYLESHEET
   Tác giả: Senior Python Developer
   Mô tả: Toàn bộ hiệu ứng nền, trái tim bay, glassmorphism, animation chữ,
          thanh điều khiển nhạc và responsive cho mọi thiết bị.
   Bản tối ưu hiệu năng: giảm blur, giảm shadow, thêm chế độ máy yếu (.low-fx).
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
    backdrop-filter: blur(4px) saturate(120%);
    -webkit-backdrop-filter: blur(4px) saturate(120%);
    background: linear-gradient(
        135deg,
        rgba(255, 77, 109, 0.55) 0%,
        rgba(43, 10, 24, 0.75) 60%,
        rgba(255, 143, 163, 0.55) 100%
    );
    pointer-events: none;
    contain: strict;
}

/* Ánh sáng lung linh - lớp glow tĩnh phía sau (KHÔNG animate blur để đỡ tốn
   GPU: chỉ dịch chuyển bằng transform, filter được tính 1 lần rồi cache) */
.aurora-light {
    position: fixed;
    inset: -20%;
    z-index: 0;
    background:
        radial-gradient(circle at 20% 30%, var(--glow-color) 0%, transparent 35%),
        radial-gradient(circle at 80% 70%, var(--accent-color) 0%, transparent 40%),
        radial-gradient(circle at 50% 90%, var(--secondary-color) 0%, transparent 45%);
    filter: blur(40px);
    opacity: 0.5;
    animation: auroraMove 22s ease-in-out infinite alternate;
    pointer-events: none;
    will-change: transform;
    transform: translateZ(0);
    contain: strict;
}

@keyframes auroraMove {
    0%   { transform: translate3d(0, 0, 0) scale(1); }
    50%  { transform: translate3d(-4%, 3%, 0) scale(1.08); }
    100% { transform: translate3d(4%, -3%, 0) scale(1.03); }
}

/* Chế độ máy yếu: tắt hẳn aurora động, giảm xuống lớp tĩnh nhẹ */
body.low-fx .aurora-light {
    animation: none;
    filter: blur(24px);
    opacity: 0.35;
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

/* Máy yếu: ẩn hẳn lớp particle canvas để tiết kiệm CPU */
body.low-fx #particle-canvas {
    display: none;
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
    contain: strict;
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
    /* Bỏ drop-shadow: filter trên nhiều phần tử animate cùng lúc rất tốn,
       thay bằng viền glow nhẹ ở chính SVG (xem HEART_SVG trong JS). */
}

.heart svg {
    width: 100%;
    height: 100%;
    display: block;
}

@keyframes floatUp {
    0% {
        transform: translate3d(0, 0, 0) rotate(0deg) scale(0.6);
        opacity: 0;
    }
    10% {
        opacity: 1;
    }
    50% {
        transform: translate3d(var(--drift, 30px), -50vh, 0) rotate(180deg) scale(1);
    }
    100% {
        transform: translate3d(calc(var(--drift, 30px) * -1), -110vh, 0) rotate(360deg) scale(0.5);
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
    will-change: transform, opacity;
}

@keyframes sparklePop {
    0% { transform: scale(0) translate3d(0, 0, 0); opacity: 1; }
    100% { transform: scale(1.6) translate3d(var(--sx, 20px), var(--sy, -20px), 0); opacity: 0; }
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
    backdrop-filter: blur(8px);
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
    backdrop-filter: blur(12px) saturate(130%);
    -webkit-backdrop-filter: blur(12px) saturate(130%);
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

/* Máy yếu: bỏ backdrop-filter (rất tốn khi có nội dung động phía sau),
   thay bằng nền đặc gần giống hiệu ứng kính mờ nhưng rẻ hơn nhiều */
body.low-fx .glass-card,
body.low-fx .music-bar,
body.low-fx .bg-overlay,
body.low-fx .tap-overlay {
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
}
body.low-fx .glass-card {
    background: rgba(43, 10, 24, 0.55);
}
body.low-fx .music-bar {
    background: rgba(43, 10, 24, 0.65);
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
    will-change: transform;
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
        0 0 24px var(--glow-color);
    animation:
        messageFadeScale 1.4s ease-out both,
        glowPulse 3.4s ease-in-out infinite 1.4s;
}

@keyframes messageFadeScale {
    0% { opacity: 0; transform: scale(0.7); filter: blur(6px); }
    60% { opacity: 1; transform: scale(1.05); filter: blur(0); }
    100% { opacity: 1; transform: scale(1); }
}

@keyframes glowPulse {
    0%, 100% {
        text-shadow: 0 0 10px var(--glow-color), 0 0 24px var(--glow-color);
    }
    50% {
        text-shadow: 0 0 16px var(--glow-color), 0 0 34px var(--glow-color);
    }
}

/* Máy yếu: tắt glow pulse nhấp nháy liên tục, giữ 1 lớp bóng tĩnh */
body.low-fx .main-message {
    animation: messageFadeScale 1.4s ease-out both;
    text-shadow: 0 0 12px var(--glow-color);
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
    backdrop-filter: blur(12px) saturate(130%);
    -webkit-backdrop-filter: blur(12px) saturate(130%);
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
    0%   { transform: translate3d(0, 0, 0); }
    100% { transform: translate3d(-50%, 0, 0); }
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


        /* ================= GHI ĐÈ BIẾN MÀU THEO NGƯỜI DÙNG CHỌN ================= */
        :root {
            --primary-color: #ff4d6d;
            --secondary-color: #ff8fa3;
            --accent-color: #ffd6e0;
            --glow-color: rgba(255,77,109,0.75);
            --heart-speed: 8s;
        }

        
    </style>
</head>
<body
    class=""
    data-heart-count="20"
    data-heart-speed="8"
    data-youtube-id="dQw4w9WgXcQ"
    data-song-title="Test Song"
    data-primary-color="#ff4d6d"
    data-message="Anh yêu em ❤️"
>
    <!-- Ghi chú: class "low-fx" được JS tự thêm vào <body> lúc chạy nếu phát
         hiện thiết bị yếu (xem detectLowPerfDevice() trong effects.js),
         không cần Jinja2 render sẵn vì phải kiểm tra bằng JS phía trình duyệt. -->

    <!-- ====================================================================
         LỚP NỀN: overlay hồng blur + ánh sáng lung linh (aurora)
         ==================================================================== -->
    <div class="bg-overlay"></div>
    <div class="aurora-light"></div>

    <!-- ====================================================================
         LỚP PARTICLE (canvas) - vẽ bằng JS, tự ẩn khi máy yếu
         ==================================================================== -->
    <canvas id="particle-canvas"></canvas>

    <!-- ====================================================================
         LỚP TRÁI TIM BAY LIÊN TỤC
         ==================================================================== -->
    <div id="hearts-container"></div>

    <!-- ====================================================================
         OVERLAY "CHẠM ĐỂ BẮT ĐẦU" (xử lý autoplay bị trình duyệt chặn)
         ==================================================================== -->
    
    <div class="tap-overlay" id="tap-overlay">
        <div class="pulse-heart">❤️</div>
        <p>Chạm vào màn hình để bắt đầu</p>
        <span class="small">Test Song</span>
    </div>
    

    <!-- ====================================================================
         NỘI DUNG TRUNG TÂM: avatar + dòng chữ + ngày tháng
         ==================================================================== -->
    <div class="center-wrapper">
        <div class="glass-card">

            

            <div class="main-message">Anh yêu em ❤️</div>

            <div class="sub-text">Được gửi bằng tất cả yêu thương</div>

            
            <div class="date-text">24/07/2026</div>
            
        </div>
    </div>

    <!-- ====================================================================
         THANH ĐIỀU KHIỂN NHẠC (chỉ hiện nếu có bài hát)
         ==================================================================== -->
    
    <div class="music-bar">
        <button id="play-pause-btn" class="play-btn" aria-label="Play/Pause"></button>

        <div class="track-info">
            <span class="track-title">Test Song</span>
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
    

    <!-- ====================================================================
         CHỮ KÝ CUỐI TRANG
         ==================================================================== -->
    <div class="signature-footer">💌 made with Love Page Generator</div>

    <!-- ====================================================================
         SCRIPT: nhúng toàn bộ static/js/effects.js
         ==================================================================== -->
    <script>
        /* ==========================================================================
   LOVE PAGE GENERATOR - CLIENT SIDE EFFECTS (bản tối ưu hiệu năng)
   File này chạy trong trang HTML đã tạo (được nhúng trực tiếp vào <script>).
   Toàn bộ config (số lượng tim, tốc độ, youtube id...) được đọc từ
   thuộc tính data-* gắn trên thẻ <body> do Jinja2 render ra.

   Các thay đổi chính để hết giật/lag trên máy yếu:
     - Tự phát hiện thiết bị yếu (CPU, RAM, độ rộng màn hình, mạng chậm,
       prefers-reduced-motion) -> bật class "low-fx" trên <body>.
     - Bỏ shadowBlur trong canvas particle (phép vẽ tốn nhất), dùng
       fillStyle đơn giản; giảm số hạt và tự tắt hẳn canvas khi low-fx.
     - Giới hạn số tim bay tối đa cùng lúc trong DOM (không tạo vô hạn).
     - Giảm số lượng sparkle sinh ra mỗi lần chạm, giới hạn tần suất.
     - Tạm dừng toàn bộ vòng lặp animation khi tab bị ẩn (visibilitychange)
       hoặc khi phần tử particle không nằm trong khung nhìn.
     - Giảm nhịp tim mặc định + chỉ vẽ canvas ở khoảng 30fps thay vì 60fps.
   ========================================================================== */

(function () {
    "use strict";

    /* ----------------------------------------------------------------------
       0. ĐỌC CẤU HÌNH TỪ BODY DATA ATTRIBUTES
       ---------------------------------------------------------------------- */
    var body = document.body;
    var CONFIG = {
        heartCount: parseInt(body.getAttribute("data-heart-count") || "20", 10),
        heartSpeed: parseFloat(body.getAttribute("data-heart-speed") || "8"),
        youtubeId: body.getAttribute("data-youtube-id") || "",
        songTitle: body.getAttribute("data-song-title") || "",
        primaryColor: body.getAttribute("data-primary-color") || "#ff4d6d",
        message: body.getAttribute("data-message") || ""
    };

    /* ----------------------------------------------------------------------
       0b. PHÁT HIỆN THIẾT BỊ / TRÌNH DUYỆT YẾU -> BẬT "low-fx"
       ---------------------------------------------------------------------- */
    function detectLowPerfDevice() {
        try {
            var reducedMotion =
                window.matchMedia &&
                window.matchMedia("(prefers-reduced-motion: reduce)").matches;
            if (reducedMotion) return true;

            var cores = navigator.hardwareConcurrency || 4;
            var mem = navigator.deviceMemory || 4; // GB, không phải mọi trình duyệt hỗ trợ
            var narrowScreen = window.innerWidth <= 480;
            var slowNet =
                navigator.connection &&
                (navigator.connection.saveData ||
                    /2g/.test(navigator.connection.effectiveType || ""));

            if (cores <= 4 && mem <= 4) return true;
            if (slowNet) return true;
            if (narrowScreen && cores <= 6) return true;

            return false;
        } catch (err) {
            return false;
        }
    }

    var LOW_FX = detectLowPerfDevice();
    if (LOW_FX) {
        body.classList.add("low-fx");
    }

    // Ngân sách hiệu ứng tuỳ theo mức hiệu năng thiết bị
    var MAX_CONCURRENT_HEARTS = LOW_FX ? 10 : 26;
    var HEART_SPAWN_TARGET = LOW_FX
        ? Math.min(CONFIG.heartCount, 12)
        : Math.min(CONFIG.heartCount, 45);
    var PARTICLE_COUNT = LOW_FX ? 0 : (window.innerWidth < 700 ? 24 : 40);
    var MAX_CONCURRENT_SPARKLES = LOW_FX ? 4 : 10;
    var SPARKLE_PER_TAP = LOW_FX ? 1 : 2;

    var pageIsVisible = !document.hidden;
    document.addEventListener("visibilitychange", function () {
        pageIsVisible = !document.hidden;
    });

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
       - Không dùng shadowBlur (rất tốn CPU/GPU khi lặp lại hàng chục lần
         mỗi frame). Thay vào đó vẽ 2 vòng tròn chồng nhau (lõi + viền mờ)
         để vẫn có cảm giác lung linh nhưng rẻ hơn nhiều.
       - Giới hạn ~30fps thay vì chạy tối đa theo màn hình (thường 60-120fps)
         vì particle nền không cần mượt như animation chính.
       - Tự dừng vẽ khi tab bị ẩn.
       ---------------------------------------------------------------------- */
    function ParticleEngine(canvasId, count) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas || !count) return;
        this.ctx = this.canvas.getContext("2d", { alpha: true });
        this.particles = [];
        this.count = count;
        this.lastFrameTime = 0;
        this.frameInterval = 1000 / 30; // giới hạn ~30fps
        this.dpr = Math.min(window.devicePixelRatio || 1, 1.5); // tránh canvas quá to trên màn hình retina
        this.resize();
        this.init();

        var resizeTimer = null;
        window.addEventListener("resize", function () {
            if (resizeTimer) window.clearTimeout(resizeTimer);
            resizeTimer = window.setTimeout(this.resize.bind(this), 200);
        }.bind(this));

        this.loop = this.loop.bind(this);
        requestAnimationFrame(this.loop);
    }

    ParticleEngine.prototype.resize = function () {
        this.canvas.width = Math.floor(window.innerWidth * this.dpr);
        this.canvas.height = Math.floor(window.innerHeight * this.dpr);
        this.canvas.style.width = "100%";
        this.canvas.style.height = "100%";
        this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    };

    ParticleEngine.prototype.init = function () {
        this.particles = [];
        for (var i = 0; i < this.count; i++) {
            this.particles.push({
                x: rand(0, window.innerWidth),
                y: rand(0, window.innerHeight),
                r: rand(0.8, 2.2),
                vx: rand(-0.12, 0.12),
                vy: rand(-0.2, -0.04),
                alpha: rand(0.15, 0.7),
                twinkleSpeed: rand(0.004, 0.014),
                twinkleDir: pick([1, -1])
            });
        }
    };

    ParticleEngine.prototype.loop = function (now) {
        requestAnimationFrame(this.loop);

        if (!pageIsVisible || !this.ctx) return;

        if (now - this.lastFrameTime < this.frameInterval) return;
        this.lastFrameTime = now;

        var w = window.innerWidth;
        var h = window.innerHeight;
        this.ctx.clearRect(0, 0, w, h);

        for (var i = 0; i < this.particles.length; i++) {
            var p = this.particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.alpha += p.twinkleSpeed * p.twinkleDir;

            if (p.alpha <= 0.1 || p.alpha >= 0.85) {
                p.twinkleDir *= -1;
            }
            if (p.y < -10) {
                p.y = h + 10;
                p.x = rand(0, w);
            }
            if (p.x < -10) p.x = w + 10;
            if (p.x > w + 10) p.x = -10;

            // Không có shadowBlur: chỉ 1 lần fill tròn, rẻ hơn rất nhiều
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            this.ctx.fillStyle = "rgba(255,255,255," + p.alpha.toFixed(2) + ")";
            this.ctx.fill();
        }
    };

    /* ----------------------------------------------------------------------
       3. TRÁI TIM BAY LIÊN TỤC (Floating Hearts) - có giới hạn số lượng
       ---------------------------------------------------------------------- */
    var HEART_SVG =
        '<svg viewBox="0 0 32 29" xmlns="http://www.w3.org/2000/svg">' +
        '<path fill="currentColor" d="M23.6 0c-3 0-5.9 1.6-7.6 4.3C14.3 1.6 11.4 0 8.4 0 3.8 0 0 3.8 0 8.4c0 8.4 12 17.3 15.2 19.6.5.4 1.1.4 1.6 0C20 25.7 32 16.8 32 8.4 32 3.8 28.2 0 23.6 0z"/>' +
        "</svg>";
    // (Lưu ý: path phía trên giữ nguyên hình trái tim gốc, chỉ tối ưu phần JS xung quanh.)

    var liveHeartCount = 0;

    function createHeart(container) {
        if (liveHeartCount >= MAX_CONCURRENT_HEARTS) return;

        var heart = document.createElement("div");
        heart.className = "heart";

        var size = rand(14, 30);
        var left = rand(0, 100);
        var drift = rand(-50, 50);
        var duration = rand(CONFIG.heartSpeed * 0.8, CONFIG.heartSpeed * 1.25);
        var delay = rand(0, 1.5);

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
        liveHeartCount++;

        window.setTimeout(function () {
            if (heart.parentNode) heart.parentNode.removeChild(heart);
            liveHeartCount = Math.max(0, liveHeartCount - 1);
        }, (duration + delay) * 1000 + 400);
    }

    function startFloatingHearts() {
        var container = document.getElementById("hearts-container");
        if (!container) return;

        for (var i = 0; i < HEART_SPAWN_TARGET; i++) {
            window.setTimeout(function () {
                createHeart(container);
            }, rand(0, 4000));
        }

        // Nhịp sinh tim mới: chậm hơn khi ở chế độ máy yếu, và không bao giờ
        // vượt quá MAX_CONCURRENT_HEARTS nhờ kiểm tra trong createHeart().
        var intervalMs = LOW_FX ? 900 : Math.max(350, 6000 / Math.max(HEART_SPAWN_TARGET, 1));
        window.setInterval(function () {
            if (!pageIsVisible) return;
            createHeart(container);
        }, intervalMs);
    }

    /* ----------------------------------------------------------------------
       4. SPARKLE LẤP LÁNH KHI CHẠM / CLICK MÀN HÌNH (có giới hạn + throttle)
       ---------------------------------------------------------------------- */
    var liveSparkleCount = 0;
    var lastSparkleTime = 0;
    var SPARKLE_THROTTLE_MS = 80;

    function spawnSparkle(x, y) {
        if (liveSparkleCount >= MAX_CONCURRENT_SPARKLES) return;

        var s = document.createElement("div");
        s.className = "sparkle";
        s.style.left = x + "px";
        s.style.top = y + "px";
        s.style.setProperty("--sx", rand(-30, 30) + "px");
        s.style.setProperty("--sy", rand(-40, -10) + "px");
        document.body.appendChild(s);
        liveSparkleCount++;

        window.setTimeout(function () {
            if (s.parentNode) s.parentNode.removeChild(s);
            liveSparkleCount = Math.max(0, liveSparkleCount - 1);
        }, 950);
    }

    function bindSparkleEvents() {
        document.addEventListener("click", function (e) {
            var now = performance.now();
            if (now - lastSparkleTime < SPARKLE_THROTTLE_MS) return;
            lastSparkleTime = now;
            for (var i = 0; i < SPARKLE_PER_TAP; i++) {
                spawnSparkle(e.clientX + rand(-8, 8), e.clientY + rand(-8, 8));
            }
        });
        document.addEventListener(
            "touchstart",
            function (e) {
                var now = performance.now();
                if (now - lastSparkleTime < SPARKLE_THROTTLE_MS) return;
                lastSparkleTime = now;
                var t = e.touches[0];
                if (!t) return;
                for (var i = 0; i < SPARKLE_PER_TAP; i++) {
                    spawnSparkle(t.clientX + rand(-8, 8), t.clientY + rand(-8, 8));
                }
            },
            { passive: true }
        );
    }

    /* ----------------------------------------------------------------------
       5. ĐIỀU KHIỂN NHẠC QUA YOUTUBE IFRAME API
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
       6. OVERLAY "CHẠM ĐỂ BẮT ĐẦU" - xử lý chính sách chặn autoplay có âm thanh
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

        window.setTimeout(function () {
            if (isPlaying) {
                overlay.classList.add("hidden");
            }
        }, 1200);
    }

    /* ----------------------------------------------------------------------
       7. MARQUEE TÊN BÀI HÁT NẾU QUÁ DÀI
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
       8. KHỞI TẠO TOÀN BỘ KHI TRANG SẴN SÀNG
       ---------------------------------------------------------------------- */
    function init() {
        if (PARTICLE_COUNT > 0) {
            new ParticleEngine("particle-canvas", PARTICLE_COUNT);
        }
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

        // Sparkle định kỳ quanh chữ chính: giảm tần suất, tắt hẳn ở low-fx
        if (!LOW_FX) {
            var messageEl = document.querySelector(".main-message");
            if (messageEl) {
                window.setInterval(function () {
                    if (!pageIsVisible) return;
                    var rect = messageEl.getBoundingClientRect();
                    spawnSparkle(
                        rect.left + rand(0, rect.width),
                        rect.top + rand(0, rect.height)
                    );
                }, 2400);
            }
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();

    </script>
</body>
</html>
