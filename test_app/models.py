from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

# --- 1. CONFIGURATION DE LA STRUCTURE ADMINISTRATIVE ---

class Service(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom du service")
    directeur = models.ForeignKey(
        "Agent", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="dirige_service",
        verbose_name="Directeur / Chef de service"
    )

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.nom


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


class Poste(models.Model):
    """ L'intitulé du poste / de la fonction dans l'établissement """
    intitule = models.CharField(max_length=100, unique=True, verbose_name="Intitulé du poste")

    class Meta:
        verbose_name = "Poste"
        verbose_name_plural = "Postes"

    def __str__(self):
        return self.intitule


# --- 2. GESTION DES AGENTS ---

class Agent(models.Model):
    class GenreChoices(models.TextChoices):
        HOMME = 'M', 'Masculin'
        FEMME = 'F', 'Féminin'

    matricule = models.CharField(max_length=20, unique=True, verbose_name="N° Matricule")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom(s)")
    genre = models.CharField(max_length=1, choices=GenreChoices.choices, default=GenreChoices.HOMME, verbose_name="Genre")
    date_naissance = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    
    # Relations
    poste = models.ForeignKey(Poste, on_delete=models.PROTECT, verbose_name="Poste / Fonction")
    grille = models.ForeignKey(GrilleIndiciaire, on_delete=models.PROTECT, verbose_name="Situation Indiciaire (Grade/Échelon)")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="agents", verbose_name="Service affecté")
    
    date_recrutement = models.DateField(verbose_name="Date de recrutement")
    email = models.EmailField(unique=True, verbose_name="Adresse Email")
    est_actif = models.BooleanField(default=True, verbose_name="Agent en activité")

    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"[{self.matricule}] {self.nom.upper()} {self.prenom}"


# --- 3. SUIVI DE CARRIÈRE ET ABSENCES ---

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
    
    # Champ de stockage de durée pour optimiser les requêtes des graphiques
    duree_jours_stockee = models.IntegerField(default=0, editable=False, verbose_name="Nombre de jours")

    class Meta:
        verbose_name = "Congé"
        verbose_name_plural = "Congés"

    def clean(self):
        if self.date_debut and self.date_fin and self.date_debut > self.date_fin:
            raise ValidationError("La date de début ne peut pas être postérieure à la date de fin.")

    def save(self, *args, **kwargs):
        # On calcule et stocke la durée en jours de manière définitive à la sauvegarde
        if self.date_fin and self.date_debut:
            self.duree_jours_stockee = (self.date_fin - self.date_debut).days + 1
        super().save(*args, **kwargs)

    @property
    def duree_jours(self):
        return self.duree_jours_stockee


# --- 4. ÉVALUATIONS PERFORMANCE ---

class Evaluation(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="evaluations", verbose_name="Agent évalué")
    evaluateur = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="evaluations_effectuees", verbose_name="Supérieur Hiérarchique")
    date_entretien = models.DateField(verbose_name="Date de l'entretien")
    annee_eval_nom = models.IntegerField(default=2026, verbose_name="Année évaluée")
    
    note_validateur = [MinValueValidator(0), MaxValueValidator(20)]
    
    competence_technique = models.DecimalField(max_digits=4, decimal_places=2, default=10, validators=note_validateur, verbose_name="Compétences Techniques (/20)")
    sens_du_service = models.DecimalField(max_digits=4, decimal_places=2, default=10, validators=note_validateur, verbose_name="Sens du Service (/20)")
    assiduite = models.DecimalField(max_digits=4, decimal_places=2, default=10, validators=note_validateur, verbose_name="Assiduité (/20)")
    objectif_atteint = models.DecimalField(max_digits=4, decimal_places=2, default=10, validators=note_validateur, verbose_name="Objectifs Atteints (/20)")
    commentaire_general = models.TextField(blank=True, verbose_name="Commentaires")
    souhaits_evolution = models.TextField(blank=True, verbose_name="Souhaits d'évolution")

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"

    @property
    def note_finale(self):
        return (self.competence_technique + self.sens_du_service + self.assiduite + self.objectif_atteint) / 4


# --- 5. GESTION SÉCURISÉE DE LA PAIE ---

class Paie(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT, related_name="bulletins_paie", verbose_name="Agent")
    mois = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name="Mois")
    annee = models.IntegerField(verbose_name="Année")
    
    # Données figées pour l'historique comptable et requêtes de graphiques rapides
    salaire_base_historique = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name="Salaire de base (Figé)")
    net_a_payer_stocke = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0, verbose_name="Net à Payer (Stocké)")
    
    # Primes et Indemnités
    primes = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Primes complémentaires")
    indemnite_residence = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Indemnité de résidence")
    SFT = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Supplément Familial de Traitement (SFT)")
    
    # Retenues
    retenues = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Autres retenues / Avances")
    retenues_retraite = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Retenue Retraite")

    class Meta:
        unique_together = ('agent', 'mois', 'annee')
        verbose_name = "Bulletin de Paie"
        verbose_name_plural = "Bulletins de Paie"

    def save(self, *args, **kwargs):
        VALEUR_POINT = 4.92  # Valeur du point d'indice
        
        # 1. On fige définitivement le salaire de base à la création
        if not self.pk:
            self.salaire_base_historique = self.agent.grille.indice_brut * VALEUR_POINT
        
        # 2. On calcule et on met à jour le Net à Payer stocké
        brut = self.salaire_base_historique + self.indemnite_residence + self.SFT + self.primes
        charges = self.retenues_retraite + self.retenues
        self.net_a_payer_stocke = brut - charges
        
        super().save(*args, **kwargs)

    @property
    def net_a_payer(self):
        return self.net_a_payer_stocke

    @property
    def montant(self):
        """ Renvoie le net à payer pour le calcul de la masse salariale du Dashboard """
        return self.net_a_payer_stocke