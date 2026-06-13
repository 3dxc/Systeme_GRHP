# agents/filters.py
import django_filters
from .models import Agent # Adaptez selon le nom de votre modèle

class AgentFilter(django_filters.FilterSet):
    class Meta:
        model = Agent
        fields = '__all__'