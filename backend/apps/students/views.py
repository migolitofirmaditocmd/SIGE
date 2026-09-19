from rest_framework import viewsets, filters
from .models import Guardian, Student
from .serializers import GuardianSerializer, StudentSerializer

class GuardianViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para tutores legales.
    """
    queryset = Guardian.objects.all().prefetch_related('students')
    serializer_class = GuardianSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'phone_number', 'email']
    ordering_fields = ['full_name', 'created_at']
    ordering = ['full_name']


class StudentViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para estudiantes de la Escuela Secundaria Mixta 5.
    Permite búsqueda por matrícula, CURP, apellidos y filtrado por grado y grupo.
    """
    queryset = Student.objects.all().select_related('guardian').prefetch_related('qr_tokens')
    serializer_class = StudentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['enrollment_id', 'curp', 'first_name', 'last_name_father', 'last_name_mother']
    ordering_fields = ['grade', 'group', 'last_name_father', 'created_at']
    ordering = ['grade', 'group', 'last_name_father']

    def get_queryset(self):
        qs = super().get_queryset()
        grade = self.request.query_params.get('grade')
        group = self.request.query_params.get('group')
        shift = self.request.query_params.get('shift')
        status = self.request.query_params.get('status')

        if grade:
            qs = qs.filter(grade=grade)
        if group:
            qs = qs.filter(group=group.upper())
        if shift:
            qs = qs.filter(shift=shift.upper())
        if status:
            qs = qs.filter(status=status.upper())
        return qs
