from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "armazem-2026"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://neondb_owner:npg_bhiXJef0M3pz@ep-ancient-tree-b43mk2n7-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), default="funcionario")

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    preco_compra = db.Column(db.Float, default=0)
    quantidade = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    quantidade = db.Column(db.Integer)
    valor_total = db.Column(db.Float)
    lucro = db.Column(db.Float, default=0)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    produto = db.relationship("Produto")

class FechamentoDia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    data = db.Column(db.Date)
    total_bruto = db.Column(db.Float)
    total_lucro = db.Column(db.Float, default=0)
    qtd_vendas = db.Column(db.Integer)
    data_fechamento = db.Column(db.DateTime, default=datetime.utcnow)

class Caixa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    valor = db.Column(db.Float, default=0)

class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    descricao = db.Column(db.String(200))
    valor = db.Column(db.Float)
    data = db.Column(db.DateTime, default=datetime.utcnow)

class Resto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    descricao = db.Column(db.String(200))
    valor = db.Column(db.Float)
    data = db.Column(db.DateTime, default=datetime.utcnow)

class ResetDashboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_reset = db.Column(db.DateTime, default=datetime.utcnow)

T = """<!DOCTYPE html><html lang="pt"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Armazém</title><style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,sans-serif}
body{background:#f8f9fa;color:#212529}
.top{background:#1a365d;color:#fff;padding:12px 16px;position:sticky;top:0;z-index:50}
.top h1{font-size:1.1rem}
.top .user{font-size:.75rem;opacity:.85;margin-top:2px}
.nav{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}
.nav a{background:rgba(255,255,255,.15);color:#fff;padding:5px 11px;border-radius:16px;text-decoration:none;font-size:.75rem}
.c{max-width:920px;margin:0 auto;padding:12px}
.card{background:#fff;border-radius:10px;padding:14px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.card h2{font-size:1rem;margin-bottom:10px;color:#1a365d}
input,button,select,textarea{width:100%;padding:10px;margin:4px 0;border-radius:7px;border:1px solid #ddd;font-size:14px}
button{background:#2b6cb0;color:#fff;border:none;font-weight:500;cursor:pointer}
.g{background:#2f855a}.o{background:#dd6b20}.r{background:#c53030}
.s{width:auto;padding:6px 10px;font-size:12px;margin:2px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}
.box{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:10px;text-align:center}
.box b{display:block;color:#1a365d;margin-bottom:3px}
.box div{font-size:.75rem;color:#555;margin:2px 0}
.stat{background:#fff;border-radius:12px;padding:16px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,.08);border-top:4px solid #2b6cb0}
.stat b{display:block;font-size:1.5rem;margin-top:6px;font-weight:700}
table{width:100%;border-collapse:collapse;font-size:13px}
th{background:#edf2f7;padding:7px;text-align:left}
td{padding:7px;border-bottom:1px solid #eee}
.flash{background:#e6fffa;padding:8px 12px;border-radius:6px;margin-bottom:10px;font-size:.85rem}
</style></head><body>{% if session.get('user_id') %}<div class="top"><h1>Armazém</h1><div class="user">{{ session.get('nome','') }}</div><div class="nav"><a href="/">Vender</a><a href="/dashboard">Dashboard</a><a href="/hoje">Hoje</a><a href="/relatorio">Relatório</a><a href="/caixa">Caixa</a><a href="/produtos">Produtos</a><a href="/stock">Stock</a><a href="/compras">Compras</a><a href="/restos">Restos</a><a href="/logout">Sair</a></div></div>{% endif %}<div class="c">{% with messages = get_flashed_messages() %}{% if messages %}{% for msg in messages %}<div class="flash">{{ msg }}</div>{% endfor %}{% endif %}{% endwith %}{{ content|safe }}</div></body></html>"""

def is_admin():
    return session.get("tipo") == "admin"

def calcular_lucro_unidade(preco, preco_compra):
    if preco_compra:
        return preco - preco_compra
    return 0

