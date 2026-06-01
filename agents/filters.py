import django_filters
from django_filters import rest_framework as filters
from .models import Agent, Service, Poste

class AgentFilter(django_filters.FilterSet):
    # Recherche partielle insensible à la casse (icontains)
    nom = django_filters.CharFilter(lookup_expr='icontains', label="Nom")
    matricule = django_filters.CharFilter(lookup_expr='exact', label="Matricule exact")
    
    class Meta:
        model = Agent
        fields = ['structure', 'statut', 'corps']
        
class AgentFilter(django_filters.FilterSet):
    # Recherche partielle (contient) et insensible à la casse
    nom = django_filters.CharFilter(lookup_expr='icontains', label="Nom de l'agent")
    matricule = django_filters.CharFilter(lookup_expr='icontains', label="N° Matricule")
    
    # Filtres par listes déroulantes basées sur vos modèles
    service = django_filters.ModelChoiceFilter(queryset=Service.objects.all(), label="Service")
    poste = django_filters.ModelChoiceFilter(queryset=Poste.objects.all(), label="Poste / Fonction")
    
    # Filtre sur le statut de l'activité
    est_actif = django_filters.BooleanFilter(label="En activité uniquement")

    class Meta:
        model = Agent
        fields = ['matricule', 'nom', 'service', 'poste', 'est_actif']