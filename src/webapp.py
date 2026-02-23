"""Aplicação web do sistema financeiro com módulo BI."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from bi import carregar_dashboard_99food, importar_arquivos_99food
from database import init_db


def create_app() -> Flask:
    app = Flask(__name__)

    init_db()

    @app.get("/")
    def home() -> str:
        return render_template("home.html")

    @app.get("/bi/99food")
    def bi_99food_page() -> str:
        dashboard = carregar_dashboard_99food()
        return render_template("bi_99food.html", dashboard=dashboard)

    @app.post("/bi/99food/upload")
    def bi_99food_upload():
        arquivos = request.files.getlist("arquivos")
        payload = [(arquivo.filename, arquivo.read()) for arquivo in arquivos if arquivo.filename]
        try:
            resultado = importar_arquivos_99food(payload)
            return jsonify({"status": "ok", "resultado": resultado})
        except Exception as exc:
            return jsonify({"status": "erro", "mensagem": str(exc)}), 400

    @app.get("/bi/99food/dashboard")
    def bi_99food_dashboard():
        data_inicial = request.args.get("data_inicial")
        data_final = request.args.get("data_final")
        produto = request.args.get("produto")
        return jsonify(carregar_dashboard_99food(data_inicial, data_final, produto))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
