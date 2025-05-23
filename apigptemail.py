import openai

# LER TXT COM API
with open("apikeychatgpt.txt", "r", encoding="utf8") as arcapikey:
    apikey = arcapikey.read()

# LER TXT COM PROMT
with open("promtgptemail.txt", "r", encoding="utf8") as arcpromtgpt:
    promtchatgpt = arcpromtgpt.read()

# DEFINIR FUNCAO DE ANALISE GPT
def apichatgptemail(email):
        
    # DEFININDO PARÂMETROS QUE ENVIO DO PYTHON DA API PARA O ARQUIVO PYTHON FLASK PARA O HTML
    clas='Filtros Pendentes'
    domi='Aqui forneceremos dados a respeito da notabilidade do autor do email'
    just='Aqui reportaremos informações sobre o julgamento do conteúdo geral do email'
    segu='Aqui recomendaremos medidas de segurança gerais'
    corl="#58697a"

    client = openai.OpenAI(api_key=f"{apikey}")

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
            "role": "system",
            "content": [
                {
                "type": "input_text",
                "text": f"{promtchatgpt}" # VARIAVEL QUE IMPORTEI DO TXT
                }
            ]
            },
            {
            "role": "system",
            "content": [
                {
                "type": "input_text",
                "text": "Não insira nenhum hyperlink na sua resposta!!!!!"
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "input_text",
                "text": f"{email}" # VARIAVEL QUE ESTOU REQUISITANDO NA FUNÇÃO
                }
            ]
            }
        ],
        text={
            "format": {
            "type": "text"
            }
        },
        reasoning={},
        tools=[
            {
            "type": "web_search_preview",
            "user_location": {
                "type": "approximate"
            },
            "search_context_size": "medium"
            }
        ],
        temperature=0,
        max_output_tokens=1000,
        top_p=1,
        store=False
        )
    
    print(response.usage.total_tokens)
    
    retornogrup=str(repr(response.output_text))
    retornolinha = [parte.strip() for parte in retornogrup.split('/////')]
    
    # SEPARACAO DO PROMT QUE O CHAT GPT MANDA EM 4 TOPICOS...
    # PEDI PARA ELE SEPARAR OS TOPICOS POR '/////' PARA PODER MOSTRAR NO SITE
    # OS TOPICOS SAO 1. CONFIAVEL, SUSPEITO, DESCONHECIDO OU MALICIOSO (1 PALAVRA) 2. DOMINIO 3. JUSTIFICATIVA 4. DICAS SEGURANÇA

    # FIZ O CHATGPT DAR UM OUTPUT ESCRITO "0" PARA QUAISQUER INPUTS QUE NÃO SEJAM SITES
    if len(retornolinha)<4 and len(email)>0: # ISSO LÊ QUALQUER RESPOSTA QUEBRADA OU QUE SEJA "0" DEFINIR AS VARIÁVEIS
        clas='Tente Novamente'
        domi='Aqui forneceremos dados a respeito da notabilidade do autor do email'
        just='Aqui reportaremos informações sobre o julgamento do conteúdo geral do email'
        segu='Aqui recomendaremos medidas de segurança gerais'
        corl="#58697a"

    # TRATAMENTO DE TEXTO PARA DEIXAR BONITINHO PARA COLOCAR NO SITE
    elif len(retornolinha)>=4:
        clas=retornolinha[0].replace('\\n', '').replace("'",'').lower()
        domi=retornolinha[1].replace('\\n','<br>')
        just=retornolinha[2].replace('\\n','<br>')
        segu=retornolinha[3].replace('\\n','<br>').replace("'",'')
    
    # DEFINIR CORES PARA COLOCAR NO FUNDO DO RETÂNGULO
    if "confiável" in clas:
        corl="#27772e"
    elif "malicioso" in clas:
        corl="#961616"
    elif "suspeito" in clas:
        corl="#8d3d7c"
    elif corl=="#58697a":
        corl="#58697a"
    else:
        corl="#733179"
    
    # RETORNAR CLASSIFICAÇÃO, DOMINIO, JUSTIFICATIVA, SEGURANÇA, LISTA DE ITENS DO OUTPUT SEPARADO, COR
    return [clas,domi,just,segu,retornolinha,corl]