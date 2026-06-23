import os
import telebot
import urllib.parse
import random
import string
from telebot import types
from database import (
    init_db, get_lang_db, set_lang_db, get_all_users, get_user_count,
    get_lang_counts, get_recent_users, get_maintenance, set_maintenance,
    get_total_msgs, increment_total_msgs, get_user_links, ensure_link,
    increment_link_views, increment_link_msgs, delete_link, delete_all_links,
    get_waiting_list, add_to_waiting_list, clear_waiting_list,
    ban_user, unban_user, is_banned, get_all_banned,
    has_sent_to_link, mark_sent_to_link,
    is_reply_token_used, mark_reply_token_used, start_token_cleaner, DB_PATH
)

# --- SETTINGS ---
TOKEN = "YOUR_BOT_TOKEN"
BOT_USERNAME = "YOUR_BOT_USERNAME"
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0000000000))
except ValueError:
    ADMIN_ID = 0000000000
ADMIN_USERNAME = "YOUR_ADMIN_USERNAME"

bot = telebot.TeleBot(TOKEN)

user_states = {}

# --- LANGUAGE DICTIONARY ---
TEXTS = {
    'tr': {
        'welcome': "👋 **Anonim İtiraf 2.0'a Hoş Geldin!**\n\nArkadaşlarının senin hakkında ne düşündüğünü öğren. Alttaki menüden linkini oluştur!",
        'btn_general': "🔗 Link Al (Platform Seç)", 'btn_topic': "🏷️ Konulu Link Oluştur",
        'btn_stats': "📊 İstatistiklerim", 'btn_admin': "🛠️ Admin Paneli",
        'btn_help': "💡 Nasıl Çalışır?", 'btn_settings': "⚙️ Ayarlar (Dil / Language)",
        'help_text': "1️⃣ Platform seçip linkini oluştur.\n2️⃣ Instagram veya diğer hikayelerine ekle.\n3️⃣ Gelen anonim mesajları burada oku ve cevapla!",
        'ask_topic': "📝 Bu link hangi hikayen için? Kısa bir konu yaz:\n(Örn: Kombinim, SoruCevap, İtiraf)",
        'link_ready': "✅ **{topic} Bağlantın Hazır:**\n`{link}`\n\nBunu ilgili platformda paylaş!",
        'general_link': "🎯 **Genel Linkin:**\n`{link}`",
        'write_anon': "🤫 **{topic}** konulu anonim mesajını yaz:\n(Kimliğin asla paylaşılmayacak)",
        'cancel': "❌ İptal", 'cancelled': "❌ İşlem iptal edildi.",
        'sent': "✅ Mesajın anonim olarak iletildi!",
        'new_msg': "📩 **YENİ MESAJ!**\n📱 **Platform:** {platform}\n🏷️ **Konu:** {topic}\n\n💬 _{msg}_",
        'reply_btn': "↩️ Cevapla", 'reply_ask': "✍️ **Cevap Yaz:**\nKarşı tarafa kimliğin gizlenerek iletilecek.",
        'reply_notify': "🔔 **İtirafına Bir Cevap Geldi!**\n\n💬 _{msg}_",
        'lang_menu': "🌍 **Dil seçiniz / Select Language / Выберите язык:**",
        'lang_changed': "✅ Dil Türkçe olarak güncellendi.",
        'maintenance': "⚙️ **Sistem Bakımda!**\nŞu an bir güncelleme yapıyoruz. Bakım bittiğinde size haber vereceğiz! 🔔",
        'maint_over': "🔔 **Bakım sona erdi!** Artık botu kullanmaya devam edebilirsin. /start yazarak başlayabilirsin.",
        'platform_menu': "📱 **Hangi platform için link oluşturmak istersin?**",
        'stats_main': "📊 **Hangi bağlantının istatistiklerini görmek istersin?**\nDetaylar için aşağıdaki link butonlarına tıkla:",
        'stats_detail': "📊 **{topic} Bağlantı İstatistikleri**\n\n👁️ **Tıklanma (Görüntülenme):** `{views}`\n💌 **Gelen Mesaj:** `{msgs}`",
        'no_links': "❌ Henüz oluşturulmuş bir linkin yok.",
        'admin_title': "👑 **Gelişmiş Yönetici Paneli**",
        'admin_stats_btn': "📊 İstatistikler", 'admin_bc_btn': "📢 Toplu Mesaj",
        'admin_maint_btn': "🛑 Bakım Modu: ", 'admin_backup_btn': "💾 Yedek İndir",
        'confirm_del': "⚠️ **{topic}** bağlantısını ve tüm istatistiklerini kalıcı olarak silmek istediğine emin misin?",
        'confirm_del_all': "⚠️ **Tüm bağlantılarını ve istatistiklerini** kalıcı olarak silmek istediğine emin misin?\n*(Bu işlem geri alınamaz)*",
        'deleted': "🗑️ Bağlantı başarıyla silindi.",
        'deleted_all': "🗑️ Tüm bağlantıların başarıyla temizlendi.",
        'back': "⬅️ Geri",
        'del_all_btn': "⚠️ Tüm Linkleri Sil",
        'del_link_btn': "🗑️ Bu Linki Sil",
        'btn_yes_del': "✅ Evet, Sil",
        'btn_yes_del_all': "✅ Evet, Tümünü Sil",
        'btn_no': "❌ Vazgeç",
        'rnd_btn': "🎲 Rastgele Oluştur",
        'tumu_btn': "🎲 Tümü İçin (Rastgele Link)",
        'self_msg_error': "❌ Kendi linkinize mesaj atamazsınız.",
        'send_error': "⚠️ Mesaj gönderilemedi.",
        'reply_error': "⚠️ Cevap gönderilemedi.",
        'token_used': "⚠️ Bu cevap butonu zaten kullanıldı.",
        'backup_error': "⚠️ Backup alınamadı.",
        'share_link_btn': "📤 Linki Paylaş",
        'share_bot_btn': "📤 Botu Paylaş",
        'already_sent': "⛔ Bu linke daha önce mesaj gönderdin. Aynı kişiye aynı link üzerinden tekrar mesaj gönderemezsin.",
        'banned': "🚫 Bottan engellendiniz. Devam edemezsiniz.",
        'admin_users_btn': "👥 Kullanıcı Listesi",
        'admin_ban_btn': "🚫 Ban / Unban",
        'ban_list_empty': "✅ Hiç engelli kullanıcı yok.",
        'user_list_title': "👥 **Son 20 Kullanıcı:**\n\n",
        'btn_support': "📩 Destek / İletişim",
        'support_title': "📩 **Destek & İletişim**\n\nAdminle iletişime geçmek için aşağıdaki seçeneklerden birini kullan:",
        'support_telegram_btn': "👤 Admini Telegram'da Aç",
        'support_bot_btn': "🤖 Bot Üzerinden Mesaj Gönder",
        'support_write': "✍️ **Admine Mesajın:**\nMesajını yaz, admin görecek (kimliğin görünecek):",
        'support_sent': "✅ Mesajın admine iletildi!",
        'support_new_msg': "📬 **DESTEK MESAJI**\n\n👤 **Kullanıcı:** {name}{username}\n🆔 **ID:** `{uid}`\n\n💬 {msg}",
    },
    'en': {
        'welcome': "👋 **Welcome to Anonymous Confession 2.0!**\n\nFind out what your friends think. Create your link below!",
        'btn_general': "🔗 Get Link (Select Platform)", 'btn_topic': "🏷️ Create Topic Link",
        'btn_stats': "📊 My Statistics", 'btn_admin': "🛠️ Admin Panel",
        'btn_help': "💡 How It Works?", 'btn_settings': "⚙️ Settings (Language)",
        'help_text': "1️⃣ Select a platform and create your link.\n2️⃣ Share on stories.\n3️⃣ Read anonymous messages here and reply!",
        'ask_topic': "📝 Enter a short topic for this link:\n(e.g., MyOutfit, AskMe, Confession)",
        'link_ready': "✅ **Your link for {topic} is ready:**\n`{link}`\n\nShare this on your story!",
        'general_link': "🎯 **Your General Link:**\n`{link}`",
        'write_anon': "🤫 Write your anonymous message about **{topic}**:\n(Your identity is hidden)",
        'cancel': "❌ Cancel", 'cancelled': "❌ Action cancelled.",
        'sent': "✅ Message sent anonymously!",
        'new_msg': "📩 **NEW MESSAGE!**\n📱 **Platform:** {platform}\n🏷️ **Topic:** {topic}\n\n💬 _{msg}_",
        'reply_btn': "↩️ Reply", 'reply_ask': "✍️ **Write a reply:**\nIt will be sent secretly.",
        'reply_notify': "🔔 **You got a reply to your confession!**\n\n💬 _{msg}_",
        'lang_menu': "🌍 **Select Language:**", 'lang_changed': "✅ Language updated to English.",
        'maintenance': "⚙️ **System under maintenance!**\nWe are updating the bot. We will notify you when it's back! 🔔",
        'maint_over': "🔔 **Maintenance is over!** You can continue using the bot. Type /start to begin.",
        'platform_menu': "📱 **Which platform do you want to create a link for?**",
        'stats_main': "📊 **Which link's statistics do you want to see?**\nClick a link button below for details:",
        'stats_detail': "📊 **{topic} Link Statistics**\n\n👁️ **Views (Clicks):** `{views}`\n💌 **Received Messages:** `{msgs}`",
        'no_links': "❌ No links created yet.",
        'admin_title': "👑 **Advanced Admin Panel**",
        'admin_stats_btn': "📊 Statistics", 'admin_bc_btn': "📢 Broadcast",
        'admin_maint_btn': "🛑 Maintenance: ", 'admin_backup_btn': "💾 Backup",
        'confirm_del': "⚠️ Are you sure you want to permanently delete the link **{topic}** and its stats?",
        'confirm_del_all': "⚠️ Are you sure you want to permanently delete **ALL your links and stats**?\n*(This cannot be undone)*",
        'deleted': "🗑️ Link deleted successfully.",
        'deleted_all': "🗑️ All links cleared successfully.",
        'back': "⬅️ Back",
        'del_all_btn': "⚠️ Delete All Links",
        'del_link_btn': "🗑️ Delete This Link",
        'btn_yes_del': "✅ Yes, Delete",
        'btn_yes_del_all': "✅ Yes, Delete All",
        'btn_no': "❌ Cancel",
        'rnd_btn': "🎲 Generate Randomly",
        'tumu_btn': "🎲 For All (Random Link)",
        'self_msg_error': "❌ You cannot send a message to your own link.",
        'send_error': "⚠️ Message could not be sent.",
        'reply_error': "⚠️ Reply could not be sent.",
        'token_used': "⚠️ This reply button has already been used.",
        'backup_error': "⚠️ Backup failed.",
        'share_link_btn': "📤 Share Link",
        'share_bot_btn': "📤 Share Bot",
        'already_sent': "⛔ You've already sent a message to this link. You can't message the same person via the same link again.",
        'banned': "🚫 You have been banned from the bot.",
        'admin_users_btn': "👥 User List",
        'admin_ban_btn': "🚫 Ban / Unban",
        'ban_list_empty': "✅ No banned users.",
        'user_list_title': "👥 **Last 20 Users:**\n\n",
        'btn_support': "📩 Support / Contact",
        'support_title': "📩 **Support & Contact**\n\nChoose one of the options below to reach the admin:",
        'support_telegram_btn': "👤 Open Admin on Telegram",
        'support_bot_btn': "🤖 Send Message via Bot",
        'support_write': "✍️ **Message to Admin:**\nWrite your message, admin will see it (your identity will be visible):",
        'support_sent': "✅ Your message has been sent to the admin!",
        'support_new_msg': "📬 **SUPPORT MESSAGE**\n\n👤 **User:** {name}{username}\n🆔 **ID:** `{uid}`\n\n💬 {msg}",
    },
    'ru': {
        'welcome': "👋 **Добро пожаловать в Анонимные Признания 2.0!**\n\nУзнай, что о тебе думают. Создай свою ссылку ниже!",
        'btn_general': "🔗 Создать ссылку (Платформа)", 'btn_topic': "🏷️ Ссылка с темой",
        'btn_stats': "📊 Моя статистика", 'btn_admin': "🛠️ Админ панель",
        'btn_help': "💡 Как это работает?", 'btn_settings': "⚙️ Настройки (Язык)",
        'help_text': "1️⃣ Выберите платформу и создайте ссылку.\n2️⃣ Поделись в сторис.\n3️⃣ Читай анонимные сообщения здесь и отвечай!",
        'ask_topic': "📝 Напиши короткую тему для этой ссылки:\n(Напр: МойЛук, Вопрос, Признание)",
        'link_ready': "✅ **Ссылка для {topic} готова:**\n`{link}`\n\nПоделись ею в сторис!",
        'general_link': "🎯 **Твоя общая ссылка:**\n`{link}`",
        'write_anon': "🤫 Напиши анонимное сообщение на тему **{topic}**:\n(Твоя личность скрыта)",
        'cancel': "❌ Отмена", 'cancelled': "❌ Действие отменено.",
        'sent': "✅ Сообщение отправлено анонимно!",
        'new_msg': "📩 **НОВОЕ СООБЩЕНИЕ!**\n📱 **Платформа:** {platform}\n🏷️ **Тема:** {topic}\n\n💬 _{msg}_",
        'reply_btn': "↩️ Ответить", 'reply_ask': "✍️ **Напиши ответ:**\nОн будет доставлен втайне.",
        'reply_notify': "🔔 **Пришел ответ на твое признание!**\n\n💬 _{msg}_",
        'lang_menu': "🌍 **Выберите язык:**", 'lang_changed': "✅ Язык изменен на русский.",
        'maintenance': "⚙️ **Технические работы!**\nМы обновляем бота. Мы сообщим вам, когда всё будет готово! 🔔",
        'maint_over': "🔔 **Техработы завершены!** Вы можете продолжить использование бота. Напишите /start.",
        'platform_menu': "📱 **Для какой платформы вы хотите создать ссылку?**",
        'stats_main': "📊 **Статистику какой ссылки вы хотите посмотреть?**\nНажмите на кнопку ссылки ниже:",
        'stats_detail': "📊 **Статистика ссылки {topic}**\n\n👁️ **Просмотры (Клики):** `{views}`\n💌 **Получено сообщений:** `{msgs}`",
        'no_links': "❌ У вас еще нет созданных ссылок.",
        'admin_title': "👑 **Панель администратора**",
        'admin_stats_btn': "📊 Статистика", 'admin_bc_btn': "📢 Рассылка",
        'admin_maint_btn': "🛑 Техработы: ", 'admin_backup_btn': "💾 Скачать бэкап",
        'confirm_del': "⚠️ Вы уверены, что хотите навсегда удалить ссылку **{topic}** и её статистику?",
        'confirm_del_all': "⚠️ Вы уверены, что хотите навсегда удалить **ВСЕ свои ссылки и статистику**?\n*(Это действие необратимо)*",
        'deleted': "🗑️ Ссылка успешно удалена.",
        'deleted_all': "🗑️ Все ссылки успешно очищены.",
        'back': "⬅️ Назад",
        'del_all_btn': "⚠️ Удалить все ссылки",
        'del_link_btn': "🗑️ Удалить эту ссылку",
        'btn_yes_del': "✅ Да, удалить",
        'btn_yes_del_all': "✅ Да, удалить всё",
        'btn_no': "❌ Отмена",
        'rnd_btn': "🎲 Создать случайно",
        'tumu_btn': "🎲 Для всех (Случайная ссылка)",
        'self_msg_error': "❌ Нельзя отправить сообщение на собственную ссылку.",
        'send_error': "⚠️ Не удалось отправить сообщение.",
        'reply_error': "⚠️ Не удалось отправить ответ.",
        'token_used': "⚠️ Эта кнопка ответа уже была использована.",
        'backup_error': "⚠️ Не удалось создать резервную копию.",
        'share_link_btn': "📤 Поделиться ссылкой",
        'share_bot_btn': "📤 Поделиться ботом",
        'already_sent': "⛔ Вы уже отправляли сообщение по этой ссылке. Повторно нельзя.",
        'banned': "🚫 Вы заблокированы в боте.",
        'admin_users_btn': "👥 Список пользователей",
        'admin_ban_btn': "🚫 Бан / Разбан",
        'ban_list_empty': "✅ Нет заблокированных пользователей.",
        'user_list_title': "👥 **Последние 20 пользователей:**\n\n",
        'btn_support': "📩 Поддержка / Контакт",
        'support_title': "📩 **Поддержка & Контакт**\n\nВыберите способ связи с администратором:",
        'support_telegram_btn': "👤 Открыть профиль админа",
        'support_bot_btn': "🤖 Написать через бота",
        'support_write': "✍️ **Сообщение администратору:**\nНапишите сообщение, админ увидит (ваша личность будет видна):",
        'support_sent': "✅ Ваше сообщение отправлено администратору!",
        'support_new_msg': "📬 **СООБЩЕНИЕ ПОДДЕРЖКИ**\n\n👤 **Пользователь:** {name}{username}\n🆔 **ID:** `{uid}`\n\n💬 {msg}",
    }
}

