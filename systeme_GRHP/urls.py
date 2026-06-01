from django.contrib import admin
from django.urls import path, include
from agents import views as agents_views  # Ton import actuel

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 🛠️ CORRECTION ICI : Remplacer accueil_sgrhp par index_view
    path('', agents_views.index_view, name='accueil_agents'), 
    
    path('', include('agents.urls')),
]