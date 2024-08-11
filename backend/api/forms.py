from django import forms
from users.models import User


class CustomUserChangeForm(forms.ModelForm):
    """
    Кастомная форма для шифрования пароля при сохранении в админке
    """
    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'avatar'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
