"""Funções e views que dão suporte ao LOGIN dos endpoints de API

Funções e classes para gerenciar login e tokens (Flask jwt)

"""
from flask import Blueprint
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_raw_jwt
)

from ajna_commons.flask.log import logger
from ajna_commons.flask.login import authenticate
from ajna_commons.flask.user import DBUser
from ajna_commons.utils.sanitiza import mongo_sanitizar


def configure(app: Flask):
    """Insere as views de login e logout na api.

    Para utilizar, importar modulo api_login e chamar configure(app)
    em uma aplicação Flask.

    """
    api = Blueprint('loginapi', __name__)
    app.config['JWT_SECRET_KEY'] = app.secret_key
    app.config['JWT_BLACKLIST_ENABLED'] = True
    jwt = JWTManager(app)

    blacklist = set()

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return jti in blacklist

    @api.route('/api/login', methods=['POST'])
    def login():
        """Endpoint para efetuar login (obter token)."""
        if not request.json or not request.is_json:
            return jsonify({"msg": "JSON requerido"}), 400

        username = request.json.get('username', None)
        password = request.json.get('password', None)
        if not username:
            return jsonify({"msg": "Parametro username requerido"}), 400
        if not password:
            return jsonify({"msg": "Parametro password requerido"}), 400

        user = verify_password(username, password)
        if user is None:
            return jsonify({"msg": "username ou password invalidos"}), 401
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    @api.route('/api/login_certificado')
    def login_certificado():
        """Endpoint para efetuar login (obter token).

        Este endpoint apenas verifica se CN do Certificado (CPF)
        está no banco de dados.
        Portanto DEVE estar protegido no Servidor Apache

        """
        s_dn = request.environ.get('HTTP_SSL_CLIENT_S_DN')
        if s_dn:
            name = dict([x.split('=') for x in s_dn.split('/')[1:]])['CN']
            user = DBUser.get(name)
            if not user:
                return jsonify({'msg': 'Usuário não cadastrado'}), 403
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token), 200
        return jsonify({'msg': 'Certificado inválido ou não fornecido'}), 401

    @api.route('/api/logout', methods=['DELETE'])
    @jwt_required
    def logout():
        jti = get_raw_jwt()['jti']
        blacklist.add(jti)
        current_user = get_jwt_identity()
        logger.info('Usuário %s efetuou logout' % current_user)
        return jsonify({"msg": "Logout efetuado"}), 200

    @api.route('/api/test')
    @jwt_required
    def get_resource():
        current_user = get_jwt_identity()
        return jsonify({'user.id': current_user}), 200

    @api.after_request
    def after_request_callback(response):
        path = None
        method = None
        ip = None
        current_user = None
        try:
            path = request.path
            method = request.method
            ip = request.environ.get('HTTP_X_REAL_IP',
                                     request.remote_addr)
            try:
                current_user = get_jwt_identity()
            except:
                current_user = 'no user'
        finally:
            app.logger.info('API LOG url: %s %s IP:%s User: %s' %
                            (path, method, ip, current_user))
            return response

    def verify_password(username, password):
        username = mongo_sanitizar(username)
        # Não aceitar senha vazia!!
        password = mongo_sanitizar(password)
        user = authenticate(username, password)
        if user is not None:
            logger.info('Usuário %s %s autenticou via API' %
                        (user.id, user.name))
        return user

    app.register_blueprint(api)
    return api
