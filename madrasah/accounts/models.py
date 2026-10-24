from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# 0. Колдонуучу (User) модели
class User(AbstractUser):
    middle_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Атасынын аты")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон номери")
    role = models.CharField(
        max_length=20, 
        choices=[('student', 'Окуучу'), ('teacher', 'Мугалим'), ('admin', 'Админ')], 
        default='student', 
        verbose_name="Ролу"
    )


# 1. Тайпалар (Гуруҳлар) модели
class Group(models.Model):
    name = models.CharField(max_length=50, verbose_name="Тайпанын аты")  # Мисалы: 1-тайпа
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Түзүлгөн убактысы")

    class Meta:
        verbose_name = "Тайпа"
        verbose_name_plural = "Тайпалар"

    def __str__(self):
        return self.name


# 2. Окуучулар профили
class StudentProfile(models.Model):
    STATUS_CHOICES = (
        ('active', 'Активдүү'),
        ('archive', 'Архив'),
        ('transferred', 'Которулган'),
        ('expelled', 'Чыгарылган'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, verbose_name="Колдонуучу")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Тайпасы")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Абалы (Статусу)")
    
    class Meta:
        verbose_name = "Окуучу профили"
        verbose_name_plural = "Окуучулар профили"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.group})"


# 3. Мугалимдер профили
class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, verbose_name="Мугалим")
    specialty = models.CharField(max_length=100, verbose_name="Адистиги (Сабагы)")  # Мисалы: Фиқҳ, Тажвид
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон номери")

    class Meta:
        verbose_name = "Мугалим профили"
        verbose_name_plural = "Мугалимдер профили"

    def __str__(self):
        return f"Устоз: {self.user.get_full_name()}"


# 4. Сабактар модели
class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Сабактын аты")  # Фиқҳ, Араб тили, Тажвид
    description = models.TextField(blank=True, null=True, verbose_name="Кыскача маалымат")

    class Meta:
        verbose_name = "Сабак"
        verbose_name_plural = "Сабактар"

    def __str__(self):
        return self.name


# 5. Сабак жадыбалы (Schedule)
class Schedule(models.Model):
    time_slot = models.CharField(max_length=50, verbose_name="Убактысы")  # Мисалы: 08:00 - 08:30
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Сабак")
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, verbose_name="Мугалим")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Тайпа")
    room = models.CharField(max_length=20, verbose_name="Кабинет номери")

    class Meta:
        verbose_name = "Сабак жадыбалы"
        verbose_name_plural = "Сабак жадыбалдары"

    def __str__(self):
        return f"{self.time_slot} | {self.subject} ({self.group})"


# 6. Катышуу / Сабакка келбегендер (Attendance)
class Attendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, verbose_name="Окуучу")
    date = models.DateField(verbose_name="Күнү")
    days_missed = models.IntegerField(default=1, verbose_name="Келбеген күндөрү (канча күн)")
    status_note = models.CharField(max_length=100, default="Кечигүү", verbose_name="Абалы / Эскертүү")  # Сабакка келбеди / Кечигүү

    class Meta:
        verbose_name = "Катышуу (Келбегендер)"
        verbose_name_plural = "Катышуу журналы"

    def __str__(self):
        return f"{self.student} | {self.date} ({self.status_note})"


# 7. Электрондук журнал / Баалар (Grade)
class Grade(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, verbose_name="Окуучу")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Сабак")
    score = models.FloatField(verbose_name="Баасы / Балл")  # Мисалы: 5, 4 же 4.7
    term = models.CharField(max_length=50, verbose_name="Чейрек / Мезгил")  # Мисалы: 2-семестр
    date = models.DateField(auto_now_add=True, verbose_name="Коюлган күнү")

    class Meta:
        verbose_name = "Баа"
        verbose_name_plural = "Баалар (Электрондук журнал)"

    def __str__(self):
        return f"{self.student} | {self.subject}: {self.score}"