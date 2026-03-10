from rest_framework import serializers
from .models import Page, PageVersion, Comment, Attachment

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'

class PageVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageVersion
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'
