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


def add_new_author():
    insert_author_query = authors.insert().values(name='Mark Lutz')
    conn.execute(insert_author_query)

    conn.commit()


def add_new_books():
    insert_book_query = books.insert().values(title='Learning Python Tom 1', author_id='1', genre='Education',
                                              price=3000
                                              )

    conn.execute(insert_book_query)

    try:
        insert_book_query = books.insert().values(title='Learning Python Tom 1', author_id='1', genre='Education',
                                                  price=3000
                                                  )

        conn.execute(insert_book_query)
    except Exception as ex:
        print()
        print(f'Exception: {ex}!!!')
        print()

    insert_book_query = books.insert().values(title='Learning Python Tom 2', author_id='1', genre='Education',
                                              price=4000
                                              )

    conn.execute(insert_book_query)

    conn.commit()


def select_query():
    books_select_query = books.select().where(books.c.price >= 4000)

    print()
    print(books_select_query)
    print()

    result = conn.execute(books_select_query)

    print(result)
    print()

    for row in result:
        print(row)

    result = conn.execute(books_select_query).all()
    print(result)

    select_query = select(books, authors).where(books.c.author_id == authors.c.id)

    result = conn.execute(select_query).all()

    print()
    print(result)
    print()


if __name__ == '__main__':
    add_new_author()

    add_new_books()

    select_query()
