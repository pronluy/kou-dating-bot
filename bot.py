import logging
import requests
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from geopy.geocoders import Nominatim
import os

API_TOKEN = '8675039854:AAE_anpP2Z-MPxxQbW0NRRXlr6RnAzpuja8'
PORT = os.environ.get("PORT", 8000)
BASE_URL = f"http://127.0.0.1:{PORT}"
BOT_USERNAME = "KouMatch_bot"

geolocator = Nominatim(user_agent="kou_dating_app")
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# កញ្ចប់វចនានុក្រមភាសា (I18N LANGUAGE PACK)
TEXTS = {
    "kh": {
        "welcome": "ស្វាគមន៍មកកាន់ KOU! Wellcome KOU\nសូមជ្រើសរើសភាសា! Select Language:",
        "ask_name": "សូមបំពេញឈ្មោះរបស់អ្នក:",
        "ask_age": "បំពេញអាយុរបស់អ្នក:",
        "err_age": "សូមវាយជាលេខ:",
        "ask_gender": "ជ្រើសរើសភេទរបស់អ្នកខាងក្រោម:",
        "ask_looking_for": "តើអ្នកចង់ស្វែងរកភេទអ្វី?",
        "btn_male": "ប្រុស",
        "btn_female": "ស្រី",
        "ask_location": "📍សូមកំណត់ទីតាំងរបស់អ្នក (Location)\n\n📱ទូរស័ព្ទ:ចុចប៊ូតុង 'ផ្ញើទីតាំងបច្ចុប្បន្ន' ខាងក្រោម\n💻កុំព្យូទ័រ:សូមវាយឈ្មោះ ទីក្រុង, ប្រទេស (ឧ. Phnom Penh, Cambodia):",
        "btn_gps": "📍ផ្ញើទីតាំងបច្ចុប្បន្ន (GPS) 📱",
        "loc_found": "✅ចាប់បានទីតាំង៖{}, {}\n\n✍️សូមសរសេរពីចំណូលចិត្ត ឬ ប្រភេទដៃគូ (ឧ. ចូលចិត្តស្តាប់ចម្រៀង/ខ្ពស់/ស្គម...):",
        "ask_photo": "📸 ជិតរួចរាល់ហើយ! សូមផ្ញើរូបថតរបស់អ្នកមួយសន្លឹក:",
        "loc_err": "❌ មិនអាចចាប់ទីតាំងបានទេ។ សូមវាយឈ្មោះទីក្រុងជាអក្សរវិញ",
        "loc_err_map": "❌ រកមិនឃើញទីតាំងនេះលើផែនទីទេ។ សូមវាយឈ្មោះ ទីក្រុង និងប្រទេស ឱ្យបានច្បាស់",
        "reg_success": "🎉 រួចរាល់! គណនីរបស់អ្នកត្រូវបានរក្សាទុកដោយជោគជ័យ!",
        
        "btn_match": "🔍 រកគូ (Match)",
        "btn_profile": "👤 គណនី (Profile)",
        "btn_pref": "⚙️ កំណត់ទីតាំងស្វែងរក",
        "btn_lang": "🌐 ភាសា",
        
        "profile_cap": "👤 ឈ្មោះ: {}\n🎂 អាយុ: {}\n📍 ទីតាំង: {}, {}\n📝 Bio: {}",
        "btn_edit": "✏️ កែប្រែគណនី",
        "btn_delete": "🗑️ លុបគណនី",
        "btn_invite": "🎁 ណែនាំមិត្ត (Invite)",
        "invite_text": "🎁 អញ្ជើញមិត្តភក្តិរបស់អ្នក!\n\nចំនួនដែលអ្នកបានចែករំលែក: {} នាក់\n\nនេះគឺជា Link របស់អ្នក:\n👉 `https://t.me/{}?start=ref_{}`\n\nផ្ញើ Link នេះទៅមិត្តភក្តិ ឬ Share លើ Social Media ដើម្បីអញ្ជើញពួកគេចូលរួម ដើម្បីទទួលបានរង្វាន់🎁!",
        
        "no_profile": "រកមិនឃើញគណនីទេ។ សូមវាយ /start ដើម្បីចុះឈ្មោះ។",
        "del_success": "🗑️ គណនីរបស់អ្នកត្រូវបានលុបដោយជោគជ័យចេញពីប្រព័ន្ធ។\nវាយ /start ដើម្បីចុះឈ្មោះម្តងទៀត។",
        "del_fail": "❌ មិនអាចលុបបានទេ។",
        "edit_start": "📝 តោះ! ចាប់ផ្តើមកែប្រែគណនីរបស់អ្នក។\nសូមជ្រើសរើសភាសា:",
        
        "match_title": "✨ ពេញចិត្តទេ?\n👤 ឈ្មោះ: {}\n🎂 អាយុ: {}\n📍 ទីក្រុង: {}, {}\n📝 Bio: {}",
        "btn_like": "❤️ Like",
        "btn_skip": "⏭️ Skip",
        "no_match": "ស្វែងរកអស់ហើយ! ពេលនេះមិនទាន់មានគូថ្មីនៅក្នុងតំបន់របស់អ្នកទេ។ 🥺\n💡 គន្លឹះ៖ សូមចុចប៊ូតុង [⚙️ កំណត់ទីតាំងស្វែងរក] នៅខាងក្រោម ដើម្បីប្តូរទៅជា (គ្រប់ទីកន្លែង) វិញ! ដើម្បីស្វែងរកអ្នកនៅតំបន់ផ្សេងៗទៀត!",
        "req_acc": "❌ អ្នកត្រូវមានគណនីសិន ទើបអាច Match បាន។",
        "like_sent": "💖 ផ្ញើក្តីស្រឡាញ់ជោគជ័យ!",
        "skip_sent": "⏭️ រំលង...",
        "its_match": "🎉 It's a Match! អ្នកទាំងពីរបានពេញចិត្តគ្នាទៅវិញទៅមក! 💞",
        "chat_him": "💬 ចុចទីនេះដើម្បីជជែកគ្នា",
        "chat_back": "💬 ចុចទីនេះដើម្បីជជែកគ្នា",
        "match_notif": "🎉 Match ថ្មី! មនុស្សដែលអ្នកបាន Like ទើបតែ Like អ្នកវិញហើយ! កុំឱ្យឱកាសនេះកន្លងផុតទៅ!",
        
        "pref_title": "⚙️ កំណត់ទីតាំងស្វែងរកដៃគូរបស់អ្នក៖\nសូមជ្រើសរើសជម្រើសខាងក្រោម៖",
        "pref_local_btn": "📍 នៅជិតខ្ញុំ (ទីក្រុងតែមួយ)",
        "pref_global_btn": "🌍 គ្រប់ទីកន្លែង (ទូទាំងពិភពលោក)",
        "pref_specific_btn": "✍️ ជ្រើសរើសទីក្រុងផ្សេង...",
        "pref_local_set": "✅ បានកំណត់! ប្រព័ន្ធនឹងស្វែងរកតែអ្នកដែលនៅ ទីក្រុងជាមួយអ្នក ប៉ុណ្ណោះ។",
        "pref_global_set": "✅ បានកំណត់! ប្រព័ន្ធនឹងស្វែងរកអ្នក ទូទាំងពិភពលោក។",
        "pref_ask_spec": "🌍 សូមវាយឈ្មោះ ទីក្រុង និងប្រទេស ដែលអ្នកចង់ស្វែងរកដៃគូ (ឧ. Tokyo, Japan):",
        "pref_spec_set": "✅ បានកំណត់! ប្រព័ន្ធនឹងស្វែងរកតែអ្នកដែលនៅ {} ប៉ុណ្ណោះ។",
        
        "ask_lang": "🌐 សូមជ្រើសរើសភាសារបស់អ្នក:",
        "lang_set": "✅ ភាសាត្រូវបានប្តូរទៅជា ខ្មែរ ដោយជោគជ័យ!",
        "got_liked": "🔔 <b>ដំណឹងពិសេស!</b>\nមាននរណាម្នាក់ទើបតែលួច <b>Like ❤️</b> Profile របស់អ្នកហើយ!\n\nសូមបន្តចុច <b>🔍 រកគូ (Match)</b> ដើម្បីស្វែងរកថាគាត់ជានរណា! 😉"
    },
    "en": {
        "welcome": "Welcome to KOU!\nPlease select your language:",
        "ask_name": "Please enter your full name:",
        "ask_age": "Enter your age:",
        "err_age": "Please enter a valid number:",
        "ask_gender": "Select your gender:",
        "ask_looking_for": "Who are you looking for?",
        "btn_male": "Male",
        "btn_female": "Female",
        "ask_location": "📍 Please set your location\n\n📱 Mobile: Tap 'Send GPS' below\n💻 PC: Type your City, Country (e.g. Seoul, South Korea):",
        "btn_gps": "📍 Send GPS Location 📱",
        "loc_found": "✅ Location found: {}, {}\n\n✍️ Please write a short bio about yourself (e.g., Hobbies, interests):",
        "ask_photo": "📸 Almost done! Send your photo:",
        "loc_err": "❌ Cannot detect location. Please type your city.",
        "loc_err_map": "❌ Location not found on map. Please type clearly.",
        "reg_success": "🎉 All set! Your profile has been saved successfully!",
        
        "btn_match": "🔍 Match",
        "btn_profile": "👤 Profile",
        "btn_pref": "⚙️ Search Preferences",
        "btn_lang": "🌐 Language",
        
        "profile_cap": "👤 Name: {}\n🎂 Age: {}\n📍 Location: {}, {}\n📝 Bio: {}",
        "btn_edit": "✏️ Edit Profile",
        "btn_delete": "🗑️ Delete Account",
        "btn_invite": "🎁 Invite Friends",
        "invite_text": "🎁 Invite your friends!\n\nTotal Invites: {} users\n\nHere is your unique referral link:\n👉 `https://t.me/{}?start=ref_{}`\n\nShare this link to invite your friends to KOU! and get rewards!🎁",
        
        "no_profile": "Profile not found. Send /start to register.",
        "del_success": "🗑️ Account deleted successfully.\nSend /start to register again.",
        "del_fail": "❌ Cannot delete account.",
        "edit_start": "📝 Let's edit your profile.\nSelect your language:",
        
        "match_title": "✨ Like what you see?\n👤 Name: {}\n🎂 Age: {}\n📍 City: {}, {}\n📝 Bio: {}",
        "btn_like": "❤️ Like",
        "btn_skip": "⏭️ Skip",
        "no_match": "No more profiles found in your area right now! 🥺\n💡 Tip: Tap on [⚙️ Search Preferences] below and switch to (Global) to discover more people!",
        "req_acc": "❌ You need an account to match.",
        "like_sent": "💖 Like sent!",
        "skip_sent": "⏭️ Skipped...",
        "its_match": "🎉 It's a Match! The feeling is mutual! 💞",
        "chat_him": "💬 Click here to chat Now",
        "chat_back": "💬 Click here to chat back",
        "match_notif": "🎉 New Match! Someone you liked just liked you back! Don't miss out!",
        
        "pref_title": "⚙️ Set your search preferences:\nSelect an option below:",
        "pref_local_btn": "📍 Local (Same City)",
        "pref_global_btn": "🌍 Global (Worldwide)",
        "pref_specific_btn": "✍️ Choose another city...",
        "pref_local_set": "✅ Set! Searching only in your city.",
        "pref_global_set": "✅ Set! Searching worldwide.",
        "pref_ask_spec": "🌍 Type the City and Country you want to search in (e.g. Tokyo, Japan):",
        "pref_spec_set": "✅ Set! Searching only in {}.",
        
        "ask_lang": "🌐 Please select your language:",
        "lang_set": "✅ Language successfully changed to **English**!",
        "got_liked": "🔔 <b>Special Notification!</b>\nSomeone just <b>Liked ❤️</b> your profile!\n\nKeep tapping <b>🔍 Match</b> to find out who! 😉"
    }
}

