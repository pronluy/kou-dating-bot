import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_KB5WCm3wvGHU@ep-wild-sea-aoi12454.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

def build_dating_ecosystem_db():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("--- 🚀 ចាប់ផ្ដើមសាងសង់ Database សម្រាប់គម្រោងទាំងមូល... ---")

        # ១. បង្កើត ENUM Types (ដើម្បីកម្រិតទិន្នន័យឱ្យមានស្តង់ដារ)
        # ភាសាទាំង ៦ តាមប្លង់មេ
        cur.execute("CREATE TYPE lang_type AS ENUM ('kh', 'en', 'cn', 'es', 'fr', 'ar');")
        # ភេទ
        cur.execute("CREATE TYPE gender_type AS ENUM ('male', 'female', 'other');")
        # ប្រភេទ Profile (Avatar ឬ រូបពិត)
        cur.execute("CREATE TYPE profile_mode AS ENUM ('avatar', 'real_photo');")
        # ស្ថានភាព Match
        cur.execute("CREATE TYPE match_status AS ENUM ('pending', 'matched', 'rejected');")

        # ២. តារាង Users ( handle ទាំង Bot និង App)
        cur.execute('''
            CREATE TABLE users (
                user_id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE, -- សម្រាប់ Onboarding តាម Bot
                full_name VARCHAR(100) NOT NULL,
                age INTEGER CHECK (age >= 18),
                gender gender_type NOT NULL,
                looking_for gender_type NOT NULL,
                city VARCHAR(100),
                language lang_type DEFAULT 'kh', -- ខ្មែរជា Default
                profile_type profile_mode DEFAULT 'avatar', -- Onboarding ជាមួយ Avatar សិន
                photo_url TEXT, -- Link ទៅកាន់រូបភាព
                is_verified BOOLEAN DEFAULT FALSE, -- សម្រាប់ Verify រូបពិត
                bio TEXT, -- ព័ត៌មានរៀបរាប់ពីខ្លួនឯង
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # ៣. តារាង Interactions (សម្រាប់ទុកការ Swipe Like/Pass)
        cur.execute('''
            CREATE TABLE interactions (
                id SERIAL PRIMARY KEY,
                actor_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                target_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                action VARCHAR(10) NOT NULL, -- 'like' ឬ 'pass'
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(actor_id, target_id)
            );
        ''')

        # ៤. តារាង Matches (ស្នូលនៃស្មារតី Matching)
        cur.execute('''
            CREATE TABLE matches (
                match_id SERIAL PRIMARY KEY,
                user_one_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                user_two_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                status match_status DEFAULT 'matched',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_one_id, user_two_id)
            );
        ''')

        # ៥. តារាង Messages (សម្រាប់ Chat ពេល Match ហើយ)
        cur.execute('''
            CREATE TABLE messages (
                message_id SERIAL PRIMARY KEY,
                match_id INTEGER REFERENCES matches(match_id) ON DELETE CASCADE,
                sender_id INTEGER REFERENCES users(user_id),
                content TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # ៦. បង្កើត INDEX សម្រាប់ឱ្យ App ដើរលឿន (Optimization)
        cur.execute("CREATE INDEX idx_users_location_gender ON users(city, gender);")
        cur.execute("CREATE INDEX idx_users_tg_id ON users(telegram_id);")

        conn.commit()
        print("--- ✅ Database ថ្មីត្រូវបានបង្កើតឡើងដោយជោគជ័យ និងមានសុវត្ថិភាពខ្ពស់! ---")

    except Exception as e:
        print(f"❌ កំហុសបច្ចេកទេស៖ {e}")
        if conn: conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    build_dating_ecosystem_db()