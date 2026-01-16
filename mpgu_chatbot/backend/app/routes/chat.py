from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import json
import random
import re

router = APIRouter()

class Message(BaseModel):
    message: str
    user_id: str = "anonymous"

# Smart response database for MPGU
mpgu_responses = {
    # Russian responses
    "привет": [
        "Здравствуйте! Я MPGU Assistant. Чем могу помочь с вопросами об университете?",
        "Привет! Я ваш помощник по МПГУ. Задавайте вопросы!",
        "Добрый день! Чем могу помочь с Московским педагогическим государственным университетом?"
    ],
    "здравствуйте": [
        "Здравствуйте! Я MPGU Assistant. Как могу помочь с вопросами об университете?",
        "Добрый день! Задавайте вопросы о МПГУ и платформе Enlight.",
        "Здравствуйте! Готов помочь с информацией о МПГУ."
    ],
    "курс": [
        "Для регистрации на курсы:\n\n1. Войдите на платформу Enlight Russia: https://enlightrussia.ru\n2. Перейдите в раздел 'Мои курсы'\n3. Выберите интересующий курс\n4. Нажмите 'Записаться' или 'Enroll'\n\nДоступны курсы для школьников (ЕГЭ) и студентов.",
        "Регистрация на курсы МПГУ проходит через платформу Enlight. Выберите нужный курс и нажмите регистрацию.",
        "Курсы доступны на enlightrussia.ru. Выберите подходящий курс и нажмите регистрацию."
    ],
    "расписание": [
        "Расписание занятий доступно:\n\n• В личном кабинете студента\n• На официальном сайте МПГУ: https://mpgu.su\n• Через мобильное приложение МПГУ\n• В учебном отделе вашего факультета",
        "Актуальное расписание можно найти в студенческом кабинете или на сайте университета.",
        "Расписание обновляется каждый семестр. Проверяйте в личном кабинете или на сайте МПГУ."
    ],
    "преподаватель": [
        "Поиск преподавателей:\n\n1. Платформа Enlight → Раздел 'Преподаватели'\n2. Фильтр по предметам и рейтингу\n3. Просмотр профилей и отзывов\n4. Запись на консультации\n\nТакже можно обратиться в деканат вашего факультета.",
        "Преподаватели МПГУ доступны для консультаций через платформу Enlight.",
        "Вы можете найти преподавателей по предметам в разделе 'Найти преподавателя' на Enlight."
    ],
    "мпгу": [
        "**МПГУ - Московский педагогический государственный университет**\n\n📍 Адрес: Москва, ул. Малая Пироговская, 1\n🌐 Сайт: https://mpgu.su\n📞 Телефон: +7 (495) 438-18-77\n📧 Email: info@mpgu.su\n\n🎓 Основан в 1872 году\n🏫 Один из ведущих педагогических вузов России\n📚 Факультеты: педагогический, психологический, иностранных языков, исторический и другие",
        "МПГУ - ведущий педагогический университет России с богатой историей с 1872 года.",
        "Московский педагогический государственный университет - крупный образовательный центр в Москве."
    ],
    "enlight": [
        "**Enlight Russia - образовательная платформа МПГУ**\n\n🌐 Сайт: https://enlightrussia.ru\n📚 Для кого: школьники, студенты, преподаватели\n🎯 Направления:\n   • Подготовка к ЕГЭ\n   • Университетские курсы\n   • Повышение квалификации\n   • Научные работы\n\n💡 Бесплатная платформа для обучения и преподавания.",
        "Enlight - это единая обучающая платформа МПГУ для школьников и студентов.",
        "Платформа Enlight Russia предоставляет курсы и учебные материалы для всех уровней образования."
    ],
    "егэ": [
        "**Подготовка к ЕГЭ в МПГУ:**\n\n• Курсы на платформе Enlight: https://enlightrussia.ru\n• Занятия с опытными преподавателями университета\n• Все предметы ЕГЭ: математика, русский язык, физика, химия, биология, история, обществознание\n• Пробные тестирования и консультации\n\n📞 Запись: +7 (495) 438-18-00",
        "МПГУ предлагает комплексную подготовку к ЕГЭ по всем предметам на платформе Enlight.",
        "Курсы ЕГЭ доступны на платформе Enlight Russia с преподавателями МПГУ."
    ],
    "контакт": [
        "**Контакты МПГУ:**\n\n📞 Приёмная комиссия: +7 (495) 438-18-00\n📞 Общий отдел: +7 (495) 438-18-77\n📧 Email: info@mpgu.su\n📍 Адрес: Москва, ул. Малая Пироговская, 1\n🌐 Сайт: https://mpgu.su\n\n🕒 Часы работы: пн-пт 9:00-18:00",
        "Основные контакты университета доступны на сайте mpgu.su в разделе 'Контакты'.",
        "Свяжитесь с МПГУ по телефону +7 (495) 438-18-77 или через сайт университета."
    ],
    
    # English responses
    "hello": [
        "Hello! I'm MPGU Assistant. How can I help you with Moscow Pedagogical State University?",
        "Hi! I'm your MPGU helper. Ask me anything about the university!",
        "Hello! I'm here to help with Moscow Pedagogical State University matters."
    ],
    "hi": [
        "Hi! I'm MPGU Assistant. What would you like to know about our university?",
        "Hello! How can I assist you with MPGU today?",
        "Hi there! I'm your MPGU helper for university information."
    ],
    "course": [
        "**Course Registration at MPGU:**\n\n1. Login to Enlight Russia platform: https://enlightrussia.ru\n2. Go to 'My Courses' section\n3. Select your desired course\n4. Click 'Enroll' or 'Register'\n\nAvailable courses for school students (ЕГЭ prep) and university students.",
        "Course registration is done through the Enlight platform. Choose your course and enroll.",
        "You can find and enroll in courses at enlightrussia.ru in the courses section."
    ],
    "schedule": [
        "**Class Schedule Information:**\n\n• Check your student dashboard\n• MPGU official website: https://mpgu.su\n• MPGU mobile application\n• Your faculty's academic office\n\nSchedules are updated each semester.",
        "Class schedules are available in the student portal and on the university website.",
        "The current academic schedule is posted on the MPGU website and in student accounts."
    ],
    "tutor": [
        "**Finding Tutors at MPGU:**\n\n1. Enlight Platform → 'Tutors' section\n2. Filter by subjects and ratings\n3. View tutor profiles and reviews\n4. Schedule consultations\n\nYou can also contact your faculty dean's office for tutor recommendations.",
        "MPGU tutors are available through the Enlight platform for various subjects.",
        "Find tutors by subject in the 'Find Tutors' section on Enlight platform."
    ],
    "mpgu info": [
        "**MPGU - Moscow Pedagogical State University**\n\n📍 Address: Moscow, Malaya Pirogovskaya Street, 1\n🌐 Website: https://mpgu.su\n📞 Phone: +7 (495) 438-18-77\n📧 Email: info@mpgu.su\n\n🎓 Founded in 1872\n🏫 One of Russia's leading pedagogical universities\n📚 Faculties: pedagogy, psychology, foreign languages, history, and more",
        "MPGU is a leading pedagogical university in Russia with history since 1872.",
        "Moscow Pedagogical State University is a major educational center in Moscow."
    ],
    "enlight platform": [
        "**Enlight Russia - MPGU's Educational Platform**\n\n🌐 Website: https://enlightrussia.ru\n📚 For: school students, university students, teachers\n🎯 Programs:\n   • ЕГЭ preparation\n   • University courses\n   • Professional development\n   • Research projects\n\n💡 Free platform for learning and teaching.",
        "Enlight is MPGU's unified learning platform for students and teachers.",
        "The Enlight Russia platform provides educational courses and materials."
    ],
    "help": [
        "**I can help you with:**\n\n🎓 **University Information**\n• MPGU contacts, address, and history\n• University programs and faculties\n• Campus information and facilities\n\n📚 **Academic Assistance**\n• Course registration procedures\n• Class schedules and academic calendar\n• Study materials and resources\n• Tutor and teacher search\n\n🌐 **Platform Support**\n• Enlight Russia navigation\n• Technical support guidance\n• Educational resource finding\n\nJust ask me anything about MPGU!",
        "I'm here to help with MPGU-related questions. Ask me about courses, schedules, contacts, or the Enlight platform.",
        "I specialize in MPGU information. Try asking about courses, schedules, or university services."
    ]
}

