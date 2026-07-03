"""Lightweight i18n support.

A tiny dictionary-based translation catalog with no external dependencies and no
compilation step. The selected language is stored in the Flask session. Templates
receive the ``t`` helper, ``current_lang`` and ``languages`` via a context
processor (see ``app/__init__.py``); WTForms labels use ``lazy_translate`` so the
text is resolved per request instead of at import time.
"""

from flask import session
from markupsafe import escape

# Supported languages: code -> human-readable name shown in the switcher.
LANGUAGES = {
    "en": "English",
    "uk": "Українська",
}

DEFAULT_LANGUAGE = "en"


def get_locale():
    """Return the active language code from the session, falling back to default."""
    try:
        lang = session.get("lang")
    except RuntimeError:
        # Outside of a request context (e.g. import time): use the default.
        lang = None
    return lang if lang in LANGUAGES else DEFAULT_LANGUAGE


def translate(key):
    """Translate a catalog key for the active language.

    Falls back to English and then to the key itself, so a missing key never
    raises and is easy to spot in the rendered page.
    """
    locale = get_locale()
    catalog = TRANSLATIONS.get(locale, {})
    if key in catalog:
        return catalog[key]
    return TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)


class _LazyString:
    """A string proxy that resolves a translation key at render time.

    Used for WTForms field/button labels, which are evaluated when the form class
    is imported. Rendering (str/escape) happens inside a request, so the correct
    language is picked up then.
    """

    def __init__(self, key):
        self._key = key

    def __str__(self):
        return translate(self._key)

    def __html__(self):
        return str(escape(str(self)))

    def __mod__(self, other):
        # WTForms applies "message % values" to validator messages.
        return str(self) % other


def lazy_translate(key):
    """Return a lazily-evaluated translation proxy for use in form definitions."""
    return _LazyString(key)


