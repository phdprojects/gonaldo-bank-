import streamlit as st
from datetime import datetime
import random
from io import BytesIO
from reportlab.pdfgen import canvas
import qrcode
import os

# =========================
# 🟢 STYLE RETRO TERMINAL
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Courier+Prime&display=swap');

.stApp {
    background-color: black;
    color: #00ff00;
    font-family: 'Courier Prime', monospace;
}

input, textarea {
    background-color: black !important;
    color: #00ff00 !important;
    border: 1px solid #00ff00 !important;
}

button {
    background-color: black !important;
    color: #00ff00 !important;
    border: 1px solid #00ff00 !important;
}

/* CARD STYLE */
.card-container {
    perspective: 1200px;
    margin: 20px 0;
}

.card {
    width: 380px;
    height: 230px;
    position: relative;
    transform-style: preserve-3d;
    transition: transform 1s;
    cursor: pointer;
}

.card:hover {
    transform: rotateY(180deg);
}

.front, .back {
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 16px;
    background: #111;
    border: 1px solid #00ff00;
    color: #00ff00;
    font-family: monospace;
    backface-visibility: hidden;
    padding: 20px;
}

.back {
    transform: rotateY(180deg);
}

.chip {
    width: 60px;
    height: 45px;
    background: gold;
    border-radius: 8px;
    margin-top: 15px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🧠 STATE
# =========================
if "sessao" not in st.session_state:
    st.session_state.sessao = {"logado": False}

if "db" not in st.session_state:
    st.session_state.db = {}

# =========================
# 🏦 HEADER
# =========================
def header():
    st.markdown("""
========================================
GONALDO BANK SYSTEM
RETRO CORE BANKING TERMINAL
""")

# =========================
# 🧾 CARTÃO
# =========================
def gerar_cartao():
    numero = " ".join([str(random.randint(1000, 9999)) for _ in range(4)])
    validade = f"{random.randint(1,12):02d}/{random.randint(26,32)}"
    cvv = str(random.randint(100, 999))

    return {
        "numero": numero,
        "validade": validade,
        "cvv": cvv
    }

# =========================
# 📄 QR
# =========================
def gerar_qr(payload):
    qr = qrcode.make(payload)
    path = "qr_tmp.png"
    qr.save(path)
    return path

# =========================
# 📄 PDF
# =========================
def gerar_pdf(titulo, dados):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)

    y = 800
    c.setFont("Courier", 12)

    c.drawString(50, y, "GONALDO BANK")
    y -= 20

    c.drawString(50, y, titulo.upper())
    y -= 30

    qr_payload = titulo

    for k, v in dados.items():
        c.drawString(50, y, f"{k}: {v}")
        y -= 18
        qr_payload += str(v)

    qr_path = gerar_qr(qr_payload)
    c.drawImage(qr_path, 420, 650, width=120, height=120)

    c.save()
    buffer.seek(0)

    if os.path.exists(qr_path):
        os.remove(qr_path)

    return buffer

# =========================
# 💳 CARTÃO UI (FIXADO)
# =========================
def mostrar_cartao_ui(cartao, iban, nome):

    st.markdown(f"""
<div class="card-container">
  <div class="card">

    <div class="front">
        🟢 GONALDO BANK<br>
        <small>CARD SYSTEM</small>

        <div class="chip"></div>

        <div style="margin-top:20px;">
            {cartao['numero']}
        </div>

        <div>
            {nome}
        </div>

        <div>
            VALID {cartao['validade']} | CVV {cartao['cvv']}
        </div>
    </div>

    <div class="back">
        IBAN:<br>{iban}
        <br><br>
        ⚠ NOT REAL CARD
    </div>

  </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 🔐 LOGIN
# =========================
def login():
    header()

    user = st.text_input("ID")
    email = st.text_input("EMAIL")

    if st.button("LOGIN"):
        if user == "0001" and email == "gm@teste.com":
            st.session_state.sessao["logado"] = True
            st.rerun()
        else:
            st.error("ACCESS DENIED")

# =========================
# 🏦 CRIAR CONTA
# =========================
def criar_conta():
    header()

    tipo = st.selectbox("TIPO", ["PARTICULAR", "EMPRESARIAL"])
    nome = st.text_input("NOME")
    nif = st.text_input("NIF")

    if st.button("CRIAR CONTA"):
        conta = str(random.randint(100000, 999999))
        iban = f"PT50 0007 0000 {conta[:4]} {conta[4:]} 8045"

        cartao = gerar_cartao()

        st.session_state.db[conta] = {
            "nome": nome,
            "nif": nif,
            "tipo": tipo,
            "iban": iban,
            "saldo": 0.0,
            "cartao": cartao,
            "extrato": []
        }

        st.success(f"CONTA CRIADA: {conta}")

        mostrar_cartao_ui(cartao, iban, nome)

        pdf = gerar_pdf("CONTRATO", {
            "Titular": nome,
            "NIF": nif,
            "Conta": conta,
            "IBAN": iban,
            "Tipo": tipo,
            "Data": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

        st.download_button("📄 PDF", pdf, file_name=f"contrato_{conta}.pdf")

# =========================
# 💰 SALDO
# =========================
def saldo():
    header()

    conta = st.text_input("CONTA")

    if st.button("CONSULTAR"):
        if conta in st.session_state.db:
            st.success(f"SALDO: {st.session_state.db[conta]['saldo']:.2f} EUR")

# =========================
# 💸 OPERAÇÕES
# =========================
def operacoes():
    header()

    op = st.text_input("1 DEP / 2 LEV")
    conta = st.text_input("CONTA")
    valor = st.number_input("VALOR", min_value=0.01)

    if st.button("EXECUTAR"):
        if conta in st.session_state.db:
            d = st.session_state.db[conta]

            if op == "1":
                d["saldo"] += valor
                d["extrato"].append(f"{datetime.now()} DEP +{valor}")
                st.success("OK")

            elif op == "2":
                if valor <= d["saldo"]:
                    d["saldo"] -= valor
                    d["extrato"].append(f"{datetime.now()} LEV -{valor}")
                    st.success("OK")

# =========================
# 📊 EXTRATO
# =========================
def extrato():
    header()

    conta = st.text_input("CONTA")

    if st.button("GERAR"):
        if conta in st.session_state.db:
            d = st.session_state.db[conta]

            pdf = gerar_pdf("EXTRATO", {
                "Conta": conta,
                "Movimentos": "\n".join(d["extrato"]) if d["extrato"] else "SEM MOVIMENTOS"
            })

            st.download_button("DOWNLOAD", pdf, file_name=f"extrato_{conta}.pdf")

# =========================
# 🧭 MENU
# =========================
def menu():
    header()

    st.write("""
[1] SALDO  
[2] OPERAÇÕES  
[3] CRIAR CONTA  
[5] EXTRATO  
[6] LOGOUT
""")

    return st.text_input("COMMAND")

# =========================
# 🔁 ROUTER
# =========================
def router(cmd):
    if cmd == "1":
        saldo()
    elif cmd == "2":
        operacoes()
    elif cmd == "3":
        criar_conta()
    elif cmd == "5":
        extrato()
    elif cmd == "6":
        st.session_state.sessao["logado"] = False
        st.rerun()

# =========================
# 🚀 APP
# =========================
if not st.session_state.sessao["logado"]:
    login()
else:
    cmd = menu()
    router(cmd)