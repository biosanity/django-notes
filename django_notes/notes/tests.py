from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Note

class NotesViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        self.note1 = Note.objects.create(title='Note 1', content='Content 1', author=self.user)
        self.note2 = Note.objects.create(title='Note 2', content='Content 2', author=self.user)
        
    def test_editor_view_create_note(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('home'), data={'title': 'New Note', 'content': 'New Content'})
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Note.objects.filter(title='New Note', content='New Content', author=self.user).exists())
        
    def test_editor_view_edit_note(self):
        response = self.client.post(reverse('home'), data={'title': 'Updated Title', 'content': 'Updated Content', 'note_id': self.note1.pk})
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.title, 'Updated Title')
        self.assertEqual(self.note1.content, 'Updated Content')
        
    def test_delete_note_view(self):
        response = self.client.get(reverse('delete_note', args=[self.note2.id]))
        self.assertEqual(response.status_code, 302)

        self.assertFalse(Note.objects.filter(id=self.note2.id).exists())