# --- HELPER FUNCTIONS ---
def get_lang(user):
    return get_lang_db(user, bot, ADMIN_ID)

def create_main_menu(lang, chat_id=None):
    markup = types.InlineKeyboardMarkup(row_width=2)
    t = TEXTS[lang]
    markup.add(types.InlineKeyboardButton(t['btn_general'], callback_data="menu:general"))
    markup.add(types.InlineKeyboardButton(t['btn_stats'], callback_data="menu:stats"),
               types.InlineKeyboardButton(t['btn_settings'], callback_data="menu:settings"))
    markup.add(types.InlineKeyboardButton(t['btn_help'], callback_data="menu:help"))
    
    share_bot_url = f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME.replace('@', '')}"
    markup.add(types.InlineKeyboardButton(t['share_bot_btn'], url=share_bot_url))
    markup.add(types.InlineKeyboardButton(t['btn_support'], callback_data="menu:support"))
    
    if chat_id == ADMIN_ID:
        markup.add(types.InlineKeyboardButton(t['btn_admin'], callback_data="menu:admin"))
    return markup

def build_admin_markup(lang):
    t = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    status_icon = "🔴 OFF" if not get_maintenance() else "🟢 ON"
    markup.add(types.InlineKeyboardButton(t['admin_stats_btn'], callback_data="admin:stats"),
               types.InlineKeyboardButton(t['admin_bc_btn'], callback_data="admin:broadcast"))
    markup.add(types.InlineKeyboardButton(f"{t['admin_maint_btn']}{status_icon}", callback_data="admin:maint"),
               types.InlineKeyboardButton(t['admin_backup_btn'], callback_data="admin:backup"))
    markup.add(types.InlineKeyboardButton(t['admin_users_btn'], callback_data="admin:users"),
               types.InlineKeyboardButton(t['admin_ban_btn'], callback_data="admin:banlist"))
    markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu:back"))
    return markup