def get_user_lang(tg_id):
    try:
        res = requests.get(f"{BASE_URL}/profile/{tg_id}", timeout=2)
        if res.status_code == 200:
            return res.json().get('language', 'kh')
    except: pass
    return 'kh'

class RegisterState(StatesGroup):
    waiting_for_lang = State()
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_gender = State()
    waiting_for_looking_for = State()
    waiting_for_location = State()
    waiting_for_bio = State() 
    waiting_for_photo = State()
    waiting_for_specific_pref = State() 

def get_main_menu(lang):
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["btn_match"]), KeyboardButton(text=t["btn_lang"])],
            [KeyboardButton(text=t["btn_profile"]), KeyboardButton(text=t["btn_pref"])]
        ], 
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referred_by = int(args[1].split("_")[1])
            await state.update_data(referred_by=referred_by)
        except: pass

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🇰🇭 ខ្មែរ", callback_data='lang_kh'), InlineKeyboardButton(text="🇬🇧 English", callback_data='lang_en')]])
    await message.answer(TEXTS["kh"]["welcome"], reply_markup=kb)
    await state.set_state(RegisterState.waiting_for_lang)

@dp.callback_query(RegisterState.waiting_for_lang)
async def set_lang(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split('_')[1]
    await state.update_data(lang=lang)
    await callback.message.answer(TEXTS[lang]["ask_name"])
    await state.set_state(RegisterState.waiting_for_name)

@dp.message(RegisterState.waiting_for_name)
async def set_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    lang = (await state.get_data()).get('lang', 'kh')
    await message.answer(TEXTS[lang]["ask_age"])
    await state.set_state(RegisterState.waiting_for_age)

@dp.message(RegisterState.waiting_for_age)
async def set_age(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'kh')
    if not message.text.isdigit(): 
        return await message.answer(TEXTS[lang]["err_age"])
    
    await state.update_data(age=int(message.text))
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=TEXTS[lang]["btn_male"]), KeyboardButton(text=TEXTS[lang]["btn_female"])]], resize_keyboard=True, one_time_keyboard=True)
    await message.answer(TEXTS[lang]["ask_gender"], reply_markup=kb)
    await state.set_state(RegisterState.waiting_for_gender)

