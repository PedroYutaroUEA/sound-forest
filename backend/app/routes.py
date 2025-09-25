import requests
from flask import Blueprint
from app.controllers.recommendation_controller import RecommendationController

# Crie um Blueprint para agrupar as rotas
api_bp = Blueprint("api", __name__)

# A IMPLEMENTAR:
# - rotas de consulta de usuarios e instrumentos
# - rotas de recomendação e geraçaõ de metricas


@api_bp.route("/initial-recommend", methods=["POST"])
def generate_first_recommendation():
    controller = RecommendationController()
    return controller.initial_recommendation()
