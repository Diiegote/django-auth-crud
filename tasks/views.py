from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse as response
from django.contrib.auth import login, logout, authenticate
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, "signup.html", {'form': UserCreationForm})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except:
                return render(request, "signup.html", {'form': UserCreationForm, 'errors': 'User already exists'})
        return render(request, "signup.html", {'form': UserCreationForm, 'errors': 'Password do not match'})
#Usamos @login_required para que el usuario no pueda entrar a las paginas si no esta logiado. En setting creamos una variable LOGIN_URL = '/signin' al final de todo para que nos pueda redireccionar a /signin
@login_required
def tasks(request):
    # filtramos las tareas que pertenezcan a un usuario y tambien filtramos por el campo de datecompleted(le agregamos __isnull=True) para que muestre las tareas que no estan completadas
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {"tasks": tasks})
@login_required
def tasks_completed(request):
    # lo mismo que arriba pero solo que ahora nos muestra las tareas que ya estan completas
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False)
    return render(request, 'tasks.html', {"tasks": tasks})
@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_tasks.html', {
            'form': TaskForm
        })
    else:
        try:
            # Usamos TaskForm para guardar los datos en el formulario.(recordar que TaskForm es una clase que creamos nosotros en el archivo forms.py)
            form = TaskForm(request.POST)
            # Guardamos el formulario pero usamos el commit=False para que se muestre y no se guarde
            new_task = form.save(commit=False)
            new_task.user = request.user  # Aca le decimos a que usuario pertenece
            new_task.save()  # Y aca si lo guardamos en la base de datos
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_tasks.html', {
                'form': TaskForm,
                'error': 'Por favor completa los campos'
            })
@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        # Buscamos una tarea por su id y al usuario que le pertenece
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        # Aca guardamos en la variable form lo que ya tiene la tarea para poder actualizar
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Error updating task'})
@login_required
def complete_task(request, task_id):
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        if request.method == 'POST':
             task.datecompleted = timezone.now() 
             task.save()
             return redirect('tasks')
@login_required
def delete_task(request, task_id):
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        if request.method == 'POST':
             task.delete()
             return redirect('tasks')
@login_required   
def cerrar_session(request):
    logout(request)
    return redirect('home')
def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request,
                            username=request.POST['username'],
                            password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        else:
            login(request, user)
            return redirect('tasks')
