from django.urls import path
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from .views import register, delete_movie, save_movie, purchase_tokens, favorites, HomeView, poster_design, generate_image, SearchResultsPageView, add_to_cart, cart_view, remove_from_cart, checkout, cancel, success
#from .views import get_token_count
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('favorites/', favorites, name='favorites'),
    path('delete-movie/<int:movie_id>/', delete_movie, name='delete_movie'),
    path('search/', SearchResultsPageView.as_view(), name='search_results'),
    path('save_movie/', save_movie, name='save_movie'),
    path('poster_design/', poster_design, name='poster_design'),
    path('generate_image/<int:mov_id>/', generate_image, name='generate_image'),
    path('add-to-cart/<int:image_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_view, name='cart_view'),
    path('cart/remove/<int:image_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('success/', success, name='success'),
    path('cancel/', cancel, name='cancel'),
    path('purchase_tokens/', purchase_tokens, name='purchase_tokens'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)