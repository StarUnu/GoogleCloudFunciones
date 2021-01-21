def get_google_books_data(author, lang):
    """ Obtiene datos de la API de Google Books """
    from requests import get
    
    books = []
    url = 'https://www.googleapis.com/books/v1/volumes'
    book_fields = (
        'items('
        'id'
        ',accessInfo(epub/isAvailable)'
        ',volumeInfo(title,subtitle,language,pageCount)'
        ')'
    )
    req_item_idx = 0  # La respuesta está paginada
    req_item_cnt = 40  # Por default=10, maximo=40
    while True:
        params = {
            'q': 'inauthor:%s' % author,
            'startIndex': req_item_idx,
            'maxResults': req_item_cnt,
            'langRestrict': lang,
            'download': 'epub',
            'printType': 'books',
            'showPreorders': 'true',
            'fields': book_fields,
        }
        response = get(url, params=params)
        response.raise_for_status()
        book_items = response.json().get('items', None)
        if book_items is None:
            break
        books += book_items
        if len(book_items) != req_item_cnt:
            break  # Last response page
        req_item_idx += req_item_cnt
    return books
def print_author_books(author, lang):
    """ Devuelve datos del libro en una tabla de texto sin formato """
    def sort_by_page_count(book):
        return book['volumeInfo'].get('pageCount', 0)
    books = get_google_books_data(author, lang)
    books.sort(key=sort_by_page_count, reverse=True)

    line_fmt = '{:>4} | {:>5} | {:.65}\n'
    lines = [
        '{sep}{h1}{sep}{h2}'.format(
            h1='{:^80}\n'.format('"%s" ebooks (lang=%s)' % (author, lang)),
            h2=line_fmt.format('#', 'Pages', 'Title'),
            sep='{:=<80}\n'.format('')
        )]
    for idx, book in enumerate(books, 1):
        accessInfo = book['accessInfo']
        if not accessInfo['epub']['isAvailable']:
            continue
        volumeInfo = book['volumeInfo']
        title = volumeInfo['title']
        subtitle = volumeInfo.get('subtitle')
        if subtitle is not None:
            title += ' / ' + subtitle
        count = volumeInfo.get('pageCount')
        pages = '{:,}'.format(count) if count is not None else ''
        lines.append(line_fmt.format(idx, pages, title))
    return ''.join(lines)

def get_ebooks_by_author(request2):
    author = request2.args.get('author', 'JRR Tolkien')
    lang = request2.args.get('lang', 'en')
    author_books =print_author_books(author, lang)
    author_books2=str(author_books)
    a="ere"
    headers = {'Content-Type': 'text/plain; charset=utf-8'}
    return author_books, headers
