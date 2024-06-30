import streamlit as st
import pandas as pd
import pickle
import requests
from concurrent.futures import ThreadPoolExecutor

# Set the page configuration
st.set_page_config(page_title="Movie Recommender", layout="wide")


@st.cache
def fetch_poster(movie_title):
    """Fetches poster image URL for a given movie title from OMDb."""
    api_key = '4ab1678b'
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if 'Poster' in data and data['Poster'] != 'N/A':
            return data['Poster']
        else:
            return None  # Return None if poster couldn't be fetched
    else:
        return None  # Return None if poster couldn't be fetched


@st.cache
def fetch_imdb_url(movie_title):
    """Fetches IMDb URL for a given movie title from OMDb."""
    api_key = 'd68b7635'
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if 'imdbID' in data and data['imdbID'] != 'N/A':
            return f"https://www.imdb.com/title/{data['imdbID']}/"
        else:
            return None  # Return None if IMDb URL couldn't be fetched
    else:
        return None  # Return None if IMDb URL couldn't be fetched


def recommend(movie):
    """Recommends movies based on similarity to the input movie."""
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]  # Top 5 similar movies

    recommended_movies = []
    recommended_movie_posters = []
    recommended_movie_urls = []

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda i: fetch_movie_data(movies.iloc[i[0]].title), movies_list))

    for result in results:
        movie_title, poster, imdb_url = result
        recommended_movies.append(movie_title)
        recommended_movie_posters.append(poster)
        recommended_movie_urls.append(imdb_url)

    return recommended_movies, recommended_movie_posters, recommended_movie_urls


def fetch_movie_data(movie_title):
    """Fetches movie data (poster and IMDb URL) for a given movie title."""
    poster = fetch_poster(movie_title)
    imdb_url = fetch_imdb_url(movie_title)
    return movie_title, poster, imdb_url


# Load movie data and similarity matrix from pickle files
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))


# Add custom CSS for styling
st.markdown("""
    <style>
        body {
            background: url('https://cdn.nimbusthemes.com/2017/09/09233341/Free-Nature-Backgrounds-Seaport-During-Daytime-by-Pexels.jpeg') no-repeat center center fixed;
            background-size: cover;
            color: #FFFFFF;
        }

        .stApp {
            background: rgba(0, 0, 0, 0.5);  /* Ensure background of app is semi-transparent */
        }

        .title {
            font-size: 2.5em;
            text-align: center;
        }

        .subtitle {
            text-align: center;
        }

        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            transition-duration: 0.4s;
            cursor: pointer;
        }

        .stButton>button:hover {
            background-color: white;
            color: black;
            border: 2px solid #4CAF50;
        }

        .stSelectbox>div {
            background-color: rgba(0, 0, 0, 0.6);
            border-radius: 5px;
            padding: 10px;
        }

        .stImage {
            border-radius: 10px;
            margin-bottom: 10px;
        }

        .stMarkdown>p {
            font-size: 18px;
            font-weight: bold;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit app layout
st.markdown("<h1 class='title'>CINESPHERE</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='title'>🎥 Movie Recommender System 🎬</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='subtitle'>Find Your Next Favorite Movie</h2>", unsafe_allow_html=True)

# Movie selection
selected_movie_name = st.selectbox('Choose a movie:', movies['title'].values)

# Recommend button and display
if st.button('Recommend'):
    names, posters, urls = recommend(selected_movie_name)
    cols = st.columns(len(names))  # Create columns dynamically

    for i, (name, poster, url) in enumerate(zip(names, posters, urls)):
        with cols[i]:
            st.markdown(f"<a href='{url}' target='_blank' style='color: white;'>{name}</a>", unsafe_allow_html=True)
            if poster:
                st.image(poster)
            else:
                st.text("Poster not found")  # Indicate missing poster


