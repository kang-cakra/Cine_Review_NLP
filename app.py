import os
import random
import joblib
import re
from flask import Flask, render_template, request, jsonify

# ── App Setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-fallback-key")

# ── Load NLP Models ───────────────────────────────────────────────────────────
# Models are stored in models/ inside the project root (required for Vercel)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

sentiment_model = joblib.load(os.path.join(MODEL_DIR, "sentiment_model.pkl"))
tfidf_vectorizer = joblib.load(os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"))

# ── Movie Data Bank (30 films) ────────────────────────────────────────────────
MOVIES = [
    {
        "id": 1,
        "title": "The Shawshank Redemption",
        "year": 1994,
        "genre": "Drama",
        "rating": 9.3,
        "poster": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
        "synopsis": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency. A story of hope that endures even in the darkest of places.",
        "cast": ["Tim Robbins", "Morgan Freeman", "Bob Gunton"],
    },
    {
        "id": 2,
        "title": "The Godfather",
        "year": 1972,
        "genre": "Crime / Drama",
        "rating": 9.2,
        "poster": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsLori8pJxiP.jpg",
        "synopsis": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son, leading to an epic saga of family, power, and betrayal.",
        "cast": ["Marlon Brando", "Al Pacino", "James Caan"],
    },
    {
        "id": 3,
        "title": "The Dark Knight",
        "year": 2008,
        "genre": "Action / Crime",
        "rating": 9.0,
        "poster": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "synopsis": "When the menace known as the Joker wreaks havoc and chaos on Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"],
    },
    {
        "id": 4,
        "title": "Schindler's List",
        "year": 1993,
        "genre": "Biography / Drama",
        "rating": 9.0,
        "poster": "https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg",
        "synopsis": "In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce after witnessing their persecution by the Nazis.",
        "cast": ["Liam Neeson", "Ralph Fiennes", "Ben Kingsley"],
    },
    {
        "id": 5,
        "title": "Pulp Fiction",
        "year": 1994,
        "genre": "Crime / Drama",
        "rating": 8.9,
        "poster": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
        "synopsis": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption in this nonlinear masterpiece.",
        "cast": ["John Travolta", "Uma Thurman", "Samuel L. Jackson"],
    },
    {
        "id": 6,
        "title": "Forrest Gump",
        "year": 1994,
        "genre": "Drama / Romance",
        "rating": 8.8,
        "poster": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
        "synopsis": "The presidencies of Kennedy and Johnson, the Vietnam War, and other historical events unfold through the perspective of an Alabama man with an extraordinary journey and a pure heart.",
        "cast": ["Tom Hanks", "Robin Wright", "Gary Sinise"],
    },
    {
        "id": 7,
        "title": "Inception",
        "year": 2010,
        "genre": "Action / Sci-Fi",
        "rating": 8.8,
        "poster": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
        "synopsis": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O. in this mind-bending thriller.",
        "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"],
    },
    {
        "id": 8,
        "title": "The Matrix",
        "year": 1999,
        "genre": "Action / Sci-Fi",
        "rating": 8.7,
        "poster": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
        "synopsis": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers in this groundbreaking sci-fi action film.",
        "cast": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"],
    },
    {
        "id": 9,
        "title": "Goodfellas",
        "year": 1990,
        "genre": "Biography / Crime",
        "rating": 8.7,
        "poster": "https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg",
        "synopsis": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners Jimmy Conway and Tommy DeVito in the Italian-American mob.",
        "cast": ["Ray Liotta", "Robert De Niro", "Joe Pesci"],
    },
    {
        "id": 10,
        "title": "Fight Club",
        "year": 1999,
        "genre": "Drama / Thriller",
        "rating": 8.8,
        "poster": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
        "synopsis": "An insomniac office worker and a devil-may-care soap maker form an underground fight club that evolves into something much, much more in this provocative psychological drama.",
        "cast": ["Brad Pitt", "Edward Norton", "Helena Bonham Carter"],
    },
    {
        "id": 11,
        "title": "Interstellar",
        "year": 2014,
        "genre": "Adventure / Sci-Fi",
        "rating": 8.7,
        "poster": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "synopsis": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival as Earth's resources are depleted in this epic Christopher Nolan film.",
        "cast": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"],
    },
    {
        "id": 12,
        "title": "The Silence of the Lambs",
        "year": 1991,
        "genre": "Crime / Thriller",
        "rating": 8.6,
        "poster": "https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg",
        "synopsis": "A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer, a madman who skins his victims.",
        "cast": ["Jodie Foster", "Anthony Hopkins", "Scott Glenn"],
    },
    {
        "id": 13,
        "title": "Saving Private Ryan",
        "year": 1998,
        "genre": "Drama / War",
        "rating": 8.6,
        "poster": "https://image.tmdb.org/t/p/w500/uqx37oZhL0NTnlBW6QZkVbQLgkc.jpg",
        "synopsis": "Following the Normandy Landings, a group of U.S. soldiers go behind enemy lines to retrieve a paratrooper whose brothers have been killed in action in this visceral war film.",
        "cast": ["Tom Hanks", "Tom Sizemore", "Matt Damon"],
    },
    {
        "id": 14,
        "title": "The Lord of the Rings: The Return of the King",
        "year": 2003,
        "genre": "Adventure / Fantasy",
        "rating": 9.0,
        "poster": "https://image.tmdb.org/t/p/w500/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg",
        "synopsis": "Gandalf and Aragorn lead the World of Men against Sauron's army to draw his gaze from Frodo and Sam as they approach Mount Doom with the One Ring.",
        "cast": ["Elijah Wood", "Viggo Mortensen", "Ian McKellen"],
    },
    {
        "id": 15,
        "title": "Avengers: Endgame",
        "year": 2019,
        "genre": "Action / Adventure",
        "rating": 8.4,
        "poster": "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg",
        "synopsis": "After the devastating events of Infinity War, the Avengers assemble once more to reverse Thanos's actions and restore balance to the universe in this epic conclusion.",
        "cast": ["Robert Downey Jr.", "Chris Evans", "Mark Ruffalo"],
    },
    {
        "id": 16,
        "title": "Parasite",
        "year": 2019,
        "genre": "Comedy / Drama / Thriller",
        "rating": 8.5,
        "poster": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
        "synopsis": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan in this Oscar-winning South Korean masterpiece.",
        "cast": ["Song Kang-ho", "Lee Sun-kyun", "Cho Yeo-jeong"],
    },
    {
        "id": 17,
        "title": "Joker",
        "year": 2019,
        "genre": "Crime / Drama / Thriller",
        "rating": 8.4,
        "poster": "https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg",
        "synopsis": "In Gotham City, mentally troubled comedian Arthur Fleck is disregarded and mistreated by society. He then embarks on a downward spiral of revolution and bloody crime.",
        "cast": ["Joaquin Phoenix", "Robert De Niro", "Zazie Beetz"],
    },
    {
        "id": 18,
        "title": "Whiplash",
        "year": 2014,
        "genre": "Drama / Music",
        "rating": 8.5,
        "poster": "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg",
        "synopsis": "A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an instructor who will stop at nothing to realize a student's potential.",
        "cast": ["Miles Teller", "J.K. Simmons", "Paul Reiser"],
    },
    {
        "id": 19,
        "title": "La La Land",
        "year": 2016,
        "genre": "Drama / Musical / Romance",
        "rating": 8.0,
        "poster": "https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg",
        "synopsis": "While navigating their careers in Los Angeles, a pianist and an actress fall in love while attempting to reconcile their aspirations for the future in this enchanting musical.",
        "cast": ["Ryan Gosling", "Emma Stone", "John Legend"],
    },
    {
        "id": 20,
        "title": "Spirited Away",
        "year": 2001,
        "genre": "Animation / Adventure / Family",
        "rating": 8.6,
        "poster": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
        "synopsis": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits, where humans are changed into beasts.",
        "cast": ["Daveigh Chase", "Suzanne Pleshette", "Miyu Irino"],
    },
    {
        "id": 21,
        "title": "The Lion King",
        "year": 1994,
        "genre": "Animation / Adventure / Drama",
        "rating": 8.5,
        "poster": "https://image.tmdb.org/t/p/w500/sKCr78MXSLixwmZ8DyJLrpMsd15.jpg",
        "synopsis": "Lion prince Simba and his father are targeted by his bitter uncle, who wants to ascend the throne himself in this beloved Disney animated classic.",
        "cast": ["Matthew Broderick", "Jeremy Irons", "James Earl Jones"],
    },
    {
        "id": 22,
        "title": "Titanic",
        "year": 1997,
        "genre": "Drama / Romance",
        "rating": 7.9,
        "poster": "https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg",
        "synopsis": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic in James Cameron's epic romantic disaster film.",
        "cast": ["Leonardo DiCaprio", "Kate Winslet", "Billy Zane"],
    },
    {
        "id": 23,
        "title": "Gladiator",
        "year": 2000,
        "genre": "Action / Adventure / Drama",
        "rating": 8.5,
        "poster": "https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg",
        "synopsis": "A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery in this Oscar-winning historical epic.",
        "cast": ["Russell Crowe", "Joaquin Phoenix", "Connie Nielsen"],
    },
    {
        "id": 24,
        "title": "The Departed",
        "year": 2006,
        "genre": "Crime / Drama / Thriller",
        "rating": 8.5,
        "poster": "https://image.tmdb.org/t/p/w500/nT97ifVT2J1yMQmeq20Qblg61T.jpg",
        "synopsis": "An undercover cop and a mole in the police attempt to identify each other while simultaneously each tries to figure out the identity of the other's criminal organization.",
        "cast": ["Leonardo DiCaprio", "Matt Damon", "Jack Nicholson"],
    },
    {
        "id": 25,
        "title": "No Country for Old Men",
        "year": 2007,
        "genre": "Crime / Drama / Thriller",
        "rating": 8.2,
        "poster": "https://image.tmdb.org/t/p/w500/6d5XOczc0Xw7RCActN9rAm6Kqah.jpg",
        "synopsis": "Violence and mayhem ensue after a hunter stumbles upon a drug deal gone wrong and more than two million dollars in cash near the Rio Grande in this Coen Brothers masterwork.",
        "cast": ["Tommy Lee Jones", "Javier Bardem", "Josh Brolin"],
    },
    {
        "id": 26,
        "title": "Mad Max: Fury Road",
        "year": 2015,
        "genre": "Action / Adventure / Sci-Fi",
        "rating": 8.1,
        "poster": "https://image.tmdb.org/t/p/w500/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg",
        "synopsis": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners, a psychotic worshiper, and a drifter named Max.",
        "cast": ["Tom Hardy", "Charlize Theron", "Nicholas Hoult"],
    },
    {
        "id": 27,
        "title": "Everything Everywhere All at Once",
        "year": 2022,
        "genre": "Action / Adventure / Comedy",
        "rating": 7.8,
        "poster": "https://image.tmdb.org/t/p/w500/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg",
        "synopsis": "A middle-aged Chinese immigrant is swept up into an insane adventure in which she alone can save existence by exploring other universes and connecting with the lives she could have led.",
        "cast": ["Michelle Yeoh", "Stephanie Hsu", "Ke Huy Quan"],
    },
    {
        "id": 28,
        "title": "Oppenheimer",
        "year": 2023,
        "genre": "Biography / Drama / History",
        "rating": 8.3,
        "poster": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
        "synopsis": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II, brought to life by Christopher Nolan.",
        "cast": ["Cillian Murphy", "Emily Blunt", "Robert Downey Jr."],
    },
    {
        "id": 29,
        "title": "Dune: Part Two",
        "year": 2024,
        "genre": "Adventure / Drama / Sci-Fi",
        "rating": 8.5,
        "poster": "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
        "synopsis": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family, facing a choice between love and the fate of the universe.",
        "cast": ["Timothée Chalamet", "Zendaya", "Rebecca Ferguson"],
    },
    {
        "id": 30,
        "title": "Spider-Man: Into the Spider-Verse",
        "year": 2018,
        "genre": "Animation / Action / Adventure",
        "rating": 8.4,
        "poster": "https://image.tmdb.org/t/p/w500/iiZZdoQBEYBv6id8MChcYIuLQZa.jpg",
        "synopsis": "Teen Miles Morales becomes the Spider-Man of his universe and must join with five spider-powered individuals from other dimensions to stop a threat for all realities.",
        "cast": ["Shameik Moore", "Jake Johnson", "Hailee Steinfeld"],
    },
]


