"""
==============================================================================
LOVE PAGE GENERATOR
------------------------------------------------------------------------------
Ứng dụng Streamlit cho phép người dùng tạo một trang HTML "tình yêu" (love
page) với nhạc nền tự phát, hiệu ứng trái tim bay, particle, glassmorphism...
Sau khi tạo, ứng dụng lưu file HTML vào thư mục static/pages/ (được Streamlit
serve công khai nhờ enableStaticServing = true trong .streamlit/config.toml)
và trả về một link chia sẻ dạng:

    http://localhost:8501/app/static/pages/<page_id>.html      (chạy local)
    https://<domain-that-is-hosting-app>/app/static/pages/<page_id>.html (deploy)

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
import requests
import streamlit as st
from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image

# yt_dlp được dùng để TÌM video Youtube phù hợp với tên bài hát người dùng
# nhập (chỉ lấy metadata / video id, KHÔNG tải file nhạc về).
import yt_dlp


# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
CSS_PATH = os.path.join(STATIC_DIR, "css", "style.css")
JS_PATH = os.path.join(STATIC_DIR, "js", "effects.js")
PAGES_DIR = os.path.join(STATIC_DIR, "pages")
INDEX_JSON_PATH = os.path.join(PAGES_DIR, "_index.json")

# Đảm bảo thư mục lưu trang đã tạo luôn tồn tại
os.makedirs(PAGES_DIR, exist_ok=True)

MAX_IMAGE_DIMENSION = 1600      # giới hạn chiều dài cạnh lớn nhất của ảnh nền
MAX_AVATAR_DIMENSION = 500      # giới hạn cho avatar
JPEG_QUALITY = 82               # chất lượng nén ảnh khi convert sang JPEG


# ==============================================================================
# 2. HÀM ĐỌC FILE TĨNH (CÓ CACHE ĐỂ TĂNG TỐC)
# ==============================================================================
@st.cache_data(show_spinner=False)
def load_text_file(path: str) -> str:
    """Đọc nội dung file text (CSS/JS) và cache lại để không đọc lại mỗi lần."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


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

            # Khi search, kết quả thường nằm trong result["entries"]
            if result and "entries" in result and len(result["entries"]) > 0:
                entry = result["entries"][0]
                video_id = entry.get("id")
                title = entry.get("title", song_name)
                return video_id, title

            # Trường hợp result trả về trực tiếp 1 video (hiếm khi xảy ra với search)
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
# 5. XỬ LÝ ẢNH UPLOAD (nén + chuyển sang base64 data URI để nhúng thẳng vào HTML)
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
        image = Image.open(uploaded_file)

        # Chuyển ảnh có kênh alpha (PNG) sang nền trắng khi nén JPEG
        if image.mode in ("RGBA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image.convert("RGBA"), mask=image.convert("RGBA").split()[-1])
            image = background
        else:
            image = image.convert("RGB")

        # Resize nếu ảnh quá lớn (giữ tỉ lệ)
        image.thumbnail((max_dimension, max_dimension), Image.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"

    except Exception as exc:  # noqa: BLE001
        st.warning(f"⚠️ Không thể xử lý ảnh đã upload: {exc}")
        return ""


# ==============================================================================
# 6. RENDER TRANG HTML BẰNG JINJA2
# ==============================================================================
def get_jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(disabled_extensions=("html",), default=False),
    )


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

    env = get_jinja_env()
    template = env.get_template("page.html")

    css_content = load_text_file(CSS_PATH)
    js_content = load_text_file(JS_PATH)

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
        css_content=css_content,
        js_content=js_content,
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
    """Ghi lại lịch sử các trang đã tạo (phục vụ thống kê / quản lý)."""
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


# ==============================================================================
# 8. XÁC ĐỊNH DOMAIN HIỆN TẠI ĐỂ SINH LINK CHIA SẺ
# ==============================================================================
def get_base_url() -> str:
    """
    Tự động nhận diện domain đang chạy ứng dụng để sinh link chia sẻ đúng:
      - Nếu có biến môi trường / secrets PUBLIC_BASE_URL -> ưu tiên dùng (khi
        bạn deploy sau một domain riêng, ví dụ domain.com).
      - Nếu chạy trên Streamlit Cloud / Render -> tự lấy Host từ request header.
      - Nếu chạy local -> mặc định http://localhost:8501
    """
    # 1) Cho phép override thủ công qua secrets.toml hoặc biến môi trường
    try:
        custom_url = st.secrets.get("PUBLIC_BASE_URL", "")
        if custom_url:
            return custom_url.rstrip("/")
    except Exception:  # noqa: BLE001 - không có secrets.toml cũng không sao
        pass

    env_url = os.environ.get("PUBLIC_BASE_URL", "")
    if env_url:
        return env_url.rstrip("/")

    # 2) Cố gắng đọc Host header từ request hiện tại (Streamlit >= 1.37)
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

    # 3) Mặc định khi chạy local
    return "http://localhost:8501"


def build_share_url(page_id: str) -> str:
    base_url = get_base_url()
    return f"{base_url}/app/static/pages/{page_id}.html"


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
# 10. GIAO DIỆN STREAMLIT
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
        # Bước 1: xác định video Youtube (nếu có)
        progress_bar.progress(15, text="🎵 Đang tìm bài hát trên YouTube...")
        youtube_id, song_title = resolve_youtube_id(
            inputs["song_name"], inputs["youtube_link"]
        )
        if inputs["song_name"] and not youtube_id and not inputs["youtube_link"]:
            st.warning(
                "⚠️ Không tìm thấy bài hát trên YouTube, trang sẽ được tạo mà không có nhạc nền."
            )

        # Bước 2: xử lý ảnh nền / avatar
        progress_bar.progress(40, text="🖼️ Đang xử lý hình ảnh...")
        bg_image_data = uploaded_image_to_data_uri(
            inputs["bg_image_file"], MAX_IMAGE_DIMENSION
        )
        avatar_data = uploaded_image_to_data_uri(
            inputs["avatar_file"], MAX_AVATAR_DIMENSION
        )

        # Bước 3: render HTML
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

        # Bước 4: lưu file + sinh link chia sẻ
        progress_bar.progress(85, text="💾 Đang lưu trang lên server...")
        page_id = save_generated_page(html_content)
        share_url = build_share_url(page_id)

        # Bước 5: sinh QR code
        progress_bar.progress(97, text="📱 Đang tạo mã QR...")
        qr_bytes = generate_qr_code_bytes(share_url)

        progress_bar.progress(100, text="✅ Hoàn tất!")

        # Lưu kết quả + lịch sử vào session_state để hiển thị sau khi rerun
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
    import streamlit.components.v1 as components

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
        import streamlit.components.v1 as components

        page_path = os.path.join(PAGES_DIR, f"{result['page_id']}.html")
        if os.path.exists(page_path):
            with open(page_path, "r", encoding="utf-8") as f:
                preview_html = f.read()
            components.html(preview_html, height=650, scrolling=True)
        else:
            st.info("Không tìm thấy file xem trước.")


def render_history_section():
    """Hiển thị danh sách các trang đã tạo trong phiên làm việc hiện tại."""
    history = st.session_state.get("history", [])
    if not history or len(history) <= 1:
        return

    with st.expander(f"📜 Lịch sử đã tạo trong phiên này ({len(history)} trang)"):
        for item in history:
            st.write(
                f"💗 `{item['page_id']}` — {item['created_at']} — "
                f"[{item['share_url']}]({item['share_url']})"
            )


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
# 11. MAIN
# ==============================================================================
def main():
    setup_page_config()
    render_intro()

    inputs = render_sidebar()

    if inputs["submitted"]:
        handle_generation(inputs)

    render_result_section()
    render_history_section()

    st.divider()
    st.caption(
        "Made with ❤️ using Streamlit · Jinja2 · yt-dlp · qrcode · Pillow"
    )


if __name__ == "__main__":
    main()
