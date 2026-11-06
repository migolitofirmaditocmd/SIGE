from django.urls import path
from .views import ValidateQRTokenView, RenderQRImageView, IssueQRTokenView
from .diagnostics.views import QRScannerTestView

urlpatterns = [
    path('validate/', ValidateQRTokenView.as_view(), name='qr-validate'),
    path('issue/', IssueQRTokenView.as_view(), name='qr-issue'),
    path('scanner/', QRScannerTestView.as_view(), name='qr-test-scanner'),
    path('<uuid:token>/image/', RenderQRImageView.as_view(), name='qr-render-image'),
]
