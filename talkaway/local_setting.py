DEBUG_DATABASE = False

MYSQL_DATABASE = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "talkaway",
        "USER": "talkaway_admin",
        "PASSWORD": "talkaway@2024",
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {            
            "use_unicode": True,
            "charset": "utf8mb4",
        },
    }
}

OPENAI_API_KEY = ""