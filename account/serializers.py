from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=1, required=True)
    password_confirm = serializers.CharField(min_length=1, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name')

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Такой пользователь уже существует')
        return email

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.create_activate_code()
        User.send_activation_mail(user.email, user.activation_code)
        return user


class ActivationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    activation_code = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        activation_code = attrs.get('activation_code')
        if not User.objects.filter(email=email, activation_code=activation_code).exists():
            raise serializers.ValidationError('Пользователь не найден')
        return attrs

    def activate(self):
        data = self.validated_data
        user = User.objects.get(**data)
        user.is_active = True
        user.activation_code = ''
        user.save()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password, request=self.context.get('request'))
            if not user:
                raise serializers.ValidationError('Неверно указан email или пароль')
        else:
            raise serializers.ValidationError('Email и пароль обязательны')
        attrs['user'] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Такого пользователя нет!')
        return email

    def send_reset_email(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.create_activate_code()
        message = f"Код для смены пароля: {user.activation_code}"
        send_mail(
            'Смена пароля',
            message,
            'badumkgz@gmail.com',
            [email]
        )


class CreateNewPasswordSerializer(serializers.Serializer):
    activation_code = serializers.CharField(required=True)
    password = serializers.CharField(min_length=1, required=True)
    password_confirm = serializers.CharField(min_length=1, required=True)

    def validate_activation_code(self, code):
        if not User.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError('Неверный код активации')
        return code

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def create_pass(self):
        code = self.validated_data.get('activation_code')
        password = self.validated_data.get('password')
        user = User.objects.get(activation_code=code)
        user.set_password(password)
        user.save()


