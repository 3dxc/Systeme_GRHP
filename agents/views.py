from django.shortcuts import render
from django.urls import reverse_lazy
from django_filters.views import FilterView
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from .filters import AgentFilter
from .models import Agent

# ==============================================================================
# VUES GÉNÉRALES ET AUTHENTIFICATION
# ==============================================================================

def index_view(request):
    """ Page d'accueil / Formulaire de connexion de l'application agents """
    return render(request, 'agents/index.html', {
        'user': request.user,
        'is_index_page': True 
    })

def base_auth_view(request):
    """ Page d'authentification (si affichée directement) """
    return render(request, 'agents/base_auth.html')


# ==============================================================================
# TABLEAUX DE BORD DÉDIÉS AUX RÔLES (Profils Métier)
# ==============================================================================

def admin_dashboard(request):
    """ Tableau de bord de l'administrateur système """
    return render(request, 'agents/dashboards/admin.html', {'role': 'Administrateur'})

def manager_dashboard(request):
    """ Tableau de bord du Manager RH """
    return render(request, 'agents/dashboards/manager.html', {'role': 'Manager'})

def agent_dashboard(request):
    """ Espace personnel de l'Agent de la fonction publique """
    return render(request, 'agents/dashboards/agent.html', {'role': 'Agent'})

def comptable_dashboard(request):
    """ Espace de gestion pour le Comptable """
    return render(request, 'agents/dashboards/comptable.html', {'role': 'Comptable'})


# ==============================================================================
# GESTION DES AGENTS (CRUD - Vues basées sur des classes - CBV)
# ==============================================================================

# LIST (Affichage des agents avec filtres, tri dynamique et pagination)
class AgentListView(FilterView):
    model = Agent
    template_name = 'agents/agent_list.html'
    context_object_name = 'agents'
    filterset_class = AgentFilter
    paginate_by = 10  # Affiche 10 agents par page

    def get_queryset(self):
        """ Gère le tri dynamique par colonne en toute sécurité """
        queryset = super().get_queryset()
        
        # Récupère le paramètre 'sort' dans l'URL (ex: ?sort=nom)
        critere_tri = self.request.GET.get('sort', 'matricule')  # Tri par matricule par défaut
        
        # Liste des tris autorisés pour éviter les injections SQL
        tris_autorises = ['nom', '-nom', 'matricule', '-matricule', 'date_recrutement', '-date_recrutement']
        
        if critere_tri in tris_autorises:
            queryset = queryset.order_by(critere_tri)
            
        return queryset

    def get_context_data(self, **kwargs):
        """ Permet de conserver les filtres actifs lors du changement de page """
        context = super().get_context_data(**kwargs)
        queries_without_page = self.request.GET.copy()
        if 'page' in queries_without_page:
            del queries_without_page['page']
        context['queries_get'] = queries_without_page.urlencode()
        return context


# CREATE (Formulaire de création d'un agent)
class AgentCreateView(CreateView):
    model = Agent
    fields = ['matricule', 'nom', 'prenom', 'date_naissance', 'date_recrutement', 'structure', 'statut', 'corps', 'grade', 'echelon']
    template_name = 'agents/agent_form.html'
    success_url = reverse_lazy('agents:agent_list')


# READ (Affichage des détails complets d'un agent)
class AgentDetailView(DetailView):
    model = Agent
    template_name = 'agents/agent_detail.html'


# UPDATE (Formulaire de modification d'un agent)
class AgentUpdateView(UpdateView):
    model = Agent
    fields = ['nom', 'prenom', 'structure', 'statut', 'corps', 'grade', 'echelon']
    template_name = 'agents/agent_form.html'
    success_url = reverse_lazy('agents:agent_list')


# DELETE (Confirmation et suppression définitive d'un agent)
class AgentDeleteView(DeleteView):
    model = Agent
    template_name = 'agents/agent_confirm_delete.html'
    success_url = reverse_lazy('agents:agent_list')