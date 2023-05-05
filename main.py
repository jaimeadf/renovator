from datetime import datetime, date
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
            'withdrawnAt': cells[4].text.strip(),
            'returnAt': cells[5].text.strip(),
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

def should_renew(borrowing: dict) -> None:
    today = date.today()

    return borrowing['returnAt'] == today.strftime('%d/%m/%Y')

parser = ArgumentParser(
    prog='Renovator',
    description='Renova livros da UFSM automaticamente pelo portal estudantil.'
)

parser.add_argument('-u --username', dest='username', help='Sua matrícula para o portal.')
parser.add_argument('-p --password', dest='password', help='Sua senha para o portal.')

args = parser.parse_args()
session = Session()

try:
    print('Logando...')
    login(session, args.username, args.password)
except Exception as exception:
    print(f'Ocorreu um erro ao logar: {str(exception)}')
else:
    print('Extraindo empréstimos...')
    borrowings = scrape_borrowings(session)

    print(f'{len(borrowings)} empréstimos foram encontrados.')

    for borrowing in borrowings:
        if should_renew(borrowing):
            print(f"Renovando {borrowing['id']} {borrowing['title']} - {borrowing['library']}...")

            try:
                renew_borrowing(session, borrowing['id'])
                print(f"{borrowing['id']} {borrowing['title']} - {borrowing['library']} foi renovado com sucesso.")
            except Exception as exception:
                print(f"{borrowing['id']} {borrowing['title']} - {borrowing['library']} não pode ser renovado: {str(exception)}")
        else:
            print(f"Pulando {borrowing['id']} {borrowing['title']} - {borrowing['library']}, pois a renovação não gera benefício.")
