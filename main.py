from flask import Flask, render_template, request, redirect, url_for,session
from apigptsite import apichatgptsite
from apigptemail import apichatgptemail
from email_analysis_py import login_email,buscar_emails,remetentes,data

with open("appkey.txt", "r", encoding="utf8") as keyapp:
    secretkeyapp = keyapp.read()

# DEFININDO APP
app = Flask(__name__)
app.secret_key = f'{secretkeyapp}'

# VARIÁVEL QUE RECEBE SOTES DE INPUT
valores = ['nenhum site foi inserido']

servico_email=''
emails_totais=None
filtro_on=False

# DEFININDO INSTRUÇÕES PARA ENVIAR AO SITE
pytohtmllist=[
    'Site Pendente',
    'Aqui forneceremos dados a respeito da notabilidade do site',
    'Aqui reportaremos informações sobre o julgamento do site',
    'Aqui recomendaremos medidas de segurança gerais',
    '0',
    "#58697a"
]

pytohtmllist02=[
    'Email Pendente',
    'Aqui forneceremos dados a respeito da notabilidade do autor do email',
    'Aqui reportaremos informações sobre o julgamento do conteúdo geral do email',
    'Aqui recomendaremos medidas de segurança gerais',
    '0',
    "#58697a",
    'Assunto do email'
]

quesito=False
filtros={}

analisaremail=False

# ROTA PRINCIPAL
@app.route("/")
def home():
    return render_template("mainhome.html")

# ROTA DE SELEÇÃO DE OPÇÕES
@app.route("/info")
def info():
    return render_template("index.html")

# ROTA DE ANÁLISE DO SITE
@app.route("/siteanalysis", methods=["GET", "POST"])
def site():
    
    # IMPORTANDO VARIÁVEL DE LISTA
    global pytohtmllist
    
    # CRIANDO INPUT DE SITE
    if request.method == "POST":
        novo_valor = request.form.get("valor")
        if novo_valor:
            valores.append(novo_valor)
            if len(valores)>1:
                valores.pop(0) 
            pytohtmllist=apichatgptsite(valores) # ATRIBUIR VALOR A VARIÁVEL VALORES

        # CONDICIONAL SE VALOR INSERIDO FOR INVÁLIDO
        if pytohtmllist[5]=="#58697a" or pytohtmllist[5]=="#733179":
            return redirect(url_for("site")) # RETORNAR AO ESTADO NORMAL DA PÁGINA

        return redirect(url_for("site")) # RETORNAR AO ESTADO NORMAL DA PÁGINA
    
    # RENDERIZAR SITE E ENVIAR VALORES EM PYTHON PARA HTML
    return render_template("siteanalysis.html", valores=valores, classificacao=pytohtmllist[0],dominio=pytohtmllist[1],justificativa=pytohtmllist[2],seguranca=pytohtmllist[3],coloracao=pytohtmllist[5])

@app.route("/logingoogle",  methods=["GET", "POST"])
def logingoogle():
    
    global servico_email
    
    servico_email=login_email()
    return redirect(url_for('email'))

# ROTA DE ANÁLISE DE EMAIL
@app.route("/emailanalysis", methods=["GET", "POST"])
def email():

    global analisaremail,pytohtmllist02,quesito,email_especifico,servico_email,emails_totais,filtro_on

    if filtro_on == False:
        emails_totais=buscar_emails(servico_email)

    if quesito==True: 
        quesito=False
        return render_template("emailanalysis.html", filtros=session.get('filtros'),classificacao02=pytohtmllist02[0],dominio02=pytohtmllist02[1],justificativa02=pytohtmllist02[2],seguranca02=pytohtmllist02[3],coloracao=pytohtmllist02[5],assuntoemail=pytohtmllist02[6],emails_totais=emails_totais)
        session.pop('filtros', None)
    if 'filtros' not in session:
        session['filtros'] = {}

    if request.method == 'POST':
        filtro = request.form.get('filtro')
        valor = request.form.get(filtro)

        if filtro and valor:
            # Adiciona ou atualiza o filtro na sessão
            session['filtros'][filtro] = valor
            session.modified = True  # Garante que a sessão será atualizada
        return redirect(url_for('email'))

    return render_template("emailanalysis.html", filtros=session.get('filtros'),classificacao02=pytohtmllist02[0],dominio02=pytohtmllist02[1],justificativa02=pytohtmllist02[2],seguranca02=pytohtmllist02[3],coloracao=pytohtmllist02[5],assuntoemail=pytohtmllist02[6],emails_totais=emails_totais)

@app.route('/limpar', methods=['POST'])
def limpar():
    global pytohtmllist02,filtro_on
    pytohtmllist02=[
        'Email Pendente',
        'Aqui forneceremos dados a respeito da notabilidade do autor do email',
        'Aqui reportaremos informações sobre o julgamento do conteúdo geral do email',
        'Aqui recomendaremos medidas de segurança gerais',
        '0',
        "#58697a",
        'Assunto do email'
    ]
    filtro_on=False
    session.pop('filtros', None)
    return redirect(url_for('email'))

@app.route('/enviar', methods=['POST'])
def enviar():

    global pytohtmllist02,quesito,filtro_on,emails_totais

    dictemail={'data':'0','autor':'0'}

    try:
        dictemail['data']=session['filtros']['data']
    except:
        ValueError
    try:
        dictemail['autor']=session['filtros']['autor']
    except:
        ValueError
        
    print(dictemail)

    if len(dictemail['data']) > 2:
        emails_totais=data(emails_totais,dictemail['data'])
        print(dictemail['data'])
        filtro_on=True
    if len(dictemail['autor']) > 2:
        emails_totais=remetentes(emails_totais,dictemail['autor'])
        print(dictemail['autor'])
        filtro_on=True

    quesito=True

    return redirect(url_for('email'))

@app.route('/analisaremail', methods=['POST'])
def analisaremail():

    global pytohtmllist02,quesito

    pytohtmllist02=apichatgptemail(request.form.get("email_especifico"))
    pytohtmllist02.append(request.form.get("assunto_email_especifico"))

    quesito=True

    return redirect(url_for('email'))

# RODAR APP SOMENTE SE SITE TIVER ABERTO
if __name__ == "__main__":
    app.run(debug=True)