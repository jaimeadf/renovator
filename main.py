from requests import Session
from argparse import ArgumentParser
from bs4 import BeautifulSoup

PORTAL_URL = 'https://portal.ufsm.br'

def login(session: Session, username: str, password: str) -> None:
    response = session.post(
        f'{PORTAL_URL}/estudantil/j_security_check',
        data={
            'j_username': username,
            'j_password': password,
            'enter': ''
        },
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )

    soup = BeautifulSoup(response.text, 'html.parser')
    error = soup.find('div', {'class': 'error'})

    if error:
        raise Exception(error.text.strip())

def scrape_borrowings(session: Session) -> list[dict]:
    response = session.get(f'{PORTAL_URL}/biblioteca/leitor/situacao.html')
    
    soup = BeautifulSoup(response.text, 'html.parser')

    borrowing_table = soup.find(id='emprestimos')
    borrowing_body = borrowing_table.find('tbody')
    borrowing_rows = borrowing_body.find_all('tr')

    borrowings = []

    for row in borrowing_rows:
        cells = row.find_all('td')

        borrowings.append({
            'id': cells[0].find('button').attrs['data-id'],
            'code': cells[1].text.strip(),
            'title': cells[2].text.strip(),
            'library': cells[3].text.strip(),
            'renewals': int(cells[6].text)
        })

    return borrowings

def renew_borrowing(session: Session, id: str) -> None:
    response = session.get(
        f'{PORTAL_URL}/biblioteca/leitor/renovaEmprestimo.html',
        params={'idEmprestimo': id}
    )

    soup = BeautifulSoup(response.text, 'html.parser')
    error = soup.find('p', {'class': 'error'})

    if error:
        raise Exception(error.text.strip())

parser = ArgumentParser(
    prog='Renovator',
    description='Renova livros da UFSM automaticamente pelo portal estudantil'
)

parser.add_argument('-u --username', dest='username', help='Sua matrícula para o portal')
parser.add_argument('-p --password', dest='password', help='Sua senha para o portal')

args = parser.parse_args()
session = Session()

try:
    print('Logging in...')
    login(session, args.username, args.password)
except Exception as exception:
    print(f'Failed to log in: {str(exception)}')
else:
    print('Scraping borrowings...')
    borrowings = scrape_borrowings(session)

    print(f'Found {len(borrowings)} borrowings.')

    for borrowing in borrowings:
        print(f"Renewing {borrowing['id']} {borrowing['title']} - {borrowing['library']}...")

        try:
            renew_borrowing(session, borrowing['id'])
            print(f"Successfully renewed {borrowing['id']} {borrowing['title']} - {borrowing['library']}.")
        except Exception as exception:
            print(f"Unable to renew {borrowing['id']} {borrowing['title']} - {borrowing['library']}: {str(exception)}")

