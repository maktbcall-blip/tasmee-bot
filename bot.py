import subprocess
import sys

# تثبيت المكتبات تلقائياً عند بدء التشغيل لضمان عدم حدوث خطأ
def install_packages():
    required = {'python-telegram-bot', 'openai'}
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_packages()

import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from openai import OpenAI

# قراءة المفاتيح بأمان من متغيرات البيئة في المنصة
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    voice = update.message.voice
    
    processing_msg = await update.message.reply_text(f"🎙️ أهلاً بك يا {user_name}! جاري استقبال بصمتك الصوتية وتحليلها بدقة...")
    file_path = "recitation.ogg"
    
    try:
        file = await context.bot.get_file(voice.file_id)
        await file.download_to_drive(file_path)
        
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ar",
                prompt="قرآن كريم، حديث نبوي، متون علمية، شعر عربي فصيح"
            )
        user_text = transcript.text
        
        prompt = f"""
        أنت معلم خبير ومرشد محترف في تحفيظ القرآن الكريم وتصحيح المتون العلمية والشعر العربي.
        استمعت إلى الطالب (عبر تحويل الصوت إلى نص) وكان التسميع كالتالي:
        "{user_text}"
        
        يرجى تقديم رد متطور ومفيد يشمل الآتي:
        1. **النص المُسمّع بوضوح:** اعرض ما قاله الطالب بدقة.
        2. **التصحيح اللفظي والإملائي:** نبهه إذا كان هناك خطأ في الكلمات أو الحركات المحتملة.
        3. **التوجيه والتقييم:** بأسلوب تربوي مشجّع ولطيف، أعطه نصيحة أو تقديراً لإتقانه.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        correction_result = response.choices[0].message.content
        
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_msg.message_id)
        
        await update.message.reply_text(
            f"📖 **تقرير التسميع الذكي:**\n\n{correction_result}"
        )
        
    except Exception as e:
        await update.message.reply_text(f"⚠️ حدث خطأ أثناء معالجة التسميع: {str(e)}")
        
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    if not TOKEN:
        print("خطأ: يجدر تعيين TELEGRAM_TOKEN")
        return
        
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    print("البوت المتطور يعمل الآن ويستمع للتلاوات...")
    app.run_polling()

if __name__ == '__main__':
    main()
