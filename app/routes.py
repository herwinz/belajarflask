from app import app, response
from app.controller import DosenController
from app.controller import UserController
from flask import request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt,
    create_access_token,
    create_refresh_token
)


@app.route('/')
def index():
    return 'Hello Flask App'


# ========================= DOSEN ROUTES =========================

@app.route('/api/dosen/page')
def paginations():
    return DosenController.paginate()


@app.route('/dosen', methods=['GET', 'POST'])
@jwt_required()  # optional: hanya aktifkan kalau kamu ingin aman
def dosens():
    if request.method == 'GET':
        return DosenController.index()
    else:
        return DosenController.save()


@app.route('/dosen/<id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def dosensDetail(id):
    if request.method == 'GET':
        return DosenController.detail(id)
    elif request.method == 'PUT':
        return DosenController.ubah(id)
    elif request.method == 'DELETE':
        return DosenController.hapus(id)


# ========================= AUTH & USER =========================

@app.route('/createadmin', methods=['POST'])
def admins():
    return UserController.buatAdmin()


@app.route('/login', methods=['POST'])
def logins():
    return UserController.login()


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    new_token = create_access_token(identity=identity)
    return response.success({"access_token": new_token}, "Token refreshed")


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    try:
        current_user_id = get_jwt_identity()
        jwt_payload = get_jwt()  # if you use additional_claims

        return response.success({
            "user_id": current_user_id,
            # "email": jwt_payload.get("email"),  # if added
        }, 'Token valid')
    except Exception as e:
        print("❌ ERROR di /protected:", e)
        return response.badRequest([], str(e))


# ========================= FILE UPLOAD =========================

@app.route('/file-upload', methods=['POST'])
def uploads():
    return UserController.upload()