# --- COMMANDS ---
@bot.message_handler(commands=['admin'])
def open_admin_panel(message):
    if message.chat.id != ADMIN_ID:
        return
    lang = get_lang(message.from_user)
    t = TEXTS[lang]
    bot.send_message(ADMIN_ID, t['admin_title'], parse_mode="Markdown", reply_markup=build_admin_markup(lang))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    chat_id = message.chat.id
    lang = get_lang(user)
    t = TEXTS[lang]

    # Ban check
    if is_banned(chat_id):
        bot.send_message(chat_id, t['banned'])
        return

    if get_maintenance() and chat_id != ADMIN_ID:
        add_to_waiting_list(chat_id)
        bot.send_message(chat_id, t['maintenance'], parse_mode="Markdown")
        return

    parts = message.text.split()
    if len(parts) > 1:
        try:
            payload = parts[1].split('_')
            target_id = payload[0]
            platform = payload[1] if len(payload) > 1 else "Genel"
            topic = payload[2] if len(payload) > 2 else "Genel"
        except IndexError:
            bot.send_message(chat_id, t['welcome'], reply_markup=create_main_menu(lang, chat_id))
            return

        if str(target_id) == str(chat_id):
            bot.send_message(chat_id, t['self_msg_error'])
            return

        link_display_name = f"{platform} - {topic}"
        ensure_link(target_id, link_display_name)
        increment_link_views(target_id, link_display_name)

        # 1 comment limit: has the same sender + same link been used before?
        if has_sent_to_link(chat_id, target_id, link_display_name):
            bot.send_message(chat_id, t['already_sent'], parse_mode="Markdown")
            return

        user_states[chat_id] = {
            'mode': 'sending_anon',
            'target': target_id,
            'platform': platform,
            'topic': topic,
            'link_display_name': link_display_name
        }
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(t['cancel'], callback_data="cancel"))
        bot.send_message(chat_id, t['write_anon'].format(topic=topic), parse_mode="Markdown", reply_markup=markup)
    else:
        try:
            rm_msg = bot.send_message(chat_id, "🔄", reply_markup=types.ReplyKeyboardRemove())
            bot.delete_message(chat_id, rm_msg.message_id)
        except telebot.apihelper.ApiException:
            pass
        bot.send_message(chat_id, t['welcome'], parse_mode="Markdown", reply_markup=create_main_menu(lang, chat_id))

