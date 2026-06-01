from django.urls import path
from . import views

# Ce 'app_name' permet d'utiliser des espaces de noms (ex: {% url 'agents:index' %} dans ton HTML)
app_name = 'agents'

urlpatterns = [
    # -------------------------------------------------------------
    # Vues d'authentification et d'accueil général
    # -------------------------------------------------------------
    # Page de connexion / Accueil générale (ex: /agents/)
    path('', views.index_view, name='index'),
    
    # Authentification de base (ex: /agents/auth/)
    path('auth/', views.base_auth_view, name='base_auth'),


    # -------------------------------------------------------------
    # Tableaux de bord dédiés à chaque rôle (Profils métier)
    # -------------------------------------------------------------
    # Tableau de bord Admin (ex: /agents/dashboard/admin/)
    path('dashboard/admin/', views.admin_dashboard, name='dashboard_admin'),
    
    # Tableau de bord Manager (ex: /agents/dashboard/manager/)
    path('dashboard/manager/', views.manager_dashboard, name='dashboard_manager'),
    
    # Tableau de bord Agent (ex: /agents/dashboard/agent/)
    path('dashboard/agent/', views.agent_dashboard, name='dashboard_agent'),
    
    # Tableau de bord Comptabilité (ex: /agents/dashboard/comptabilite/)
    path('dashboard/comptabilite/', views.comptable_dashboard, name='dashboard_comptable'),


    # -------------------------------------------------------------
    # Gestion du CRUD des Agents (Vues basées sur des classes - CBV)
    # -------------------------------------------------------------
    # Liste complète et filtrée des agents (ex: /agents/liste/)
    path('liste/', views.AgentListView.as_view(), name='agent_list'),
    
    # Créer un nouvel agent (ex: /agents/nouveau/)
    path('nouveau/', views.AgentCreateView.as_view(), name='agent_create'),
    
    # Voir les détails complets d'un agent (ex: /agents/5/)
    path('<int:pk>/', views.AgentDetailView.as_view(), name='agent_detail'),
    
    # Modifier les informations d'un agent (ex: /agents/5/modifier/)
    path('<int:pk>/modifier/', views.AgentUpdateView.as_view(), name='agent_edit'),
    
    # Supprimer définitivement un agent (ex: /agents/5/supprimer/)
    path('<int:pk>/supprimer/', views.AgentDeleteView.as_view(), name='agent_delete'),
]