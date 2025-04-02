from django.views import View
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import copy

from . import models
from . import forms

class BasePerfil(View):
    template_name = 'perfil/criar.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.carrinho = copy.deepcopy(self.request.session.get('carrinho', {}))

        self.perfil = None

        if self.request.user.is_authenticated:
            self.perfil = models.Perfil.objects.filter(
                usuario=self.request.user).first()

            self.contexto = {
                'userForm':forms.UserForm(
                    data=self.request.POST or None,
                    usuario=self.request.user,
                    instance= self.request.user,
                    ),
                'perfilForm':forms.PerfilForm(
                    data=self.request.POST or None
                    ),

            }
        else:
            self.contexto = {
                'userForm':forms.UserForm(
                    data=self.request.POST or None
                    ),
                'perfilForm':forms.PerfilForm(
                    data=self.request.POST or None, 
                    instance=self.perfil 
                    ),

            }

        self.userform = self.contexto['userForm']
        self.perfilform = self.contexto['perfilForm']

        if self.request.user.is_authenticated:
            self.template_name = 'perfil/atualizar.html'

        self.renderizar = render(self.request, self.template_name, self.contexto)

    def get(self, *args, **kwargs):
        return self.renderizar

class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        if not self.userform.is_valid() or not self.perfilform.is_valid():
            messages.error(
                self.request,
                'Existe algum erro no formulário de cadastro. Por favor revise seus dados.'
            )
            return self.renderizar

        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('password')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')
        email = self.userform.cleaned_data.get('email')

        if self.request.user.is_authenticated:
            usuario = get_object_or_404(
                User, username=self.request.user.username)  # type: ignore
            usuario.username = username  # type: ignore

            if not self.perfil:
                # Garante que o perfil seja salvo corretamente
                self.perfilform.cleaned_data['usuario'] = usuario
                perfil = models.Perfil(**self.perfilform.cleaned_data)
                perfil.save()

            else:
                perfil = self.perfilform.save(commit=False)
                perfil.usuario = usuario
                perfil.save()

            if password:
                usuario.set_password(password)

            usuario.email = email  # type: ignore
            usuario.first_name = first_name  # type: ignore
            usuario.last_name = last_name  # type: ignore

            usuario.save()

            # Recupera ou cria o perfil para o usuário
            perfil, created = models.Perfil.objects.get_or_create(usuario=usuario)
            # Atualiza os dados do perfil com os dados do formulário
            perfil_form_instance = self.perfilform.save(commit=False)
            # Copia os dados do formulário para o objeto perfil
            for field, value in self.perfilform.cleaned_data.items():
                setattr(perfil, field, value)
            perfil.usuario = usuario  # Garantindo a associação
            perfil.save()

        else:
            usuario = self.userform.save(commit=False)
            usuario.set_password(password)
            usuario.save()

            perfil = self.perfilform.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

        if password:
            autentica = authenticate(
                self.request,
                username=usuario.username,  # Corrigido para username
                password=password)
            
            if autentica:
                login(self.request, user=usuario)

        self.request.session['carrinho'] = self.carrinho
        self.request.session.save()

        messages.success(
            self.request,
            'Seu cadastro foi criado ou atualizado com sucesso.'
        )

        messages.success(
            self.request,
            'Você fez login e pode concluir sua compra.'
        )

        return redirect('produto:carrinho')


class Atualizar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Atualizar')

class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        if not username or not password:
            messages.error(
            self.request,
            'Usuário ou senha inválida.'
        )
            return redirect('perfil:criar')
        
        usuario = authenticate(
            self.request,
            username=username, password=password)
        
        if not usuario:
            messages.error(
            self.request,
            'Usuário ou senha inválida.'
        )
            return redirect('perfil:criar')
        
        login(self.request, user=usuario)
        messages.success(
            self.request,
            'Você fez login no sistema.'
        )
        return redirect('produto:carrinho')

class Logout(View):
    def get(self, *args, **kwargs):
        carrinho = copy.deepcopy(self.request.session.get('carrinho'))
        
        logout(self.request)

        self.request.session['carrinho'] = carrinho
        self.request.session.save()

        return redirect('produto:lista')