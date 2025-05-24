from app.model.user import User
from app.model.gambar import Gambar
from flask import request
import os
from app import response, app, db, uploadconfig
import uuid
from werkzeug.utils import secure_filename

from datetime import timedelta
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)


# ==============================
# Upload File (Gambar)
# ==============================
def upload():
    try:
        judul = request.form.get('judul')

        if 'file' not in request.files:
            return response.badRequest([], 'File tidak tersedia')

        file = request.files['file']

        if file.filename == '':
            return response.badRequest([], 'File tidak tersedia')

        if file and uploadconfig.allowed_file(file.filename):
            uid = uuid.uuid4()
            filename = secure_filename(file.filename)
            renamefile = "Flask-" + str(uid) + filename

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], renamefile))

            uploads = Gambar(judul=judul, pathname=renamefile)
            db.session.add(uploads)
            db.session.commit()

            return response.success(
                {
                    'judul': judul,
                    'pathname': renamefile
                },
                "Sukses mengupload file"
            )
        else:
            return response.badRequest([], 'File tidak diizinkan')

    except Exception as e:
        print("❌ ERROR upload():", e)
        return response.badRequest([], str(e))


# ==============================
# Buat Admin
# ==============================
def buatAdmin():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        level = 1

        users = User(name=name, email=email, level=level)
        users.setPassword(password)
        db.session.add(users)
        db.session.commit()

        return response.success('', 'Sukses Menambahkan Data Admin!')
    except Exception as e:
        print("❌ ERROR buatAdmin():", e)
        return response.badRequest([], str(e))


# ==============================
# Serialize User
# ==============================
def singleObject(data):
    return {
        'id': data.id,
        'name': data.name,
        'email': data.email,
        'level': data.level
    }


# ==============================
# Login
# ==============================
def login():
    try:
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return response.badRequest([], 'Email dan password harus diisi')

        user = User.query.filter_by(email=email).first()

        if not user:
            return response.badRequest([], 'Email tidak terdaftar')

        if not user.checkPassword(password):
            return response.badRequest([], 'Kombinasi password salah')

        expires = timedelta(days=7)
        refresh_expires = timedelta(days=7)

        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=expires
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            expires_delta=refresh_expires
        )

        return response.success({
            "data": singleObject(user),
            "access_token": access_token,
            "refresh_token": refresh_token
        }, "Sukses Login!")

    except Exception as e:
        print("❌ ERROR login():", e)
        return response.badRequest([], str(e))