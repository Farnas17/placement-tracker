from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import Task
from .serializers import TaskSerializer


# =========================
# USER REGISTRATION
# =========================
def register_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Username already exists"
            })

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)
        return redirect("dashboard-ui")

    return render(request, "register.html")


# =========================
# TOKEN LOGIN (Mobile)
# =========================
@api_view(['POST'])
def api_login(request):

    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({"error": "Invalid credentials"}, status=400)

    token, created = Token.objects.get_or_create(user=user)

    return Response({"token": token.key})


# =========================
# TASK LIST + CREATE
# =========================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_list_create(request):

    if request.method == 'GET':
        tasks = Task.objects.filter(user=request.user).order_by('-created_at')
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================
# UPDATE + DELETE
# =========================
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_task(request, pk):

    try:
        task = Task.objects.get(pk=pk, user=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=404)

    if request.method == 'DELETE':
        task.delete()
        return Response({'message': 'Deleted successfully'})

    serializer = TaskSerializer(task, data=request.data, partial=True)

    if serializer.is_valid():
        updated_task = serializer.save()

        if updated_task.status == 'completed':
            updated_task.date_completed = timezone.now().date()
        else:
            updated_task.date_completed = None

        updated_task.save()

        return Response(TaskSerializer(updated_task).data)

    return Response(serializer.errors, status=400)


# =========================
# DASHBOARD API
# =========================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):

    user = request.user
    today = timezone.now().date()

    total_tasks = Task.objects.filter(user=user).count()
    completed_tasks = Task.objects.filter(user=user, status='completed').count()
    pending_tasks = Task.objects.filter(user=user, status='pending').count()

    completion_percentage = round((completed_tasks / total_tasks) * 100, 2) if total_tasks > 0 else 0

    last_7_days = today - timedelta(days=7)

    weekly_completed = Task.objects.filter(
        user=user,
        status='completed',
        date_completed__gte=last_7_days
    ).count()

    weekly_consistency = min(round((weekly_completed / 7) * 100, 2), 100)

    streak = 0
    completed_dates = Task.objects.filter(
        user=user,
        status='completed'
    ).values_list('date_completed', flat=True)

    unique_days = sorted(set(completed_dates), reverse=True)
    current_day = today

    for d in unique_days:
        if d == current_day:
            streak += 1
            current_day -= timedelta(days=1)
        else:
            break

    streak_score = min(streak * 10, 100)

    weekly_labels = []
    weekly_counts = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Task.objects.filter(
            user=user,
            status='completed',
            date_completed=day
        ).count()

        weekly_labels.append(day.strftime("%a"))
        weekly_counts.append(count)

    category_stats = (
        Task.objects
        .filter(user=user)
        .values('category')
        .annotate(count=Count('id'))
    )

    weekly_insights = []

    if weekly_consistency < 40:
        weekly_insights.append("Low weekly consistency. Increase daily execution.")

    if pending_tasks > completed_tasks:
        weekly_insights.append("Backlog increasing. Clear pending tasks.")

    if streak >= 3:
        weekly_insights.append("Strong streak momentum. Stay consistent.")

    if not weekly_insights:
        weekly_insights.append("Good progress this week. Maintain focus.")

    readiness_score = round(
        (completion_percentage * 0.4) +
        (weekly_consistency * 0.3) +
        (streak_score * 0.3),
        2
    )

    return Response({
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "readiness_score": readiness_score,
        "weekly_trend_labels": weekly_labels,
        "weekly_trend_counts": weekly_counts,
        "category_breakdown": category_stats,
        "weekly_insights": weekly_insights
    })


# =========================
# UI PAGES
# =========================
@login_required
def dashboard_page(request):
    return render(request, "dashboard.html")


@login_required
def tasks_page(request):
    return render(request, "tasks.html")