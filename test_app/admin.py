from django.contrib import admin
from .models import Service, GrilleIndiciaire, Poste, Agent, EvolutionCarriere, Conge, Evaluation, Paie

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'directeur')
    search_fields = ('nom',)


@admin.register(GrilleIndiciaire)
class GrilleIndiciaireAdmin(admin.ModelAdmin):
    list_display = ('grade', 'echelon', 'indice_brut', 'duree_minimum_mois')
    list_filter = ('grade', 'echelon')
    search_fields = ('grade',)


@admin.register(Poste)
class PosteAdmin(admin.ModelAdmin):
    # 🌟 CORRECTION : On n'affiche plus que l'intitulé pur ici
    list_display = ('id', 'intitule')
    search_fields = ('intitule',)


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'genre', 'poste', 'grille', 'service', 'est_actif')
    list_filter = ('genre', 'est_actif', 'service', 'poste')
    search_fields = ('matricule', 'nom', 'prenom', 'email')


@admin.register(EvolutionCarriere)
class EvolutionCarriereAdmin(admin.ModelAdmin):
    list_display = ('agent', 'ancien_grade_echelon', 'nouveau_grade_echelon', 'date_promotion', 'motif')
    list_filter = ('date_promotion',)
    search_fields = ('agent__nom', 'agent__prenom', 'motif')


@admin.register(Conge)
class CongeAdmin(admin.ModelAdmin):
    list_display = ('agent', 'type_conge', 'date_debut', 'date_fin', 'duree_jours_stockee', 'statut')
    list_filter = ('type_conge', 'statut', 'date_debut')
    search_fields = ('agent__nom', 'agent__prenom')


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('agent', 'annee_eval_nom', 'evaluateur', 'note_finale', 'date_entretien')
    list_filter = ('annee_eval_nom', 'date_entretien')
    search_fields = ('agent__nom', 'agent__prenom')


@admin.register(Paie)
class PaieAdmin(admin.ModelAdmin):
    # 🌟 CORRECTION : Utilisation de salaire_base_historique et net_a_payer_stocke
    list_display = ('agent', 'mois', 'annee', 'salaire_base_historique', 'primes', 'net_a_payer_stocke')
    list_filter = ('mois', 'annee', 'agent__service')
    search_fields = ('agent__nom', 'agent__matricule')