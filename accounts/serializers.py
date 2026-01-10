from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "company",
            "country",
            "phone",
            "password",
            "confirm_password",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "first_name": {"required": False, "allow_blank": True},
            "last_name": {"required": False, "allow_blank": True},
            "company": {"required": False, "allow_blank": True},
            "country": {"required": False, "allow_blank": True},
            "phone": {"required": False, "allow_blank": True},
        }

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        validated_data.setdefault("company", "")
        validated_data.setdefault("country", "")
        validated_data.setdefault("phone", "")

        user = User.objects.create_user(**validated_data)
        return user