def get_ultimo_reset():
    r = ResetDashboard.query.order_by(ResetDashboard.data_reset.desc()).first()
    return r.data_reset if r else datetime(2000, 1, 1)

@app.route("/")
def index():
    if "user_id" not in session: return redirect("/login")
    busca = request.args.get("busca", "")
    q = Produto.query
    if busca:
        q = q.filter(Produto.nome.ilike("%"+busca+"%"))
    boxes = ""
    for p in q.order_by(Produto.nome).all():
        lucro = calcular_lucro_unidade(p.preco, p.preco_compra or 0)
        boxes += f'''
        <div class="box">
            <b>{p.nome}</b>
            <div>Venda: Kz {int(p.preco)}</div>
            <div>Compra: Kz {int(p.preco_compra or 0)}</div>
            <div>Lucro: Kz {int(lucro)}</div>
            <div>Stock: {p.quantidade}</div>
            <form method="POST" action="/vender">
                <input type="hidden" name="produto_id" value="{p.id}">
                <input type="number" name="quantidade" value="1" min="1" max="{p.quantidade}" style="width:60px;display:inline-block">
                <button class="g s">Vender</button>
            </form>
        </div>
        '''
    return render_template_string(T, content=f'<div class="card"><h2>Vender</h2><form method="GET"><input name="busca" placeholder="Pesquisar produto..." value="{busca}"><button>Pesquisar</button></form><div class="grid">{boxes}</div></div>')

@app.route("/vender", methods=["POST"])
def vender():
    if "user_id" not in session: return redirect("/login")
    p = Produto.query.get(int(request.form["produto_id"]))
    qtd = int(request.form.get("quantidade", 1))
    if p and qtd > 0 and p.quantidade >= qtd:
        lucro_un = calcular_lucro_unidade(p.preco, p.preco_compra or 0)
        db.session.add(Venda(produto_id=p.id, user_id=session["user_id"], quantidade=qtd, valor_total=p.preco*qtd, lucro=lucro_un*qtd))
        p.quantidade -= qtd
        db.session.commit()
        flash(f"Vendido {qtd}x {p.nome}")
    else:
        flash("Stock insuficiente")
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session: return redirect("/login")
    ultimo = get_ultimo_reset()
    vendas = Venda.query.filter(Venda.data >= ultimo).all()
    bruto = sum(v.valor_total for v in vendas)
    lucro = sum(v.lucro or 0 for v in vendas)
    
    ontem = date.today() - timedelta(days=1)
    vendas_ontem = Venda.query.filter(db.func.date(Venda.data)==ontem).all()
    bruto_ontem = sum(v.valor_total for v in vendas_ontem)
    lucro_ontem = sum(v.lucro or 0 for v in vendas_ontem)
    
    compras = Compra.query.filter(Compra.data >= ultimo).all()
    total_compras = sum(c.valor for c in compras)
    
    restos = Resto.query.filter(Resto.data >= ultimo).all()
    total_restos = sum(r.valor for r in restos)
    
    caixa = Caixa.query.filter_by(user_id=session["user_id"]).first()
    cv = caixa.valor if caixa else 0
    
    baixos = Produto.query.filter(Produto.quantidade <= Produto.stock_minimo).count()
    
    botao = ""
    if is_admin():
        botao = '<form method="POST" action="/reiniciar-dashboard" style="margin-top:12px"><button class="r" onclick="return confirm(\'Reiniciar o Dashboard?\')">Reiniciar Dashboard</button></form>'
    
    return render_template_string(T, content=f'''
    <h2>Dashboard</h2>
    <div class="grid">
        <div class="stat">Vendas (desde último reset)<b>Kz {int(bruto)}</b><div style="font-size:.75rem;color:#666">Ontem: Kz {int(bruto_ontem)}</div></div>
        <div class="stat">Lucro<b>Kz {int(lucro)}</b><div style="font-size:.75rem;color:#666">Ontem: Kz {int(lucro_ontem)}</div></div>
        <div class="stat">Nº Vendas<b>{len(vendas)}</b></div>
        <div class="stat">Compras<b>Kz {int(total_compras)}</b></div>
        <div class="stat">Restos<b>Kz {int(total_restos)}</b></div>
        <div class="stat">Caixa<b>Kz {int(cv)}</b></div>
        <div class="stat">Stock Baixo<b>{baixos}</b></div>
    </div>
    {botao}
    ''')

