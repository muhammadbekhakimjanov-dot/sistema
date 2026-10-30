import io
import json
import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView

# ReportLab китепканасы (PDF түзүү үчүн)
from telegram import Update
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from madrasah.accounts.permissions import RoleRequiredMixin
from .models import (
    Announcement,
    Attendance,
    AuditLog,
    DutyLog,
    DutySchedule,
    Exam,
    Grade,
    Payment,
    Accounting,
    Schedule,
    Student,
    Teacher,
    ParentPortal,
    Quiz,
    Question,
    AnswerChoice,
    QuizResult,
    ArchiveDocument,  # <-- Архив модели импортко кошулду
)

# Импорт бота для вебхука
from .telegram_bot import application

User = get_user_model()


# --- TELEGRAM БОТ АРКЫЛУУ ЭСКЕРТҮҮ ЖӨНДӨӨ ФУНКЦИЯСЫ ---
def send_telegram_alert(chat_id, message):
    token = "8723045070:AAGCb6vWDINDNTbKSLYDLthP9_ufxYJq2II"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram API Катасы: {e}")


# --- TELEGRAM WEBHOOK VIEW (ИНТЕРНЕТ ОРҚАЛИ ХАБАР ҚАБУЛ ҚИЛИШ) ---
@csrf_exempt
async def telegram_webhook(request):
    if request.method == 'POST':
        try:
            # Telegram юборган JSON маълумотни ўқиймиз
            data = json.loads(request.body.decode('utf-8'))
            update = Update.de_json(data, application.bot)
            
            # Ботни инициализация қилиш
            if not application.running:
                await application.initialize()
            
            # Янгиликни ботга қайта ишлаш учун узатамиз
            await application.process_update(update)
            
            return JsonResponse({"status": "ok"})
        except Exception as e:
            print(f"Webhook хатолиги: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
            
    return HttpResponse("Фақат POST сўровлар қабул қилинади", status=405)


@login_required
def dashboard(request):
    teachers_count = Teacher.objects.count()
    students_count = Student.objects.count()
    announcements = Announcement.objects.all().order_by("-created_at")[:5]
    exams = Exam.objects.all().order_by("date")[:5]
    duty_teachers = DutyLog.objects.all()[:5]

    ctx = {
        "teachers_count": teachers_count,
        "students_count": students_count,
        "announcements": announcements,
        "exams": exams,
        "duty_teachers": duty_teachers,
        "jaryalar": announcements,
    }

    if request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == "admin":
        role_choices = [
            ("student", "Окуучу"),
            ("teacher", "Мугалим"),
            ("admin", "Админ"),
        ]
        ctx["counts"] = [
            {
                "label": label,
                "count": User.objects.filter(role=code, is_active=True).count(),
            }
            for code, label in role_choices
        ]

    return render(request, "dashboard.html", ctx)


@login_required
def teachers_list_view(request):
    if request.method == "POST" and (request.user.is_superuser or getattr(request.user, "role", "") == "admin"):
        name = request.POST.get("name")
        subject = request.POST.get("subject")
        phone = request.POST.get("phone")
        photo = request.FILES.get("photo")
        if name and subject:
            Teacher.objects.create(name=name, subject=subject, phone=phone, photo=photo)
        return redirect("teachers_list")

    teachers = Teacher.objects.all()
    return render(request, "core/teachers_list.html", {"teachers": teachers})


@login_required
def students_list_view(request):
    if request.method == "POST" and (request.user.is_superuser or getattr(request.user, "role", "") == "admin"):
        name = request.POST.get("name")
        group = request.POST.get("group")
        phone = request.POST.get("phone")
        photo = request.FILES.get("photo")
        
        if name:
            Student.objects.create(name=name, group=group, phone=phone, photo=photo)
        return redirect("students_list")

    students = Student.objects.all()
    return render(request, "core/students_list.html", {"students": students})


@login_required
def update_student_documents(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        student.doc_1_application = request.POST.get("doc_1_application") == "on"
        student.doc_2_passport = request.POST.get("doc_2_passport") == "on"
        student.doc_3_certificate = request.POST.get("doc_3_certificate") == "on"
        student.doc_4_reference = request.POST.get("doc_4_reference") == "on"
        student.doc_5_military = request.POST.get("doc_5_military") == "on"
        student.doc_6_juvenile = request.POST.get("doc_6_juvenile") == "on"
        student.doc_7_no_criminal = request.POST.get("doc_7_no_criminal") == "on"
        student.doc_8_photos = request.POST.get("doc_8_photos") == "on"
        student.doc_9_exam_sheet = request.POST.get("doc_9_exam_sheet") == "on"
        student.doc_10_contract = request.POST.get("doc_10_contract") == "on"
        student.doc_11_parent_passport = request.POST.get("doc_11_parent_passport") == "on"
        student.doc_12_residence = request.POST.get("doc_12_residence") == "on"
        student.save()
        return redirect("students_list")

    return render(request, "core/student_documents.html", {"student": student})


@login_required
def attendance_view(request):
    students = Student.objects.all()
    user = request.user
    role = getattr(user, "role", "")

    if request.method == "POST" and (user.is_staff or role in ["admin", "teacher"] or user.is_superuser):
        date = request.POST.get("date")
        for student in students:
            status = request.POST.get(f"status_{student.id}", "present")
            note = request.POST.get(f"note_{student.id}", "")
            
            Attendance.objects.update_or_create(
                student=student,
                date=date,
                defaults={'status': status, 'note': note}
            )

            if status == 'absent':
                parent = ParentPortal.objects.filter(student=student).first()
                if parent and hasattr(parent, 'telegram_chat_id') and parent.telegram_chat_id:
                    msg = (
                        f"📌 *Имам Аль-Бухорий медресеси*\n\n"
                        f"Урматтуу ата-эне *{parent.parent_name}*!\n"
                        f"Сиздин балаңыз/кызыңыз *{student.name}* ({student.group}) "
                        f"бүгүнкү сабакка келген жок.\n"
                        f"📅 Күнү: {date}"
                    )
                    send_telegram_alert(parent.telegram_chat_id, msg)

        return redirect("attendance")

    recent_attendances = Attendance.objects.select_related('student').order_by("-date")[:50]
    return render(request, "core/attendance_list.html", {
        "students": students,
        "attendances": recent_attendances
    })


@login_required
def schedule_list_view(request):
    schedules = Schedule.objects.all()
    return render(request, "core/schedule_list.html", {"schedules": schedules})


@login_required
def exams_list_view(request):
    exams = Exam.objects.all().order_by("date")
    quizzes = Quiz.objects.filter(is_active=True).order_by("-id")
    return render(request, "core/exams_list.html", {"exams": exams, "quizzes": quizzes})


@login_required
def duty_schedule_list_view(request):
    if request.method == "POST":
        teacher_id = request.POST.get("teacher_id")
        shift = request.POST.get("shift")
        date = request.POST.get("date")
        teachers_attendance = request.POST.get("teachers_attendance")
        students_attendance = request.POST.get("students_attendance")
        note = request.POST.get("note", "")

        if teacher_id:
            teacher_obj = Teacher.objects.filter(id=teacher_id).first()
            DutyLog.objects.create(
                teacher=teacher_obj,
                shift=shift,
                date=date,
                teachers_attendance=teachers_attendance,
                students_attendance=students_attendance,
                note=note
            )
        return redirect("duty_schedule_list")

    teachers = Teacher.objects.all()
    duties = DutyLog.objects.all().order_by("-date")
    return render(request, "core/duty_schedule_list.html", {"teachers": teachers, "duties": duties})


@login_required
def announcements_list_view(request):
    if request.method == "POST" and (request.user.is_superuser or getattr(request.user, "role", "") == "admin"):
        title = request.POST.get("title")
        content = request.POST.get("content")
        if title and content:
            Announcement.objects.create(title=title, content=content)
        return redirect("announcements_list")

    announcements = Announcement.objects.all().order_by("-created_at")
    return render(request, "core/announcements_list.html", {"announcements": announcements})


@login_required
def parents_cabinet_view(request):
    user = request.user
    role = getattr(user, "role", "")

    if role == "student" or not user.is_superuser and role != "admin":
        students = Student.objects.filter(name__icontains=user.username).prefetch_related('grades', 'attendances')
        if not students.exists():
            students = Student.objects.all().prefetch_related('grades', 'attendances')
    else:
        students = Student.objects.all().prefetch_related('grades', 'attendances')

    return render(request, "core/parents_list.html", {"students": students})


@login_required
def discipline_view(request):
    students = Student.objects.all()
    return render(request, "core/discipline_list.html", {"students": students})


@login_required
def documents_view(request):
    documents = ArchiveDocument.objects.all().order_by("-uploaded_at")
    if request.method == "POST" and (request.user.is_superuser or getattr(request.user, "role", "") == "admin"):
        title = request.POST.get("title")
        file = request.FILES.get("file")
        if title and file:
            ArchiveDocument.objects.create(title=title, file=file)
            return redirect("documents")
    return render(request, "core/documents_list.html", {"documents": documents})


@login_required
def gradebook_view(request):
    user = request.user
    role = getattr(user, "role", "")

    if role == "student":
        grades = Grade.objects.filter(student__name__icontains=user.username).order_by("-date")
    elif role == "teacher":
        try:
            teacher_obj = Teacher.objects.get(user=user)
            grades = Grade.objects.filter(teacher=teacher_obj).order_by("-date")
        except Teacher.DoesNotExist:
            grades = Grade.objects.none()
    else:
        grades = Grade.objects.all().order_by("-date")

    if request.method == "POST" and (user.is_staff or role == "admin" or role == "teacher"):
        student_id = request.POST.get("student")
        subject = request.POST.get("subject")
        score = request.POST.get("score")
        comment = request.POST.get("comment", "")

        if student_id and subject and score:
            student = get_object_or_404(Student, id=student_id)
            teacher_obj = None
            if role == "teacher":
                teacher_obj = Teacher.objects.filter(user=user).first()

            Grade.objects.create(student=student, subject=subject, score=score, comment=comment, teacher=teacher_obj)
            return redirect("gradebook")

    students = Student.objects.all()
    return render(request, "core/gradebook.html", {"grades": grades, "students": students})


@login_required
def admin_management_view(request):
    user = request.user
    role = getattr(user, "role", "")
    if role != "admin" and not user.is_superuser:
        return redirect("dashboard")

    context = {
        "teachers": Teacher.objects.all(),
        "students": Student.objects.all(),
        "announcements": Announcement.objects.all(),
    }
    return render(request, "core/admin_management.html", context)


class AuditListView(RoleRequiredMixin, ListView):
    allowed_roles = ["admin"]
    model = AuditLog
    template_name = "core/audit_list.html"
    paginate_by = 50


@login_required
def accounting_view(request):
    students = Student.objects.all()
    payments = Payment.objects.select_related('student').order_by('-date')
    accountings = Accounting.objects.all().order_by('-id')

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "payment":
            student_id = request.POST.get("student_id")
            amount = request.POST.get("amount")
            description = request.POST.get("description", "")
            if student_id and amount:
                student_obj = Student.objects.filter(id=student_id).first()
                Payment.objects.create(student=student_obj, amount=amount, description=description)
            return redirect("accounting")

        elif form_type == "salary":
            employee = request.POST.get("employee")
            amount = request.POST.get("amount")
            month = request.POST.get("month")
            if employee and amount:
                Accounting.objects.create(employee=employee, amount=amount, month=month)
            return redirect("accounting")

        elif form_type == "set_contract":
            student_id = request.POST.get("student_id")
            contract_amount = request.POST.get("contract_amount")
            if student_id and contract_amount:
                student_obj = Student.objects.filter(id=student_id).first()
                if student_obj:
                    student_obj.contract_amount = contract_amount
                    student_obj.save()
            return redirect("accounting")

    context = {"students": students, "payments": payments, "accountings": accountings}
    return render(request, "core/accounting_list.html", context)


@login_required
def export_student_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, alignment=1, spaceAfter=15)
    story.append(Paragraph("<b>ИМАМ АЛЬ-БУХАРИЙ МЕДРЕСЕСИ</b>", title_style))
    story.append(Paragraph("<b>Студенттин карточкасы жана документтер абалы</b>", styles['Heading2']))
    story.append(Spacer(1, 10))

    info_data = [
        ["Аты-жөнү:", student.name],
        ["Тайпасы:", student.group],
        ["Телефон номери:", student.phone or "Көрсөтүлгөн эмес"],
        ["Туулган күнү:", str(student.birth_date) if student.birth_date else "Көрсөтүлгөн эмес"],
        ["Документтер абалы:", "ТОЛУК" if student.is_documents_complete else f"Жетишпегени: {student.missing_documents_count} та"]
    ]
    info_table = Table(info_data, colWidths=[150, 350])
    info_table.setStyle(TableStyle([('BACKGROUND', (0,0), (0,-1), colors.lightgrey), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(info_table)
    story.append(Spacer(1, 15))

    doc.build(story)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={'Content-Disposition': f'attachment; filename="student_{student.id}.pdf"'})


# --- ОНЛАЙН ТЕСТ ФУНКЦИЯЛАРЫ ---
@login_required
def quiz_create_view(request):
    user = request.user
    role = getattr(user, "role", "")
    if not (user.is_superuser or user.is_staff or role in ["admin", "teacher"]):
        return redirect("exams_list")

    if request.method == "POST":
        title = request.POST.get("title")
        subject = request.POST.get("subject")
        group_name = request.POST.get("group_name")
        time_limit = request.POST.get("time_limit", 30)

        if title and subject:
            quiz = Quiz.objects.create(title=title, subject=subject, group_name=group_name, time_limit_minutes=time_limit)
            return redirect("quiz_add_questions", quiz_id=quiz.id)

    return render(request, "core/quiz_create.html")


@login_required
def quiz_add_questions_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user = request.user
    role = getattr(user, "role", "")
    if not (user.is_superuser or user.is_staff or role in ["admin", "teacher"]):
        return redirect("exams_list")

    if request.method == "POST":
        question_text = request.POST.get("question_text")
        choice1 = request.POST.get("choice1")
        choice2 = request.POST.get("choice2")
        choice3 = request.POST.get("choice3")
        choice4 = request.POST.get("choice4")
        correct_choice = request.POST.get("correct_choice")

        if question_text and choice1 and choice2:
            question = Question.objects.create(quiz=quiz, text=question_text)
            choices = [("1", choice1), ("2", choice2), ("3", choice3), ("4", choice4)]
            for code, text in choices:
                if text:
                    AnswerChoice.objects.create(question=question, text=text, is_correct=(code == correct_choice))
            return redirect("quiz_add_questions", quiz_id=quiz.id)

    questions = quiz.questions.prefetch_related('choices').all()
    return render(request, "core/quiz_add_questions.html", {"quiz": quiz, "questions": questions})


@login_required
def quiz_take_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == "POST":
        score = 0
        questions = quiz.questions.all()
        total_questions = questions.count()

        for question in questions:
            selected_choice_id = request.POST.get(f"question_{question.id}")
            if selected_choice_id:
                selected_choice = AnswerChoice.objects.filter(id=selected_choice_id, is_correct=True).first()
                if selected_choice:
                    score += 1

        QuizResult.objects.create(quiz=quiz, student_name=request.user.username, score=score, total_questions=total_questions)
        return render(request, "core/quiz_result.html", {"quiz": quiz, "score": score, "total_questions": total_questions, "percentage": round((score / total_questions) * 100) if total_questions > 0 else 0})

    return render(request, "core/quiz_take.html", {"quiz": quiz})


@login_required
def quiz_results_list_view(request):
    results = QuizResult.objects.select_related('quiz').order_by('-completed_at')
    return render(request, "core/quiz_results_list.html", {"results": results})