@dp.message(RegisterState.waiting_for_gender)
async def set_gender(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'kh')
    gender = 'male' if message.text in [TEXTS["kh"]["btn_male"], TEXTS["en"]["btn_male"]] else 'female'
    await state.update_data(gender=gender)
    
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=TEXTS[lang]["btn_male"]), KeyboardButton(text=TEXTS[lang]["btn_female"])]], resize_keyboard=True, one_time_keyboard=True)
    await message.answer(TEXTS[lang]["ask_looking_for"], reply_markup=kb)
    await state.set_state(RegisterState.waiting_for_looking_for)

@dp.message(RegisterState.waiting_for_looking_for)
async def request_location(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'kh')
    look = 'male' if message.text in [TEXTS["kh"]["btn_male"], TEXTS["en"]["btn_male"]] else 'female'
    await state.update_data(looking_for=look)
    
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=TEXTS[lang]["btn_gps"], request_location=True)]], resize_keyboard=True, one_time_keyboard=True)
    await message.answer(TEXTS[lang]["ask_location"], reply_markup=kb, parse_mode="Markdown")
    await state.set_state(RegisterState.waiting_for_location)

@dp.message(RegisterState.waiting_for_location, F.location)
async def handle_location_gps(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'kh')
    try:
        loc = geolocator.reverse(f"{message.location.latitude}, {message.location.longitude}", language='en')
        addr = loc.raw.get('address', {})
        city = addr.get('state') or addr.get('city') or addr.get('province') or "Unknown"
        country = addr.get('country') or "Unknown"
        city = city.replace("Province", "").replace("City", "").strip()
        
        await state.update_data(city=city, country=country)
        await message.answer(TEXTS[lang]["loc_found"].format(city, country), reply_markup=types.ReplyKeyboardRemove(), parse_mode="Markdown")
        await state.set_state(RegisterState.waiting_for_bio)
    except:
        await message.answer(TEXTS[lang]["loc_err"])

