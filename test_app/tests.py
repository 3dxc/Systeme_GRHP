from django.test import TestCase
from django.urls import reverse
from .models import Poste, Agent, Paie, Service
import datetime

class SGRHPTestCase(TestCase):
    def setUp(self):
        """Préparation des données fictives pour les tests"""
        # 1. On crée d'abord un service fictif (obligatoire pour l'agent)
        self.service = Service.objects.create(
            nom="Ressources Humaines"
        )

        # 2. On crée un poste fictif
        self.poste = Poste.objects.create(
            intitule="Développeur Python",
            grade="A",
            indice_brut=500
        )
        
        # 3. On crée l'agent en ajoutant le champ service
        self.agent = Agent.objects.create(
            matricule="X001",
            nom="Maiga",
            prenom="Oumar",
            poste=self.poste,
            service=self.service,  # <-- C'est cette ligne qui manquait !
            email="oumar@2026.com",
            date_recrutement=datetime.date.today(),
        )

    def test_calcul_salaire_base(self):
        """Vérifie si le calcul automatique du salaire de base est correct"""
        paie = Paie.objects.create(agent=self.agent, mois=5, annee=2026)
        # 500 (indice_brut) * 4.92 (VALEUR_POINT) = 2460
        self.assertEqual(float(paie.salaire_base), 2460.00)

    def test_accessibilite_accueil(self):
        """Vérifie si la page d'accueil charge correctement"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)