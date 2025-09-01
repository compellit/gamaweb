from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import gettext as _

# Create your tests here.

class IndexTests(TestCase):
    def setUp(self):
        self.client = Client()

        # urls
        self.index_url = reverse('gama:index')
        self.analysis_url = reverse('gama:analysis')
        self.clear_session_url = reverse('gama:clear_session')

    def test_index_GET(self):
        response = self.client.get(self.index_url)

        # Vérifie que la page répond bien (status HTTP 200)
        self.assertEqual(response.status_code, 200)

        # Vérifie que le bon template est utilisé
        self.assertTemplateUsed(response, 'gama/index.html')

    def test_index_forms(self):
        # Vérifications formulaires d'analyse page index
        response = self.client.get(self.index_url)

        # Vérifie que le formulaire pour analyse simple est présent
        self.assertContains(response, f'<form action="{self.analysis_url}"', html=False)

        # Vérifie que le formulaire pour analyse multi est présent
        self.assertContains(response, 'id="bulk-form"', html=False)

    def test_index_fields(self):
        # Vérifications champs page index
        response = self.client.get(self.index_url)

        # Vérifie que le champ texte est présent
        self.assertContains(response, 'id="text"')

        # Vérifie que les champs metadata sont présents
        metadata_fields = ["corpus_name", "author", "date", "doc_name", "doc_subtitle"]
        for field in metadata_fields:
            self.assertContains(response, f'id="{field}"')

        # Vérifie que le champ pour upload ZIP est présent
        self.assertContains(response, 'id="zip_file"')

    def test_index_example_selector(self):
        # Vérification sélecteur d'exemples page index
        response = self.client.get(self.index_url)

        # Vérifie que le sélecteur d'exemples est présent
        self.assertContains(response, 'id="exampleSelector"')

        # Vérifie que le context contient bien les poèmes exemples
        self.assertIn('example_poems', response.context)
        example_poems = response.context['example_poems']

        # Vérifie qu'il contient au moins l'option par défaut
        self.assertContains(response, _('Select a text'))

        # Vérifie que chaque exemple est disponible dans le sélecteur
        for key, ex in example_poems.items():
            option_text = f"{ex['doc_name']} – {ex['author']}"
            self.assertContains(response, option_text, html=True)

    def test_index_buttons(self):
        # Vérification boutons page index
        response = self.client.get(self.index_url)

        # Vérifie que les boutons principaux sont présents
        self.assertContains(response, _('Submit'))
        self.assertContains(response, f'href="{self.clear_session_url}"', html=False)
        self.assertContains(response, _('Analyze ZIP'))

