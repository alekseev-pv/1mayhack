import sqlite3 as sq


def text(t, z):
    result = []
    for i in t:
        for j in i.split(z):
            result.append(j)
    return result


def get_text_in_words(x):
    for k in list(x):
        return k.split()


file = open('book.txt', encoding='utf-8')
base = [file.read()]
for sep in ['.', '?', '!', '(', ')']:
    base = text(base, sep)

bas = []
for i in base[1:]:
    i = i.strip()
    if '/' not in i:
        if '\n' not in i:
            if len(i.split(' ')) > 3:
                if not i.isspace():
                    bas.append([i])

words = []
for i in bas:
    words.append(''.join(i))
words = ''.join(words)
wo = words.split()
words = []
for i in wo:
    words.append([i])

with sq.connect("book.db") as con:
    cur = con.cursor()

    cur.execute("DROP TABLE IF EXISTS book")
    cur.execute("DROP TABLE IF EXISTS word")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS book (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        line TEXT)
        """)

    cur.execute("""CREATE TABLE IF NOT EXISTS words_book (
        words_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        word TEXT,
        FOREIGN KEY (book_id) REFERENCES customers(book_id))
        """)
    con.commit()

    cur.executemany("INSERT INTO book (line) VALUES(?)", bas)
    con.commit()

    for i in range(1, len(bas) + 1):
        for j in get_text_in_words(bas[i - 1]):
            cur.execute("INSERT INTO words_book (book_id, word) VALUES(?, ?)", (i, j))
    con.commit()

    #cur.execute("SELECT * FROM book")
    #for result_text in cur:
    #    print(result_text)

    # cur.execute("SELECT * FROM words_book")
    # for result_text in cur:
    #    print(result_text)
