import json
import os
import time
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recommender")
DATA_DIR = os.path.dirname(__file__)

ITEMS_FILE = os.path.join(DATA_DIR, "new_items.csv")
RATINGS_FILE = os.path.join(DATA_DIR, "ratings.csv")
GENRE_WEIGHTS_FILE = os.path.join(DATA_DIR, "genre_weights.json")

app = FastAPI(title="Music Recommender (Pearson)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Utilitários simples para carregar/salvar ---
def load_items():
    return pd.read_csv(ITEMS_FILE)


def load_ratings():
    return pd.read_csv(RATINGS_FILE)


def save_ratings(df):
    df.to_csv(RATINGS_FILE, index=False)


def load_genre_weights():
    if os.path.exists(GENRE_WEIGHTS_FILE):
        with open(GENRE_WEIGHTS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_genre_weights(d):
    with open(GENRE_WEIGHTS_FILE, "w") as f:
        json.dump(d, f)


# --- Pearson similarity (user-based) ---
def pearson_similarity_cached(u1, u2, user_item_dict, sim_cache):
    """Calcula Pearson entre u1 e u2 usando dicionários user->items.
    Usa cache para evitar recomputação."""
    key = tuple(sorted((int(u1), int(u2))))
    if key in sim_cache:
        return sim_cache[key]

    u1_items = user_item_dict.get(u1, {})
    u2_items = user_item_dict.get(u2, {})
    common = set(u1_items.keys()).intersection(u2_items.keys())
    if len(common) < 2:
        sim_cache[key] = 0.0
        return 0.0

    r1 = np.array([u1_items[i] for i in common], dtype=float)
    r2 = np.array([u2_items[i] for i in common], dtype=float)
    r1m = r1.mean()
    r2m = r2.mean()

    num = ((r1 - r1m) * (r2 - r2m)).sum()
    den = np.sqrt(((r1 - r1m) ** 2).sum() * ((r2 - r2m) ** 2).sum())
    sim = float(num / den) if den != 0 else 0.0
    sim_cache[key] = sim
    return sim


def cosine_similarity_cached(u1, u2, user_item_dict, sim_cache):
    """Calcula Similaridade de Cossenos (mais robusta para esparsidade)."""
    key = tuple(sorted((int(u1), int(u2))))
    if key in sim_cache:
        return sim_cache[key]

    u1_items = user_item_dict.get(u1, {})
    u2_items = user_item_dict.get(u2, {})
    common = set(u1_items.keys()).intersection(u2_items.keys())

    if len(common) < 1:  # Cossenos precisa de apenas 1 item em comum.
        sim_cache[key] = 0.0
        return 0.0

    r1 = np.array([u1_items[i] for i in common], dtype=float)
    r2 = np.array([u2_items[i] for i in common], dtype=float)

    dot_product = np.dot(r1, r2)
    norm_u1 = np.linalg.norm(r1)
    norm_u2 = np.linalg.norm(r2)

    if norm_u1 == 0 or norm_u2 == 0:
        sim_cache[key] = 0.0
        return 0.0

    sim = float(dot_product / (norm_u1 * norm_u2))
    sim_cache[key] = sim
    return sim


def predict_rating_opt(
    ratings_df, user_id, item_id, user_item_dict, user_means, sim_cache, item_to_ratings
):
    """Predição de nota para (user,item) usando Pearson + cache."""
    global_mean = ratings_df.rating.mean() if not ratings_df.empty else 3.0
    user_mean = user_means.get(user_id, global_mean)

    if item_id not in item_to_ratings:
        return user_mean

    num, den = 0.0, 0.0
    for other_user, other_rating in item_to_ratings[item_id]:
        if other_user == user_id:
            continue
        sim = cosine_similarity_cached(user_id, other_user, user_item_dict, sim_cache)
        if sim == 0:
            continue
        other_mean = user_means.get(other_user, global_mean)
        num += sim * (other_rating - other_mean)
        den += abs(sim)

    if den == 0:
        return user_mean
    return user_mean + (num / den)


def compute_accuracy(
    user_id: int, n_recommend: int, test_frac: float, ratings, items, genre_weights
):
    user_r = ratings[ratings.user_id == user_id]
    liked = user_r[user_r.rating >= 3]
    if len(liked) < 1:
        return {
            "user_id": user_id,
            "accuracy": None,
            "reason": "poucos itens curtidos para teste",
        }

    test = liked.sample(max(1, int(len(liked) * test_frac)))
    train = ratings.drop(test.index)

    recs = recommend_items_opt(
        user_id,
        n=n_recommend,
        ratings_df=train,
        items_df=items,
        genre_weights=genre_weights,
        max_items_to_check=5000,
    )
    rec_ids = set([r["item_id"] for r in recs])
    hits = sum(1 for iid in test.item_id if iid in rec_ids)
    acc = hits / len(recs) if len(recs) > 0 else 0.0

    return {
        "user_id": user_id,
        "hits": int(hits),
        "recommended": len(recs),
        "accuracy": acc,
    }


# --- Recomendação otimizada ---
def recommend_items_opt(
    user_id,
    n=10,
    ratings_df=None,
    items_df=None,
    genre_weights=None,
    max_items_to_check=2000,
):
    start = time.time()
    logger.info(f"recommend_items_opt start user_id={user_id} n={n}")

    if ratings_df is None:
        ratings_df = load_ratings()
    if items_df is None:
        items_df = load_items()
    if genre_weights is None:
        genre_weights = load_genre_weights()

    # Pré-computações
    user_item_dict = {}
    user_means = {}
    item_to_ratings = {}

    for uid, g in ratings_df.groupby("user_id"):
        d = dict(zip(g["item_id"], g["rating"]))
        user_item_dict[int(uid)] = d
        user_means[int(uid)] = float(g["rating"].mean())

    for iid, g in ratings_df.groupby("item_id"):
        item_to_ratings[int(iid)] = list(
            zip(g["user_id"].astype(int), g["rating"].astype(float))
        )

    rated_items = set(ratings_df[ratings_df.user_id == user_id].item_id.tolist())
    candidates = []
    sim_cache = {}

    # Cold-start: gêneros curtidos
    liked_items = ratings_df[
        (ratings_df.user_id == user_id) & (ratings_df.rating >= 4)
    ].item_id.tolist()
    liked_genres = (
        items_df[items_df.id.isin(liked_items)].genre.unique().tolist()
        if liked_items
        else []
    )

    # Amostra para acelerar

    total_items = len(items_df)
    sample_size = min(
        max_items_to_check if max_items_to_check else total_items, total_items
    )
    items_sample = items_df.sample(
        n=sample_size, random_state=int(time.time() * 1000) % 10000
    ).to_dict(orient="records")

    # Calcular predições
    for item in items_sample:
        item_id = int(item["id"])
        if item_id in rated_items:
            continue
        base_pred = predict_rating_opt(
            ratings_df,
            user_id,
            item_id,
            user_item_dict,
            user_means,
            sim_cache,
            item_to_ratings,
        )
        genre = str(item["genre"])
        weight = float(genre_weights.get(genre, 0.0))

        max_boost = 0.05  # máximo 5% de aumento
        applied_boost = min(weight, max_boost)
        score = base_pred * (1.0 + applied_boost)

        candidates.append(
            {
                "item_id": item_id,
                "title": item["title"],
                "artist": item.get("artist", ""),
                "genre": genre,
                "score": float(score),
                "base_pred": float(base_pred),
            }
        )

    candidates.sort(key=lambda x: x["score"], reverse=True)

    # Diversidade no cold-start: sempre incluir 1 item de outro gênero
    if (not any(genre_weights.values())) or (len(liked_items) <= 2):
        top = candidates[: max(0, n - 1)]
        other_pool = items_df[
            ~items_df.genre.isin(liked_genres) & ~items_df.id.isin(rated_items)
        ]
        if not other_pool.empty:
            surprise = other_pool.sample(
                n=1, random_state=int(time.time() % 10000)
            ).iloc[0]
            surprise_rec = {
                "item_id": int(surprise.id),
                "title": surprise.title,
                "artist": getattr(surprise, "artist", ""),
                "genre": str(surprise.genre),
                "score": float(0.5),
                "base_pred": float(0.5),
            }
            final = top[: n - 1] + [surprise_rec]
            elapsed = time.time() - start
            logger.info(
                f"recommend_items_opt finished user_id={user_id} time={elapsed:.3f}s (cold-start with surprise)"
            )
            return final

    elapsed = time.time() - start
    logger.info(f"recommend_items_opt finished user_id={user_id} time={elapsed:.3f}s")
    return candidates[:n]


# --- Endpoints ---
@app.get("/genres")
def get_genres():
    items = load_items()
    return sorted(items.genre.dropna().unique().tolist())


@app.post("/simulate")
def simulate_user(body: SimulateRequest):
    items = load_items()
    ratings = load_ratings()

    # new user id
    if ratings.empty:
        new_id = 1
    else:
        new_id = int(ratings.user_id.max()) + 1

    # pick até 5 músicas de cada gênero escolhido e dar nota inicial 5
    new_rows = []
    for g in body.genres:
        choices = items[items.genre == g]
        if choices.empty:
            continue
        sample = choices.sample(min(5, len(choices)), random_state=42)
        for _, row in sample.iterrows():
            new_rows.append(
                {"user_id": int(new_id), "item_id": int(row.id), "rating": 5}
            )

    if new_rows:
        ratings = pd.concat([ratings, pd.DataFrame(new_rows)], ignore_index=True)
        save_ratings(ratings)

    initial_weights = {g: 0.05 for g in body.genres}
    save_genre_weights(initial_weights)

    return {"user_id": new_id, "status": "simulated"}


@app.post("/feedback")
def feedback(fb: Feedback):
    ratings = load_ratings()
    new_row = {
        "user_id": int(fb.user_id),
        "item_id": int(fb.item_id),
        "rating": int(fb.rating),
    }
    ratings = pd.concat([ratings, pd.DataFrame([new_row])], ignore_index=True)
    save_ratings(ratings)

    # Atualizar pesos de gênero (incremental + decay)
    items = load_items()
    item_row = items[items.id == fb.item_id]

    if not item_row.empty:
        genre = str(item_row.iloc[0].genre)
        gw = load_genre_weights()

        # positiva (4–5) aumenta peso
        if fb.rating >= 4:
            delta = (fb.rating - 3) * 0.02
            gw[genre] = gw.get(genre, 0.0) * 0.9 + delta

        # negativa (1–2) reduz peso
        elif fb.rating <= 2:
            delta = (3 - fb.rating) * 0.02
            gw[genre] = gw.get(genre, 0.0) * 0.9 - delta

        # limitar intervalo [0,1]
        if gw[genre] < 0.0:
            gw[genre] = 0.0
        if gw[genre] > 1.0:
            gw[genre] = 1.0

        save_genre_weights(gw)


@app.get("/recomendar")
def recomendar(user_id: int, n: int = 10):
    items = load_items()
    ratings = load_ratings()
    gw = load_genre_weights()
    recs = recommend_items_opt(
        user_id,
        n=n,
        ratings_df=ratings,
        items_df=items,
        genre_weights=gw,
        max_items_to_check=3000,  # ajuste para performance
    )
    return {"user_id": user_id, "recommendations": recs}


@app.get("/accuracy")
def accuracy(
    user_id: int = None,
    n_recommend: int = 10,
    test_frac: float = 0.3,
    max_users: int = 20,  # limite padrão
):
    ratings = load_ratings()
    items = load_items()
    gw = load_genre_weights()

    if user_id is not None:
        return compute_accuracy(user_id, n_recommend, test_frac, ratings, items, gw)

    else:
        users = ratings.user_id.unique().tolist()

        # escolher apenas até max_users usuários (aleatórios)
        if len(users) > max_users:
            users = list(np.random.choice(users, size=max_users, replace=False))

        accs = []
        for u in users:
            res = compute_accuracy(int(u), n_recommend, test_frac, ratings, items, gw)
            if res.get("accuracy") is not None:
                accs.append(res["accuracy"])

        mean_acc = float(np.mean(accs)) if accs else None
        return {
            "mean_accuracy": mean_acc,
            "n_users_evaluated": len(accs),
            "max_users": max_users,
        }
