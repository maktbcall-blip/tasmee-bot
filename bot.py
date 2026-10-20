import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# إعداد نظام التسجيل لمتابعة حالة البوت
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# دالة معالجة الرسائل النصية
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"📖 استلمت التسميع النصي:\n> {user_text}\n\n⏳ جاري التحقق من الصحة...")

# دالة معالجة الرسائل الصوتية (البصمات)
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    voice = update.message.voice
    
    # الحصول على ملف الصوت من سيرفرات تلغرام
    file = await context.bot.get_file(voice.file_id)
    
    # حفظ الملف الصوتي محلياً بصيغة ogg
    file_path = "recitation.ogg"
    await file.download_to_drive(file_path)
    
    await update.message.reply_text(
        f" أهلاً بك يا {user_name}! 🎙️\n"
        f"استلمت بصمتك الصوتية وجاري حفظها ومعالجتها...\n"
        f"⏳ سيتم تحويل الصوت إلى نص ومقارنته قريباً!"
    )
    
    # هنا لاحقاً سنقوم بإرسال ملف 'recitation.ogg' إلى نموذج الذكاء الاصطناعي (مثل Whisper) لتحويله لنص ثم مقارنته

def main():
    # التوكن الخاص ببوتك الذي أنشأته عبر BotFather
    TOKEN = "8575007507:AAEX1xEObQr3rmqeA-xJJ7XgQw6YIYuM9ts"
    
    app = ApplicationBuilder().token(TOKEN).build()

    # ربط البوت باستقبال الرسائل النصية والصوتية
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("البوت يعمل الآن ويستمع للبصمات الصوتية والنصوص...")
    app.run_polling()

if __name__ == '__main__':
    main()