@app.route("/reiniciar-dashboard", methods=["POST"])
def reiniciar_dashboard():
    if not is_admin(): return redirect("/")
    db.session.add(ResetDashboard())
    db.session.commit()
    flash("Dashboard reiniciado.")
    return redirect("/dashboard")

@app.route("/hoje")
def hoje():
    if "user_id" not in session: return redirect("/login")
    vendas = Venda.query.filter(db.func.date(Venda.data)==date.today()).all()
    bruto = sum(v.valor_total for v in vendas)
    lucro = sum(v.lucro or 0 for v in vendas)
    linhas = "".join(f"<tr><td>{v.produto.nome}</td><td>{v.quantidade}</td><td>Kz {int(v.valor_total)}</td><td>Kz {int(v.lucro or 0)}</td></tr>" for v in vendas)
    return render_template_string(T, content=f'<div class="card"><h2>Hoje</h2><p>Total: Kz {int(bruto)}</p><p>Lucro: Kz {int(lucro)}</p><form method="POST" action="/finalizar"><button class="o">Finalizar Dia</button></form><table><tr><th>Produto</th><th>Qtd</th><th>Valor</th><th>Lucro</th></tr>{linhas}</table></div>')

@app.route("/finalizar", methods=["POST"])
def finalizar():
    if "user_id" not in session: return redirect("/login")
    vendas = Venda.query.filter(db.func.date(Venda.data)==date.today()).all()
    bruto = sum(v.valor_total for v in vendas)
    lucro = sum(v.lucro or 0 for v in vendas)
    db.session.add(FechamentoDia(user_id=session["user_id"], data=date.today(), total_bruto=bruto, total_lucro=lucro, qtd_vendas=len(vendas)))
    db.session.commit()
    flash("Dia finalizado.")
    return redirect("/hoje")

@app.route("/relatorio")
def relatorio():
    if "user_id" not in session: return redirect("/login")
    fs = FechamentoDia.query.order_by(FechamentoDia.data.desc()).all()
    linhas = "".join(f"<tr><td>{f.data.strftime('%d/%m/%Y')}</td><td>Kz {int(f.total_bruto or 0)}</td><td>Kz {int(f.total_lucro or 0)}</td><td>{f.qtd_vendas}</td></tr>" for f in fs)
    return render_template_string(T, content=f'<div class="card"><h2>Relatório</h2><table><tr><th>Data</th><th>Total</th><th>Lucro</th><th>Vendas</th></tr>{linhas}</table></div>')

@app.route("/caixa", methods=["GET","POST"])
def caixa():
    if "user_id" not in session: return redirect("/login")
    c = Caixa.query.filter_by(user_id=session["user_id"]).first()
    if not c:
        c = Caixa(user_id=session["user_id"], valor=0)
        db.session.add(c)
        db.session.commit()
    if request.method == "POST":
        c.valor = float(request.form["valor"])
        db.session.commit()
        return redirect("/caixa")
    return render_template_string(T, content=f'<div class="card"><h2>Caixa</h2><p>Kz {int(c.valor)}</p><form method="POST"><input type="number" name="valor" value="{c.valor}"><button>Alterar</button></form></div>')

