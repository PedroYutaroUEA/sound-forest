from flask import jsonify, request
from ..services.recommendation_service import RecommendationService


class RecommendationController:
    def __init__(self):
        self.recommender = RecommendationService()

    def initial_recommendation(self):
        data = request.get_json()
        genres = data.get("genres", [])

        if not genres:
            return jsonify({"error": "Nenhum gênero fornecido."}), 400
        recommendations = self.recommender.first_recommendation(genres)
        return jsonify(recommendations), 200
