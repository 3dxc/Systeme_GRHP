from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Role, Utilisateur, Structure, Poste, GrilleIndiciaire, 
    Agent, Service, EvolutionCarriere, Conge, 
    EvaluationAnnuelle, Evaluation, Paie
)

# --- 1. CONFIGURATION DE L'AUTHENTIFICATION & DES RÔLES ---

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('code', 'description')
    search_fields = ('code',)
    fieldsets = (('Informations Générales', {'fields': ('code', 'description')}),)

@admin.register(Utilisateur)
class UtilisateurAdmin(BaseUserAdmin):
    list_display = ('matricule', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('matricule', 'email')
    ordering = ('matricule',)
    fieldsets = (
        (None, {'fields': ('matricule', 'password')}),
        ('Informations personnelles', {'fields': ('email', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

# --- 2. STRUCTURES ET ORGANISATION ---

@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom')
    search_fields = ('code', 'nom')
    fieldsets = (('Détails de la Structure', {'fields': ('code', 'nom')}),)

@admin.register(Poste)
class PosteAdmin(admin.ModelAdmin):
    list_display = ('intitule',)
    search_fields = ('intitule',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'directeur')
    search_fields = ('nom',)
    fieldsets = (('Informations Générales', {'fields': ('nom', 'directeur')}),)

@admin.register(GrilleIndiciaire)
class GrilleIndiciaireAdmin(admin.ModelAdmin):
    list_display = ('grade', 'echelon', 'indice_brut', 'duree_minimum_mois')
    list_filter = ('grade', 'echelon')
    search_fields = ('grade',)

# --- 3. GESTION DES AGENTS (CORRIGÉ VOS CHAMPS RÉELS) ---

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'structure', 'statut', 'corps', 'grade', 'echelon')
    list_filter = ('statut', 'structure', 'grade')
    search_fields = ('matricule', 'nom', 'prenom')
    fieldsets = (
        ('Identité', {'fields': ('matricule', 'nom', 'prenom', 'date_naissance')}),
        ('Situation Professionnelle', {'fields': ('structure', 'statut', 'date_recrutement', 'corps', 'grade', 'echelon')}),
        ('Liaison Système', {'fields': ('compte_user',)}),
    )

# --- 4. RH, CARRIÈRE ET ABSENCES ---

@admin.register(EvolutionCarriere)
class EvolutionCarriereAdmin(admin.ModelAdmin):
    list_display = ('agent', 'ancien_grade_echelon', 'nouveau_grade_echelon', 'date_promotion')
    list_filter = ('date_promotion',)
    search_fields = ('agent__nom', 'agent__matricule')
    fieldsets = (('Détails de l\'Évolution', {'fields': ('agent', 'ancien_grade_echelon', 'nouveau_grade_echelon', 'motif')}),)

@admin.register(Conge)
class CongeAdmin(admin.ModelAdmin):
    list_display = ('agent', 'type_conge', 'date_debut', 'date_fin', 'statut', 'afficher_duree')
    list_filter = ('type_conge', 'statut')
    search_fields = ('agent__nom', 'agent__matricule')
    fieldsets = (
        ('Informations du Congé', {'fields': ('agent', 'type_conge', 'statut')}),
        ('Période', {'fields': ('date_debut', 'date_fin')}),
    )
    def afficher_duree(self, obj):
        return f"{obj.duree_jours} jours"
    afficher_duree.short_description = "Durée"

# --- 5. ÉVALUATIONS ---

@admin.register(EvaluationAnnuelle)
class EvaluationAnnuelleAdmin(admin.ModelAdmin):
    list_display = ('agent', 'annee', 'note')
    list_filter = ('annee',)
    search_fields = ('agent__nom', 'agent__matricule')

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('agent', 'annee_eval_nom', 'afficher_note_finale', 'date_entretien')
    list_filter = ('annee_eval_nom',)
    search_fields = ('agent__nom', 'agent__matricule')
    fieldsets = (
        ('Général', {'fields': ('agent', 'evaluateur', 'annee_eval_nom', 'date_entretien')}),
        ('Notation', {'fields': ('competence_technique', 'sens_du_service', 'assiduite', 'objectif_atteint')}),
        ('Commentaires', {'fields': ('commentaire_general', 'souhaits_evolution')}),
    )
    def afficher_note_finale(self, obj):
        return f"{obj.note_finale:.2f} / 20"
    afficher_note_finale.short_description = "Note Finale"

# --- 6. PAIE ---

@admin.register(Paie)
class PaieAdmin(admin.ModelAdmin):
    list_display = ('agent', 'mois', 'annee', 'salaire_base_historique', 'net_a_payer_stocke')
    list_filter = ('annee', 'mois')
    search_fields = ('agent__nom', 'agent__matricule')
    readonly_fields = ('salaire_base_historique', 'net_a_payer_stocke')
    fieldsets = (
        ('Période de Paie', {'fields': ('agent', 'mois', 'annee')}),
        ('Éléments de Salaire', {'fields': ('primes', 'indemnite_residence', 'SFT')}),
        ('Retenues', {'fields': ('retenues', 'retenues_retraite')}),
    )