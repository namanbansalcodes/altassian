from rest_framework import viewsets
from .models import Page, PageVersion, Comment, Attachment
from .serializers import PageSerializer, PageVersionSerializer, CommentSerializer, AttachmentSerializer

class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer

class PageVersionViewSet(viewsets.ModelViewSet):
    queryset = PageVersion.objects.all()
    serializer_class = PageVersionSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
