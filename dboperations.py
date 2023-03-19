import tkinter
import psycopg2
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import create_tables, Shop, Publisher, Book, Stock, Sale
from random import randrange, randint
from datetime import *
from tkinter import *

class Dbops:
    ''' все операции с БД'''
    def __init__(self, DSN, total=None, table=None, inp_name=None):
        self.dsn = DSN
        self.lbl_total = total
        self.table = table
        self.inp_name = inp_name

    def open_db_session(self) -> bool:
        try:
            self.engine = sqlalchemy.create_engine(self.dsn)
            self.engine.connect()
        except:
            print('Ошибка подключения к базе данных!')
            tkinter.messagebox.showerror('Подключение', 'Ошибка подключения к базе данных!')
            return False
        create_tables(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.s = Session()
        return True

    def close_db_session(self):
        self.s.close()

    def new_sales_list(self) -> list:
        sa_l = []
        salse_count = randint(100, 300)
        for i in range(1, salse_count):
            sa = Sale(price=randint(200, 1000),
                      date_sale = datetime.now() - timedelta(days=randint(0, 365)),
                      id_stock=randint(1, self.stock_len), count=randint(1, 30))
            sa_l.append(sa)
        return sa_l

    def initialze_tables(self):
        ''' инициализация всех таблиц БД'''
        sh_title = ['Дом книги №', 'Книжный магазин №', 'Книжный мир №', 'Магнит №']
        shop_list = [f'{sh_title[i % 4]}{i + 1}' for i in range(randint(5, 20))]
        sh_l = []
        for el in shop_list:
            sh = Shop(name=el)
            sh_l.append(sh)

        pub_list = ['Пушкин А.С.', 'Толстой Л.Н.', 'Достоевский Ф.М.', 'Есенин С.А.', 'Лермонтов М.Ю.', 'Маяковский В.В.',
                    'Гоголь Н.В.', 'Булгаков М.А.', 'Чехов А.П.']
        pb_l = []
        for el in pub_list:
            pb = Publisher(name=el)
            pb_l.append(pb)

        book_list =['Евгений Онегин', 'Руслан и Людмила', 'Повести Белкина',
                    'Война и мир', 'Анна Каренина', 'Севастопольские рассказы',
                    'Преступление и наказание', 'Игрок', 'Бесы',
                    'Черный человек', 'Анна Снегина', 'Пугачев',
                    'Бородино', 'Демон', 'Герой нашего времени',
                    'Баня', 'Облако в штанах', 'Клоп',
                    'Мертвые души', 'Вечера на хуторе близ Деканьки', 'Тарас Бульба',
                    'Мастер и Маргарита', 'Белая гвардия', 'Собачье сердце',
                    'Вишневый сад', 'Три сестры', 'Дядя Ваня'
                    ]
        b_l = []
        for i, el in enumerate(book_list):
            b = Book(title=el, id_publisher=i // 3 + 1)
            b_l.append(b)

        st_l = []
        for i in range(len(book_list)):
            for j in range(len(shop_list)):
                st = Stock(id_book=i + 1, id_shop=j + 1, count=randint(30, 100))
                st_l.append(st)
        self.stock_len = len(st_l)
        sa_l = self.new_sales_list()

        self.s.add_all(sh_l + pb_l + b_l + st_l + sa_l)
        self.s.commit()

    def tables_size_info(self) -> tuple:
        ''' кол-ва записей в каждой таблице БД'''
        tpl = (self.s.query(Shop).count(), self.s.query(Publisher).count(),
               self.s.query(Book).count(), self.s.query(Stock).count(),
               self.s.query(Sale).count())
        return tpl

    def find_publisher(self) -> int:
        '''поиск id издателя (автора) по введенному имени'''
        # сначала поиск по имени
        pname = self.inp_name.get()
        q = self.s.query(Publisher).filter(Publisher.name.ilike("%" + pname + "%"))
        if q.count() != 1:
            # теперь поиск по id
            pid = pname
            try:
                pid = int(pid)
            except:
                return -1
            q = self.s.query(Publisher).filter(Publisher.id == pid)
            if q.count() != 1:
                return -1
        # заполняем поле ввода найденным издателем
        self.inp_name.delete(0, END)
        self.inp_name.insert(0, q.all()[0].name)
        return q.all()[0].id

    def formated_num(self, num) -> str:
        if num > 999999:
            mil = num // 1000000
            return f'{mil} {((num - mil * 1000000) // 1000):03} {(num % 1000):03}'
        elif num > 999:
            return f'{num // 1000} {(num % 1000):03}'
        else:
            return str(num)

    def fill_table(self, sales, with_name=False):
        ''' построчная запись в таблицу строк из запроса sales'''
        total = 0
        self.table.delete(*self.table.get_children())
        for res in sales.all():
            money = res.count * res.price
            total += money
            if with_name:
                title = res.stock.book.publisher.name + ' ' + res.stock.book.title
            else:
                title = res.stock.book.title
            self.table.insert("", END, values=[title, res.stock.shop.name,
                                               self.formated_num(money), res.date_sale])
        self.lbl_total.configure(text=f'сумма продаж:   {self.formated_num(total)}')

    def select_all_sales_of_publisher(self, pub=None, pub_id=None):
        ''' продажи выбранного издателя'''
        total = 0
        self.table.delete(*self.table.get_children())
        pub_id = self.find_publisher()
        if pub_id == -1:
            return
        # т.к. в фильтр запроса с несколькими join надо подставлять не значение, напр., Book.publisher.id == 1, а объект (почему???),
        # ругается - Neither 'InstrumentedAttribute' OBJECT nor 'Comparator' OBJECT associated with Book.publisher has an attribute 'id'
        # создадим такой объект publ
        publ = self.s.query(Publisher).filter(Publisher.id == pub_id).all()[0]
        sales = self.s.query(Sale).join(Stock).join(Shop).join(Book).filter(Book.publisher == publ).order_by(Sale.date_sale)
        self.fill_table(sales)

    def show_all_sales(self):
        ''' все продажи всех издателей'''
        self.inp_name.delete(0, END)
        self.inp_name.insert(0, 'все издатели (авторы)')
        sales = self.s.query(Sale).join(Stock).join(Shop).join(Book).join(Publisher).order_by(Sale.date_sale)
        self.fill_table(sales, with_name=True)

    def create_new_sales_list(self):
        ''' новый список продаж записываем в таблицу Sale'''
        self.s.query(Sale).delete()
        self.s.add_all(self.new_sales_list())
        self.s.commit()
        self.show_all_sales()




