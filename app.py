import streamlit as st
from supabase import create_client
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import qrcode
import random
import time
import uuid
import os

# =====================================================
# SUPABASE
# =====================================================

SUPABASE_URL = "https://ihzgykzgdnzrlhubzwow.supabase.co"
SUPABASE_KEY = "sb_publishable_WxjkMpV4Ok9HJ9_LWdijGQ_oBNAhD3K"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="BANK GONALDO",
    layout="wide"
)

# =====================================================
# RETRO TERMINAL CSS
# =====================================================

st.markdown("""
<style>

/* =========================
   FUNDO GLOBAL (FORÇA TOTAL)
========================= */
html, body, .stApp {
    background: #000000 !important;
    color: #00FF00 !important;
}

/* =========================
   REMOVE TODAS AS MARGENS DO APP
========================= */
.stApp {
    padding: 0 !important;
    margin: 0 !important;
}

/* =========================
   REMOVE CONTAINER PRINCIPAL (AQUI ESTAVA O DESLOCAMENTO)
========================= */
.block-container {
    max-width: 80% !important;
    width: 80% !important;
    padding: 0 !important;
    margin: 0 auto !important;
    background: #000000 !important;
}

/* =========================
   REMOVE LAYOUT INTERNO DO STREAMLIT
========================= */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"],
[data-testid="stToolbar"] {
    background: #000000 !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Sidebar completamente removida */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {
    display: none !important;
}

/* =========================
   CENTRALIZAÇÃO “TERMINAL STYLE”
========================= */
.main {
    display: flex !important;
    justify-content: center !important;
    align-items: flex-start !important;
}

/* =========================
   REMOVE BLOCOS INTERNOS
========================= */
div, section, article {
    background: #000000 !important;
    color: #00FF00 !important;
    border: none !important;
    box-shadow: none !important;
}

/* =========================
   INPUTS TIPO TERMINAL
========================= */
input, textarea {
    background: #000000 !important;
    color: #00FF00 !important;
    border: none !important;
    border-bottom: 1px solid #00FF00 !important;
    border-radius: 0px !important;
    outline: none !important;
}

/* =========================
   BOTÕES TERMINAL
========================= */
button {
    background: #000000 !important;
    color: #00FF00 !important;
    border: 1px solid #00FF00 !important;
    border-radius: 0px !important;
}

button:hover {
    background: #00FF00 !important;
    color: #000000 !important;
}

/* =========================
   TABELAS
========================= */
table, th, td {
    background: #000000 !important;
    color: #00FF00 !important;
    border: 1px solid #00FF00 !important;
}

/* =========================
   ALERTAS
========================= */
[data-testid="stAlert"] {
    background: #000000 !important;
    color: #00FF00 !important;
    border: 1px solid #00FF00 !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION
# =====================================================

if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================
# HELPERS
# =====================================================

def terminal(msg):
    st.code(msg, language="text")


def loading(msg):
    with st.spinner(msg):
        time.sleep(1)


# =====================================================
# GENERATORS
# =====================================================

def gerar_conta():

    numero_conta = str(random.randint(1000000000, 9999999999))

    iban = f"PT50 0007 0000 {numero_conta[:4]} {numero_conta[4:8]} {numero_conta[8:]}"

    pin = str(random.randint(1000, 9999))

    return numero_conta, iban, pin



def gerar_cartao(nome):

    cartao = "4532 " + " ".join(
        [str(random.randint(1000, 9999)) for _ in range(3)]
    )

    validade = f"{random.randint(1,12):02d}/{random.randint(27,32)}"

    cvv = str(random.randint(100,999))

    return {
        "nome": nome.upper(),
        "numero": cartao,
        "validade": validade,
        "cvv": cvv
    }


# =====================================================
# QR CODE
# =====================================================

def gerar_qr(payload):

    qr = qrcode.make(payload)

    nome = f"qr_{uuid.uuid4()}.png"

    qr.save(nome)

    return nome


# =====================================================
# LOGS
# =====================================================

def criar_log(operador, acao, detalhes):

    try:

        supabase.table("logs_sistema").insert({
            "operador": operador,
            "acao": acao,
            "detalhes": detalhes
        }).execute()

    except:
        pass


# =====================================================
# PDF
# =====================================================

def gerar_pdf(titulo, dados):

    buffer = BytesIO()

    c = canvas.Canvas(buffer, pagesize=letter)

    y = 750

    c.setFont("Courier-Bold", 16)
    c.drawString(50, y, "GONALDO BANK")

    y -= 25

    c.setFont("Courier", 12)
    c.drawString(50, y, "RETRO CORE BANKING SYSTEM")

    y -= 20
    c.drawString(50, y, "====================================")

    y -= 35

    c.setFont("Courier-Bold", 13)
    c.drawString(50, y, titulo.upper())

    y -= 35

    payload = f"{titulo}|"

    c.setFont("Courier", 11)

    for k, v in dados.items():

        linha = f"{k}: {v}"

        c.drawString(50, y, linha)

        payload += linha + "|"

        y -= 22

    y -= 20

    c.drawString(50, y, "====================================")

    y -= 20

    c.drawString(50, y, "AUTO GENERATED BANK DOCUMENT")

    y -= 20

    c.drawString(50, y, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    qr_path = gerar_qr(payload)

    c.drawImage(qr_path, 400, 600, width=130, height=130)

    c.save()

    buffer.seek(0)

    if os.path.exists(qr_path):
        os.remove(qr_path)

    return buffer


# =====================================================
# CARD PDF
# =====================================================

def gerar_cartao_pdf(cliente, conta):

    buffer = BytesIO()

    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Courier-Bold", 18)

    c.drawString(50, 720, "GONALDO BANK")

    c.setFont("Courier", 14)

    c.drawString(50, 690, "RETRO CORE BANKING CARD")

    c.rect(40, 420, 520, 220)

    c.drawString(80, 590, "[ CHIP DOURADO ]")

    c.setFont("Courier-Bold", 18)

    c.drawString(80, 540, conta['cartao_numero'])

    c.setFont("Courier", 12)

    c.drawString(80, 500, f"CARD HOLDER: {cliente['nome']}")

    c.drawString(80, 470, f"VALID THRU: {conta['cartao_validade']}")

    c.drawString(320, 470, f"CVV: {conta['cartao_cvv']}")

    c.drawString(80, 440, f"IBAN: {conta['iban']}")

    c.save()

    buffer.seek(0)

    return buffer


# =====================================================
# FIND ACCOUNT
# =====================================================

def encontrar_conta(ref):

    try:

        conta = supabase.table("contas") \
            .select("*") \
            .or_(f"numero_conta.eq.{ref},iban.eq.{ref}") \
            .execute()

        if conta.data:
            return conta.data[0]

        return None

    except:
        return None


# =====================================================
# LOGIN
# =====================================================

terminal("""
==================================================

BANK GONALDO - CORE BANKING SYSTEM

==================================================
""")

if st.session_state.user is None:

    st.write("É NECESSÁRIA A AUTENTICAÇÃO")

    st.write("CONECTANDO AO NÚCLEO SUPABASE...")

    email = st.text_input("EMAIL")

    password = st.text_input("PASSWORD", type="password")

    if st.button("EXECUTE_LOGIN"):

        try:

            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            st.session_state.user = res.user

            supabase.table("usuarios_perfil").upsert({
                "id": str(res.user.id),
                "email": email,
                "ultimo_login": datetime.now().isoformat()
            }).execute()

            criar_log(email, "LOGIN", "OPERADOR AUTENTICADO")

            st.success("ACCESS GRANTED")

            time.sleep(1)

            st.rerun()

        except Exception as e:

            st.error(f"ACESSO NEGADO: {str(e)}")

    st.stop()

# =====================================================
# MENU
# =====================================================

terminal("""
==================================================

 BANK GONALDO - CORE BANKING SYSTEM

==================================================

[1] CONSULTAR SALDO

[2] OPERAÇÕES FINANCEIRAS

[3] ABERTURA DE CONTA

[4] GESTÃO DE CLIENTES

[5] EXTRATO

[6] LOGOUT

==================================================
""")

cmd = st.text_input("COMMAND >")

# =====================================================
# SALDO
# =====================================================

if cmd == "1":

    ref = st.text_input("CONTA / IBAN")

    if st.button("CONSULTAR"):

        loading("CONSULTANDO SALDO")

        conta = encontrar_conta(ref)

        if conta:

            st.metric("SALDO DISPONÍVEL", f"{float(conta['saldo']):.2f} EUR")

            pdf = gerar_pdf("CONSULTA SALDO", {
                "IBAN": conta['iban'],
                "CONTA": conta['numero_conta'],
                "SALDO": conta['saldo']
            })

            st.download_button(
                "📄 DOWNLOAD PDF",
                pdf,
                file_name="saldo.pdf",
                mime="application/pdf"
            )

        else:

            st.error("CONTA NÃO ENCONTRADA")

# =====================================================
# OPERACOES
# =====================================================

elif cmd == "2":

    terminal("[1] DEPÓSITO | [2] LEVANTAMENTO | [3] TRANSFERÊNCIA")

    op = st.text_input("OP >")

    conta_ref = st.text_input("CONTA")

    valor = st.number_input("VALOR", min_value=0.01)

    conta = encontrar_conta(conta_ref)

    # =====================================
    # DEPOSITO
    # =====================================

    if op == "1":

        if st.button("EXECUTAR"):

            if conta:

                novo_saldo = float(conta['saldo']) + valor

                supabase.table("contas") \
                    .update({"saldo": novo_saldo}) \
                    .eq("id", conta['id']) \
                    .execute()

                supabase.table("movimentos").insert({
                    "conta_id": conta['id'],
                    "tipo": "DEPOSITO",
                    "valor": valor,
                    "descricao": "DEPÓSITO EM NUMERÁRIO",
                    "operador": st.session_state.user.email
                }).execute()

                criar_log(
                    st.session_state.user.email,
                    "DEPOSITO",
                    f"{valor} EUR"
                )

                st.success("DEPÓSITO EXECUTADO")

                pdf = gerar_pdf("DEPÓSITO", {
                    "CONTA": conta['numero_conta'],
                    "IBAN": conta['iban'],
                    "VALOR": valor,
                    "NOVO SALDO": novo_saldo
                })

                st.download_button(
                    "📄 COMPROVATIVO PDF",
                    pdf,
                    file_name="deposito.pdf",
                    mime="application/pdf"
                )

    # =====================================
    # LEVANTAMENTO
    # =====================================

    elif op == "2":

        pin = st.text_input("PIN", type="password")

        if st.button("EXECUTAR"):

            if conta:

                if pin != conta['pin']:
                    st.error("PIN INVÁLIDO")

                elif valor > float(conta['saldo']):
                    st.error("SALDO INSUFICIENTE")

                else:

                    novo_saldo = float(conta['saldo']) - valor

                    supabase.table("contas") \
                        .update({"saldo": novo_saldo}) \
                        .eq("id", conta['id']) \
                        .execute()

                    supabase.table("movimentos").insert({
                        "conta_id": conta['id'],
                        "tipo": "LEVANTAMENTO",
                        "valor": valor,
                        "descricao": "LEVANTAMENTO ATM",
                        "operador": st.session_state.user.email
                    }).execute()

                    criar_log(
                        st.session_state.user.email,
                        "LEVANTAMENTO",
                        f"{valor} EUR"
                    )

                    st.success("LEVANTAMENTO EXECUTADO")

                    pdf = gerar_pdf("LEVANTAMENTO", {
                        "CONTA": conta['numero_conta'],
                        "VALOR": valor,
                        "NOVO SALDO": novo_saldo
                    })

                    st.download_button(
                        "📄 COMPROVATIVO PDF",
                        pdf,
                        file_name="levantamento.pdf",
                        mime="application/pdf"
                    )

    # =====================================
    # TRANSFERENCIA
    # =====================================

    elif op == "3":

        destino_ref = st.text_input("IBAN DESTINO")

        if st.button("EXECUTAR"):

            destino = encontrar_conta(destino_ref)

            if not conta:
                st.error("CONTA ORIGEM INVÁLIDA")

            elif not destino:
                st.error("DESTINO INVÁLIDO")

            elif valor > float(conta['saldo']):
                st.error("SALDO INSUFICIENTE")

            else:

                saldo_origem = float(conta['saldo']) - valor
                saldo_destino = float(destino['saldo']) + valor

                supabase.table("contas") \
                    .update({"saldo": saldo_origem}) \
                    .eq("id", conta['id']) \
                    .execute()

                supabase.table("contas") \
                    .update({"saldo": saldo_destino}) \
                    .eq("id", destino['id']) \
                    .execute()

                supabase.table("movimentos").insert({
                    "conta_id": conta['id'],
                    "tipo": "TRANSFERENCIA SAIDA",
                    "valor": valor,
                    "descricao": "TRANSFERÊNCIA BANCÁRIA",
                    "conta_destino": destino['iban'],
                    "operador": st.session_state.user.email
                }).execute()

                supabase.table("movimentos").insert({
                    "conta_id": destino['id'],
                    "tipo": "TRANSFERENCIA ENTRADA",
                    "valor": valor,
                    "descricao": "TRANSFERÊNCIA RECEBIDA",
                    "conta_destino": conta['iban'],
                    "operador": st.session_state.user.email
                }).execute()

                criar_log(
                    st.session_state.user.email,
                    "TRANSFERENCIA",
                    f"{valor} EUR"
                )

                st.success("TRANSFERÊNCIA EXECUTADA")

                pdf = gerar_pdf("TRANSFERENCIA", {
                    "ORIGEM": conta['iban'],
                    "DESTINO": destino['iban'],
                    "VALOR": valor,
                    "DATA": datetime.now().strftime("%Y-%m-%d %H:%M")
                })

                st.download_button(
                    "📄 COMPROVATIVO PDF",
                    pdf,
                    file_name="transferencia.pdf",
                    mime="application/pdf"
                )

# =====================================================
# ABERTURA DE CONTA
# =====================================================

elif cmd == "3":

    terminal("[1] PARTICULAR | [2] EMPRESA")

    tipo = st.text_input("TIPO >")

    if tipo in ["1", "2"]:

        nome = st.text_input("NOME")
        nif = st.text_input("NIF")
        email = st.text_input("EMAIL")
        telefone = st.text_input("TELEFONE")
        morada = st.text_area("MORADA")

        if st.button("CRIAR CONTA"):

            loading("CRIANDO CONTA")

            numero_conta, iban, pin = gerar_conta()

            cartao = gerar_cartao(nome)

            cliente = supabase.table("clientes").insert({
                "tipo_conta": "PARTICULAR" if tipo == "1" else "EMPRESA",
                "nome": nome,
                "nif": nif,
                "email": email,
                "telefone": telefone,
                "morada": morada
            }).execute()

            cliente_id = cliente.data[0]['id']

            conta = supabase.table("contas").insert({
                "cliente_id": cliente_id,
                "numero_conta": numero_conta,
                "iban": iban,
                "saldo": 0,
                "pin": pin,
                "cartao_numero": cartao['numero'],
                "cartao_validade": cartao['validade'],
                "cartao_cvv": cartao['cvv']
            }).execute()

            criar_log(
                st.session_state.user.email,
                "CRIACAO_CONTA",
                iban
            )

            terminal(f"""
CONTA CRIADA COM SUCESSO

CLIENTE: {nome}
CONTA: {numero_conta}
IBAN: {iban}
PIN: {pin}

CARTÃO:
{cartao['numero']}
VALIDADE: {cartao['validade']}
CVV: {cartao['cvv']}
""")

            pdf = gerar_pdf("ABERTURA CONTA", {
                "CLIENTE": nome,
                "CONTA": numero_conta,
                "IBAN": iban,
                "PIN": pin,
                "CARTAO": cartao['numero']
            })

            st.download_button(
                "📄 DOWNLOAD CONTRATO PDF",
                pdf,
                file_name="contrato.pdf",
                mime="application/pdf"
            )

            card_pdf = gerar_cartao_pdf(
                {
                    "nome": nome
                },
                {
                    "cartao_numero": cartao['numero'],
                    "cartao_validade": cartao['validade'],
                    "cartao_cvv": cartao['cvv'],
                    "iban": iban
                }
            )

            st.download_button(
                "💳 IMPRIMIR CARTÃO",
                card_pdf,
                file_name="cartao.pdf",
                mime="application/pdf"
            )

# =====================================================
# GESTAO CLIENTES
# =====================================================

elif cmd == "4":

    loading("GERANDO LISTAGEM")

    clientes = supabase.table("clientes").select("*").execute()

    contas = supabase.table("contas").select("*").execute()

    contas_map = {
        c['cliente_id']: c for c in contas.data
    }

    for c in clientes.data:

        conta = contas_map.get(c['id'])

        if conta:

            terminal(f"""
CLIENTE : {c['nome']}
NIF      : {c['nif']}
IBAN     : {conta['iban']}
SALDO    : {conta['saldo']} EUR
""")

# =====================================================
# EXTRATO
# =====================================================

elif cmd == "5":

    ref = st.text_input("CONTA / IBAN")

    if st.button("GERAR EXTRATO"):

        conta = encontrar_conta(ref)

        if conta:

            movimentos = supabase.table("movimentos") \
                .select("*") \
                .eq("conta_id", conta['id']) \
                .order("criado_em", desc=True) \
                .execute()

            texto = ""

            for m in movimentos.data:

                linha = f"{m['criado_em']} | {m['tipo']} | {m['valor']} EUR"

                terminal(linha)

                texto += linha + "\n"

            pdf = gerar_pdf("EXTRATO", {
                "IBAN": conta['iban'],
                "MOVIMENTOS": texto
            })

            st.download_button(
                "📄 DOWNLOAD EXTRATO PDF",
                pdf,
                file_name="extrato.pdf",
                mime="application/pdf"
            )

        else:
            st.error("CONTA NÃO ENCONTRADA")

# =====================================================
# LOGOUT
# =====================================================

elif cmd == "6":

    criar_log(
        st.session_state.user.email,
        "LOGOUT",
        "OPERADOR DESCONECTADO"
    )

    st.session_state.user = None

    st.success("LOGOUT EXECUTADO")

    time.sleep(1)

    st.rerun()