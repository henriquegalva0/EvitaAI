# 1. IMPORTAÇÕES
import base64 #decodifica o email
import openai #chatgbt
import tqdm #barra de progresso
import time #para controlar o limite de token por minuto
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials #carrega as credencias de autenticação
from google_auth_oauthlib.flow import InstalledAppFlow #cria o flow (aba de inspeção do google)
from googleapiclient.discovery import build #cria a conexão com a api do google
from email.utils import parsedate_to_datetime #para colocar a data em formato adequado
import re

def extrair_email(texto):
    padrao = r'<([^<>]+)>'
    resultado = re.search(padrao, texto)
    if resultado:
        return resultado.group(1)
    return None

# Configurações iniciais
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']  # Permissão só de leitura
with open("apikeychatgpt.txt", "r", encoding="utf8") as arcapikey:
    apikey = arcapikey.read()
with open("promtgptemail.txt", "r", encoding="utf8") as arcpromtgpt: #
    promtchatgpt = arcpromtgpt.read()
openai.api_key = f'{apikey}'
# AUTENTICAÇÃO GOOGLE (sempre vai redirecionar para a aba de inspeção do google)

def tratar_data(data_bruta):
    formatos_possiveis = [
        '%d/%m/%Y',  # 20/05/2024
        '%d-%m-%Y',  # 20-05-2024
        '%d/%m/%y',  # 20/05/24
        '%d-%m-%y',  # 20-05-24
        '%Y-%m-%d',  # 2024-05-20 (formato ISO)
    ]

    for formato in formatos_possiveis:
        try:
            data = datetime.strptime(data_bruta.strip(), formato)
            return data.strftime('%d-%m-%y')  # Formato desejado
        except ValueError:
            continue

    # Se nenhum formato funcionar, retorna vazio
    return ''

def login_email(): 
    try:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES) #cria o flow, seguindo as limitações do scope (só leitura)
        creds = flow.run_local_server(port=8080) #cria o flow em server local, no computador

        # 4. CONECTANDO AO GMAIL
        servico = build('gmail', 'v1', credentials=creds) #cria a conexão com o email propriamente dito
        return servico
    except Exception as e:
        return None

# 5. Função para ler e listar todos os emails na variável emails (virão como dicionários)
def buscar_emails(servico):
    results = servico.users().messages().list(userId='me', maxResults=10).execute() #lista duzentos emails recebidos
    messages = results.get('messages', []) #pega as mensagens. Se não tiver nada, cria uma lista vazia
    emails = []

    # 6. Listando todos os emails
    for msg in tqdm.tqdm(messages, desc='Processando emails...', unit='email'): #cria um looping para percorrer a lista de emails
        msg_detail = servico.users().messages().get(userId='me', id=msg['id']).execute() #busca o conteúdo do email especificado pelo Id próprio
        headers = msg_detail['payload']['headers'] #Pega o cabeçalho do email (from, subject)
        assunto = remetente = data = '' #cria uma string vazia a ser completada em seguida
        for header in headers: #percorre cada cabeçalho
            if header['name'] == 'Subject': #quando achar um assunto, vai endereçar à string vazia
                assunto = header['value'] if header['value'] else "(sem assunto)"
            elif header['name'] == 'From': #quando achar um From, vai endereçar à string vazia
                remetente = header['value'] if header['value'] else "(Remetente desconhecido)" #O if é para evitar uma lista de None
            elif header['name'] == 'Date':
                data = header['value'] if header['value'] else "(sem data)"

        if not remetente or remetente == None:
            remetente = '(remetente desconhecido)'

        # Conteúdo do email (mais simplificado - corpo)
        partes = msg_detail['payload'].get('parts', [])
        corpo = ''
        if partes:
            corpo = partes[0].get('body', {}).get('data', '')
        else:
            corpo = msg_detail['payload'].get('body', {}).get('data', '')
        
        # Decodificando o corpo
        if corpo:
            corpo = base64.urlsafe_b64decode(corpo).decode('utf-8', errors='ignore')  # Decodifica o corpo do e-mail

        emails.append({
            'remetente': remetente,
            'assunto': assunto,
            'corpo': corpo,
            'data': data
        })
    return emails

# Função para categorizar emails por remetente
def remetentes(emails, autor_alvo):

    # Normaliza o nome do autor
    escolha = autor_alvo.strip().lower()

    # Cria a lista única de remetentes normalizados
    remetentes_unicos = list(set(
        extrair_email(e.get('remetente', '(sem remetente)').strip().lower())
        for e in emails if isinstance(e, dict) and e.get('remetente')
    ))

    print(remetentes_unicos)

    # Verifica se o autor está na lista
    if escolha not in remetentes_unicos:
        return {'Resultado': 'Nenhum e-mail encontrado sobre esse remetente'}

    # Filtra os e-mails do remetente escolhido
    emails_filtrados = [
        e for e in emails
        if isinstance(e, dict) and
        extrair_email(e.get('remetente', '').strip().lower()) == escolha
    ]

    print(emails_filtrados)

    return emails_filtrados

def data(emails, data_definida_naotratada):

    data_definida = tratar_data(data_definida_naotratada)

    print("Data tratada:", data_definida)

    if not data_definida or not data_definida.strip():
        return {'Resultado': 'Data inválida ou vazia'}

    try:
        # Interpreta a data do usuário como uma data base
        data_base = datetime.strptime(data_definida, '%d-%m-%y')

        # Define início e fim do dia
        data_inicio = data_base.replace(hour=0, minute=0, second=0, microsecond=0)
        data_final = data_base.replace(hour=23, minute=59, second=59, microsecond=999999)

        emails_filtrados = []
        for email in emails:
            try:
                data_email = parsedate_to_datetime(email.get('data', ''))
                if data_email is None:
                    continue
                # Converte para UTC e remove fuso para comparação
                data_email = data_email.astimezone(timezone.utc).replace(tzinfo=None)
                if data_inicio <= data_email <= data_final:
                    emails_filtrados.append(email)
            except Exception:
                continue

        if not emails_filtrados:
            return {'Resultado': 'Nenhum e-mail encontrado nessa data'}

        return emails_filtrados

    except ValueError:
        return {'Resultado': 'Formato de data inválido. Use DD-MM-AA'}
