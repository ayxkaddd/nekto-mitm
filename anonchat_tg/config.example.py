# https://my.telegram.org/auth?to=apps
accounts = [
    {"api_id": 1111111, "api_hash": 'yourapihash1', "session_name": 'sess1'},
    {"api_id": 2222222, "api_hash": 'yourapihash2', "session_name": 'sess2'},
]

configuration = {
    '@AnonRuBot':  {
        "end_conversation_msg": "Собеседник закончил с вами связь",
        "you_end_conversation_msg":  "Вы закончили связь с вашим собеседником",
        "ignore_messages": [
            "Собеседник найден",
            "Напишите /search чтобы искать собеседника",
            "Если хотите, оставьте мнение о вашем собеседнике. Это поможет находить вам подходящих собеседников",
            "У вас нет собеседника 🤔",
            "Вы закончили связь с вашим собеседником",
            "Собеседник закончил с вами связь",
            "Мы временно ограничили вам пользование чатом за нарушение правил Анонимного чата",
        ]
    },
    '@chatbot': {
        "end_conversation_msg": "Your partner has stopped the dialog 😞",
        "you_end_conversation_msg": "You stopped the dialog 🙄",
        "ignore_messages": [
            "Looking for a partner...",
            "If you wish, leave your feedback about your partner. It will help us find better partners for you in the future",
            "Your partner has stopped the dialog 😞",
            "Partner found 😺",
            "You stopped the dialog 🙄",
            "You have been banned due to",
        ]
    }
}
