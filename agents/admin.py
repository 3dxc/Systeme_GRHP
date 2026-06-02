from django import forms
from django.contrib import admin
from django.db import models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (
    Role, Utilisateur, Structure, Poste, GrilleIndiciaire, 
    Agent, Service, EvolutionCarriere, Conge, 
    EvaluationAnnuelle, Evaluation, Paie
)

# =========================================================================
# CONFIGURATION DU SCRIPT JAZZMIN UNIQUE (Évite les boutons statiques)
# =========================================================================

class DynamicCrudSelectWidget(forms.Select):
    class Media:
        js = ('js/admin_dynamic_crud.js',)


class DynamicCrudAdminMixin:
    formfield_overrides = {
        models.ForeignKey: {'widget': DynamicCrudSelectWidget},
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if isinstance(field.widget, admin.widgets.RelatedFieldWidgetWrapper):
                field.widget.can_change_related = True
                field.widget.can_view_related = True
        return form


# =========================================================================
# FORMULAIRES CORRECTIFS POUR L'UTILISATEUR PERSONNALISÉ (MATRICULE)
# =========================================================================

class UtilisateurCustomCreationForm(UserCreationForm):
    """Formulaire de création d'un utilisateur sans le champ 'username' nativement requis"""
    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = ('matricule', 'email', 'role')


class UtilisateurCustomChangeForm(UserChangeForm):
    """Formulaire de modification d'un utilisateur ajusté sur le matricule"""
    class Meta:
        model = Utilisateur
        fields = ('matricule', 'email', 'role', 'is_active', 'is_staff', 'is_superuser')


# =========================================================================
# CONFIGURATION DES CLASSES ADMIN (SGIH)
# =========================================================================

# --- 1. CONFIGURATION DE L'AUTHENTIFICATION & DES RÔLES ---

@admin.register(Role)
class RoleAdmin(DynamicCrudAdminMixin, admin.ModelAdmin):
    list_display = ('code', 'description')
    search_fields = ('code',)
    fieldsets = (('Informations Générales', {'fields': ('code', 'description')}),)


@admin.register(Utilisateur)
class UtilisateurAdmin(DynamicCrudAdminMixin, BaseUserAdmin):
    # Utilisation de nos formulaires adaptés au champ matricule
    add_form = UtilisateurCustomCreationForm
    form = UtilisateurCustomChangeForm
    
    list_display = ('matricule', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('matricule', 'email')
    ordering = ('matricule',)
    
    # Redéfinition complète des fieldsets pour supprimer toute référence à 'username'
    fieldsets = (
        (None, {'fields': ('matricule', 'password')}),
        ('Informations personnelles', {'fields': ('email', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    # Fieldset affiché uniquement lors de l'ajout d'un nouvel utilisateur (+ / add)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('matricule', 'email', 'role', 'password', 'confirm_password' if hasattr(UserCreationForm, 'confirm_password') else 'password'),
        }),
    )


# --- 2. STRUCTURES ET ORGANISATION ---

@admin.register(Structure)
class StructureAdmin(DynamicCrudAdminMixin, admin.ModelAdmin):
    list_display = ('code', 'nom')
    search_fields = ('code', 'nom')
    fieldsets = (('Détails de la Structure', {'fields': ('code', 'nom')}),)


@admin.register(Poste)
class PosteAdmin(DynamicCrudAdminMixin, admin.ModelAdmin):
    list_display = ('intitule',)
    search_fields = ('intitule',)


@admin.register(Service)
class ServiceAdmin(DynamicCrudAdminMixin, admin.ModelAdmin):
    list_display = ('nom', 'directeur')
    search_fields = ('nom',)
    fieldsets = (('Informations Générales', {'fields': ('nom', 'directeur')}),)


@admin.register(GrilleIndiciaire)
class GrilleIndiciaireAdmin(DynamicCrudAdminMixin, admin.ModelAdmin):
    list_display = ('grade', 'echelon', 'indice_brut', 'duree_minimum_mois')
    list_filter = ('grade', 'echelon')
    search_fields = ('grade',)


# --- 3. GESTION DES AGENTS ---

@admin.register(Agent)
class AgentAdmin(DynamicCrudAdminMixin, admin.ModelAdmin):
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
class EvolutionCarriereAdmin(DynamicCrudAdminMixin, admin.ModelAdmin):
    list_display = ('agent', 'ancien_grade_echelon', 'nouveau_grade_echelon', 'date_promotion')
    list_filter = ('date_promotion',)
    search_fields = ('agent__nom', 'agent__matricule')
    fieldsets = (('Détails de l\'Évolution', {'fields': ('agent', 'ancien_grade_echelon', 'nouveau_grade_echelon', 'motif')}),)


@admin.register(Conge)
class CongeAdmin(DynamicCrudAdminMixin, admin.ModelAdmin):
    list_display = ('agent', 'type_conge', 'date_debut', 'date_fin', 'statut', 'afficher_duree')
    list_filter = ('type_conge', 'statut')
    search_fields = ('agent__nom', 'agent__matricule')
    fieldsets = (
        ('Informations du Congé', {'fields': ('agent', 'type_conge', 'statut')}),
        ('Période', {'fields': ('date_debut', 'date_fin')}),
    )
    
    def afficher_duree(self, obj):
        return f"{obj.duree_jours} jours" if hasattr(obj, 'duree_jours') and obj.duree_jours else "N/A"
    afficher_duree.short_description = "Durée"


# --- 5. ÉVALUATIONS ---

@admin.register(EvaluationAnnuelle)
class EvaluationAnnuelleAdmin(DynamicCrudAdminMixin, admin.ModelAdmin):
    list_display = ('agent', 'annee', 'note')
    list_filter = ('annee',)
    search_fields = ('agent__nom', 'agent__matricule')


@admin.register(Evaluation)
class EvaluationAdmin(DynamicCrudAdminMixin, admin.ModelAdmin):
    list_display = ('agent', 'annee_eval_nom', 'afficher_note_finale', 'date_entretien')
    list_filter = ('annee_eval_nom',)
    search_fields = ('agent__nom', 'agent__matricule')
    fieldsets = (
        ('Général', {'fields': ('agent', 'evaluateur', 'annee_eval_nom', 'date_entretien')}),
        ('Notation', {'fields': ('competence_technique', 'sens_du_service', 'assiduite', 'objectif_atteint')}),
        ('Commentaires', {'fields': ('commentaire_general', 'souhaits_evolution')}),
    )
    
    def afficher_note_finale(self, obj):
        if hasattr(obj, 'note_finale') and obj.note_finale is not None:
            return f"{obj.note_finale:.2f} / 20"
        return "Pas encore noté"
    afficher_note_finale.short_description = "Note Finale"


# --- 6. PAIE ---

@admin.register(Paie)
class PaieAdmin(DynamicCrudAdminMixin, admin.ModelAdmin):
    list_display = ('agent', 'mois', 'annee', 'salaire_base_historique', 'net_a_payer_stocke')
    list_filter = ('annee', 'mois')
    search_fields = ('agent__nom', 'agent__matricule')
    readonly_fields = ('salaire_base_historique', 'net_a_payer_stocke')
    fieldsets = (
        ('Période de Paie', {'fields': ('agent', 'mois', 'annee')}),
        ('Éléments de Salaire', {'fields': ('primes', 'indemnite_residence', 'SFT')}),
        ('Retenues', {'fields': ('retenues', 'retenues_retraite')}),
    )