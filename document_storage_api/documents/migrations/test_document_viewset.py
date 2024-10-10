import os.path
from unittest import TestCase

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Document


class DocumentViewsetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/documents/"

    def tearDown(self):
        if os.path.exists("documents/test_document.txt"):
            os.remove("documents/test_document.txt")

    def create_test_document(self):
        document_file = SimpleUploadedFile("test_document.txt", b"text content", content_type="application/pdf")
        document_data = {
            "title": "Test Document",
            "file": document_file
        }
        return self.client.post(self.url, document_data, format="multipart")

    def test_create_document(self):
        response = self.create_test_document()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected_data = {
            "id": response.data["id"],
            "title": "Test Document",
            "uploaded_at": response.data["uploaded_at"],
            "file": f"http://testserver/documents/test_document.txt"
        }
        self.assertEqual(response.data, expected_data)

    def test_update_document(self):
        create_response = self.create_test_document()
        document_id = create_response.data["id"]
        update_url = f"{self.url}{document_id}/"

        update_document_file = SimpleUploadedFile("test_document_updated.txt", b"updated content",
                                                  content_type="application/pdf")
        update_document_data = {
            "title": "Updated Test Document",
            "file": update_document_file
        }

        update_response = self.client.put(update_url, update_document_data, format="multipart")
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["title"], "Updated Test Document")

    def test_delete_document(self):
        create_response = self.create_test_document()
        document_id = create_response.data["id"]
        delete_url = f"{self.url}{document_id}/"

        delete_response = self.client.delete(delete_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the document no longer exists
        self.assertFalse(Document.objects.filter(id=document_id).exists())

    def test_retrieve_document(self):
        create_response = self.create_test_document()
        document_id = create_response.data["id"]
        retrieve_url = f"{self.url}{document_id}/"

        retrieve_response = self.client.get(retrieve_url)
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["title"], "Test Document")
        self.assertEqual(retrieve_response.data["id"], document_id)

    def test_partial_update_document(self):
        create_response = self.create_test_document()
        document_id = create_response.data["id"]
        patch_url = f"{self.url}{document_id}/"

        patch_data = {
            "title": "Partially Updated Document"
        }

        patch_response = self.client.patch(patch_url, patch_data, format="json")
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data["title"], "Partially Updated Document")
        self.assertEqual(patch_response.data["id"], document_id)