# --- CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    lang = get_lang(call.from_user)
    t = TEXTS[lang]
    data = call.data

    if data.startswith("menu:"):
        action = data.split(":", 1)[1]

        if action == "general":
            markup = types.InlineKeyboardMarkup(row_width=2)
            platforms = ["Telegram", "WhatsApp", "Instagram", "Facebook", "VK", "TikTok"]
            for p in platforms:
                markup.add(types.InlineKeyboardButton(p, callback_data=f"plat:{p}"))
            markup.add(types.InlineKeyboardButton(t['tumu_btn'], callback_data="plat:all"))
            markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu:back"))
            bot.edit_message_text(t['platform_menu'], chat_id, call.message.message_id, reply_markup=markup)

        elif action == "stats":
            user_links = get_user_links(chat_id)
            if not user_links:
                markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(t['back'], callback_data="menu:back"))
                bot.edit_message_text(t['no_links'], chat_id, call.message.message_id, reply_markup=markup)
                bot.answer_callback_query(call.id)
                return
            markup = types.InlineKeyboardMarkup(row_width=2)
            for topic_name in user_links.keys():
                markup.add(types.InlineKeyboardButton(f"🔗 {topic_name}", callback_data=f"st:{topic_name}"))
            markup.add(types.InlineKeyboardButton(t['del_all_btn'], callback_data="delallask"))
            markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu:back"))
            bot.edit_message_text(t['stats_main'], chat_id, call.message.message_id, reply_markup=markup)

        elif action == "settings":
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="setlang:tr"),
                types.InlineKeyboardButton("🇬🇧 English", callback_data="setlang:en"),
                types.InlineKeyboardButton("🇷🇺 Русский", callback_data="setlang:ru")
            )
            markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu:back"))
            bot.edit_message_text(t['lang_menu'], chat_id, call.message.message_id, reply_markup=markup)

        elif action == "help":
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(t['back'], callback_data="menu:back"))
            bot.edit_message_text(t['help_text'], chat_id, call.message.message_id, reply_markup=markup)

        elif action == "support":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t['support_telegram_btn'], url=f"https://t.me/{ADMIN_USERNAME}"))
            markup.add(types.InlineKeyboardButton(t['support_bot_btn'], callback_data="support:write"))
            markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu:back"))
            bot.edit_message_text(t['support_title'], chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

        elif action == "admin":
            if chat_id != ADMIN_ID:
                bot.answer_callback_query(call.id)
                return
            bot.edit_message_text(t['admin_title'], chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=build_admin_markup(lang))

        elif action == "back":
            bot.edit_message_text(t['welcome'], chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=create_main_menu(lang, chat_id))

        bot.answer_callback_query(call.id)
        return

    if data.startswith("admin:"):
        if chat_id != ADMIN_ID:
            bot.answer_callback_query(call.id)
            return
        action = data.split(":", 1)[1]

        if action == "stats":
            total_users = get_user_count()
            total_msgs = get_total_msgs()
            lang_counts = get_lang_counts()
            tr_c = lang_counts.get("tr", 0)
            en_c = lang_counts.get("en", 0)
            ru_c = lang_counts.get("ru", 0)

            if lang == 'ru':
                stat_msg = f"📊 **СТАТИСТИКА СИСТЕМЫ**\n\n👥 **Всего пользователей:** `{total_users}`\n💬 **Сообщений:** `{total_msgs}`\n\n🌍 **Языки:**\n🇹🇷 TR: `{tr_c}` | 🇷🇺 RU: `{ru_c}` | 🇬🇧 EN: `{en_c}`"
            elif lang == 'en':
                stat_msg = f"📊 **SYSTEM STATISTICS**\n\n👥 **Total Users:** `{total_users}`\n💬 **Messages:** `{total_msgs}`\n\n🌍 **Languages:**\n🇹🇷 TR: `{tr_c}` | 🇷🇺 RU: `{ru_c}` | 🇬🇧 EN: `{en_c}`"
            else:
                stat_msg = f"📊 **SİSTEM İSTATİSTİKLERİ**\n\n👥 **Toplam Kullanıcı:** `{total_users}`\n💬 **İletilen İtiraf:** `{total_msgs}`\n\n🌍 **Dil Dağılımı:**\n🇹🇷 TR: `{tr_c}` | 🇷🇺 RU: `{ru_c}` | 🇬🇧 EN: `{en_c}`"

            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(t['back'], callback_data="menu:admin"))
            bot.edit_message_text(stat_msg, ADMIN_ID, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

        elif action == "broadcast":
            user_states[ADMIN_ID] = {'mode': 'admin_broadcast'}
            if lang == 'ru':
                bc_text = "📢 **Рассылка**\nОтправьте сообщение (для отмены /admin):"
            elif lang == 'en':
                bc_text = "📢 **Broadcast Mode**\nSend the message (type /admin to cancel):"
            else:
                bc_text = "📢 **Toplu Mesaj Modu**\nMesajı gönderin (İptal için /admin yazın):"
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(t['back'], callback_data="menu:admin"))
            bot.edit_message_text(bc_text, ADMIN_ID, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

        elif action == "maint":
            new_val = not get_maintenance()
            set_maintenance(new_val)
            if not new_val:
                waiting = get_waiting_list()
                bot.send_message(ADMIN_ID, f"📢 Bakım bitti. {len(waiting)} kişiye bildirim gidiyor...")
                for u_id in waiting:
                    try:
                        u_lang = get_all_users().get(str(u_id), 'tr')
                        bot.send_message(u_id, TEXTS[u_lang]['maint_over'], parse_mode="Markdown")
                    except Exception as e:
                        print(f"Bildirim hatası {u_id}: {e}")
                clear_waiting_list()
            bot.answer_callback_query(call.id, f"Maintenance: {'ON' if new_val else 'OFF'}", show_alert=True)
            bot.edit_message_text(t['admin_title'], ADMIN_ID, call.message.message_id, parse_mode="Markdown", reply_markup=build_admin_markup(lang))

        elif action == "backup":
            # To take a secure backup of the SQLite database
            # we create a temporary file and use the backup() method.
            try:
                with open(DB_PATH, "rb") as doc:
                    bot.send_document(ADMIN_ID, doc)
            except Exception as e:
                print(f"Backup hatası: {e}")
                bot.send_message(ADMIN_ID, t['backup_error'])

        elif action == "users":
            recent = get_recent_users(20)
            if not recent:
                bot.send_message(ADMIN_ID, "👥 Henüz kullanıcı yok.")
            else:
                lines = []
                for uid, ulang, uname in recent:
                    if uname:
                        user_link = f"[@{uname}](https://t.me/{uname})"
                    else:
                        user_link = f"[{uid}](tg://user?id={uid})"
                    lines.append(f"🆔 `{uid}` — {user_link} — 🌍 {ulang.upper()}")
                msg = t['user_list_title'] + "\n".join(lines)
                markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(t['back'], callback_data="menu:admin"))
                bot.edit_message_text(msg, ADMIN_ID, call.message.message_id, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=markup)

        elif action == "banlist":
            banned = get_all_banned()
            if not banned:
                markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(t['back'], callback_data="menu:admin"))
                bot.edit_message_text(t['ban_list_empty'], ADMIN_ID, call.message.message_id, reply_markup=markup)
            else:
                markup = types.InlineKeyboardMarkup()
                for bid, breason in banned:
                    markup.add(types.InlineKeyboardButton(f"✅ Unban: {bid}", callback_data=f"admin:unban:{bid}"))
                markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu:admin"))
                lines = [f"🚫 `{bid}` — {breason or 'sebepsiz'}" for bid, breason in banned]
                bot.edit_message_text("🚫 **Engelli Kullanıcılar:**\n\n" + "\n".join(lines), ADMIN_ID, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

        elif action.startswith("unban:"):
            target_uid = action.split(":", 1)[1]
            unban_user(target_uid)
            bot.answer_callback_query(call.id, f"✅ {target_uid} unbanned!", show_alert=True)
            bot.edit_message_text(t['admin_title'], ADMIN_ID, call.message.message_id, parse_mode="Markdown", reply_markup=build_admin_markup(lang))
            return

        elif action.startswith("ban:"):
            target_uid = action.split(":", 1)[1]
            ban_user(target_uid, "Admin tarafından engellendi")
            bot.answer_callback_query(call.id, f"🚫 {target_uid} banned!", show_alert=True)
            return

        bot.answer_callback_query(call.id)
        return

    if data == "cancel":
        if chat_id in user_states:
            del user_states[chat_id]
        bot.edit_message_text(t['cancelled'], chat_id, call.message.message_id, reply_markup=create_main_menu(lang, chat_id))

    elif data.startswith("support:"):
        action = data.split(":", 1)[1]
        if action == "write":
            user_states[chat_id] = {'mode': 'support_msg'}
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(t['cancel'], callback_data="cancel"))
            bot.send_message(chat_id, t['support_write'], parse_mode="Markdown", reply_markup=markup)

    elif data.startswith("reply:"):
        # Token: reply:TARGET_ID:MSG_ID (one-time use)
        parts_data = data.split(":")
        target_id = parts_data[1]
        msg_id_str = parts_data[2] if len(parts_data) > 2 else "0"
        token = f"{chat_id}_{target_id}_{msg_id_str}"

        if is_reply_token_used(token):
            bot.answer_callback_query(call.id, t['token_used'], show_alert=True)
            return

        mark_reply_token_used(token)

        # Remove the reply button from the old message
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except telebot.apihelper.ApiException:
            pass

        user_states[chat_id] = {'mode': 'replying_anon', 'target': target_id, 'origin_msg_id': call.message.message_id}
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(t['cancel'], callback_data="cancel"))
        bot.send_message(chat_id, t['reply_ask'], parse_mode="Markdown", reply_markup=markup)

    elif data.startswith("setlang:"):
        new_lang = data.split(":", 1)[1]
        set_lang_db(chat_id, new_lang)
        t_new = TEXTS[new_lang]
        bot.edit_message_text(
            f"{t_new['lang_changed']}\n\n{t_new['welcome']}",
            chat_id, call.message.message_id,
            parse_mode="Markdown",
            reply_markup=create_main_menu(new_lang, chat_id)
        )

    elif data.startswith("plat:"):
        p_name = data.split(":", 1)[1]
        user_states[chat_id] = {'mode': 'setting_platform_topic', 'platform': p_name}
        if lang == 'tr':
            ask_text = f"📝 **{p_name}** için kısa bir konu başlığı yazın:"
        elif lang == 'en':
            ask_text = f"📝 Enter a short topic title for **{p_name}**:"
        else:
            ask_text = f"📝 Напишите короткую тему для **{p_name}**:"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t['rnd_btn'], callback_data=f"rndplat:{p_name}"))
        markup.add(types.InlineKeyboardButton(t['cancel'], callback_data="cancel"))
        bot.edit_message_text(ask_text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif data.startswith("rndplat:"):
        p_name = data.split(":", 1)[1]
        topic = "Link" + ''.join(random.choices(string.ascii_letters + string.digits, k=4))
        link_display_name = f"{p_name} - {topic}"
        ensure_link(chat_id, link_display_name)
        if chat_id in user_states:
            del user_states[chat_id]
        clean_bot_name = BOT_USERNAME.replace("@", "")
        link = f"https://t.me/{clean_bot_name}?start={chat_id}_{p_name}_{topic}"
        
        share_url = f"https://t.me/share/url?url={urllib.parse.quote(link)}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t['share_link_btn'], url=share_url))
        markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu:back"))
        
        bot.edit_message_text(
            t['link_ready'].format(topic=link_display_name, link=link),
            chat_id, call.message.message_id,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=markup
        )

    elif data.startswith("st:"):
        topic_name = data.split(":", 1)[1]
        user_links = get_user_links(chat_id)
        stats = user_links.get(topic_name, {"views": 0, "msgs": 0})
        clean_bot_name = BOT_USERNAME.replace("@", "")
        parts = topic_name.split(" - ", 1)
        p_name = parts[0] if len(parts) > 1 else "Genel"
        tp = parts[1] if len(parts) > 1 else topic_name
        link = f"https://t.me/{clean_bot_name}?start={chat_id}_{p_name}_{tp}"
        
        share_url = f"https://t.me/share/url?url={urllib.parse.quote(link)}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t['share_link_btn'], url=share_url))
        markup.add(types.InlineKeyboardButton(t['del_link_btn'], callback_data=f"delask:{topic_name}"))
        markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu:stats"))
        
        bot.edit_message_text(
            t['stats_detail'].format(topic=topic_name, views=stats['views'], msgs=stats['msgs']) + f"\n\n🔗 **Link:**\n`{link}`",
            chat_id, call.message.message_id,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=markup
        )

    elif data.startswith("delask:"):
        topic_name = data.split(":", 1)[1]
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(t['btn_yes_del'], callback_data=f"delyes:{topic_name}"),
            types.InlineKeyboardButton(t['btn_no'], callback_data=f"st:{topic_name}")
        )
        bot.edit_message_text(
            t['confirm_del'].format(topic=topic_name),
            chat_id, call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif data.startswith("delyes:"):
        topic_name = data.split(":", 1)[1]
        delete_link(chat_id, topic_name)
        bot.edit_message_text(t['deleted'], chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=create_main_menu(lang, chat_id))

    elif data == "delallask":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(t['btn_yes_del_all'], callback_data="delallyes"),
            types.InlineKeyboardButton(t['btn_no'], callback_data="menu:stats")
        )
        bot.edit_message_text(t['confirm_del_all'], chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif data == "delallyes":
        delete_all_links(chat_id)
        bot.edit_message_text(t['deleted_all'], chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=create_main_menu(lang, chat_id))

    bot.answer_callback_query(call.id)

# --- MESSAGE HANDLER (MEDIA, VOICE, VIDEO NOTE SUPPORT) ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'voice', 'video_note'])
def handle_all(message):
    chat_id = message.chat.id
    lang = get_lang(message.from_user)
    t = TEXTS[lang]

    # Ban check
    if is_banned(chat_id) and chat_id != ADMIN_ID:
        bot.send_message(chat_id, t['banned'])
        return
    
    # We capture the user's text or image/video caption
    text = ""
    if message.text:
        text = message.text
    elif message.caption:
        text = message.caption

    if get_maintenance() and chat_id != ADMIN_ID:
        bot.send_message(chat_id, t['maintenance'], parse_mode="Markdown")
        return

    if chat_id == ADMIN_ID and user_states.get(chat_id, {}).get('mode') == 'admin_broadcast':
        success, fail = 0, 0
        for u_id in get_all_users().keys():
            try:
                bot.copy_message(int(u_id), ADMIN_ID, message.message_id)
                success += 1
            except Exception as e:
                print(f"Broadcast hatası {u_id}: {e}")
                fail += 1
        bot.send_message(ADMIN_ID, f"📢 **YAYIN RAPORU**\n✅: {success} | ❌: {fail}", parse_mode="Markdown")
        del user_states[ADMIN_ID]
        return

    # Admin: /ban <user_id> command as text
    if chat_id == ADMIN_ID and text.startswith("/ban "):
        parts_cmd = text.split()
        if len(parts_cmd) >= 2:
            ban_target = parts_cmd[1]
            ban_user(ban_target, "Admin tarafından engellendi")
            bot.send_message(ADMIN_ID, f"🚫 `{ban_target}` engellendi.", parse_mode="Markdown")
        return

    if chat_id == ADMIN_ID and text.startswith("/unban "):
        parts_cmd = text.split()
        if len(parts_cmd) >= 2:
            unban_target = parts_cmd[1]
            unban_user(unban_target)
            bot.send_message(ADMIN_ID, f"✅ `{unban_target}` engeli kaldırıldı.", parse_mode="Markdown")
        return

    if text in [TEXTS['tr']['btn_general'], TEXTS['en']['btn_general'], TEXTS['ru']['btn_general']]:
        markup = types.InlineKeyboardMarkup(row_width=2)
        platforms = ["Telegram", "WhatsApp", "Instagram", "Facebook", "VK", "TikTok", "Tümü"]
        for p in platforms:
            markup.add(types.InlineKeyboardButton(p, callback_data=f"plat:{p}"))
        bot.send_message(chat_id, t['platform_menu'], reply_markup=markup)

    elif text in [TEXTS['tr']['btn_stats'], TEXTS['en']['btn_stats'], TEXTS['ru']['btn_stats']]:
        user_links = get_user_links(chat_id)
        if not user_links:
            bot.send_message(chat_id, t['no_links'])
            return
        markup = types.InlineKeyboardMarkup(row_width=2)
        for topic_name in user_links.keys():
            markup.add(types.InlineKeyboardButton(f"🔗 {topic_name}", callback_data=f"st:{topic_name}"))
        markup.add(types.InlineKeyboardButton(t['del_all_btn'], callback_data="delallask"))
        bot.send_message(chat_id, t['stats_main'], reply_markup=markup)

    elif text in [TEXTS['tr']['btn_admin'], TEXTS['en']['btn_admin'], TEXTS['ru']['btn_admin']]:
        open_admin_panel(message)

    elif text in [TEXTS['tr']['btn_help'], TEXTS['en']['btn_help'], TEXTS['ru']['btn_help']]:
        bot.send_message(chat_id, t['help_text'])

    elif text in [TEXTS['tr']['btn_settings'], TEXTS['en']['btn_settings'], TEXTS['ru']['btn_settings']]:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="setlang:tr"),
            types.InlineKeyboardButton("🇬🇧 English", callback_data="setlang:en"),
            types.InlineKeyboardButton("🇷🇺 Русский", callback_data="setlang:ru")
        )
        bot.send_message(chat_id, t['lang_menu'], reply_markup=markup)

    elif chat_id in user_states:
        state = user_states[chat_id]

        if state['mode'] == 'setting_platform_topic' and text:
            p_name = state['platform']
            topic = text.replace(" ", "").replace("_", "")[:30]
            if not topic:
                topic = "Konu"
            link_display_name = f"{p_name} - {topic}"
            ensure_link(chat_id, link_display_name)
            clean_bot_name = BOT_USERNAME.replace("@", "")
            link = f"https://t.me/{clean_bot_name}?start={chat_id}_{p_name}_{topic}"
            
            share_url = f"https://t.me/share/url?url={urllib.parse.quote(link)}"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t['share_link_btn'], url=share_url))
            markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu:back"))
            
            bot.send_message(
                chat_id,
                t['link_ready'].format(topic=link_display_name, link=link),
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=markup
            )
            del user_states[chat_id]

        elif state['mode'] == 'sending_anon':
            target_id = state['target']
            platform = state.get('platform', 'Genel')
            topic = state.get('topic', 'Genel')
            link_display_name = state.get('link_display_name', f"{platform} - {topic}")
            all_users = get_all_users()
            t_lang = all_users.get(str(target_id), 'tr')
            
            try:
                msg_display = text if text else "📷 [Medya]"
                
                # Simple cleanup to prevent Markdown errors (optional)
                clean_msg = msg_display.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
                
                full_caption = TEXTS[t_lang]['new_msg'].format(
                    platform=platform, topic=topic, msg=clean_msg
                )

                if message.content_type == 'text':
                    sent_msg = bot.send_message(
                        int(target_id),
                        full_caption,
                        parse_mode="Markdown"
                    )
                else:
                    sent_msg = bot.copy_message(
                        int(target_id),
                        chat_id,
                        message.message_id,
                        caption=full_caption,
                        parse_mode="Markdown"
                    )

                # Token: reply:SENDER_ID:SENT_MSG_ID (one-time use button)
                reply_token_data = f"reply:{chat_id}:{sent_msg.message_id}"
                reply_markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton(TEXTS[t_lang]['reply_btn'], callback_data=reply_token_data)
                )
                bot.edit_message_reply_markup(int(target_id), sent_msg.message_id, reply_markup=reply_markup)

                bot.send_message(chat_id, t['sent'])
                increment_total_msgs()
                increment_link_msgs(target_id, link_display_name)
                # Prevent the same person from commenting on the same link again
                mark_sent_to_link(chat_id, target_id, link_display_name)
            except Exception as e:
                print(f"Mesaj gönderme hatası: {e}")
                bot.send_message(chat_id, t['send_error'])
            del user_states[chat_id]

        elif state['mode'] == 'support_msg':
            user = message.from_user
            full_name = user.first_name or ""
            if user.last_name:
                full_name += f" {user.last_name}"
            username_str = f" (@{user.username})" if user.username else ""
            msg_display = text if text else "📷 [Medya]"
            support_text = t['support_new_msg'].format(
                name=full_name,
                username=username_str,
                uid=chat_id,
                msg=msg_display
            )
            try:
                markup_admin = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🚫 Banla", callback_data=f"admin:ban:{chat_id}")
                )
                if message.content_type == 'text':
                    bot.send_message(ADMIN_ID, support_text, parse_mode="Markdown", reply_markup=markup_admin)
                else:
                    bot.copy_message(ADMIN_ID, chat_id, message.message_id, caption=support_text, parse_mode="Markdown", reply_markup=markup_admin)
                bot.send_message(chat_id, t['support_sent'], parse_mode="Markdown")
            except Exception as e:
                print(f"Destek mesajı hatası: {e}")
                bot.send_message(chat_id, t['send_error'])
            del user_states[chat_id]

        elif state['mode'] == 'replying_anon':
            target_id = state['target']
            all_users = get_all_users()
            t_lang = all_users.get(str(target_id), 'tr')
            
            try:
                msg_display = text if text else "📷 [Medya]"
                full_caption = TEXTS[t_lang]['reply_notify'].format(msg=msg_display)
                
                if message.content_type == 'text':
                    sent_msg = bot.send_message(
                        int(target_id),
                        full_caption,
                        parse_mode="Markdown"
                    )
                else:
                    sent_msg = bot.copy_message(
                        int(target_id),
                        chat_id,
                        message.message_id,
                        caption=full_caption,
                        parse_mode="Markdown"
                    )

                # One-time use reply button for the other side
                reply_token_data = f"reply:{chat_id}:{sent_msg.message_id}"
                reply_markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton(TEXTS[t_lang]['reply_btn'], callback_data=reply_token_data)
                )
                bot.edit_message_reply_markup(int(target_id), sent_msg.message_id, reply_markup=reply_markup)

                bot.send_message(chat_id, t['sent'])
            except Exception as e:
                print(f"Cevap gönderme hatası: {e}")
                bot.send_message(chat_id, t['reply_error'])
            del user_states[chat_id]
    else:
        bot.send_message(chat_id, "👇", reply_markup=create_main_menu(lang, chat_id))

init_db()
start_token_cleaner()
print("Bot is starting...")
bot.infinity_polling()
