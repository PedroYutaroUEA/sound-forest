from .controllers import (
    AccuracyController,
    UserSimulationController,
    FeedbackController,
    QueryController,
    RecommendationController,
)
from .models.feedback import Feedback
from .models.simulate_request import SimulateRequest
from fastapi import APIRouter


router = APIRouter()


@router.get("/genres")
def get_genres():
    """Retorna todos os gêneros disponíveis no catálogo."""
    query_controller = QueryController()
    return query_controller.get_all_genres()


@router.get("/users")
def get_all_user_ids():
    """Retorna todos os IDs de usuários para o frontend."""
    query_controller = QueryController()
    return query_controller.get_all_users_ids()


@router.post("/simulate")
def simulate_user(body: SimulateRequest):
    """Simula um novo usuário (LÓGICA COPIADA DO SEU CÓDIGO ORIGINAL)."""
    user_simulation_controller = UserSimulationController()
    return user_simulation_controller.get_first_recommendation(
        body=body, random_state=42
    )


@router.post("/feedback")
def feedback(fb: Feedback):
    """Recebe o rating e atualiza os CSVs de ratings e pesos (LÓGICA COPIADA)."""
    feedback_controller = FeedbackController()
    feedback_controller.handle_feedback(fb=fb)


@router.get("/recomendar")
def recomendar(user_id: int, n: int = 10, metric: str = None):
    """Gera e retorna a lista de recomendações (Chama o Service)."""
    recommendation_controller = RecommendationController(
        user_id=user_id, n=n, metric=metric
    )
    return recommendation_controller.recommend()


@router.get("/accuracy")
def accuracy(
    metric: str = None,
    user_id: int = None,
    n_recommend: int = 10,
    test_frac: float = 0.3,
    max_users: int = 20,
):
    """Calcula e retorna a' acurácia (média ou por usuário) usando o Service."""
    accuracy_controller = AccuracyController(metric=metric)
    return accuracy_controller.get_accuracy(
        user_id=user_id,
        n_recommend=n_recommend,
        test_frac=test_frac,
        max_users=max_users,
    )