@dp.message(RegisterState.waiting_for_location, F.text)
async def handle_location_typed(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'kh')
    try:
        location = geolocator.geocode(message.text, language='en')
        if location:
            city = location.address.split(',')[0].strip()
            country = location.address.split(',')[-1].strip()
            await state.update_data(city=city, country=country)
            await message.answer(TEXTS[lang]["loc_found"].format(city, country), reply_markup=types.ReplyKeyboardRemove(), parse_mode="Markdown")
            await state.set_state(RegisterState.waiting_for_bio)
        else:
            await message.answer(TEXTS[lang]["loc_err_map"])
    except:
        await message.answer(TEXTS[lang]["loc_err_map"])

@dp.message(RegisterState.waiting_for_bio)
async def set_bio(message: types.Message, state: FSMContext):
    await state.update_data(bio=message.text)
    lang = (await state.get_data()).get('lang', 'kh')
    await message.answer(TEXTS[lang]["ask_photo"])
    await state.set_state(RegisterState.waiting_for_photo)

@dp.message(RegisterState.waiting_for_photo, F.photo)
async def set_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'kh')
    
    payload = {
        "tg_id": message.from_user.id, "full_name": data['full_name'],
        "age": data['age'], "gender": data['gender'],
        "looking_for": data['looking_for'], "city": data['city'],
        "country": data['country'], "lang": lang, 
        "photo_url": message.photo[-1].file_id,
        "bio": data.get('bio', ''),
        "referred_by": data.get('referred_by')
    }
    
    await asyncio.to_thread(requests.post, f"{BASE_URL}/register", json=payload)
    await message.answer(TEXTS[lang]["reg_success"], reply_markup=get_main_menu(lang))
    await state.clear()

