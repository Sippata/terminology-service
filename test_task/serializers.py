from rest_framework import serializers

from .models import Handbook, HandbookItem


class HandbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Handbook
        fields = ['name', 'short_name', 'description', 'version']


class HandbookItemSerializer(serializers.ModelSerializer):
    handbook_short_name = serializers.CharField(max_length=32, source='handbook.short_name')

    class Meta:
        model = HandbookItem
        fields = ['handbook_short_name', 'code', 'content']
