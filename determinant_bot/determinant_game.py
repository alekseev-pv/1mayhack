import emoji
import numpy




class DeterminantGame():
    def __init__(self):
        self.board=[[0,0,0],[0,0,0],[0,0,0]]
        self.keyboard_arrows=[
            [
                emoji.emojize(':up-left_arrow:'),
                emoji.emojize(':up_arrow:'),
                emoji.emojize(':up-right_arrow:'), 
            ],
            [
                emoji.emojize(':left_arrow:'),
                emoji.emojize(':record_button:'),
                emoji.emojize(':right_arrow:'), 
            ],
            [
                emoji.emojize(':down-left_arrow:'),
                emoji.emojize(':down_arrow:'),
                emoji.emojize(':down-right_arrow:'), 
            ],
            ['/newgame']

        ]

        self.keyboard_numbers=[
            [
                emoji.emojize(':keycap_1:'),
                emoji.emojize(':keycap_2:'),
                emoji.emojize(':keycap_3:'), 
            ],
            [
                emoji.emojize(':keycap_4:'),
                emoji.emojize(':keycap_5:'),
                emoji.emojize(':keycap_6:'), 
            ],
            [
                emoji.emojize(':keycap_7:'),
                emoji.emojize(':keycap_8:'),
                emoji.emojize(':keycap_9:'), 
            ],
            ['/newgame']
        ]


    RULES_INFO = ('Два игрока по очереди заполняют матрицу 3x3 числами от 1 до 9\n'
    'Одно число можно использовать только один раз.\n'
    '\n'
    'Когда все поля матрицы заполнены подсчитывается ее определитель.\n'
    'Выигрывает первый игрок, если определитель матрицы положительный.\n'
    'Выигрывает второй игрок, если определитель матрицы отрицательный.\n'
    'Выигрыш равен модулю полученного определителя.')

    ABOUT_GAME=('"Мне рассказывали, что одно время среди первокурсников мехмата '
    'была популярна игра в “определитель” на деньги. Двое игроков чертят на '
    'бумаге определитель 3 x 3 с незаполненными ячейками. Затем по очереди '
    'вставляют в пустые ячейки цифры от 1 до 9. Когда все клетки заполнены, '
    'определитель считают – ответ с учетом знака и есть выигрыш (или проигрыш) '
    'первого игрока, выраженный в рублях. То есть, если, например, получилось '
    'число -23, то первый игрок платит второму 23 рубля, а если, скажем, 34, то '
    'наоборот, второй платит первому 34 рубля."\n'
    '<Математики тоже шутят> С. Федин')

    

    #NUMBERS = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣']
    NUMBERS={
        emoji.emojize(':keycap_1:'):1,
        emoji.emojize(':keycap_2:'):2,
        emoji.emojize(':keycap_3:'):3,
        emoji.emojize(':keycap_4:'):4,
        emoji.emojize(':keycap_5:'):5,
        emoji.emojize(':keycap_6:'):6,
        emoji.emojize(':keycap_7:'):7,
        emoji.emojize(':keycap_8:'):8,
        emoji.emojize(':keycap_9:'):9,
    }

    #ARROWS = ['⏺','➡','⬅','⬆','⬇','↗','↘','↙','↖']
    ARROWS = {
        emoji.emojize(':up-left_arrow:'):[0,0],
        emoji.emojize(':up_arrow:'):[0,1],
        emoji.emojize(':up-right_arrow:'):[0,2], 
        emoji.emojize(':left_arrow:'):[1,0],
        emoji.emojize(':record_button:'):[1,1],
        emoji.emojize(':right_arrow:'):[1,2], 
        emoji.emojize(':down-left_arrow:'):[2,0],
        emoji.emojize(':down_arrow:'):[2,1],
        emoji.emojize(':down-right_arrow:'):[2,2]
    }

    KEYBOARD_MAINMENU=[['Начать игру'],['Правила'],['О игре']]


    def determinant(self):
        return numpy.linalg.det(self.board)

    def reset(self):
        self.board=[[0,0,0],[0,0,0],[0,0,0]]

    def fill_cell(self):
        ...
    
    def gaming(self, reply):
        result={}
        result['keyboard'] = self.KEYBOARD_MAINMENU
        result['text'] = 'ошибка'

        if reply in self.ARROWS.keys():
            result['keyboard'] = self.keyboard_numbers
            result['text'] = 'Выбери число'
            self.cell = self.ARROWS.get(reply)

        if reply in self.NUMBERS.keys():
            result['keyboard'] = self.keyboard_arrows 
            self.board[self.cell[0]][self.cell[1]] = self.NUMBERS.get(reply)
            self.board[self.cell[0]][self.cell[1]] = self.NUMBERS.get(reply)
            
            result['text'] = (
                str(self.board[0])+'\n'
                +str(self.board[1])+'\n'
                +str(self.board[2])+'\n'
                +'Детерминант равен '+str(int(self.determinant()))+'\n'
                +'Выбери ячейку для заполнения \n'
            )

        return result