@dp.message(F.text.in_([TEXTS["kh"]["btn_lang"], TEXTS["en"]["btn_lang"]]))
async def show_language_options(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇰🇭 ខ្មែរ", callback_data='setlang_kh')],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data='setlang_en')]
    ])
    await message.answer(TEXTS[lang]["ask_lang"], reply_markup=kb)

@dp.callback_query(F.data.startswith("setlang_"))
async def handle_language_change(callback: types.CallbackQuery):
    new_lang = callback.data.split('_')[1]
    payload = {"tg_id": callback.from_user.id, "lang": new_lang}
    await asyncio.to_thread(requests.post, f"{BASE_URL}/language", json=payload)
    
    await callback.message.delete()
    await callback.message.answer(TEXTS[new_lang]["lang_set"], reply_markup=get_main_menu(new_lang), parse_mode="Markdown")

@dp.message(F.text.in_([TEXTS["kh"]["btn_pref"], TEXTS["en"]["btn_pref"]]))
async def show_preferences(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]["pref_local_btn"], callback_data="pref_local")],
        [InlineKeyboardButton(text=TEXTS[lang]["pref_global_btn"], callback_data="pref_global")],
        [InlineKeyboardButton(text=TEXTS[lang]["pref_specific_btn"], callback_data="pref_specific")]
    ])
    await message.answer(TEXTS[lang]["pref_title"], reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "pref_local")
