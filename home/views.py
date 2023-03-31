from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
import requests
import json
from .models import Movie


# Create your views here.

# This view displays the home page of the website.

def home_view(request):
    return render(request, 'home.html')


# This view displays the user's dashboard, which includes trending movies from the past week

@login_required
def dashboard_view(request):
    # Make a request to the TMDB API to get the trending movies from the past week
    response = requests.get(f'https://api.themoviedb.org/3/trending/movie/week?api_key=3372059c7957b772cf7c72b570ae110f')
    # Parse the response and extract the list of trending movies
    trending_all_week_results = json.loads(response.content)['results']
    # Create a dictionary containing the trending movies to pass to the template
    context = {
        'trending_all_week_results': trending_all_week_results
    }
    # Render the dashboard template with the trending movies included
    return render(request, 'dashboard.html', context)


# This view handles user registration using the built-in UserCreationForm in Django

def register(request):
    if request.method == 'POST':
        # If the form has been submitted, create a UserCreationForm with the submitted data
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # If the form is valid, save the new user and redirect to the home page
            form.save()
            return redirect('home')
    else:
        # If the form has not been submitted, create an empty UserCreationForm
        form = UserCreationForm()

    # Render the registration page with the UserCreationForm
    return render(request, 'register.html', {'form': form})



# This view displays the list of movies saved as favorites by the logged-in user

@login_required
def favorites(request):
    # Get all the movies that belong to the logged-in user
    movies = Movie.objects.filter(user=request.user)

    # Create a context dictionary containing the list of movies
    context = {
        'movies': movies
    }

    # Render the favorites page with the list of movies
    return render(request, 'favorites.html', context)




# This view deletes a movie from the user's favorites list

def delete_movie(request, movie_id):
    # Get the movie object with the specified ID, or return a 404 error if it doesn't exist
    movie = get_object_or_404(Movie, pk=movie_id)
    
    # Check if the request method is POST
    if request.method == 'POST':
        # Delete the movie object from the database
        movie.delete()
        
        # Redirect the user to the favorites page
        return redirect('favorites')
    
    # If the request method is not POST, render the delete_movie template and pass in the movie object
    return render(request, 'delete_movie.html', {'movie': movie})



# This view saves a new movie to the user's favorites list

@login_required
def save_movie(request):
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the movie ID from the POST request
        movie_id = request.POST.get('movie_id')
        
        # Call The Movie Database API to get movie details
        api_key = '3372059c7957b772cf7c72b570ae110f'
        endpoint = f'https://api.themoviedb.org/3/movie/{movie_id}'
        response = requests.get(endpoint, params={'api_key': api_key})
        data = response.json()
        
        # Get the movie title, overview, and poster path from the API response
        movie_title = data.get('title')
        movie_overview = data.get('overview')
        movie_poster_path = data.get('poster_path')
        
        # Check if all required movie details are available
        if movie_title and movie_overview and movie_poster_path:

            # Create a new Movie object and save it to the database
            movie = Movie(title=movie_title, overview=movie_overview, poster_path=movie_poster_path, user_id=request.user.id)
            movie.save()
        
        # Redirect the user to the favorites page
        return redirect('favorites')
    
    # If the request method is not POST, render the dashboard template
    return render(request, 'dashboard')



# This view allows a user to search for movies using The Movie Database API

@login_required
def search_results(request):
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the search query from the form data
        query = request.POST.get('search_query')
        
        # If the search query is empty, render the search page again
        if not query:
            return render(request, 'search.html')
            
        # Set up API parameters and make request to The Movie Database API
        api_key = '3372059c7957b772cf7c72b570ae110f'
        endpoint = f'https://api.themoviedb.org/3/search/movie'
        params = {
            'api_key': api_key,
            'query': query
        }
        response = requests.get(endpoint, params=params)
        results = response.json()['results']

        # Process the results from the API and create a list of movies
        movies = []
        for movie in results:
            if movie['poster_path']:
                movie_data = {
                    'id': movie['id'],
                    'title': movie['title'],
                    'overview': movie['overview'],
                    'poster_path': 'https://image.tmdb.org/t/p/w500' + movie['poster_path']
                }
                movies.append(movie_data)

        # Create a context dictionary containing the list of movies and the search query
        context = {
            'movies': movies,
            'search_query': query
        }

        # Render the results page with the list of movies and the search query
        return render(request, 'results.html', context)

    # If the request method is not POST, render the dashboard page
    return render(request, 'dashboard.html')