def detect_language(text):
    """Detect if text is Russian or English"""
    russian_chars = len(re.findall('[а-яА-Я]', text))
    return 'ru' if russian_chars > len(text) * 0.3 else 'en'

def get_smart_response(user_message):
    """Generate intelligent response based on user input"""
    user_message_lower = user_message.lower()
    detected_lang = detect_language(user_message)
    
    # Check for exact matches first
    for key, responses in mpgu_responses.items():
        if key in user_message_lower:
            return random.choice(responses)
    
    # Check for partial matches
    words = user_message_lower.split()
    for word in words:
        if word in mpgu_responses:
            return random.choice(mpgu_responses[word])
    
    # Check for related topics with intelligent matching
    topic_mapping = {
        'ru': {
            'регистрац': 'курс',
            'запис': 'курс',
            'расписан': 'расписание', 
            'занят': 'расписание',
            'учитель': 'преподаватель',
            'преподавател': 'преподаватель',
            'контакт': 'контакт',
            'телефон': 'контакт',
            'адрес': 'мпгу',
            'университет': 'мпгу',
            'платформ': 'enlight',
            'обучен': 'enlight',
            'егэ': 'егэ',
            'экзамен': 'егэ',
            'помощ': 'help'
        },
        'en': {
            'register': 'course',
            'enroll': 'course',
            'signup': 'course',
            'schedule': 'schedule',
            'time': 'schedule',
            'class': 'schedule',
            'teacher': 'tutor',
            'professor': 'tutor',
            'contact': 'mpgu info',
            'phone': 'mpgu info',
            'address': 'mpgu info',
            'university': 'mpgu info',
            'platform': 'enlight platform',
            'learn': 'enlight platform',
            'exam': 'егэ',
            'help': 'help',
            'information': 'help'
        }
    }
    
    # Check for topic matches
    for keyword, response_key in topic_mapping[detected_lang].items():
        if keyword in user_message_lower:
            return random.choice(mpgu_responses[response_key])
    
    # Fallback responses
    fallback_responses = {
        'ru': [
            "Спасибо за ваш вопрос о МПГУ! Для получения точной информации рекомендую:\n\n• Посетить официальный сайт: https://mpgu.su\n• Обратиться в приёмную комиссию: +7 (495) 438-18-00\n• Проверить информацию на платформе Enlight: https://enlightrussia.ru\n\nМогу ли я помочь с чем-то ещё?",
            "Интересный вопрос! Для детальной информации по этой теме советую:\n\n• Обратиться в учебный отдел МПГУ\n• Проверить актуальную информацию на сайте университета\n• Посмотреть ответы в разделе FAQ на enlightrussia.ru\n\nЧто ещё вас интересует о МПГУ?",
            "По этому вопросу рекомендую уточнить информацию:\n\n• В студенческом офисе МПГУ\n• Через официальные каналы связи университета\n• На платформе Enlight в разделе поддержки\n\nМогу помочь с другими вопросами о университете!"
        ],
        'en': [
            "Thank you for your question about MPGU! For accurate information, I recommend:\n\n• Visiting the official website: https://mpgu.su\n• Contacting the admissions office: +7 (495) 438-18-00\n• Checking the Enlight platform: https://enlightrussia.ru\n\nCan I help with anything else about the university?",
            "Good question! For detailed information on this topic, I suggest:\n\n• Contacting the MPGU academic department\n• Checking the university website for updates\n• Looking at the FAQ section on enlightrussia.ru\n\nWhat else would you like to know about MPGU?",
            "For this specific question, I recommend checking:\n\n• The MPGU student office\n• Official university communication channels\n• The support section on Enlight platform\n\nI can help with other university-related questions!"
        ]
    }
    
    return random.choice(fallback_responses[detected_lang])

