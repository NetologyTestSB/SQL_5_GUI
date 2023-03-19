import tkinter.messagebox
from tkinter import *
from tkinter import ttk
import dboperations
import sqlalchemy
def center_position(form, width, height) -> str:
    '''создаем строку с параметрами для расположения формы по центру экрана'''
    screen_w = form.winfo_screenwidth()
    screen_h = form.winfo_screenheight()
    # отступы слева-справа и сверху-снизу одинаковы
    left = (screen_w - width) // 2
    top = (screen_h - height) // 2
    return f'{width}x{height}+{left}+{top}'

def input_entry(row=0, col=0, txt='name', parent=None, width=20, colspan=1) -> Entry:
    ''' поле для ввода данных'''
    lbl = Label(parent, text=txt)
    lbl.grid(row=row, column=col, padx=10, pady=10, sticky=E)
    entry = Entry(parent, width=width)
    entry.grid(row=row, column=col+1, padx=10, pady=10, sticky=W, columnspan=colspan)
    return entry

class Connection_form():
    ''' класс для формы параметров подключения к БД'''
    def __init__(self):
        self.engine = 'postgresql+psycopg2'
        self.server = 'localhost'
        self.port = '5432'
        self.user = 'postgres'
        self.password = 'MyBasePass'
        self.name ='bookshop'
        self.dsn = ''
        self.cancell = False

    #DSN = 'postgresql://postgres:MyBasePass@localhost:5432/bookshop'
    def set_connection_form(self):
        self.root = Tk()
        self.root.title('Подключение к базе данных')
        self.root.geometry(center_position(self.root, 680, 250))
        # поля ввода параметров
        frame_input = Frame(self.root, padx=5, pady=5)
        frame_input.pack(expand=True, fill=BOTH, side='top')
        self.inp_engine = input_entry(txt='engine', row=0, col=0, parent=frame_input, width=40)
        self.inp_server = input_entry(txt='server', row=0, col=2, parent=frame_input, width=40)
        self.inp_user = input_entry(txt='user', row=1, col=0, parent=frame_input, width=40)
        self.inp_pass = input_entry(txt='pass', row=1, col=2, parent=frame_input, width=40)
        self.inp_port = input_entry(txt='port', row=2, col=2, parent=frame_input, width=20)
        self.inp_name = input_entry(txt='name', row=2, col=0, parent=frame_input, width=40)
        self.inp_dsn = input_entry(txt='DSN', row=3, col=0, parent=frame_input, width=95, colspan=3)
        # кнопки
        frame_btn = Frame(self.root, padx=20, pady=5, height=15)
        frame_btn.pack(expand=True, fill=BOTH, side='top')
        btn_exit = Button(frame_btn, text='Отменить', height=1, width=15, command=self.quit_without_connection)
        btn_exit.pack(side='right')
        self.btn_refresh = Button(frame_btn, text='Проверка', height=1, width=12, command=self.check_connection)
        self.btn_refresh.pack(side='right', padx=5)
        self.btn_init = Button(frame_btn, text='Применить', height=1, width=12, command=self.root.destroy)
        self.btn_init.pack(side='right', padx=0)
        self.btn_init = Button(frame_btn, text='Сложить DSN', height=1, width=12, command=self.combine_dsn)
        self.btn_init.pack(side='right', padx=5)
        self.btn_init = Button(frame_btn, text='Очистить', height=1, width=12, command=self.clear_inp)
        self.btn_init.pack(side='right', padx=0)
        self.btn_default = Button(frame_btn, text='По умолчанию', height=1, width=12, command=self.set_default_params)
        self.btn_default.pack(side='right', padx=0)

    def clear_inp(self):
        ''' очистка полей параметров подключения к БД'''
        self.inp_engine.delete(0, END)
        self.inp_server.delete(0, END)
        self.inp_port.delete(0, END)
        self.inp_user.delete(0, END)
        self.inp_pass.delete(0, END)
        self.inp_name.delete(0, END)
        self.inp_dsn.delete(0, END)

    def set_default_params(self):
        ''' установка параметров подключения к БД по умолчанию'''
        self.clear_inp()
        self.engine = 'postgresql+psycopg2'
        self.server = 'localhost'
        self.port = '5432'
        self.user = 'postgres'
        self.password = 'MyBasePass'
        self.name ='bookshop'
        self.inp_engine.insert(0, self.engine)
        self.inp_server.insert(0, self.server)
        self.inp_port.insert(0, self.port)
        self.inp_user.insert(0, self.user)
        self.inp_pass.insert(0, self.password)
        self.inp_name.insert(0, self.name)

    def combine_dsn(self):
        ''' составление строки DSN из параметров подключения к БД'''
        # DSN = 'postgresql://postgres:MyBasePass@localhost:5432/bookshop'
        self.engine = self.inp_engine.get()
        self.user = self.inp_user.get()
        self.password = self.inp_pass.get()
        self.server = self.inp_server.get()
        self.port = self.inp_port.get()
        self.name = self.inp_name.get()
        #строка DSN
        self.dsn = self.engine + '://' + self.user + ':' + self.password + '@' +self.server + ':' + self.port + '/' + self.name
        self.inp_dsn.delete(0, END)
        self.inp_dsn.insert(0, self.dsn)

    def check_connection(self):
        ''' проверка соединения с БД'''
        try:
            engine = sqlalchemy.create_engine(self.dsn)
            engine.connect()
            tkinter.messagebox.showinfo('Проверка соединения с базой данных', 'Соединение успешно установлено')
        except:
            tkinter.messagebox.showerror('Проверка соединения с базой данных',
                                         'Не удалось установить соединение с базой данных')
            return False
        return True

    def quit_without_connection(self):
        ''' выход из программы без подключения к БД'''
        self.cancell = True
        self.root.quit()

