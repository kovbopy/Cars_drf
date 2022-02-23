from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    owned_cars=serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='car-detail')
    cars_count = serializers.ReadOnlyField(source='owned_cars.count')
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    ips=serializers.SerializerMethodField("_ips",read_only=True)

    all_ips = []
    unique_ips = set()

    def _ips(self, user):
        ip=user.ip
        self.all_ips.append(ip)
        self.unique_ips.add(ip)
        #return {"unique_ips":self.unique_ips,"all_ips":self.all_ips}

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'password', 'password2', 'is_driver','cars_count',
                  'owned_cars',"ips")


    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        if get_user_model().objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "User with this email already exists."})
        return attrs

    def create(self, validated_data):
        is_driver = validated_data.pop('is_driver')
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')
        user = get_user_model().objects.create_user(**validated_data)
        user.is_driver = is_driver
        user.set_password(password)
        user.save()
        return user