async def set_pref_local(callback: types.CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    payload = {"tg_id": callback.from_user.id, "preference": "local", "search_city": ""}
    await asyncio.to_thread(requests.post, f"{BASE_URL}/preference", json=payload)
    await callback.message.edit_text(TEXTS[lang]["pref_local_set"], parse_mode="Markdown")

@dp.callback_query(F.data == "pref_global")
async def set_pref_global(callback: types.CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    payload = {"tg_id": callback.from_user.id, "preference": "global", "search_city": ""}
    await asyncio.to_thread(requests.post, f"{BASE_URL}/preference", json=payload)
    await callback.message.edit_text(TEXTS[lang]["pref_global_set"], parse_mode="Markdown")

@dp.callback_query(F.data == "pref_specific")
async def set_pref_specific(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    await callback.message.edit_text(TEXTS[lang]["pref_ask_spec"])
    await state.set_state(RegisterState.waiting_for_specific_pref)

@dp.message(RegisterState.waiting_for_location, F.location)
async def handle_location_gps(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'kh')
    try:
        # ព្យាយាមចាប់ទីតាំងតាមរយៈ GPS
        loc = await asyncio.to_thread(geolocator.reverse, f"{message.location.latitude}, {message.location.longitude}", language='en', timeout=5)
        
        if loc and loc.raw.get('address'):
            addr = loc.raw.get('address', {})
            city = addr.get('state') or addr.get('city') or addr.get('province') or "Unknown"
            country = addr.get('country') or "Cambodia"
            city = city.replace("Province", "").replace("City", "").strip()
            
            await state.update_data(city=city, country=country)
            await message.answer(TEXTS[lang]["loc_found"].format(city, country), reply_markup=types.ReplyKeyboardRemove(), parse_mode="Markdown")
            await state.set_state(RegisterState.waiting_for_bio)
        else:
            # បើចាប់ GPS បាន តែផែនទីរកអាសយដ្ឋានមិនឃើញ
            await message.answer(TEXTS[lang]["loc_err"])
    except:
        # បើប្រព័ន្ធផែនទីគាំង ឬត្រូវគេ Block (ករណីដែលមិត្តប្អូនជួប)
        # យើងឱ្យគាត់វាយឈ្មោះទីក្រុងវិញ ដើម្បីកុំឱ្យទាល់ផ្លូវ
        await message.answer(TEXTS[lang]["loc_err"])

@dp.message(RegisterState.waiting_for_location, F.text)
async def handle_location_typed(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'kh')
    try:
        # ព្យាយាមឆែកពាក្យដែលគាត់វាយ
        location = await asyncio.to_thread(geolocator.geocode, message.text, language='en', timeout=5)
        if location:
            city = location.address.split(',')[0].strip()
            country = location.address.split(',')[-1].strip()
            await state.update_data(city=city, country=country)
            await message.answer(TEXTS[lang]["loc_found"].format(city, country), reply_markup=types.ReplyKeyboardRemove(), parse_mode="Markdown")
            await state.set_state(RegisterState.waiting_for_bio)
        else:
            # បើរកមិនឃើញក្នុងផែនទី យើងយកពាក្យគាត់វាយផ្ទាល់តែម្តង (ដើម្បីកុំឱ្យ Error)
            city = message.text.strip()
            await state.update_data(city=city, country="Cambodia")
            await message.answer(TEXTS[lang]["loc_found"].format(city, "Cambodia"), reply_markup=types.ReplyKeyboardRemove())
            await state.set_state(RegisterState.waiting_for_bio)
    except:
        # បើគាំងប្រព័ន្ធផែនទី យកពាក្យគាត់វាយធ្វើជាទីតាំងតែម្តង
        city = message.text.strip()
        await state.update_data(city=city, country="Cambodia")
        await message.answer(TEXTS[lang]["loc_found"].format(city, "Cambodia"), reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(RegisterState.waiting_for_bio)

@dp.message(F.text.in_([TEXTS["kh"]["btn_profile"], TEXTS["en"]["btn_profile"]]))
async def show_profile(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    res = await asyncio.to_thread(requests.get, f"{BASE_URL}/profile/{message.from_user.id}")
    if res.status_code == 200:
        d = res.json()
        cap = TEXTS[lang]["profile_cap"].format(d['full_name'], d['age'], d['city'], d['country'], d.get('bio', ''))
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]["btn_invite"], callback_data="invite_friends")],
            [InlineKeyboardButton(text=TEXTS[lang]["btn_edit"], callback_data="edit_profile"),
             InlineKeyboardButton(text=TEXTS[lang]["btn_delete"], callback_data="delete_profile")]
        ])
        await message.answer_photo(photo=d['photo_url'], caption=cap, reply_markup=kb, parse_mode="Markdown")
    else: 
        await message.answer(TEXTS[lang]["no_profile"])

