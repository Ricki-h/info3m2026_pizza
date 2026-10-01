from flask import current_app, flash, render_template, request, redirect, url_for
from models import Pizza
from utils import db, lm
from flask import Blueprint
from flask_login import login_required
import os, uuid
from werkzeug.utils import secure_filename

EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'webp'}

bp_pizza = Blueprint("pizza", __name__, template_folder='templates')

@bp_pizza.route('/get')
def get():
	pizzas = Pizza.query.all()
	return render_template('pizza_get.html', pizzas=pizzas)


@bp_pizza.route('/add', methods=['GET', 'POST'])
@login_required
def add():
	if request.method == 'GET':
		return render_template('pizza_add.html')


	arquivo = request.files.get('imagem')
	caminho_imagem = None

	if arquivo and arquivo.filename != '':
		nome = secure_filename(arquivo.filename)
		extensao = arquivo.filename.split('.')[-1].lower()
		if extensao not in EXTENSOES_PERMITIDAS:
			flash('Formato de imagem inválido. Formatos permitidos: PNG, JPG, JPEG, WEBP', 'error')
			return redirect(url_for('.add'))

		novo_nome = f"{uuid.uuid4().hex}.{extensao}"
		caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], novo_nome)
		arquivo.save(caminho)
		caminho_imagem = f"uploads/{novo_nome}"  # Caminho relativo para uso no HTML

	pizza = Pizza(
		request.form.get('sabor'),
		float(request.form.get('preco')),
		caminho_imagem
	)
	
	db.session.add(pizza)
	db.session.commit()
	return redirect(url_for('.get'))

@bp_pizza.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
	pizza = Pizza.query.get_or_404(id)
	if request.method == 'GET':
		return render_template('pizza_update.html', pizza=pizza)

	pizza.sabor = request.form.get('sabor')
	pizza.preco = float(request.form.get('preco'))
	arquivo = request.files.get('imagem')
	if arquivo and arquivo.filename != '':
		nome = secure_filename(arquivo.filename)
		extensao = nome.rsplit('.', 1)[-1].lower()
		if extensao not in EXTENSOES_PERMITIDAS:
			flash('Formato de imagem inválido. Formatos permitidos: PNG, JPG, JPEG, WEBP.', 'error')
			return redirect(url_for('.update', id=id))

		novo_nome = f"{uuid.uuid4().hex}.{extensao}"
		caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], novo_nome)
		arquivo.save(caminho)
		pizza.imagem = f"uploads/{novo_nome}"

	db.session.commit()
	return redirect(url_for('.get'))


@bp_pizza.route('/delete/<int:id>')
@login_required
def delete(id):
	pizza = Pizza.query.get_or_404(id)
	db.session.delete(pizza)
	db.session.commit()
	return redirect(url_for('.get'))