# Smart Movie Posters

The Smart Movie Poster project is a Django-based web application that leverages the power of The Movie Database (TMDB) API and OpenAI's DALL·E 2 to provide users with a unique and interactive experience. This platform allows users to discover, generate, and potentially purchase custom movie posters generated by AI while managing their account's tokens and transactions through Stripe.

## Getting Started

These instructions will guide you through setting up and running the project on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have met the following requirements:
- [Python](https://www.python.org/) (version 3.11.5)
- [Django](https://www.djangoproject.com/) (version 4.2.5)
- [SQLite](https://www.sqlite.org/) (or any other database of your choice)
- [TMDB API Key](https://www.themoviedb.org/documentation/api) (for movie data)
- [OpenAI DALL·E 2 API Key](https://beta.openai.com/signup/) (for image generation)
- [Stripe API Key](https://stripe.com/docs/keys) (for payment processing)


### Installing

#### 1. Clone the repository:
      
      git clone https://github.com/mariodelacruzjr/Smart-Movie-Posters.git

#### 2. Change directory
      
      cd Smart-Movie-Posters

#### 3. Install requirements file
   
      pip install -r requirements.txt

#### 4. Create a database and configure database settings in settings.py.

#### 5. Configure API Keys

To ensure the proper functioning of the Smart Movie Poster project, you'll need to configure the following API keys securely:

- **TMDB API Key:** Update this key in your project settings to enable access to movie data from The Movie Database (TMDB).

- **OpenAI DALL·E 2 API Key:** Store this API key securely and update it in your project's settings to enable AI-powered image generation capabilities.

- **Stripe API Key:** Store your Stripe API key securely and update it in your project's settings to facilitate secure payment processing for transactions.

Additionally, don't forget to handle your Django secret key for enhanced project security.


#### 6. Apply database migrations
   
      python manage.py makemigrations home
      python manage.py migrate

#### 7. To create a superuser (admin) account and increase the `token_count` attribute to 300, follow these steps:

   ##### I. Import the necessary models
      
      py manage.py shell
      from django.contrib.auth.models import User
      from home.models import Token
   
  ##### II. Create a superuser (admin) account
     
      
      user = User.objects.create_superuser('username', 'email', 'password')
      user.save()
   
   ##### III. Create a Token object associated with the user
      
      
      token = Token(user=user)
      token.save()
    
   ##### IV. Increase the token_count attribute to 300
     
      
      token.token_count = 300
      token.save()
   
   ##### V. Exit the Django shell
      
      exit()

#### 8. Start the Django development server
    
    python manage.py runserver

#### 9. Access the Smart Movie Poster project in your web browser by navigating to http://localhost:8000/.

## Built With

This project was built using the following technologies, libraries, and frameworks:

- [Django](https://www.djangoproject.com/) - The web framework for building the backend of the application.
- [Python](https://www.python.org/) - The programming language used for server-side development.
- [SQLite](https://www.sqlite.org/) - The relational database management system for data storage.
- [TMDB API](https://www.themoviedb.org/documentation/api) - Used to fetch movie data.
- [OpenAI DALL·E 2](https://beta.openai.com/signup/) - Utilized for AI-powered image generation.
- [Stripe](https://stripe.com/) - The payment processing platform for handling transactions.
- [HTML](https://developer.mozilla.org/en-US/docs/Web/HTML) and [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS) - Used for frontend markup and styling.
- [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) - Used for frontend interactivity.

These technologies played a crucial role in bringing the Smart Movie Poster project to life.

## Authors

* **Mario De La Cruz** - *Initial work* - [mariodelacruzjr](https://github.com/mariodelacruzjr)