@dp.callback_query(F.data == "invite_friends")
async def handle_invite(callback: types.CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    res = await asyncio.to_thread(requests.get, f"{BASE_URL}/profile/{callback.from_user.id}")
    ref_count = res.json().get('referral_count', 0) if res.status_code == 200 else 0
    
    text = TEXTS[lang]["invite_text"].format(ref_count, BOT_USERNAME, callback.from_user.id)
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "edit_profile")
async def handle_edit(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    await callback.message.delete()
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🇰🇭 ខ្មែរ", callback_data='lang_kh'), InlineKeyboardButton(text="🇬🇧 English", callback_data='lang_en')]])
    await callback.message.answer(TEXTS[lang]["edit_start"], reply_markup=kb)
    await state.set_state(RegisterState.waiting_for_lang)

@dp.callback_query(F.data == "delete_profile")
async def handle_delete(callback: types.CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    res = await asyncio.to_thread(requests.delete, f"{BASE_URL}/profile/{callback.from_user.id}")
    if res.status_code == 200:
        await callback.answer(TEXTS[lang]["del_success"], show_alert=True)
        await callback.message.delete()
        await callback.message.answer(TEXTS[lang]["del_success"], reply_markup=types.ReplyKeyboardRemove())
    else:
        await callback.answer(TEXTS[lang]["del_fail"], show_alert=True)

async def show_next_match(chat_id, user_id):
    lang = get_user_lang(user_id)
    res = await asyncio.to_thread(requests.get, f"{BASE_URL}/match/{user_id}")
    
    if res.status_code == 200:
        d = res.json()
        if d.get('status') == 'success':
            m = d['match']
            cap = TEXTS[lang]["match_title"].format(m['full_name'], m['age'], m['city'], m['country'], m.get('bio', ''))
            kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=TEXTS[lang]["btn_like"], callback_data=f"like_{m['telegram_id']}"), 
                InlineKeyboardButton(text=TEXTS[lang]["btn_skip"], callback_data=f"skip_{m['telegram_id']}")
            ]])
            await bot.send_photo(chat_id=chat_id, photo=m['photo_url'], caption=cap, reply_markup=kb)
        else:
            await bot.send_message(chat_id=chat_id, text=TEXTS[lang]["no_match"])
    else:
        await bot.send_message(chat_id=chat_id, text=TEXTS[lang]["req_acc"])

@dp.message(F.text.in_([TEXTS["kh"]["btn_match"], TEXTS["en"]["btn_match"]]))
async def cmd_match(message: types.Message):
    await show_next_match(message.chat.id, message.from_user.id)

@dp.callback_query(F.data.startswith("like_") | F.data.startswith("skip_"))
async def handle_interaction(callback: types.CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    action, to_id = callback.data.split("_")
    payload = {"from_id": callback.from_user.id, "to_id": int(to_id), "action": action}
    
    res = await asyncio.to_thread(requests.post, f"{BASE_URL}/interact", json=payload)
    res_data = res.json()
    
    if action == "like":
        await callback.answer(TEXTS[lang]["like_sent"])
        if res_data.get("is_match"):
            kb_for_a = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=TEXTS[lang]["chat_him"], url=f"tg://user?id={to_id}")]])
            await callback.message.answer(TEXTS[lang]["its_match"], reply_markup=kb_for_a)
            
            lang_b = get_user_lang(to_id)
            kb_for_b = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=TEXTS[lang_b]["chat_back"], url=f"tg://user?id={callback.from_user.id}")]])
            try:
                await bot.send_message(chat_id=int(to_id), text=TEXTS[lang_b]["match_notif"], reply_markup=kb_for_b)
            except: pass
        else:
            try:
                lang_b = get_user_lang(to_id)
                notify_text = TEXTS[lang_b]["got_liked"]
                await bot.send_message(chat_id=int(to_id), text=notify_text, parse_mode="HTML")
            except:
                pass
    else:
        await callback.answer(TEXTS[lang]["skip_sent"])
        
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass

    await show_next_match(callback.message.chat.id, callback.from_user.id)

async def main():
    print("--- 🚀 KOU Bot Is Running (V4.1 LeoMatch Scroll Effect & Notification) ---")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())