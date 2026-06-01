
from django.test import TestCase
from django.urls import reverse
from .models import Agent, Structure, EvaluationAnnuelle
from datetime import date

class SgrhpMetierTests(TestCase):

    def setUp(self):
        # Création de l'environnement de test
        self.structure = Structure.objects.create(nom="Direction des Finances", code="DF01")
        self.agent = Agent.objects.create(
            matricule="AG-2026-XYZ",
            nom="Maïga",
            prenom="Mohamed",
            date_naissance=date(2006, 6, 16),
            date_recrutement=date(2026, 1, 1),
            structure=self.structure,
            statut="ACTIF",
            corps="Informaticien",
            grade="A",
            echelon=1
        )

    def test_creation_agent(self):
        """Vérifie que l'agent est correctement enregistré en base"""
        agent_db = Agent.objects.get(matricule="AG-2026-XYZ")
        self.assertEqual(agent_db.nom, "Maïga")
        self.assertEqual(agent_db.structure.code, "DF01")

    def test_limite_note_evaluation(self):
        """Vérifie que le système rejette une note d'évaluation supérieure à 20"""
        from django.core.exceptions import ValidationError
        
        evaluation_invalide = EvaluationAnnuelle(
            agent=self.agent,
            annee=2026,
            note=22.5, # Impossible, max 20
            commentaire="Excellent travail"
        )
        # Le validateur doit lever une exception
        with self.assertRaises(ValidationError):
            evaluation_invalide.full_clean()

    def test_vue_liste_agents(self):
        """Vérifie l'accessibilité de l'écran d'affichage et la présence de l'agent"""
        url = reverse('agent_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maïga")