def try_hugging_face_api(user_message):
    """Try Hugging Face API with fallback"""
    try:
        headers = {
            "Authorization": f"Bearer {Config.HUGGING_FACE_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Simple prompt for the model
        prompt = f"""You are MPGU Assistant for Moscow Pedagogical State University. Answer this question helpfully and concisely in the same language as the question.

Question: {user_message}

Answer:"""
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 300,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        response = requests.post(Config.HUGGING_FACE_API_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '').strip()
                # Extract only the assistant's response
                if "Answer:" in generated_text:
                    return generated_text.split("Answer:")[-1].strip()
                return generated_text
        return None
    except:
        return None

@router.post("/chat")
async def chat_endpoint(msg: Message):
    try:
        user_message = msg.message.strip()
        user_id = msg.user_id
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        print(f"🔍 Processing message: {user_message}")
        
        # First try Hugging Face API
        ai_reply = None
        api_used = "Smart Response"
        
        # Only try API for non-simple messages (avoid overloading)
        if len(user_message) > 3:
            ai_reply = try_hugging_face_api(user_message)
            if ai_reply and len(ai_reply) > 10:  # Only use if we got a meaningful response
                api_used = "Hugging Face AI"
                print(f"✅ Using Hugging Face API response")
            else:
                ai_reply = None
                print(f"🔄 Hugging Face API unavailable, using smart responses")
        
        # If API failed or wasn't attempted, use smart responses
        if not ai_reply:
            ai_reply = get_smart_response(user_message)
        
        return {
            "reply": ai_reply,
            "message_id": random.randint(1000, 9999),
            "user_id": user_id,
            "api_used": api_used
        }
        
    except Exception as e:
        # Ultimate fallback - never raise HTTPException to frontend
        error_responses = {
            'ru': "Извините, возникли временные технические трудности. Для помощи с МПГУ посетите https://mpgu.su или позвоните +7 (495) 438-18-77",
            'en': "Sorry, we're experiencing temporary technical issues. For MPGU assistance visit https://mpgu.su or call +7 (495) 438-18-77"
        }
        
        user_msg = msg.message if hasattr(msg, 'message') else ""
        is_russian = any(cyrillic in user_msg for cyrillic in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        fallback = error_responses["ru"] if is_russian else error_responses["en"]
        
        return {
            "reply": fallback,
            "message_id": random.randint(1000, 9999),
            "user_id": getattr(msg, 'user_id', 'anonymous'),
            "api_used": "Fallback System"
        }