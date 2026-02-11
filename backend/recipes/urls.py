"""URL-маршруты приложении recipes проекта Foodgram."""


from django.urls import path

from recipes.views import redirect_to_recipe


urlpatterns = [
    path('s/<int:pk>/', redirect_to_recipe, name='short_link_redirect'),
]
