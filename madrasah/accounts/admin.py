from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from madrasah.accounts.models import User
from .models import Group, StudentProfile, TeacherProfile, Subject, Schedule, Attendance, Grade

# 1. User моделини админкага чиқариш
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Медресе маълумотлари', {'fields': ('role', 'phone')}),
    )

# 2. Гуруҳлар учун
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)

# 3. Ўқувчилар профили учун
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'status')
    list_filter = ('group', 'status')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

# 4. Муаллимлар профили учун
@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'phone')
    search_fields = ('user__username', 'specialty')

# 5. Фанлар учун
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# 6. Дарс жадвали учун
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('time_slot', 'subject', 'teacher', 'group', 'room')
    list_filter = ('group', 'subject')

# 7. Давомат учун
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'days_missed', 'status_note')
    list_filter = ('date', 'status_note')

# 8. Баҳолар учун
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'score', 'term', 'date')
    list_filter = ('term', 'subject')