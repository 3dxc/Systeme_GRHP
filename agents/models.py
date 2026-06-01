from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# =========================================================================
# --- 1. CONFIGURATION DE L'AUTHENTIFICATION & DES RÔLES ---
# =========================================================================

class Role(models.Model):
    """ Gère les profils d'accès pour segmenter l'Agent (réduit) et l'Admin (complet) """
    class CodeChoices(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrateur'
        RH = 'RH', 'Gestionnaire RH'
        MANAGER = 'MANAGER', 'Manager / Chef'
        AGENT = 'AGENT', 'Agent Standard'

    code = models.CharField(max_length=20, choices=CodeChoices.choices, unique=True, verbose_name="Code du rôle")
    description = models.TextField(blank=True, verbose_name="Description des droits")

    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"

    def __str__(self):
        return self.get_code_display()


class UtilisateurManager(BaseUserManager):
    def create_user(self, matricule, email, password=None, **extra_fields):
        if not matricule:
            raise ValueError("Le matricule est obligatoire pour la connexion.")
        if not email:
            raise ValueError("L'adresse email est obligatoire.")
        
        email = self.normalize_email(email)
        
        # S'assurer qu'un rôle par défaut est affecté si absent
        if 'role' not in extra_fields:
            role_agent, _ = Role.objects.get_or_create(code=Role.CodeChoices.AGENT)
            extra_fields['role'] = role_agent
            
        user = self.model(matricule=matricule, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, matricule, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        # Assigner automatiquement le rôle ADMIN au superutilisateur
        role_admin, _ = Role.objects.get_or_create(code=Role.CodeChoices.ADMIN)
        extra_fields['role'] = role_admin

        return self.create_user(matricule, email, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    """ Modèle d'authentification principal utilisant le Matricule """
    matricule = models.CharField(max_length=30, unique=True, verbose_name="Identifiant")
    email = models.EmailField(unique=True, verbose_name="Adresse Email Professionnelle")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="utilisateurs", verbose_name="Rôle d'accès")
    
    is_active = models.BooleanField(default=True, verbose_name="Compte actif")
    is_staff = models.BooleanField(default=False, verbose_name="Accès Django Admin")
    date_inscription = models.DateTimeField(auto_now_add=True)

    # Noms uniques spécifiques à l'app 'agents' pour éviter les collisions système
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='agents_utilisateur_groups_set', 
        related_query_name='agents_utilisateur'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='agents_utilisateur_permissions_set', 
        related_query_name='agents_utilisateur'
    )

    objects = UtilisateurManager()

    USERNAME_FIELD = 'matricule'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.matricule} ({self.role.get_code_display()})"


# =========================================================================
# --- 2. STRUCTURES ET AGENTS ---
# =========================================================================

class Structure(models.Model):
    nom = models.CharField(max_length=150, unique=True, verbose_name="Nom de la direction/service")
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.nom


class Poste(models.Model):
    """ L'intitulé du poste / de la fonction dans l'établissement """
    intitule = models.CharField(max_length=100, unique=True, verbose_name="Intitulé du poste")

    class Meta:
        verbose_name = "Poste"
        verbose_name_plural = "Postes"

    def __str__(self):
        return self.intitule


class GrilleIndiciaire(models.Model):
    """ Gère les grades, échelons et indices pour le calcul automatique du salaire """
    grade = models.CharField(max_length=50, verbose_name="Grade")
    echelon = models.IntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Échelon")
    indice_brut = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="Indice Brut")
    duree_minimum_mois = models.IntegerField(default=24, verbose_name="Durée minimale (mois) pour avancement")

    class Meta:
        unique_together = ('grade', 'echelon')
        verbose_name = "Grille Indiciaire"
        verbose_name_plural = "Grilles Indiciaires"
        ordering = ['grade', 'echelon']

    def __str__(self):
        return f"Grade: {self.grade} - Échelon {self.echelon} (Indice: {self.indice_brut})"


class Agent(models.Model):
    STATUT_CHOICES = [
        ('ACTIF', 'En Activité'),
        ('DETACHE', 'En Détachement'),
        ('RETRAITE', 'À la Retraite'),
    ]

    matricule = models.CharField(max_length=20, unique=True, verbose_name="Matricule de l'État")
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    date_naissance = models.DateField()
    date_recrutement = models.DateField()
    structure = models.ForeignKey(Structure, on_delete=models.PROTECT, related_name='agents')
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='ACTIF')
    
    # Données Carrière de base
    corps = models.CharField(max_length=100, help_text="Ex: Administrateur Civil, Ingénieur")
    grade = models.CharField(max_length=50)
    echelon = models.IntegerField(default=1)
    
    # Liaison avec l'authentification
    compte_user = models.OneToOneField(
        Utilisateur, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="agent_profil",
        verbose_name="Compte d'authentification"
    )

    # Audit trail basique
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom}"


