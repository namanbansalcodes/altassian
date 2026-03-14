from rest_framework_simplejwt.views import TokenObtainPairView

from .auth_serializers import FastTokenObtainPairSerializer


class FastTokenObtainPairView(TokenObtainPairView):
    serializer_class = FastTokenObtainPairSerializer
