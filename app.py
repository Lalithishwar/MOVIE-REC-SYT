import streamlit as st
import pandas as pd
import pickle
import requests
import asyncio
import aiohttp
import os

# Set Page Configuration
st.set_page_config(page_title="Movie Recommender", layout="wide")

# Load Movie Data and Similarity Matrix (with error handling)
def load_data():
    try:
        movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
        movies = pd.DataFrame(movies_dict)
        similarity_path = os.path.abspath('similarity.pkl') # To get absolute path
        similarity = pickle.load(open(similarity_path, 'rb'))
        return movies, similarity
    except (FileNotFoundError, pickle.UnpicklingError) as e:
        st.error(f"Error loading data files: {e}")
        return None, None

# Fetch Poster and IMDb URL Asynchronously
async def fetch_poster(movie_title, session):
    api_key = '4ab1678b'
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    try:
        async with session.get(url) as response:
            data = await response.json()
            return data.get('Poster', "https://via.placeholder.com/300x450.png?text=Poster+Not+Found")
    except aiohttp.ClientError as e:
        st.error(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/300x450.png?text=Poster+Not+Found"

async def fetch_imdb_url(movie_title, session):
    api_key = 'd68b7635'
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    try:
        async with session.get(url) as response:
            data = await response.json()
            if 'imdbID' in data and data['imdbID'] != 'N/A':
                return f"https://www.imdb.com/title/{data['imdbID']}/"
            else:
                return None
    except aiohttp.ClientError as e:
        st.error(f"Error fetching IMDb URL: {e}")
        return None

async def fetch_movie_data(movie_title, session):
    poster = await fetch_poster(movie_title, session)
    imdb_url = await fetch_imdb_url(movie_title, session)
    return movie_title, poster, imdb_url

# Movie Recommendation Logic
@st.cache_data  
def recommend(movie, movies, similarity):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_movie_posters = []
        recommended_movie_urls = []

        async def get_movie_data_async(movie_list):
            async with aiohttp.ClientSession() as session:
                tasks = [asyncio.ensure_future(fetch_movie_data(movies.iloc[i[0]].title, session)) for i in movie_list]
                return await asyncio.gather(*tasks)

        results = asyncio.run(get_movie_data_async(movies_list))

        for movie_title, poster, imdb_url in results:
            recommended_movies.append(movie_title)
            recommended_movie_posters.append(poster)
            recommended_movie_urls.append(imdb_url)

        return recommended_movies, recommended_movie_posters, recommended_movie_urls
    except (KeyError, IndexError) as e:
        st.error(f"Error finding movie or calculating recommendations: {e}")
        return [], [], []

# Main App Logic
movies, similarity = load_data() 

if movies is not None and similarity is not None:
    # Add your CSS Styling here (unchanged)

    # Streamlit app layout
    st.markdown("<h1 class='title'>CINESPHERE</h1>", unsafe_allow_html=True)
    st.markdown("<h1 class='title'>🎥 Movie Recommender System 🎬</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='subtitle'>Find Your Next Favorite Movie</h2>", unsafe_allow_html=True)

    # Movie selection
    selected_movie_name = st.selectbox('Choose a movie:', movies['title'].values)

    # Recommend button and display
    if st.button('Recommend'):
        names, posters, urls = recommend(selected_movie_name, movies, similarity)
        cols = st.columns(len(names))  # Create columns dynamically

        for i, (name, poster, url) in enumerate(zip(names, posters, urls)):
            with cols[i]:
                st.markdown(f"<a href='{url}' target='_blank' style='color: white;'>{name}</a>", unsafe_allow_html=True)
                if poster:
                    st.image(poster)
                else:
                    st.text("Poster not found")  # Indicate missing poster
else:
    st.error("Error: Unable to load movie data. Please check the data files.")