class Gui():
    ''' класс для создания графического интерфейса'''
    def __init__(self):
        self.inp_pub = Entry
        self.lbl_total = None
        self.table1 = None

    def create_table(self, parent):
        ''' создание таблицы'''
        col_name = ('книга', 'магазин', 'сумма', 'дата')
        col_width =(170, 100, 20, 20)
        self.table1 = ttk.Treeview(parent, columns=col_name, show="headings", height=18)
        self.table1.pack(anchor=N, fill=BOTH, expand=1, side='top')
        for i, el in enumerate(col_name):
            self.table1.heading(i, text=el, anchor=W)
            self.table1.column(i, width=col_width[i])

    def fill_base_tables_info_labels(self, base):
        ''' заполнение информационных полей о кол-ве записей в таблицах БД'''
        info_tpl = base.tables_size_info()
        self.lbl_shop.configure(text=f'shops: {info_tpl[0]}')
        self.lbl_publisher.configure(text=f'publisher: {info_tpl[1]}')
        self.lbl_book.configure(text=f'book: {info_tpl[2]}')
        self.lbl_stock.configure(text=f'stock: {info_tpl[3]}')
        self.lbl_sale.configure(text=f'sale: {info_tpl[4]}')

    def set_main_form(self):
        ''' главная форма программы'''
        self.root = Tk()
        self.root.title('Таблица продаж книг выбранного издателя (автора)')
        self.root.geometry(center_position(self.root, 720, 510))
        # верхняя часть - ввод данных, кнопка поиска и лейбл суммы продаж
        frame_input = Frame(self.root, padx=5, pady=5)
        frame_input.pack(expand=True, fill=BOTH, side='top')
        self.inp_pub = input_entry(txt='издатель (имя или номер id)', row=0, col=0, parent=frame_input, width=30)
        self.lbl_total = Label(frame_input, text='сумма продаж')
        self.lbl_total.grid(row=0, column=3, padx=60, pady=10, sticky=E)
        self.btn_find = Button(frame_input, text='Поиск', height=1, width=10)
        self.btn_find.grid(row=0, column=2, padx=0)
        # таблица
        frame_table = Frame(self.root, padx=5, pady=0, height=210)
        frame_table.pack(expand=True, fill=BOTH, side='top')
        self.create_table(frame_table)
        # кнопки
        frame_btn = Frame(self.root, padx=5, pady=5, height=15)
        frame_btn.pack(expand=True, fill=BOTH, side='top')
        btn_exit = Button(frame_btn, text='Выход', height=1, width=15, command=self.root.destroy)
        btn_exit.pack(side='right')
        self.btn_refresh = Button(frame_btn, text='Все продажи', height=1, width=15)
        self.btn_refresh.pack(side='right', padx=5)
        self.btn_init = Button(frame_btn, text='Инициализация', height=1, width=15)
        self.btn_init.pack(side='right', padx=0)
        # информационные лейблы для вывода кол-ва записей в таблицах БД
        frame_info = Frame(self.root, padx=0, pady=0)
        frame_info.pack(expand=True, fill=BOTH, side='top')
        lbl_title = Label(frame_info, text='количество записей в таблицах базы данных')
        lbl_title.grid(row=0, column=0, padx=5, pady=0)
        self.lbl_shop = Label(frame_info, text='shop')
        self.lbl_shop.grid(row=0, column=1, padx=5, pady=0)
        self.lbl_book = Label(frame_info, text='book')
        self.lbl_book.grid(row=0, column=2, padx=5, pady=0)
        self.lbl_publisher = Label(frame_info, text='publisher')
        self.lbl_publisher.grid(row=0, column=3, padx=5, pady=0)
        self.lbl_stock = Label(frame_info, text='stock')
        self.lbl_stock.grid(row=0, column=4, padx=5, pady=0)
        self.lbl_sale = Label(frame_info, text='sale')
        self.lbl_sale.grid(row=0, column=5, padx=5, pady=0)