class Service(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom du service")
    directeur = models.ForeignKey(
        Agent, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="dirige_service",
        verbose_name="Chef de service"
    )

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.nom


# =========================================================================
# --- 3. SUIVI DE CARRIÈRE ET ABSENCES ---
# =========================================================================

class EvolutionCarriere(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="historique_carriere", verbose_name="Agent")
    ancien_grade_echelon = models.ForeignKey(GrilleIndiciaire, on_delete=models.SET_NULL, null=True, blank=True, related_name="anciennes_evolutions")
    nouveau_grade_echelon = models.ForeignKey(GrilleIndiciaire, on_delete=models.PROTECT, related_name="nouvelles_evolutions", verbose_name="Nouveau Grade/Échelon")
    date_promotion = models.DateField(auto_now_add=True, verbose_name="Date de l'évolution")
    motif = models.CharField(max_length=255, default="Avancement à l'ancienneté", verbose_name="Motif")

    class Meta:
        verbose_name = "Évolution de Carrière"
        verbose_name_plural = "Évolutions de Carrière"


class Conge(models.Model):
    class StatutConge(models.TextChoices):
        ATTENTE = 'ATTENTE', 'En attente'
        VALIDE = 'VALIDE', 'Validé'
        REFUSE = 'REFUSE', 'Refusé'

    class TypeConge(models.TextChoices):
        ANNUEL = 'ANNUEL', 'Congé Annuel'
        MALADIE = 'MALADIE', 'Congé Maladie'
        MATERNITE = 'MATERNITE', 'Maternité / Paternité'
        SANS_SOLDE = 'SANS_SOLDE', 'Sans Solde'

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="conges", verbose_name="Agent")
    type_conge = models.CharField(max_length=20, choices=TypeConge.choices, default=TypeConge.ANNUEL, verbose_name="Type de congé")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    statut = models.CharField(max_length=15, choices=StatutConge.choices, default=StatutConge.ATTENTE, verbose_name="Statut")
    duree_jours_stockee = models.IntegerField(default=0, editable=False, verbose_name="Nombre de jours")

    class Meta:
        verbose_name = "Congé"
        verbose_name_plural = "Congés"

    def clean(self):
        if self.date_debut and self.date_fin and self.date_debut > self.date_fin:
            raise ValidationError("La date de début ne peut pas être postérieure à la date de fin.")

    def save(self, *args, **kwargs):
        if self.date_fin and self.date_debut:
            self.duree_jours_stockee = (self.date_fin - self.date_debut).days + 1
        super().save(*args, **kwargs)

    @property
    def duree_jours(self):
        return self.duree_jours_stockee


# =========================================================================
# --- 4. ÉVALUATIONS DE PERFORMANCE ---
# =========================================================================

class EvaluationAnnuelle(models.Model):
    """ Note globale annuelle historique """
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='evaluations_annuelles')
    annee = models.IntegerField()
    note = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(20.0)])
    commentaire = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('agent', 'annee')

    def __str__(self):
        return f"Évaluation {self.annee} - {self.agent.matricule}"


class Evaluation(models.Model):
    """ Formulaire d'entretien d'évaluation complet """
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="evaluations_generales", verbose_name="Agent évalué")
    evaluateur = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="evaluations_effectuees", verbose_name="Supérieur Hiérarchique")
    date_entretien = models.DateField(verbose_name="Date de l'entretien")
    annee_eval_nom = models.IntegerField(default=2026, verbose_name="Année évaluée")
    
    competence_technique = models.DecimalField(max_digits=4, decimal_places=2, default=10, validators=[MinValueValidator(0), MaxValueValidator(20)], verbose_name="Compétences Techniques (/20)")
    sens_du_service = models.DecimalField(max_digits=4, decimal_places=2, default=10, validators=[MinValueValidator(0), MaxValueValidator(20)], verbose_name="Sens du Service (/20)")
    assiduite = models.DecimalField(max_digits=4, decimal_places=2, default=10, validators=[MinValueValidator(0), MaxValueValidator(20)], verbose_name="Assiduité (/20)")
    objectif_atteint = models.DecimalField(max_digits=4, decimal_places=2, default=10, validators=[MinValueValidator(0), MaxValueValidator(20)], verbose_name="Objectifs Atteints (/20)")
    commentaire_general = models.TextField(blank=True, verbose_name="Commentaires")
    souhaits_evolution = models.TextField(blank=True, verbose_name="Souhaits d'évolution")

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"

    @property
    def note_finale(self):
        return (self.competence_technique + self.sens_du_service + self.assiduite + self.objectif_atteint) / 4


# =========================================================================
# --- 5. GESTION SÉCURISÉE DE LA PAIE ---
# =========================================================================

class Paie(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT, related_name="bulletins_paie", verbose_name="Agent")
    mois = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name="Mois")
    annee = models.IntegerField(verbose_name="Année")
    
    salaire_base_historique = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name="Salaire de base (Figé)")
    net_a_payer_stocke = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0, verbose_name="Net à Payer (Stocké)")
    
    primes = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Primes complémentaires")
    indemnite_residence = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Indemnité de résidence")
    SFT = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Supplément Familial de Traitement (SFT)")
    
    retenues = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Autres retenues / Avances")
    retenues_retraite = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Retenue Retraite")

    class Meta:
        unique_together = ('agent', 'mois', 'annee')
        verbose_name = "Bulletin de Paie"
        verbose_name_plural = "Bulletins de Paie"

    def save(self, *args, **kwargs):
        # Tente de chercher l'indice brut depuis la Grille Indiciaire correspondante au grade/echelon de l'agent
        if not self.salaire_base_historique and self.agent:
            try:
                grille = GrilleIndiciaire.objects.get(grade=self.agent.grade, echelon=self.agent.echelon)
                self.salaire_base_historique = Decimal(grille.indice_brut)
            except GrilleIndiciaire.DoesNotExist:
                self.salaire_base_historique = Decimal(0)

        # Conversion forcée pour SQL Server
        self.salaire_base_historique = Decimal(str(self.salaire_base_historique or 0))
        self.indemnite_residence = Decimal(str(self.indemnite_residence or 0))
        self.SFT = Decimal(str(self.SFT or 0))
        self.primes = Decimal(str(self.primes or 0))
        self.retenues = Decimal(str(self.retenues or 0))
        self.retenues_retraite = Decimal(str(self.retenues_retraite or 0))

        # Calculs
        brut = (self.salaire_base_historique + self.indemnite_residence + self.SFT + self.primes)
        total_retenues = self.retenues + self.retenues_retraite
        self.net_a_payer_stocke = brut - total_retenues

        super().save(*args, **kwargs)