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
    perm_hoje = db.Column(db.Boolean, default=False)
    perm_relatorio = db.Column(db.Boolean, default=False)
    perm_produtos = db.Column(db.Boolean, default=False)
    perm_stock = db.Column(db.Boolean, default=False)
    perm_compras = db.Column(db.Boolean, default=False)
    perm_restos = db.Column(db.Boolean, default=False)

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
    nota = db.Column(db.Text)
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
*{box-sizing:border-box;margin:0;padding:0;font-family:system-ui,-apple-system,sans-serif}
body{background:#f1f5f9;color:#1e293b;transition:all .3s}
body.dark{background:#0f172a;color:#e2e8f0}
body.dark .card,body.dark .box,body.dark .stat{background:#1e293b;color:#e2e8f0;border-color:#334155}
body.dark .top{background:#0f172a}
body.dark th{background:#1e3a5f}
body.dark input,body.dark select,body.dark textarea{background:#1e293b;color:#fff;border-color:#475569}
.top{background:linear-gradient(135deg,#1e3a8a,#1e40af);color:#fff;padding:14px 18px;position:sticky;top:0;z-index:50;box-shadow:0 2px 10px rgba(0,0,0,.1)}
.top h1{font-size:1.15rem;font-weight:600}
.top .user{font-size:.75rem;opacity:.9;margin-top:3px}
.nav{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.nav a{background:rgba(255,255,255,.12);color:#fff;padding:6px 12px;border-radius:20px;text-decoration:none;font-size:.78rem;transition:background .2s}
.nav a:hover{background:rgba(255,255,255,.22)}
.c{max-width:960px;margin:0 auto;padding:16px}
.card{background:#fff;border-radius:12px;padding:18px;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,.06);border:1px solid #e2e8f0}
.card h2{font-size:1.05rem;margin-bottom:14px;color:#1e40af;font-weight:600}
input,button,select,textarea{width:100%;padding:11px;margin:5px 0;border-radius:8px;border:1px solid #cbd5e1;font-size:14px;transition:border .2s}
input:focus,textarea:focus{outline:none;border-color:#3b82f6}
button{background:#2563eb;color:#fff;border:none;font-weight:500;cursor:pointer;border-radius:8px}
button:hover{background:#1d4ed8}
.g{background:#16a34a}.g:hover{background:#15803d}
.o{background:#ea580c}.o:hover{background:#c2410c}
.r{background:#dc2626}.r:hover{background:#b91c1c}
.s{width:auto;padding:7px 12px;font-size:12.5px;margin:2px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:12px}
.box{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.box b{display:block;color:#1e40af;margin-bottom:4px;font-size:.95rem}
.box div{font-size:.78rem;color:#475569;margin:3px 0}
.stat{background:#fff;border-radius:12px;padding:18px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06);border-top:4px solid #3b82f6}
.stat b{display:block;font-size:1.6rem;margin-top:8px;font-weight:700}
.stat.venda b{color:#2563eb}
.stat.lucro b{color:#16a34a}
.stat.compras b{color:#ea580c}
.stat.stock b{color:#7c3aed}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th{background:#f1f5f9;padding:10px;text-align:left;font-weight:600;color:#334155}
td{padding:10px;border-bottom:1px solid #e2e8f0}
.flash{background:#ecfdf5;color:#065f46;padding:10px 14px;border-radius:8px;margin-bottom:12px;font-size:.88rem;border-left:4px solid #10b981}
.btn{display:inline-block;padding:7px 14px;border-radius:8px;text-decoration:none;font-size:12.5px;font-weight:500;margin:3px;background:#2563eb;color:#fff}
.btn-red{background:#dc2626}
.btn-green{background:#16a34a}
.btn-orange{background:#ea580c}
.btn:hover{opacity:.9}
</style></head><body id="body">{% if session.get('user_id') %}<div class="top"><h1>Armazém</h1><div class="user">{{ session.get('nome','') }}</div><div class="nav"><a href="/">Vender</a><a href="/dashboard">Dashboard</a><a href="/resumo">Resumo do Dia</a><a href="/hoje">Hoje</a><a href="/relatorio">Relatório</a><a href="/ranking">Ranking</a><a href="/caixa">Caixa</a><a href="/produtos">Produtos</a><a href="/stock">Stock</a><a href="/compras">Compras</a><a href="/restos">Restos</a><a href="/utilizadores">Utilizadores</a><a href="#" onclick="toggleDark();return false;">Modo</a><a href="/logout">Sair</a></div></div>{% endif %}<div class="c">{% with messages = get_flashed_messages() %}{% if messages %}{% for msg in messages %}<div class="flash">{{ msg }}</div>{% endfor %}{% endif %}{% endwith %}{{ content|safe }}</div>
<script>
function toggleDark(){document.getElementById('body').classList.toggle('dark');localStorage.setItem('dark',document.getElementById('body').classList.contains('dark'))}
if(localStorage.getItem('dark')==='true')document.getElementById('body').classList.add('dark')
</script>
</body></html>"""

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
        admin_btns = ""
        if is_admin():
            admin_btns = f'''
            <form method="POST" action="/devolver" style="display:inline">
                <input type="hidden" name="produto_id" value="{p.id}">
                <button class="o s">Devolver</button>
            </form>
            <form method="POST" action="/eliminar-produto/{p.id}" style="display:inline" onsubmit="return confirm('Eliminar produto?')">
                <button class="r s">Eliminar</button>
            </form>
            '''
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
            {admin_btns}
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

@app.route("/devolver", methods=["POST"])
def devolver():
    if not is_admin(): return redirect("/")
    p = Produto.query.get(int(request.form["produto_id"]))
    if p:
        p.quantidade += 1
        db.session.commit()
        flash(f"Devolvido 1x {p.nome}")
    return redirect("/")

@app.route("/eliminar-produto/<int:id>", methods=["POST"])
def eliminar_produto(id):
    if not is_admin(): return redirect("/")
    p = Produto.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash("Produto eliminado")
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
    
    compras = Compra.query.filter(Compra.data >= ultimo).all()
    total_compras = sum(c.valor for c in compras)
    
    restos = Resto.query.filter(Resto.data >= ultimo).all()
    total_restos = sum(r.valor for r in restos)
    
    caixa = Caixa.query.filter_by(user_id=session["user_id"]).first()
    cv = caixa.valor if caixa else 0
    
    valor_stock = sum((p.preco_compra or 0) * p.quantidade for p in Produto.query.all())
    baixos = Produto.query.filter(Produto.quantidade <= Produto.stock_minimo).count()
    
    botao = ""
    if is_admin():
        botao = '<form method="POST" action="/reiniciar-dashboard" style="margin-top:16px"><button class="r" onclick="return confirm(\'Reiniciar o Dashboard?\')">Reiniciar Dashboard</button></form>'
    
    return render_template_string(T, content=f'''
    <h2>Dashboard</h2>
    <div class="grid">
        <div class="stat venda">Vendas (desde último reset)<b>Kz {int(bruto)}</b><div style="font-size:.75rem;color:#64748b">Ontem: Kz {int(bruto_ontem)}</div></div>
        <div class="stat lucro">Lucro<b>Kz {int(lucro)}</b></div>
        <div class="stat">Nº Vendas<b>{len(vendas)}</b></div>
        <div class="stat compras">Compras<b>Kz {int(total_compras)}</b></div>
        <div class="stat">Restos<b>Kz {int(total_restos)}</b></div>
        <div class="stat">Caixa<b>Kz {int(cv)}</b></div>
        <div class="stat stock">Valor em Stock<b>Kz {int(valor_stock)}</b></div>
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

@app.route("/resumo")
def resumo():
    if "user_id" not in session: return redirect("/login")
    hoje = date.today()
    vendas = Venda.query.filter(db.func.date(Venda.data)==hoje).all()
    bruto = sum(v.valor_total for v in vendas)
    lucro = sum(v.lucro or 0 for v in vendas)
    compras = sum(c.valor for c in Compra.query.filter(db.func.date(Compra.data)==hoje).all())
    restos = sum(r.valor for r in Resto.query.filter(db.func.date(Resto.data)==hoje).all())
    return render_template_string(T, content=f'''
    <div class="card"><h2>Resumo do Dia</h2>
    <p>Total Vendido: <b>Kz {int(bruto)}</b></p>
    <p>Lucro: <b>Kz {int(lucro)}</b></p>
    <p>Nº Vendas: <b>{len(vendas)}</b></p>
    <p>Compras: <b>Kz {int(compras)}</b></p>
    <p>Restos: <b>Kz {int(restos)}</b></p>
    </div>
    ''')

@app.route("/ranking")
def ranking():
    if "user_id" not in session: return redirect("/login")
    periodo = request.args.get("periodo", "hoje")
    if periodo == "ontem":
        d = date.today() - timedelta(days=1)
        vendas = Venda.query.filter(db.func.date(Venda.data)==d)
        titulo = "Ranking de Ontem"
    elif periodo == "semana":
        inicio = date.today() - timedelta(days=6)
        vendas = Venda.query.filter(Venda.data >= inicio)
        titulo = "Ranking da Semana"
    elif periodo == "mes":
        inicio = date.today().replace(day=1)
        vendas = Venda.query.filter(Venda.data >= inicio)
        titulo = "Ranking do Mês"
    else:
        vendas = Venda.query.filter(db.func.date(Venda.data)==date.today())
        titulo = "Ranking de Hoje"
    
    vendas = vendas.all()
    por_produto = {}
    for v in vendas:
        nome = v.produto.nome
        if nome not in por_produto:
            por_produto[nome] = {"qtd": 0, "valor": 0}
        por_produto[nome]["qtd"] += v.quantidade
        por_produto[nome]["valor"] += v.valor_total
    ranking = sorted(por_produto.items(), key=lambda x: x[1]["valor"], reverse=True)
    linhas = "".join(f"<tr><td style='font-weight:600;color:#1e40af'>{i+1}</td><td>{n}</td><td>{d['qtd']}</td><td style='font-weight:600'>Kz {int(d['valor'])}</td></tr>" for i,(n,d) in enumerate(ranking))
    filtros = '''
    <div style="margin-bottom:14px;display:flex;gap:8px;flex-wrap:wrap">
        <a href="/ranking?periodo=hoje" class="btn">Hoje</a>
        <a href="/ranking?periodo=ontem" class="btn">Ontem</a>
        <a href="/ranking?periodo=semana" class="btn">Semana</a>
        <a href="/ranking?periodo=mes" class="btn">Mês</a>
    </div>
    '''
    return render_template_string(T, content=f'<div class="card"><h2>{titulo}</h2>{filtros}<table><tr><th>#</th><th>Produto</th><th>Qtd</th><th>Valor</th></tr>{linhas}</table></div>')

@app.route("/hoje")
def hoje():
    if "user_id" not in session: return redirect("/login")
    vendas = Venda.query.filter(db.func.date(Venda.data)==date.today()).all()
    bruto = sum(v.valor_total for v in vendas)
    lucro = sum(v.lucro or 0 for v in vendas)
    linhas = "".join(f"<tr><td>{v.produto.nome}</td><td>{v.quantidade}</td><td>Kz {int(v.valor_total)}</td><td>Kz {int(v.lucro or 0)}</td></tr>" for v in vendas)
    return render_template_string(T, content=f'<div class="card"><h2>Hoje</h2><p>Total: Kz {int(bruto)}</p><p>Lucro: Kz {int(lucro)}</p><form method="POST" action="/finalizar"><textarea name="nota" placeholder="Nota do dia (opcional)"></textarea><button class="o">Finalizar Dia</button></form><table><tr><th>Produto</th><th>Qtd</th><th>Valor</th><th>Lucro</th></tr>{linhas}</table></div>')

@app.route("/finalizar", methods=["POST"])
def finalizar():
    if "user_id" not in session: return redirect("/login")
    vendas = Venda.query.filter(db.func.date(Venda.data)==date.today()).all()
    bruto = sum(v.valor_total for v in vendas)
    lucro = sum(v.lucro or 0 for v in vendas)
    nota = request.form.get("nota", "")
    db.session.add(FechamentoDia(user_id=session["user_id"], data=date.today(), total_bruto=bruto, total_lucro=lucro, qtd_vendas=len(vendas), nota=nota))
    db.session.commit()
    flash("Dia finalizado.")
    return redirect("/hoje")

@app.route("/relatorio")
def relatorio():
    if "user_id" not in session: return redirect("/login")
    fs = FechamentoDia.query.order_by(FechamentoDia.data.desc()).all()
    linhas = ""
    for f in fs:
        linhas += f"<tr><td>{f.data.strftime('%d/%m/%Y')}</td><td>Kz {int(f.total_bruto or 0)}</td><td>Kz {int(f.total_lucro or 0)}</td><td>{f.qtd_vendas}</td>"
        if is_admin():
            linhas += f"<td><a href='/editar-relatorio/{f.id}' class='btn'>Editar</a> <form method='POST' action='/eliminar-relatorio/{f.id}' style='display:inline'><button class='btn btn-red' onclick=\"return confirm('Eliminar?')\">Eliminar</button></form></td>"
        linhas += "</tr>"
    reiniciar = '<form method="POST" action="/reiniciar-relatorio" style="margin-bottom:12px"><button class="r" onclick="return confirm(\'Apagar todos os relatórios?\')">Reiniciar Relatório</button></form>' if is_admin() else ""
    return render_template_string(T, content=f'<div class="card"><h2>Relatório</h2>{reiniciar}<table><tr><th>Data</th><th>Total</th><th>Lucro</th><th>Vendas</th><th></th></tr>{linhas}</table></div>')

@app.route("/editar-relatorio/<int:id>", methods=["GET","POST"])
def editar_relatorio(id):
    if not is_admin(): return redirect("/")
    f = FechamentoDia.query.get_or_404(id)
    if request.method == "POST":
        f.total_bruto = float(request.form["bruto"])
        f.total_lucro = float(request.form["lucro"])
        f.qtd_vendas = int(request.form["qtd"])
        f.nota = request.form.get("nota","")
        db.session.commit()
        return redirect("/relatorio")
    return render_template_string(T, content=f'<div class="card"><h2>Editar Relatório</h2><form method="POST"><input type="number" name="bruto" value="{f.total_bruto or 0}"><input type="number" name="lucro" value="{f.total_lucro or 0}"><input type="number" name="qtd" value="{f.qtd_vendas or 0}"><textarea name="nota">{f.nota or ""}</textarea><button>Guardar</button></form></div>')

@app.route("/eliminar-relatorio/<int:id>", methods=["POST"])
def eliminar_relatorio(id):
    if not is_admin(): return redirect("/")
    db.session.delete(FechamentoDia.query.get_or_404(id))
    db.session.commit()
    return redirect("/relatorio")

@app.route("/reiniciar-relatorio", methods=["POST"])
def reiniciar_relatorio():
    if not is_admin(): return redirect("/")
    FechamentoDia.query.delete()
    db.session.commit()
    return redirect("/relatorio")

@app.route("/produtos", methods=["GET","POST"])
def produtos():
    if "user_id" not in session: return redirect("/login")
    busca = request.args.get("busca","")
    if request.method == "POST" and is_admin():
        db.session.add(Produto(nome=request.form["nome"], preco=float(request.form["preco"]), preco_compra=float(request.form.get("preco_compra",0)), quantidade=int(request.form["quantidade"])))
        db.session.commit()
        return redirect("/produtos")
    q = Produto.query
    if busca: q = q.filter(Produto.nome.ilike("%"+busca+"%"))
    ps = q.order_by(Produto.nome).all()
    linhas = "".join(f"<tr><td>{p.nome}</td><td>Kz {int(p.preco)}</td><td>Kz {int(p.preco_compra or 0)}</td><td>{p.quantidade}</td><td><a href='/editar-produto/{p.id}' class='btn'>Editar</a></td></tr>" for p in ps)
    form = '<form method="POST"><input name="nome" placeholder="Nome" required><input type="number" name="preco" placeholder="Preço venda" required><input type="number" name="preco_compra" placeholder="Preço compra"><input type="number" name="quantidade" placeholder="Stock" required><button>Cadastrar</button></form>' if is_admin() else ""
    return render_template_string(T, content=f'<div class="card"><h2>Produtos</h2><form method="GET"><input name="busca" placeholder="Pesquisar..." value="{busca}"><button>Pesquisar</button></form>{form}<table><tr><th>Nome</th><th>Venda</th><th>Compra</th><th>Stock</th><th></th></tr>{linhas}</table></div>')

@app.route("/editar-produto/<int:id>", methods=["GET","POST"])
def editar_produto(id):
    if not is_admin(): return redirect("/")
    p = Produto.query.get_or_404(id)
    if request.method == "POST":
        p.nome = request.form["nome"]
        p.preco = float(request.form["preco"])
        p.preco_compra = float(request.form.get("preco_compra",0))
        p.quantidade = int(request.form["quantidade"])
        db.session.commit()
        return redirect("/produtos")
    return render_template_string(T, content=f'<div class="card"><h2>Editar Produto</h2><form method="POST"><input name="nome" value="{p.nome}"><input type="number" name="preco" value="{p.preco}"><input type="number" name="preco_compra" value="{p.preco_compra or 0}"><input type="number" name="quantidade" value="{p.quantidade}"><button>Guardar</button></form></div>')

@app.route("/stock")
def stock():
    if "user_id" not in session: return redirect("/login")
    ps = Produto.query.order_by(Produto.nome).all()
    linhas = ""
    for p in ps:
        btns = ""
        if is_admin():
            btns = f'''
            <form method="POST" action="/aumentar-stock/{p.id}" style="display:inline"><button class="g s">+</button></form>
            <form method="POST" action="/diminuir-stock/{p.id}" style="display:inline"><button class="r s">-</button></form>
            '''
        linhas += f"<tr><td>{p.nome}</td><td>{p.quantidade}</td><td>{btns}</td></tr>"
    return render_template_string(T, content=f'<div class="card"><h2>Stock</h2><table><tr><th>Produto</th><th>Quantidade</th><th></th></tr>{linhas}</table></div>')

@app.route("/aumentar-stock/<int:id>", methods=["POST"])
def aumentar_stock(id):
    if not is_admin(): return redirect("/")
    p = Produto.query.get_or_404(id)
    p.quantidade += 1
    db.session.commit()
    return redirect("/stock")

@app.route("/diminuir-stock/<int:id>", methods=["POST"])
def diminuir_stock(id):
    if not is_admin(): return redirect("/")
    p = Produto.query.get_or_404(id)
    if p.quantidade > 0:
        p.quantidade -= 1
        db.session.commit()
    return redirect("/stock")

@app.route("/compras", methods=["GET","POST"])
def compras():
    if "user_id" not in session: return redirect("/login")
    if request.method == "POST":
        db.session.add(Compra(user_id=session["user_id"], descricao=request.form["descricao"], valor=float(request.form["valor"])))
        db.session.commit()
        return redirect("/compras")
    items = Compra.query.order_by(Compra.data.desc()).all()
    linhas = "".join(f"<tr><td>{c.descricao}</td><td>Kz {int(c.valor)}</td><td>{c.data.strftime('%d/%m/%Y')}</td><td><a href='/editar-compra/{c.id}' class='btn'>Editar</a></td></tr>" for c in items)
    return render_template_string(T, content=f'<div class="card"><h2>Compras</h2><form method="POST"><input name="descricao" placeholder="Descrição" required><input type="number" name="valor" placeholder="Valor" required><button>Registar</button></form><table><tr><th>Descrição</th><th>Valor</th><th>Data</th><th></th></tr>{linhas}</table></div>')

@app.route("/editar-compra/<int:id>", methods=["GET","POST"])
def editar_compra(id):
    c = Compra.query.get_or_404(id)
    if request.method == "POST":
        c.descricao = request.form["descricao"]
        c.valor = float(request.form["valor"])
        db.session.commit()
        return redirect("/compras")
    return render_template_string(T, content=f'<div class="card"><h2>Editar Compra</h2><form method="POST"><input name="descricao" value="{c.descricao}"><input type="number" name="valor" value="{c.valor}"><button>Guardar</button></form></div>')

@app.route("/restos", methods=["GET","POST"])
def restos():
    if "user_id" not in session: return redirect("/login")
    if request.method == "POST":
        db.session.add(Resto(user_id=session["user_id"], descricao=request.form["descricao"], valor=float(request.form["valor"])))
        db.session.commit()
        return redirect("/restos")
    items = Resto.query.order_by(Resto.data.desc()).all()
    linhas = "".join(f"<tr><td>{r.descricao}</td><td>Kz {int(r.valor)}</td><td>{r.data.strftime('%d/%m/%Y')}</td><td><a href='/editar-resto/{r.id}' class='btn'>Editar</a></td></tr>" for r in items)
    return render_template_string(T, content=f'<div class="card"><h2>Restos</h2><form method="POST"><input name="descricao" placeholder="Descrição" required><input type="number" name="valor" placeholder="Valor" required><button>Registar</button></form><table><tr><th>Descrição</th><th>Valor</th><th>Data</th><th></th></tr>{linhas}</table></div>')

@app.route("/editar-resto/<int:id>", methods=["GET","POST"])
def editar_resto(id):
    r = Resto.query.get_or_404(id)
    if request.method == "POST":
        r.descricao = request.form["descricao"]
        r.valor = float(request.form["valor"])
        db.session.commit()
        return redirect("/restos")
    return render_template_string(T, content=f'<div class="card"><h2>Editar Resto</h2><form method="POST"><input name="descricao" value="{r.descricao}"><input type="number" name="valor" value="{r.valor}"><button>Guardar</button></form></div>')

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
    return render_template_string(T, content=f'<div class="card"><h2>Caixa</h2><p style="font-size:1.4rem;font-weight:600">Kz {int(c.valor)}</p><form method="POST"><input type="number" name="valor" value="{c.valor}"><button>Alterar</button></form></div>')

@app.route("/utilizadores")
def utilizadores():
    if not is_admin(): return redirect("/")
    users = Usuario.query.all()
    linhas = ""
    for u in users:
        linhas += f"<tr><td>{u.nome}</td><td>{u.email}</td><td>{u.tipo}</td><td>"
        linhas += f"<a href='/permissoes/{u.id}' class='btn'>Permissões</a> "
        linhas += f"<a href='/redefinir/{u.id}' class='btn btn-orange'>Redefinir Senha</a> "
        if u.tipo != "admin":
            linhas += f"<form method='POST' action='/eliminar-utilizador/{u.id}' style='display:inline'><button class='btn btn-red' onclick=\"return confirm('Eliminar este utilizador?')\">Eliminar</button></form>"
        linhas += "</td></tr>"
    return render_template_string(T, content=f'<div class="card"><h2>Utilizadores</h2><p><a href="/criar-utilizador" class="btn btn-green">Criar Utilizador</a></p><table><tr><th>Nome</th><th>Email</th><th>Tipo</th><th>Ações</th></tr>{linhas}</table></div>')

@app.route("/criar-utilizador", methods=["GET","POST"])
def criar_utilizador():
    if not is_admin(): return redirect("/")
    if request.method == "POST":
        if not Usuario.query.filter_by(email=request.form["email"]).first():
            db.session.add(Usuario(nome=request.form["nome"], email=request.form["email"], senha=generate_password_hash(request.form["senha"]), tipo="funcionario"))
            db.session.commit()
            flash("Utilizador criado")
            return redirect("/utilizadores")
        flash("Email já existe")
    return render_template_string(T, content='<div class="card"><h2>Criar Utilizador</h2><form method="POST"><input name="nome" placeholder="Nome" required><input type="email" name="email" placeholder="Email" required><input type="password" name="senha" placeholder="Senha" required><button>Criar</button></form><p style="margin-top:10px"><a href="/utilizadores" class="btn">Voltar</a></p></div>')

@app.route("/redefinir/<int:id>", methods=["GET","POST"])
def redefinir(id):
    if not is_admin(): return redirect("/")
    u = Usuario.query.get_or_404(id)
    if request.method == "POST":
        u.senha = generate_password_hash(request.form["senha"])
        db.session.commit()
        flash(f"Senha redefinida para {u.nome}")
        return redirect("/utilizadores")
    return render_template_string(T, content=f'<div class="card"><h2>Redefinir senha de {u.nome}</h2><form method="POST"><input type="password" name="senha" placeholder="Nova senha" required><button>Guardar</button></form><p style="margin-top:10px"><a href="/utilizadores" class="btn">Voltar</a></p></div>')

@app.route("/eliminar-utilizador/<int:id>", methods=["POST"])
def eliminar_utilizador(id):
    if not is_admin(): return redirect("/")
    u = Usuario.query.get_or_404(id)
    if u.tipo == "admin":
        flash("Não podes eliminar o administrador")
        return redirect("/utilizadores")
    db.session.delete(u)
    db.session.commit()
    flash("Utilizador eliminado")
    return redirect("/utilizadores")

@app.route("/permissoes/<int:id>", methods=["GET","POST"])
def permissoes(id):
    if not is_admin(): return redirect("/")
    u = Usuario.query.get_or_404(id)
    if request.method == "POST":
        u.perm_hoje = "perm_hoje" in request.form
        u.perm_relatorio = "perm_relatorio" in request.form
        u.perm_produtos = "perm_produtos" in request.form
        u.perm_stock = "perm_stock" in request.form
        u.perm_compras = "perm_compras" in request.form
        u.perm_restos = "perm_restos" in request.form
        db.session.commit()
        flash("Permissões atualizadas")
        return redirect("/utilizadores")
    checks = ""
    for p, label in [("perm_hoje","Hoje"),("perm_relatorio","Relatório"),("perm_produtos","Produtos"),("perm_stock","Stock"),("perm_compras","Compras"),("perm_restos","Restos")]:
        checked = " checked" if getattr(u, p) else ""
        checks += f'<label style="display:block;margin:8px 0"><input type="checkbox" name="{p}"{checked}> {label}</label>'
    return render_template_string(T, content=f'<div class="card"><h2>Permissões de {u.nome}</h2><form method="POST">{checks}<button>Guardar</button></form><p style="margin-top:10px"><a href="/utilizadores" class="btn">Voltar</a></p></div>')

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
    return render_template_string(T, content='<div class="card" style="max-width:380px;margin:40px auto"><h2>Entrar</h2><form method="POST"><input type="email" name="email" placeholder="Email" required><input type="password" name="senha" placeholder="Senha" required><button>Entrar</button></form></div>')

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        try:
            db.session.execute(db.text("ALTER TABLE usuario ADD COLUMN IF NOT EXISTS perm_hoje BOOLEAN DEFAULT FALSE"))
            db.session.execute(db.text("ALTER TABLE usuario ADD COLUMN IF NOT EXISTS perm_relatorio BOOLEAN DEFAULT FALSE"))
            db.session.execute(db.text("ALTER TABLE usuario ADD COLUMN IF NOT EXISTS perm_produtos BOOLEAN DEFAULT FALSE"))
            db.session.execute(db.text("ALTER TABLE usuario ADD COLUMN IF NOT EXISTS perm_stock BOOLEAN DEFAULT FALSE"))
            db.session.execute(db.text("ALTER TABLE usuario ADD COLUMN IF NOT EXISTS perm_compras BOOLEAN DEFAULT FALSE"))
            db.session.execute(db.text("ALTER TABLE usuario ADD COLUMN IF NOT EXISTS perm_restos BOOLEAN DEFAULT FALSE"))
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
    app.run(host="0.0.0.0", port=5001, debug=True)