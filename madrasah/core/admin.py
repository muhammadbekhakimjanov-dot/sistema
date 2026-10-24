from django.contrib import admin
from .models import (
    Teacher, Student, Announcement, Exam, DutySchedule,
    ArchiveDocument, ElectronicJournal, Grade, ParentPortal,
    Accounting, Payment, Schedule, DisciplineRecord, AuditLog, SystemSetting
)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'phone', 'user')
    search_fields = ('name', 'subject')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'contract_amount', 'total_paid', 'remaining_debt', 'phone', 'is_documents_complete')
    list_filter = ('group',)
    search_fields = ('name',)
    fieldsets = (
        ('Негизги маалыматтар', {
            'fields': ('name', 'group', 'contract_amount', 'phone', 'birth_date', 'photo')
        }),
        ('Тапшырылуучу 12 документтер', {
            'fields': (
                'doc_1_application', 'doc_2_passport', 'doc_3_certificate',
                'doc_4_reference', 'doc_5_military', 'doc_6_juvenile',
                'doc_7_no_criminal', 'doc_8_photos', 'doc_9_exam_sheet',
                'doc_10_contract', 'doc_11_parent_passport', 'doc_12_residence'
            )
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'date', 'description')
    search_fields = ('student__name',)
    list_filter = ('date',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('subject', 'group_name', 'date', 'time')

@admin.register(DutySchedule)
class DutyScheduleAdmin(admin.ModelAdmin):
    list_display = ('teacher_name', 'date', 'day_of_week')

@admin.register(ArchiveDocument)
class ArchiveDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')

@admin.register(ElectronicJournal)
class ElectronicJournalAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'grade', 'date')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'subject', 'score', 'date')

@admin.register(ParentPortal)
class ParentPortalAdmin(admin.ModelAdmin):
    list_display = ('parent_name', 'student', 'phone')

@admin.register(Accounting)
class AccountingAdmin(admin.ModelAdmin):
    list_display = ('employee', 'amount', 'month', 'status')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'day_of_week', 'time')

@admin.register(DisciplineRecord)
class DisciplineRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'incident_type', 'date', 'action_type')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'ip_address', 'created_at')
    list_filter = ('action', 'model_name')

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')