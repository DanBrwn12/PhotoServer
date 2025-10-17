import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from models import db, User
import config

# Создаём приложение
app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

# Инициализация базы и добавление админа
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username=config.ADMIN_USERNAME).first():
        admin = User(username=config.ADMIN_USERNAME)
        admin.set_password(config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()


# -------- Авторизация -------- #
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user"] = username
            return redirect(url_for("index"))
        else:
            return "Неверный логин или пароль"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# -------- Главная страница -------- #
@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    years = [f for f in os.listdir(config.PHOTOS_PATH)
             if os.path.isdir(os.path.join(config.PHOTOS_PATH, f))]

    data = []
    for year in years:
        year_path = os.path.join(config.PHOTOS_PATH, year)
        all_photos = []
        for root, dirs, files in os.walk(year_path):
            for file in files:
                if file.lower().endswith(("jpg", "jpeg", "png")):
                    all_photos.append(os.path.relpath(os.path.join(root, file), config.PHOTOS_PATH))
        cover = random.choice(all_photos) if all_photos else None
        data.append((year, cover))
    return render_template("index.html", years=data)


# -------- Создание/удаление годов -------- #
@app.route("/add_year", methods=["POST"])
def add_year():
    if "user" not in session:
        return redirect(url_for("login"))

    year_name = request.form["year_name"].strip()
    if year_name:
        year_path = os.path.join(config.PHOTOS_PATH, year_name)
        os.makedirs(year_path, exist_ok=True)
    return redirect(url_for("index"))


@app.route("/delete_year/<year>", methods=["POST"])
def delete_year(year):
    if "user" not in session:
        return redirect(url_for("login"))

    year_path = os.path.join(config.PHOTOS_PATH, year)
    if os.path.exists(year_path):
        import shutil
        shutil.rmtree(year_path)
    return redirect(url_for("index"))


# -------- Страница года -------- #
@app.route("/year/<year>")
def year_view(year):
    if "user" not in session:
        return redirect(url_for("login"))

    year_path = os.path.join(config.PHOTOS_PATH, year)
    if not os.path.exists(year_path):
        return "Такого года нет"

    albums = [f for f in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, f))]
    data = []
    for album in albums:
        album_path = os.path.join(year_path, album)
        photos = [f for f in os.listdir(album_path) if f.lower().endswith(("jpg", "jpeg", "png"))]
        cover = random.choice(photos) if photos else None
        data.append((album, cover))
    return render_template("year.html", year=year, albums=data)


# -------- Создание/удаление альбомов -------- #
@app.route("/year/<year>/add_album", methods=["POST"])
def add_album(year):
    if "user" not in session:
        return redirect(url_for("login"))

    album_name = request.form["album_name"].strip()
    if album_name:
        album_path = os.path.join(config.PHOTOS_PATH, year, album_name)
        os.makedirs(album_path, exist_ok=True)
    return redirect(url_for("year_view", year=year))


@app.route("/year/<year>/delete_album/<album>", methods=["POST"])
def delete_album(year, album):
    if "user" not in session:
        return redirect(url_for("login"))

    album_path = os.path.join(config.PHOTOS_PATH, year, album)
    if os.path.exists(album_path):
        import shutil
        shutil.rmtree(album_path)
    return redirect(url_for("year_view", year=year))


# -------- Страница альбома -------- #
@app.route("/year/<year>/<album>")
def album_view(year, album):
    if "user" not in session:
        return redirect(url_for("login"))

    album_path = os.path.join(config.PHOTOS_PATH, year, album)
    if not os.path.exists(album_path):
        return "Такой альбом не найден"

    photos = [f for f in os.listdir(album_path) if f.lower().endswith(("jpg", "jpeg", "png"))]
    return render_template("album.html", year=year, album=album, photos=photos)


# -------- Отдача фото -------- #
@app.route("/photo/<path:filename>")
def photo(filename):
    return send_from_directory(config.PHOTOS_PATH, filename)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")