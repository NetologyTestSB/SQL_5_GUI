from dboperations import Dbops
from gui import Gui, Connection_form

def generate_new_sales():
    ''' формирование нового списка продаж'''
    db.create_new_sales_list()
    app.fill_base_tables_info_labels(db)


if __name__ == '__main__':
    # сначала форма для ввода параметров подключения к БД
    conform = Connection_form()
    conform.set_connection_form()
    conform.root.mainloop()

    # главня форма с таблицей данных из БД
    app = Gui()
    app.set_main_form()
    # DSN = 'postgresql+psycopg2://postgres:MyBasePass@localhost:5432/bookshop'
    DSN = conform.dsn
    db = Dbops(DSN, total=app.lbl_total, table=app.table1, inp_name=app.inp_pub)
    # если из формы параметров подключения вышли по cancell - программа завершается
    if not conform.cancell and db.open_db_session():
        db.initialze_tables()
        app.fill_base_tables_info_labels(db)
        db.show_all_sales()

        # обработчики события нажатия на кнопку
        app.btn_find.configure(command=db.select_all_sales_of_publisher)
        app.btn_refresh.configure(command=db.show_all_sales)
        app.btn_init.configure(command=generate_new_sales)

        app.root.mainloop()

        db.close_db_session()