def preprocess_text(text: str) -> str:
    """Basic text cleaning pipeline matching training preprocessing."""
    text = text.lower()
    text = re.sub(r"<[^>]+>", " ", text)          # strip HTML
    text = re.sub(r"http\S+|www\S+", " ", text)   # strip URLs
    text = re.sub(r"[^a-z\s]", " ", text)          # remove non-alpha
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    featured = random.sample(MOVIES, 5)
    return render_template("index.html", movies=featured, all_movies=MOVIES)


@app.route("/api/sentiment", methods=["POST"])
def analyze_sentiment():
    data = request.get_json(silent=True)
    if not data or "review" not in data:
        return jsonify({"error": "No review text provided."}), 400

    raw_text = data["review"].strip()
    if len(raw_text) < 5:
        return jsonify({"error": "Review text is too short."}), 400

    cleaned = preprocess_text(raw_text)
    vectorized = tfidf_vectorizer.transform([cleaned])
    prediction = sentiment_model.predict(vectorized)[0]
    proba = sentiment_model.predict_proba(vectorized)[0]

    label = "positive" if str(prediction).lower() in ("1", "positive", "pos") else "negative"
    confidence = float(max(proba)) * 100

    return jsonify({
        "sentiment": label,
        "confidence": round(confidence, 2),
        "review_length": len(raw_text.split()),
    })


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(debug=debug_mode, port=5000)
