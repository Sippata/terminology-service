from rest_framework import serializers

from .models import Handbook, HandbookItem


class HandbookSerializer(serializers.ModelSerializer):
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Handbook
        fields = ['name', 'short_name', 'description', 'version', 'create_date']


class HandbookItemSerializer(serializers.ModelSerializer):
    handbook_name = serializers.CharField(max_length=32, source='handbook.name')

    class Meta:
        model = HandbookItem
        fields = ['handbook_name', 'code', 'content']