# Translation catalog. English values are kept verbatim with the existing UI text.
TRANSLATIONS = {
    "en": {
        # --- Brand / common ---
        "site_title": "Literary Diary",
        # --- Navigation (header.html) ---
        "nav_home": "Home",
        "nav_login": "Login",
        "nav_register": "Register",
        "nav_api": "API",
        "nav_about": "About",
        "nav_contact": "Contact",
        "nav_menu": "Menu",
        "nav_my_notes": "MY NOTES",
        "nav_log_out": "LOG OUT",
        "nav_account_settings": "ACCOUNT SETTINGS",
        "nav_language": "Language",
        # --- Footer / cookie banner ---
        "footer_privacy": "Privacy Policy",
        "cookie_text": "This site uses a session cookie for authentication. No analytics or third-party tracking.",
        "cookie_ok": "OK",
        # --- Home (index.html) ---
        "index_my_notes_title": "My Notes",
        "index_my_notes_subtitle": "Notes you have published on Literary Diary.",
        "index_subtitle": "A quiet place for readers to record, reflect, and share.",
        "btn_create_note": "Create New Note",
        "btn_older_notes": "Older Notes →",
        "btn_newer_notes": "← Newer Notes",
        # --- Note meta (index.html, note.html) ---
        "meta_book": "Book:",
        "meta_posted_by": "Posted by",
        "meta_on": "on",
        # --- Note detail (note.html) ---
        "btn_edit_note": "Edit Note",
        "btn_delete_note": "Delete Note",
        "btn_discuss_ai": "Discuss with AI",
        "discuss_title": "Discuss with AI",
        "discuss_placeholder": "Type your message…",
        "discuss_send": "Send",
        "discuss_thinking": "Thinking…",
        "discuss_error": "Something went wrong. Please try again.",
        "discuss_back": "Back to note",
        "discuss_notice": "This conversation is temporary — it isn't saved and disappears when you leave the page.",
        "btn_generate_image": "Generate new image with AI",
        "img_generating": "Generating…",
        # --- New/edit note (make-note.html) ---
        "note_new_title": "New Note",
        "note_edit_title": "Edit Note",
        "note_make_subtitle": "You're going to make a great note!",
        "btn_search": "Search",
        # --- About (about.html) ---
        "about_title": "About Literary Diary",
        "about_subtitle": "Why we built this space.",
        "about_p1": "Literary Diary is a space for passionate readers to record their thoughts, impressions, and discoveries while reading.",
        "about_p2": "Each note you write becomes part of your personal reading history - a quiet reflection of your inner world as it grows with every book.",
        "about_p3": "Whether you jot down favorite quotes, summarize a chapter, or capture a fleeting idea - this is your place to preserve those moments.",
        # --- Contact (contact.html) ---
        "contact_title": "Get in Touch",
        "contact_subtitle": "We'd love to hear from you.",
        "contact_p1": "Have a suggestion, bug report, or just a kind word? Fill out the form below to send us a message.",
        "contact_notice_pre": "Your name, email address, and message will be sent to our team via",
        "contact_notice_mid": ". They will not be stored in our database. See our",
        "contact_notice_privacy_link": "Privacy Policy",
        "contact_notice_post": "for details.",
        # --- API docs (api.html) ---
        "api_title": "API Documentation",
        "api_subtitle": "REST API for the Literature Diary.",
        "api_overview_heading": "API Overview",
        "api_overview_body": "The Literature Diary API provides programmatic access to public notes and allows authenticated users to create, update, and delete their own content.",
        "api_base_url_heading": "Base URL",
        "api_auth_heading": "Authentication",
        "api_auth_public": "read-only access to notes",
        "api_auth_authenticated": "create, update, and delete notes",
        "api_auth_public_label": "Public:",
        "api_auth_authenticated_label": "Authenticated:",
        "api_auth_session": "Session-based authentication using",
        "api_notes_heading": "Notes Endpoints",
        "api_get_desc": "List notes: anonymous users see only public ones; signed-in users also see their private notes; site admin (",
        "api_get_desc_2": " 1) sees all. Each item includes boolean",
        "api_post_desc": "Create a new note (authentication required). Request body may include optional boolean",
        "api_post_desc_2": " (default public); the created note and list/detail responses include",
        "api_put_desc": "Update an existing note (owner only); you can change visibility with",
        "api_put_desc_2": ", reflected in the JSON response.",
        "api_delete_desc": "Delete a note (owner only).",
        "api_delete_id": "integer note identifier",
        "api_footer_pre": "Full API description and examples are available on",
        "api_footer_link": "GitHub",
        # --- Privacy (privacy.html) ---
        "privacy_title": "Privacy Policy",
        "privacy_subtitle": "How we collect, use, and protect your data.",
        "privacy_last_updated": "Last updated: June 2026",
        "privacy_h1": "1. Data We Collect",
        "privacy_collect_intro": "When you register and use Literary Diary, we store the following personal data:",
        "privacy_collect_account_label": "Account information",
        "privacy_collect_account": "— your email address, display name, and a hashed (PBKDF2-SHA256) copy of your password. Your plain-text password is never stored.",
        "privacy_collect_notes_label": "Notes",
        "privacy_collect_notes": "— title, subtitle, body, book title, date, cover image URL, and visibility setting (public or private).",
        "privacy_collect_comments_label": "Comments",
        "privacy_collect_comments": "— the text of comments you post on notes.",
        "privacy_collect_no_contact": "We do",
        "privacy_collect_no_contact_strong": "not",
        "privacy_collect_no_contact_2": "store contact form submissions locally. Messages sent through the contact form are forwarded via SendGrid (see Section 3) and are not retained in our database.",
        "privacy_h2": "2. Cookies",
        "privacy_cookies_p1": "We set a single session cookie when you log in. It keeps you authenticated while you browse. It is deleted when your session ends.",
        "privacy_cookies_p2_pre": "We use",
        "privacy_cookies_p2_strong": "no analytics cookies",
        "privacy_cookies_p2_post": ", advertising cookies, or third-party tracking cookies.",
        "privacy_h3": "3. Third-Party Processors",
        "privacy_third_party_intro": "Using the site causes your browser to contact several external services. Each receives limited technical data (typically your IP address and browser User-Agent):",
        "privacy_table_service": "Service",
        "privacy_table_when": "When contacted",
        "privacy_table_data": "Data sent",
        "privacy_gravatar_when": "Pages that show comments",
        "privacy_gravatar_data": "An MD5 hash of your email address, used to load your avatar",
        "privacy_sendgrid_when": "When you submit the contact form",
        "privacy_sendgrid_data": "Your name, email address, and message",
        "privacy_gfonts_when": "Every page load",
        "privacy_gfonts_data": "IP address, browser User-Agent, timestamp",
        "privacy_fa_when": "Every page load",
        "privacy_fa_data": "IP address, browser User-Agent, timestamp",
        "privacy_jsdelivr_when": "Every page load",
        "privacy_jsdelivr_data": "IP address, browser User-Agent, timestamp",
        "privacy_openlibrary_when": "When you search for a book while writing a note",
        "privacy_openlibrary_data": "Your search query",
        "privacy_anthropic_when": "When you use \"Discuss with AI\" on one of your notes",
        "privacy_anthropic_data": "The note's title, subtitle, book, and content, plus the messages you send in the discussion",
        "privacy_ai_discussions": "AI discussions of your notes are processed by Anthropic to generate replies and are not stored in our database. The conversation is temporary and is lost when you leave the page.",
        "privacy_h4": "4. Your Rights",
        "privacy_rights_intro": "Under the General Data Protection Regulation (GDPR) you have the following rights over your personal data:",
        "privacy_rights_access_label": "Right of access and portability (Art. 15, 20)",
        "privacy_rights_access_pre": "— You can download a full copy of your data (profile, notes, and comments) in JSON format at any time via the",
        "privacy_rights_access_link": "data export endpoint",
        "privacy_rights_access_post": ".",
        "privacy_rights_rectification_label": "Right to rectification (Art. 16)",
        "privacy_rights_rectification": "— You can edit or update any note you have written from within the app.",
        "privacy_rights_erasure_label": "Right to erasure (Art. 17)",
        "privacy_rights_erasure": "— You can permanently delete your account, including all your notes and comments, from the account menu (DELETE ACCOUNT). This action is irreversible.",
        "privacy_rights_restrict_label": "Right to restrict processing or object (Art. 18, 21)",
        "privacy_rights_restrict": "— You can set any note to private at any time, limiting its visibility to yourself only. For broader restrictions or objections, contact us using the details below.",
        "privacy_h5": "5. Contact",
        "privacy_contact_pre": "For any privacy-related requests not covered by the self-service options above, please use the",
        "privacy_contact_link": "contact form",
        "privacy_contact_post": ".",
        # --- Auth pages (login/register/reset) ---
        "auth_login_title": "Log In",
        "auth_login_subtitle": "Enter your world of books and reflections.",
        "auth_forgot_link": "Forgot your password?",
        "auth_register_title": "Register",
        "auth_register_subtitle": "Join our community of readers.",
        "auth_forgot_title": "Forgot Password",
        "auth_forgot_subtitle": "Enter your email to receive a reset link.",
        "auth_reset_title": "Reset Password",
        "auth_reset_subtitle": "Enter your new password.",
        # --- Account (account.html) ---
        "account_title": "Account Settings",
        "account_name": "Name",
        "account_email": "Email",
        "account_download": "DOWNLOAD MY DATA",
        "account_download_help": "Returns your profile, notes, and comments as JSON.",
        "account_change_password": "CHANGE PASSWORD",
        "account_change_password_help": "A reset link will be sent to your email address.",
        "account_delete": "DELETE ACCOUNT",
        "account_delete_help": "Permanently removes your account, notes, and comments.",
        # --- Delete account (delete_account.html) ---
        "delete_title": "Delete Account",
        "delete_subtitle": "This action cannot be undone",
        "delete_warning": "Deleting your account will permanently remove your profile, all your notes, and all comments — including comments left by others on your notes.",
        "delete_confirm": "DELETE MY ACCOUNT",
        "delete_cancel": "CANCEL",
        # --- Form labels (WTForms) ---
        "form_email": "Email",
        "form_email_address": "Email address",
        "form_password": "Password",
        "form_name": "Name",
        "form_new_password": "New Password",
        "form_confirm_password": "Confirm Password",
        "form_passwords_must_match": "Passwords must match.",
        "form_sign_up": "SIGN ME UP!",
        "form_log_in": "LET ME IN!",
        "form_delete_account": "DELETE MY ACCOUNT",
        "form_send_reset_link": "SEND RESET LINK",
        "form_set_new_password": "SET NEW PASSWORD",
        "form_note_title": "Note Title",
        "form_note_subtitle": "Note Subtitle",
        "form_note_image_url": "Note Image URL",
        "form_book": "Book",
        "form_visibility": "Note visibility",
        "form_visibility_public": "Public — visible to everyone",
        "form_visibility_private": "Private — only you (and site admin)",
        "form_note_content": "Note Content",
        "form_submit_note": "Submit Note",
        "form_comment": "Comment",
        "form_submit_comment": "Submit Comment",
        "form_message": "Message",
        "form_submit_message": "Submit Message",
        # --- Flash messages ---
        "flash_email_exists": "You've already singed up with that email, log in instead!",
        "flash_email_not_found": "That email does not exist, please retry again.",
        "flash_password_incorrect": "Password incorrect, please try again.",
        "flash_reset_sent": "If that email is registered, a reset link has been sent.",
        "flash_reset_invalid": "The reset link is invalid or has expired.",
        "flash_password_updated": "Your password has been updated. Please log in.",
        "flash_message_sent": "Your message has been sent successfully!",
        "flash_message_failed": "Something went wrong. Please try again later.",
        "flash_image_generated": "A new image has been generated for your note.",
        "flash_image_failed": "Image generation failed. Please try again later.",
    },
    "uk": {
        # --- Brand / common ---
        "site_title": "Літературний щоденник",
        # --- Navigation (header.html) ---
        "nav_home": "Головна",
        "nav_login": "Увійти",
        "nav_register": "Реєстрація",
        "nav_api": "API",
        "nav_about": "Про нас",
        "nav_contact": "Контакти",
        "nav_menu": "Меню",
        "nav_my_notes": "МОЇ НОТАТКИ",
        "nav_log_out": "ВИЙТИ",
        "nav_account_settings": "НАЛАШТУВАННЯ АКАУНТА",
        "nav_language": "Мова",
        # --- Footer / cookie banner ---
        "footer_privacy": "Політика конфіденційності",
        "cookie_text": "Цей сайт використовує сесійний cookie для автентифікації. Без аналітики та сторонніх трекерів.",
        "cookie_ok": "OK",
        # --- Home (index.html) ---
        "index_my_notes_title": "Мої нотатки",
        "index_my_notes_subtitle": "Нотатки, які ви опублікували в Літературному щоденнику.",
        "index_subtitle": "Тихе місце, де читачі занотовують, осмислюють і діляться.",
        "btn_create_note": "Створити нотатку",
        "btn_older_notes": "Старіші нотатки →",
        "btn_newer_notes": "← Новіші нотатки",
        # --- Note meta (index.html, note.html) ---
        "meta_book": "Книга:",
        "meta_posted_by": "Автор:",
        "meta_on": "·",
        # --- Note detail (note.html) ---
        "btn_edit_note": "Редагувати нотатку",
        "btn_delete_note": "Видалити нотатку",
        "btn_discuss_ai": "Обговорити з AI",
        "discuss_title": "Обговорення з AI",
        "discuss_placeholder": "Введіть повідомлення…",
        "discuss_send": "Надіслати",
        "discuss_thinking": "Думаю…",
        "discuss_error": "Щось пішло не так. Спробуйте ще раз.",
        "discuss_back": "Назад до нотатки",
        "discuss_notice": "Ця розмова тимчасова — вона не зберігається і зникає, коли ви залишаєте сторінку.",
        "btn_generate_image": "Згенерувати зображення з AI",
        "img_generating": "Генеруємо…",
        # --- New/edit note (make-note.html) ---
        "note_new_title": "Нова нотатка",
        "note_edit_title": "Редагувати нотатку",
        "note_make_subtitle": "У вас вийде чудова нотатка!",
        "btn_search": "Пошук",
        # --- About (about.html) ---
        "about_title": "Про Літературний щоденник",
        "about_subtitle": "Навіщо ми створили цей простір.",
        "about_p1": "Літературний щоденник — це простір для пристрасних читачів, щоб занотовувати свої думки, враження та відкриття під час читання.",
        "about_p2": "Кожна написана вами нотатка стає частиною вашої особистої історії читання — тихим відображенням вашого внутрішнього світу, що зростає з кожною книгою.",
        "about_p3": "Чи то улюблені цитати, чи короткий переказ розділу, чи скороминуща думка — це ваше місце, щоб зберегти ці миті.",
        # --- Contact (contact.html) ---
        "contact_title": "Зв'яжіться з нами",
        "contact_subtitle": "Ми будемо раді почути вас.",
        "contact_p1": "Маєте пропозицію, звіт про помилку чи просто добре слово? Заповніть форму нижче, щоб надіслати нам повідомлення.",
        "contact_notice_pre": "Ваше ім'я, адреса електронної пошти та повідомлення будуть надіслані нашій команді через",
        "contact_notice_mid": ". Вони не зберігаються в нашій базі даних. Докладніше — у нашій",
        "contact_notice_privacy_link": "Політиці конфіденційності",
        "contact_notice_post": ".",
        # --- API docs (api.html) ---
        "api_title": "Документація API",
        "api_subtitle": "REST API для Літературного щоденника.",
        "api_overview_heading": "Огляд API",
        "api_overview_body": "API Літературного щоденника надає програмний доступ до публічних нотаток і дозволяє автентифікованим користувачам створювати, оновлювати та видаляти власний вміст.",
        "api_base_url_heading": "Базова URL-адреса",
        "api_auth_heading": "Автентифікація",
        "api_auth_public": "доступ до нотаток лише для читання",
        "api_auth_authenticated": "створення, оновлення та видалення нотаток",
        "api_auth_public_label": "Публічний:",
        "api_auth_authenticated_label": "Автентифікований:",
        "api_auth_session": "Автентифікація на основі сесії з використанням",
        "api_notes_heading": "Ендпоінти нотаток",
        "api_get_desc": "Список нотаток: анонімні користувачі бачать лише публічні; авторизовані також бачать свої приватні нотатки; адміністратор сайту (",
        "api_get_desc_2": " 1) бачить усі. Кожен елемент містить булеве",
        "api_post_desc": "Створити нову нотатку (потрібна автентифікація). Тіло запиту може містити необов'язкове булеве",
        "api_post_desc_2": " (за замовчуванням публічна); створена нотатка та відповіді списку/деталей містять",
        "api_put_desc": "Оновити наявну нотатку (лише власник); видимість можна змінити через",
        "api_put_desc_2": ", що відображається у відповіді JSON.",
        "api_delete_desc": "Видалити нотатку (лише власник).",
        "api_delete_id": "цілочисельний ідентифікатор нотатки",
        "api_footer_pre": "Повний опис API та приклади доступні на",
        "api_footer_link": "GitHub",
        # --- Privacy (privacy.html) ---
        "privacy_title": "Політика конфіденційності",
        "privacy_subtitle": "Як ми збираємо, використовуємо та захищаємо ваші дані.",
        "privacy_last_updated": "Останнє оновлення: червень 2026",
        "privacy_h1": "1. Дані, які ми збираємо",
        "privacy_collect_intro": "Коли ви реєструєтеся та користуєтеся Літературним щоденником, ми зберігаємо такі персональні дані:",
        "privacy_collect_account_label": "Інформація про акаунт",
        "privacy_collect_account": "— вашу адресу електронної пошти, відображуване ім'я та хешовану (PBKDF2-SHA256) копію вашого пароля. Ваш пароль у відкритому вигляді ніколи не зберігається.",
        "privacy_collect_notes_label": "Нотатки",
        "privacy_collect_notes": "— заголовок, підзаголовок, текст, назва книги, дата, URL обкладинки та налаштування видимості (публічна чи приватна).",
        "privacy_collect_comments_label": "Коментарі",
        "privacy_collect_comments": "— текст коментарів, які ви залишаєте до нотаток.",
        "privacy_collect_no_contact": "Ми",
        "privacy_collect_no_contact_strong": "не",
        "privacy_collect_no_contact_2": "зберігаємо надіслані через контактну форму повідомлення локально. Повідомлення, надіслані через контактну форму, пересилаються через SendGrid (див. Розділ 3) і не зберігаються в нашій базі даних.",
        "privacy_h2": "2. Cookie",
        "privacy_cookies_p1": "Ми встановлюємо єдиний сесійний cookie, коли ви входите. Він тримає вас автентифікованим під час перегляду. Він видаляється, коли ваша сесія завершується.",
        "privacy_cookies_p2_pre": "Ми",
        "privacy_cookies_p2_strong": "не використовуємо аналітичні cookie",
        "privacy_cookies_p2_post": ", рекламні cookie чи сторонні трекінгові cookie.",
        "privacy_h3": "3. Сторонні обробники",
        "privacy_third_party_intro": "Користування сайтом змушує ваш браузер звертатися до кількох зовнішніх сервісів. Кожен отримує обмежені технічні дані (зазвичай вашу IP-адресу та User-Agent браузера):",
        "privacy_table_service": "Сервіс",
        "privacy_table_when": "Коли відбувається звернення",
        "privacy_table_data": "Надіслані дані",
        "privacy_gravatar_when": "Сторінки, що показують коментарі",
        "privacy_gravatar_data": "MD5-хеш вашої адреси електронної пошти, що використовується для завантаження аватара",
        "privacy_sendgrid_when": "Коли ви надсилаєте контактну форму",
        "privacy_sendgrid_data": "Ваше ім'я, адреса електронної пошти та повідомлення",
        "privacy_gfonts_when": "Кожне завантаження сторінки",
        "privacy_gfonts_data": "IP-адреса, User-Agent браузера, мітка часу",
        "privacy_fa_when": "Кожне завантаження сторінки",
        "privacy_fa_data": "IP-адреса, User-Agent браузера, мітка часу",
        "privacy_jsdelivr_when": "Кожне завантаження сторінки",
        "privacy_jsdelivr_data": "IP-адреса, User-Agent браузера, мітка часу",
        "privacy_openlibrary_when": "Коли ви шукаєте книгу під час написання нотатки",
        "privacy_openlibrary_data": "Ваш пошуковий запит",
        "privacy_anthropic_when": "Коли ви використовуєте «Обговорити з AI» для своєї нотатки",
        "privacy_anthropic_data": "Заголовок, підзаголовок, книга та зміст нотатки, а також повідомлення, які ви надсилаєте в обговоренні",
        "privacy_ai_discussions": "Обговорення ваших нотаток з AI обробляються Anthropic для генерації відповідей і не зберігаються в нашій базі даних. Розмова тимчасова й зникає, коли ви залишаєте сторінку.",
        "privacy_h4": "4. Ваші права",
        "privacy_rights_intro": "Відповідно до Загального регламенту про захист даних (GDPR) ви маєте такі права щодо ваших персональних даних:",
        "privacy_rights_access_label": "Право на доступ і перенесення (ст. 15, 20)",
        "privacy_rights_access_pre": "— Ви можете будь-коли завантажити повну копію ваших даних (профіль, нотатки та коментарі) у форматі JSON через",
        "privacy_rights_access_link": "ендпоінт експорту даних",
        "privacy_rights_access_post": ".",
        "privacy_rights_rectification_label": "Право на виправлення (ст. 16)",
        "privacy_rights_rectification": "— Ви можете редагувати чи оновлювати будь-яку написану вами нотатку прямо в застосунку.",
        "privacy_rights_erasure_label": "Право на видалення (ст. 17)",
        "privacy_rights_erasure": "— Ви можете назавжди видалити свій акаунт, включно з усіма нотатками та коментарями, з меню акаунта (DELETE ACCOUNT). Ця дія незворотна.",
        "privacy_rights_restrict_label": "Право на обмеження обробки чи заперечення (ст. 18, 21)",
        "privacy_rights_restrict": "— Ви можете будь-коли зробити нотатку приватною, обмеживши її видимість лише собою. Для ширших обмежень чи заперечень звертайтеся до нас за наведеними нижче контактами.",
        "privacy_h5": "5. Контакти",
        "privacy_contact_pre": "Для будь-яких запитів щодо конфіденційності, не охоплених наведеними вище опціями самообслуговування, скористайтеся",
        "privacy_contact_link": "контактною формою",
        "privacy_contact_post": ".",
        # --- Auth pages (login/register/reset) ---
        "auth_login_title": "Вхід",
        "auth_login_subtitle": "Увійдіть у свій світ книг і роздумів.",
        "auth_forgot_link": "Забули пароль?",
        "auth_register_title": "Реєстрація",
        "auth_register_subtitle": "Приєднуйтеся до нашої спільноти читачів.",
        "auth_forgot_title": "Забули пароль",
        "auth_forgot_subtitle": "Введіть свою електронну пошту, щоб отримати посилання для скидання.",
        "auth_reset_title": "Скидання пароля",
        "auth_reset_subtitle": "Введіть новий пароль.",
        # --- Account (account.html) ---
        "account_title": "Налаштування акаунта",
        "account_name": "Ім'я",
        "account_email": "Електронна пошта",
        "account_download": "ЗАВАНТАЖИТИ МОЇ ДАНІ",
        "account_download_help": "Повертає ваш профіль, нотатки та коментарі у форматі JSON.",
        "account_change_password": "ЗМІНИТИ ПАРОЛЬ",
        "account_change_password_help": "Посилання для скидання буде надіслано на вашу електронну пошту.",
        "account_delete": "ВИДАЛИТИ АКАУНТ",
        "account_delete_help": "Назавжди видаляє ваш акаунт, нотатки та коментарі.",
        # --- Delete account (delete_account.html) ---
        "delete_title": "Видалення акаунта",
        "delete_subtitle": "Цю дію неможливо скасувати",
        "delete_warning": "Видалення акаунта назавжди прибере ваш профіль, усі ваші нотатки та всі коментарі — включно з коментарями, залишеними іншими до ваших нотаток.",
        "delete_confirm": "ВИДАЛИТИ МІЙ АКАУНТ",
        "delete_cancel": "СКАСУВАТИ",
        # --- Form labels (WTForms) ---
        "form_email": "Електронна пошта",
        "form_email_address": "Адреса електронної пошти",
        "form_password": "Пароль",
        "form_name": "Ім'я",
        "form_new_password": "Новий пароль",
        "form_confirm_password": "Підтвердьте пароль",
        "form_passwords_must_match": "Паролі мають збігатися.",
        "form_sign_up": "ЗАРЕЄСТРУВАТИ МЕНЕ!",
        "form_log_in": "ВПУСТІТЬ МЕНЕ!",
        "form_delete_account": "ВИДАЛИТИ МІЙ АКАУНТ",
        "form_send_reset_link": "НАДІСЛАТИ ПОСИЛАННЯ",
        "form_set_new_password": "ВСТАНОВИТИ НОВИЙ ПАРОЛЬ",
        "form_note_title": "Заголовок нотатки",
        "form_note_subtitle": "Підзаголовок нотатки",
        "form_note_image_url": "URL зображення нотатки",
        "form_book": "Книга",
        "form_visibility": "Видимість нотатки",
        "form_visibility_public": "Публічна — видима всім",
        "form_visibility_private": "Приватна — лише ви (та адміністратор сайту)",
        "form_note_content": "Вміст нотатки",
        "form_submit_note": "Надіслати нотатку",
        "form_comment": "Коментар",
        "form_submit_comment": "Надіслати коментар",
        "form_message": "Повідомлення",
        "form_submit_message": "Надіслати повідомлення",
        # --- Flash messages ---
        "flash_email_exists": "Ви вже зареєструвалися з цією поштою, увійдіть натомість!",
        "flash_email_not_found": "Такої електронної пошти не існує, спробуйте ще раз.",
        "flash_password_incorrect": "Невірний пароль, спробуйте ще раз.",
        "flash_reset_sent": "Якщо ця пошта зареєстрована, посилання для скидання надіслано.",
        "flash_reset_invalid": "Посилання для скидання недійсне або застаріло.",
        "flash_password_updated": "Ваш пароль оновлено. Будь ласка, увійдіть.",
        "flash_message_sent": "Ваше повідомлення успішно надіслано!",
        "flash_message_failed": "Щось пішло не так. Спробуйте пізніше.",
        "flash_image_generated": "Для вашої нотатки згенеровано нове зображення.",
        "flash_image_failed": "Не вдалося згенерувати зображення. Спробуйте пізніше.",
    },
}
