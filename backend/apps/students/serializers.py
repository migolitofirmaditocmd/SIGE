from rest_framework import serializers
from .models import Guardian, Student

class GuardianSerializer(serializers.ModelSerializer):
    relationship_display = serializers.CharField(source='get_relationship_display', read_only=True)

    class Meta:
        model = Guardian
        fields = [
            'id',
            'full_name',
            'phone_number',
            'relationship',
            'relationship_display',
            'email',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentSerializer(serializers.ModelSerializer):
    guardian_detail = GuardianSerializer(source='guardian', read_only=True)
    full_name = serializers.CharField(read_only=True)
    academic_group = serializers.CharField(read_only=True)
    active_qr_token_id = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id',
            'enrollment_id',
            'curp',
            'first_name',
            'last_name_father',
            'last_name_mother',
            'full_name',
            'grade',
            'group',
            'shift',
            'academic_group',
            'status',
            'medical_notes',
            'guardian',
            'guardian_detail',
            'active_qr_token_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_active_qr_token_id(self, obj):
        token = obj.active_qr_token
        return str(token.token) if token else None
