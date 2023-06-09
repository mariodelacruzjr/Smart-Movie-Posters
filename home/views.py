import requests
import json
import openai
import stripe
from .models import MovieImage, FavoriteMovie, Token
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
from django.views import View
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages
from django.urls import reverse





@login_required
def purchase_tokens(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    token_price=1
    token_ammount=200
    cart_items=[]
    cart_items.append({
        'price_data': {
            'currency': 'usd',
            'unit_amount': token_price*100,
            'product_data': {
                'name': f'{token_ammount} Tokens', 
            },
        },
        'quantity': 1,
    })

    try:
        session=stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=cart_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('purchase_tokens')) + '?success=true',
            cancel_url='http://localhost:8000/cancel/',
        )
    except stripe.error.StripeError as e:
        # Display an error message to the user
        messages.error(request, "An error occurred while processing your payment. Please try again later.")
        return redirect('home')
        

    if request.GET.get('success'):
        # Add tokens to the user's token count
        try:
            token_obj = Token.objects.get(user=request.user)
            user_tokens = token_obj.token_count
            user_tokens += token_ammount
            token_obj.token_count = user_tokens
            token_obj.save()
        except Token.DoesNotExist:
            # If the user doesn't have a token object, create one
            token_obj = Token.objects.create(user=request.user, token_count=0)
            messages.error(request, "An error occurred with your tokens. Please try again later.")
            return redirect('home')
        messages.success(request, f"{token_ammount} Tokens purchased successfully!")
        return redirect('home')

    # Render purchase page
    return render(request, 'purchase_tokens.html', {
        'session_id': session.id,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })




@receiver(user_logged_in)
def create_token(sender, user, request, **kwargs):
    if not Token.objects.filter(user=user).exists():
        token = Token.objects.create(user=user, token_count=0)

def checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for item in cart.values():
        
        total += float(item['price'])
        image_url = request.build_absolute_uri(item['image_url'])
        cart_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(item['price']*100),
                'product_data': {
                    'name': item['title'],
                    'images': [image_url],
                    
                },
            },
            'quantity': 1,
        })
       

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=cart_items,
        mode='payment',
        success_url='http://localhost:8000/success/',
        cancel_url='http://localhost:8000/cancel/',
    )
    

    return render(request, 'checkout.html', {
        'session_id': session.id,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

def success(request):
    return render(request, 'success.html')

def cancel(request):
    return render(request, 'cancel.html')

def remove_from_cart(request, image_id):
    cart = request.session.get('cart', {})
    cart_item = cart.get(str(image_id))

    if cart_item:
        del cart[str(image_id)]
        request.session['cart'] = cart

    return redirect('cart_view')

def add_to_cart(request, image_id):
    image = get_object_or_404(MovieImage, id=image_id)
    cart = request.session.get('cart', {})
    cart_item = cart.get(str(image_id))

    if cart_item:
        cart_item['quantity'] += 1
        cart_item['price'] = float(cart_item['price']) + float(request.POST.get('price'))
        cart_item['size'] = request.POST.get('size') # Add selected size to cart
    else:
        size = request.POST.get('size')
        price = 10 if size == 'small' else 20 if size == 'medium' else 30
        cart[str(image_id)] = {
            'id': str(image.id),
            'title': image.movie.title,
            'image_url': image.image.url,
            'quantity': 1,
            'price': float(price),
            'size': size # Add selected size to cart
        }

    request.session['cart'] = cart
    print(f"cart is {cart}")
    print(f"cart items are {cart.items}")
    return redirect('cart_view')

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for item in cart.values():
        total += float(item['price'])
        item['image_url'] = item.get('image_url', '')
        cart_items.append(item)
    print("Cart Items:", cart_items)
    print("Total:", total)
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'cart.html', context)

class HomeView(View):
    template_name = 'home.html'
    dashboard_template_name = 'dashboard.html'
    

    def get(self, request):
        if request.user.is_authenticated:
            #user_favorites = Movie.objects.filter(user=request.user)
            user_favorites = FavoriteMovie.objects.filter(user=request.user).values_list('title', flat=True)
            user_favorites1 = FavoriteMovie.objects.filter(user=request.user).values_list('mov_id', flat=True)
            print(user_favorites1)
            # Make a request to the TMDB API to get the trending movies from the past week
            response = requests.get(f'https://api.themoviedb.org/3/trending/movie/week?api_key={settings.TMDB_API_KEY}')
            #print(response)
            # Parse the response and extract the list of trending movies
            trending_all_week_results = json.loads(response.content)['results']
            # Create a dictionary containing the trending movies to pass to the template
            context = {
                'trending_all_week_results': trending_all_week_results,
                'user_favorites' : user_favorites
            }
            return render(request, self.dashboard_template_name, context)
        return render(request, self.template_name)

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

from django.contrib import messages

def generate_image(request, mov_id):
    try:
        user_tokens = Token.objects.get(user=request.user).token_count
    except Token.DoesNotExist:
        user_tokens = 0

    if user_tokens < 20:
        messages.error(request, "You need at least 20 tokens to generate an image.")
        return redirect('home')

    # Use the movie description as the text prompt
    BASE_URL = f"https://api.themoviedb.org/3/"
    endpoint = f"movie/{mov_id}"
    params = {"api_key": settings.TMDB_API_KEY}
    tmdb_response = requests.get(BASE_URL + endpoint, params=params)
    tmdb_response_json = json.loads(tmdb_response.text)
    text_prompt = tmdb_response_json.get("overview")
    m_title = tmdb_response_json.get("title")

    # Try to retrieve a movie with the given mov_id from the database
    openai.api_key=settings.OPENAI_API_KEY
    res = openai.Image.create(prompt=text_prompt, n=1, size="1024x1024")
    image_url = res["data"][0]["url"]
    img_temp = NamedTemporaryFile()
    img_temp.write(urlopen(image_url).read())
    img_temp.flush()
    my_movie, created = FavoriteMovie.objects.get_or_create(
        mov_id=mov_id, defaults={"title": m_title}
    )
    movie_image = MovieImage(movie=my_movie)
    movie_image.image.save(f"{my_movie.title}.jpg", img_temp)

    user_tokens -= 20
    token_obj, created = Token.objects.get_or_create(user=request.user)
    token_obj.token_count = user_tokens
    token_obj.save()

    messages.success(request, "Image generated successfully. 20 tokens deducted from your account.")
    return render(request, "generated_image.html", {"movie_image": movie_image})


def poster_design(request):
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        movie_title = request.POST.get('movie_title')
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={settings.TMDB_API_KEY}&language=en-US'
        response = requests.get(url)
        movie = response.json()
        return render(request, 'poster_design.html', {'movie': movie, 'movie_title': movie_title})
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def favorites(request):
    # Get all the movies that belong to the logged-in user
    movies = FavoriteMovie.objects.filter(user=request.user)


    # Create a context dictionary containing the list of movies
    context = {
        'movies': movies,
    }

    # Render the favorites page with the list
    return render(request, 'favorites.html', context)

def delete_movie(request, movie_id):
    movie = get_object_or_404(FavoriteMovie, pk=movie_id)
    
    if request.method == 'POST':
        movie.delete()
        return HttpResponse('', status=204)
    
    return render(request, 'delete_movie.html', {'movie': movie})

@login_required
def save_movie(request):
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        endpoint = f'https://api.themoviedb.org/3/movie/{movie_id}'
        response = requests.get(endpoint, params={'api_key': settings.TMDB_API_KEY})
        data = response.json()
        movie_title = data.get('title')
        movie_overview = data.get('overview')
        movie_poster_path = data.get('poster_path')

        # Check if the movie is already saved by the user
        if FavoriteMovie.objects.filter(user=request.user, mov_id=movie_id).exists():
            # Display a warning message using Django messages framework
            messages.warning(request, 'You have already saved this movie.')
            return redirect('favorites')

        # If the movie is not saved, save it to the database
        if movie_title and movie_overview and movie_poster_path:
            movie = FavoriteMovie(title=movie_title, overview=movie_overview, poster_path=movie_poster_path, user=request.user, mov_id=movie_id)
            movie.save()

        # Display a success message using Django messages framework
        messages.success(request, 'Movie saved successfully.')
        
        # Redirect the user to the favorites page
        return redirect('favorites')

    return render(request, 'dashboard.html')

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
@method_decorator(login_required, name='dispatch')
class SearchResultsPageView(View):
    def get(self, request):
        return render(request, 'search.html')

    def post(self, request):
        query = request.POST.get('search_query')

        if not query:
            return render(request, 'search_results.html')

        endpoint = f'https://api.themoviedb.org/3/search/movie'
        params = {
            'api_key': settings.TMDB_API_KEY,
            'query': query
        }
        response = requests.get(endpoint, params=params)
        results = response.json()['results']

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

        context = {
            'movies': movies,
            'search_query': query
        }

        return render(request, 'search_results.html', context)