@app.route("/produtos", methods=["GET","POST"])
def produtos():
    if "user_id" not in session: return redirect("/login")
    if request.method == "POST" and is_admin():
        db.session.add(Produto(nome=request.form["nome"], preco=float(request.form["preco"]), preco_compra=float(request.form.get("preco_compra",0)), quantidade=int(request.form["quantidade"])))
        db.session.commit()
        return redirect("/produtos")
    ps = Produto.query.order_by(Produto.nome).all()
    linhas = "".join(f"<tr><td>{p.nome}</td><td>Kz {int(p.preco)}</td><td>Kz {int(p.preco_compra or 0)}</td><td>{p.quantidade}</td></tr>" for p in ps)
    form = '<form method="POST"><input name="nome" placeholder="Nome" required><input type="number" name="preco" placeholder="Preço venda" required><input type="number" name="preco_compra" placeholder="Preço compra"><input type="number" name="quantidade" placeholder="Stock" required><button>Cadastrar</button></form>' if is_admin() else ""
    return render_template_string(T, content=f'<div class="card"><h2>Produtos</h2>{form}<table><tr><th>Nome</th><th>Venda</th><th>Compra</th><th>Stock</th></tr>{linhas}</table></div>')

@app.route("/stock")
def stock():
    if "user_id" not in session: return redirect("/login")
    ps = Produto.query.order_by(Produto.nome).all()
    linhas = "".join(f"<tr><td>{p.nome}</td><td>{p.quantidade}</td></tr>" for p in ps)
    return render_template_string(T, content=f'<div class="card"><h2>Stock</h2><table><tr><th>Produto</th><th>Quantidade</th></tr>{linhas}</table></div>')

@app.route("/compras", methods=["GET","POST"])
def compras():
    if "user_id" not in session: return redirect("/login")
    if request.method == "POST":
        db.session.add(Compra(user_id=session["user_id"], descricao=request.form["descricao"], valor=float(request.form["valor"])))
        db.session.commit()
        return redirect("/compras")
    items = Compra.query.order_by(Compra.data.desc()).all()
    linhas = "".join(f"<tr><td>{c.descricao}</td><td>Kz {int(c.valor)}</td><td>{c.data.strftime('%d/%m/%Y')}</td></tr>" for c in items)
    return render_template_string(T, content=f'<div class="card"><h2>Compras</h2><form method="POST"><input name="descricao" placeholder="Descrição" required><input type="number" name="valor" placeholder="Valor" required><button>Registar</button></form><table><tr><th>Descrição</th><th>Valor</th><th>Data</th></tr>{linhas}</table></div>')

@app.route("/restos", methods=["GET","POST"])
def restos():
    if "user_id" not in session: return redirect("/login")
    if request.method == "POST":
        db.session.add(Resto(user_id=session["user_id"], descricao=request.form["descricao"], valor=float(request.form["valor"])))
        db.session.commit()
        return redirect("/restos")
    items = Resto.query.order_by(Resto.data.desc()).all()
    linhas = "".join(f"<tr><td>{r.descricao}</td><td>Kz {int(r.valor)}</td><td>{r.data.strftime('%d/%m/%Y')}</td></tr>" for r in items)
    return render_template_string(T, content=f'<div class="card"><h2>Restos</h2><form method="POST"><input name="descricao" placeholder="Descrição" required><input type="number" name="valor" placeholder="Valor" required><button>Registar</button></form><table><tr><th>Descrição</th><th>Valor</th><th>Data</th></tr>{linhas}</table></div>')

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = Usuario.query.filter_by(email=request.form["email"]).first()
        if u and check_password_hash(u.senha, request.form["senha"]):
            session["user_id"] = u.id
            session["nome"] = u.nome
            session["tipo"] = u.tipo or "funcionario"
            return redirect("/dashboard")
        flash("Email ou senha incorretos")
    return render_template_string(T, content='<div class="card" style="max-width:360px;margin:30px auto"><h2>Entrar</h2><form method="POST"><input type="email" name="email" placeholder="Email" required><input type="password" name="senha" placeholder="Senha" required><button>Entrar</button></form></div>')

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5001, debug=True)