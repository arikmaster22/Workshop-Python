from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy import select

meta = MetaData()

authors = Table('Authors', meta,
                Column('id', Integer, primary_key=True),
                Column('name', String, nullable=False, unique=True),
                )

books = Table('Books', meta,
              Column('id', Integer, primary_key=True),
              Column('title', String, nullable=False, unique=True),
              Column('author_id', String, ForeignKey('Authors.id')),
              Column('genre', String, nullable=False),
              Column('price', Integer)
              )

engine = create_engine('sqlite:///database.db', echo=True)

conn = engine.connect()

meta.create_all(engine)


def add_new_author(name: str):
    insert_author_query = authors.insert().values(name=name) # сам SQL-запрос

    conn.execute(insert_author_query) # выполнение запроса

    conn.commit() # сохранение изменений


def add_new_book(title: str, author_id: int, genre: str, price: int):
    insert_book_query = books.insert().values(title=title, author_id=author_id, genre=genre,
                                              price=price
                                              )

    conn.execute(insert_book_query)

    conn.commit()


def select_query():
    books_select_query = books.select().where(books.c.price >= 4000)

    print()
    print(f'SQL-запрос:\n{books_select_query}') # посмотрим на сам запрос
    print()

    result = conn.execute(books_select_query)

    print()
    print(f'Результат запроса:\n {result}') # посмотрим на результат запроса
    print()

    for row in result:
        print(row)

    result = conn.execute(books_select_query).all() # просто select
    
    print()
    print(f'Результат запроса:\n {result}')
    print()

    select_query = select(books, authors).where(books.c.author_id == authors.c.id) # select с фильтрацией

    result = conn.execute(select_query).all()

    print()
    print(f'Результат запроса:\n {result}')
    print()


if __name__ == '__main__':
    add_new_author('Mark Lutz')

    add_new_book(title='Learning Python Tom 1', author_id='1', genre='Education', price=3000)

    add_new_book(title='Learning Python Tom 2', author_id='1', genre='Education', price=4000)
    
    try:
    add_new_book(title='Learning Python Tom 1', author_id='1', genre='Education', price=3000)

    except Exception as ex:
        print()
        print(f'Exception:\n{ex}!!!')
        print()

    select_query()
