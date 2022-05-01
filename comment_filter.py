KEYWORDS = [
    'найти',
    'как ',
    'вопрос',
    '...',
    'что такое',
    'что означает',
    'купить',
    'поискать',
    'какая',
    'какой',
    'какое',
    'что',
    'помогите',
    'поиск',
    'оноайн',
    'онлайн'
]

def filter_comments(comments_list: list) -> list:
    """Отбирает только комментарии, содержащие ключивые слова"""
    res = []
    for comment in comments_list:
        if any(keyword in comment for keyword in KEYWORDS) and len(comment) < 500:
            res.append(comment)

    return res