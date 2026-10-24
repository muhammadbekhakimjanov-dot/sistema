from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin-panel/', views.admin_management_view, name='admin_management'),
    path('teachers/', views.teachers_list_view, name='teachers_list'),
    path('students/', views.students_list_view, name='students_list'),
    path('student/<int:student_id>/documents/', views.update_student_documents, name='student_documents'),  # <-- Мана бу янги қўшилди
    path('gradebook/', views.gradebook_view, name='gradebook'),
    path('schedule/', views.schedule_list_view, name='schedule_list'),
    path('exams/', views.exams_list_view, name='exams_list'),
    path('duty-schedule/', views.duty_schedule_list_view, name='duty_schedule_list'),
    path('announcements/', views.announcements_list_view, name='announcements_list'),
    path('audit-log/', views.AuditListView.as_view(), name='audit_list'),
    path('parents/', views.parents_cabinet_view, name='parents_cabinet'),
    path('discipline/', views.discipline_view, name='discipline'),
    path('documents/', views.documents_view, name='documents'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('student/<int:student_id>/pdf/', views.export_student_pdf, name='export_student_pdf'),
    path('accounting/', views.accounting_view, name='accounting'),
    path('quiz/create/', views.quiz_create_view, name='quiz_create'),
    path('quiz/<int:quiz_id>/add-questions/', views.quiz_add_questions_view, name='quiz_add_questions'),
    path('quiz/<int:quiz_id>/take/', views.quiz_take_view, name='quiz_take'),
    path('quiz/results/', views.quiz_results_list_view, name='quiz_results'),
]