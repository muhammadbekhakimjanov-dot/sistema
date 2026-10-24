import requests
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
    )
    action = models.CharField('Аракет', max_length=50)
    model_name = models.CharField('Объект', max_length=100)
    object_id = models.CharField(max_length=50, blank=True)
    details = models.JSONField('Деталдар', default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Аракеттер тарыхы'
        verbose_name_plural = 'Аракеттер тарыхы'

    def __str__(self):
        return f"{self.action} - {self.model_name} ({self.created_at})"


class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name='Ачкыч')
    value = models.TextField(blank=True, verbose_name='Мааниси')
    description = models.TextField(blank=True, verbose_name='Сүрөттөмө')

    class Meta:
        verbose_name = 'Системалык жөндөө'
        verbose_name_plural = 'Системалык жөндөөлөр'

    def __str__(self):
        return self.key


class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Колдонуучу (Логин)'
    )
    photo = models.ImageField(
        upload_to='teachers/', blank=True, null=True, verbose_name='Сүрөтү'
    )
    name = models.CharField(max_length=100, verbose_name='Аты-жөнү')
    subject = models.CharField(max_length=100, verbose_name='Предмети')
    phone = models.CharField(max_length=20, verbose_name='Телефон номери')

    class Meta:
        verbose_name = 'Мугалим'
        verbose_name_plural = 'Мугалимдер'

    def __str__(self):
        return self.name


class Student(models.Model):
    photo = models.ImageField(
        upload_to='students/', blank=True, null=True, verbose_name='Сүрөтү'
    )
    name = models.CharField(max_length=100, verbose_name='Аты-жөнү')
    group = models.CharField(max_length=50, verbose_name='Тайпасы')
    birth_date = models.DateField(
        null=True, blank=True, verbose_name='Туулган күнү'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон номери')

    contract_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name='Контракт суммасы'
    )

    doc_1_application = models.BooleanField(default=False, verbose_name='1. Мүдүрдүн атына арыз')
    doc_2_passport = models.BooleanField(default=False, verbose_name='2. Паспорт же туулгандыгы тууралуу күбөлүк')
    doc_3_certificate = models.BooleanField(default=False, verbose_name='3. 9-классты бүтүргөндүгү күбөлүк/аттестат/диплом')
    doc_4_reference = models.BooleanField(default=False, verbose_name='4. Акыркы окуган/иштеген жеринен мүнөздөмө')
    doc_5_military = models.BooleanField(default=False, verbose_name='5. Аскердик каттоо күбөлүгү же приписной')
    doc_6_juvenile = models.BooleanField(default=False, verbose_name='6. ИИБдө ИЖИ каттоодо турбайт деген маалымат')
    doc_7_no_criminal = models.BooleanField(default=False, verbose_name='7. Соттолгон эмес деген маалымат')
    doc_8_photos = models.BooleanField(default=False, verbose_name='8. 3x4 өлчөмүндөгү сүрөт (6 даана)')
    doc_9_exam_sheet = models.BooleanField(default=False, verbose_name='9. Кабыл алуу сынагынын ведомосту')
    doc_10_contract = models.BooleanField(default=False, verbose_name='10. Келишим')
    doc_11_parent_passport = models.BooleanField(default=False, verbose_name='11. Ата-энесинин паспортунан көчүрмө')
    doc_12_residence = models.BooleanField(default=False, verbose_name='12. Жашаган жеринен маалымат')

    @property
    def is_documents_complete(self):
        docs = [
            self.doc_1_application, self.doc_2_passport, self.doc_3_certificate,
            self.doc_4_reference, self.doc_5_military, self.doc_6_juvenile,
            self.doc_7_no_criminal, self.doc_8_photos, self.doc_9_exam_sheet,
            self.doc_10_contract, self.doc_11_parent_passport, self.doc_12_residence
        ]
        return all(docs)

    @property
    def missing_documents_count(self):
        docs = [
            self.doc_1_application, self.doc_2_passport, self.doc_3_certificate,
            self.doc_4_reference, self.doc_5_military, self.doc_6_juvenile,
            self.doc_7_no_criminal, self.doc_8_photos, self.doc_9_exam_sheet,
            self.doc_10_contract, self.doc_11_parent_passport, self.doc_12_residence
        ]
        return docs.count(False)

    @property
    def total_paid(self):
        payments = self.payments.all()
        return sum(p.amount for p in payments) if payments else 0

    @property
    def remaining_debt(self):
        debt = float(self.contract_amount) - float(self.total_paid)
        return debt if debt > 0 else 0

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенттер'

    def __str__(self):
        return self.name


class Announcement(models.Model):
    title = models.CharField(max_length=200, verbose_name='Аталышы')
    content = models.TextField(verbose_name='Мазмуну')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Кошулган убакыты'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Жарыя'
        verbose_name_plural = 'Жарыялар'


class Exam(models.Model):
    subject = models.CharField(max_length=100, verbose_name='Фан')
    group_name = models.CharField(max_length=50, verbose_name='Тайпа (Гуруҳ)')
    date = models.DateField(verbose_name='Күнү')
    time = models.TimeField(verbose_name='Убакыты')

    def __str__(self):
        return f'{self.subject} - {self.group_name} ({self.date})'

    class Meta:
        verbose_name = 'Экзамен'
        verbose_name_plural = 'Экзамендер'


class DutySchedule(models.Model):
    teacher_name = models.CharField(max_length=100, verbose_name='Мугалимдин аты-жөнү')
    date = models.DateField(verbose_name='Кезекчилик күнү')
    day_of_week = models.CharField(max_length=50, verbose_name='Апта күнү')

    def __str__(self):
        return f'{self.teacher_name} ({self.date})'

    class Meta:
        verbose_name = 'Нөөмөтчү мугалим'
        verbose_name_plural = 'Нөөмөтчү мугалимдер'


class ArchiveDocument(models.Model):
    title = models.CharField(max_length=200, verbose_name='Документтин аты')
    file = models.FileField(upload_to='archive_pdfs/', verbose_name='PDF Файл')
    uploaded_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Жүктөлгөн убакыты'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Архив документи'
        verbose_name_plural = 'Архив документтери'


class ElectronicJournal(models.Model):
    student = models.ForeignKey(
        'Student', on_delete=models.CASCADE, verbose_name='Окуучу'
    )
    subject = models.CharField(max_length=100, verbose_name='Фан')
    grade = models.IntegerField(verbose_name='Баасы')
    date = models.DateField(auto_now_add=True, verbose_name='Күнү')

    def __str__(self):
        return f'{self.student} - {self.subject}: {self.grade}'

    class Meta:
        verbose_name = 'Электрондук журнал'
        verbose_name_plural = 'Электрондук журнал'


class Grade(models.Model):
    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='Студент',
    )
    teacher = models.ForeignKey(
        'Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Мугалим',
    )
    subject = models.CharField(max_length=100, verbose_name='Предмет / Фан')
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name='Баа / Балл',
    )
    date = models.DateField(auto_now_add=True, verbose_name='Дата')
    comment = models.CharField(
        max_length=255, blank=True, null=True, verbose_name='Изох / Комментарий'
    )

    class Meta:
        verbose_name = 'Баа'
        verbose_name_plural = 'Баалар журналы'
        ordering = ['-date']

    def __str__(self):
        return f'{self.student} - {self.subject}: {self.score}'


class ParentPortal(models.Model):
    parent_name = models.CharField(max_length=100, verbose_name='Ата-эненин аты-жөнү')
    student = models.ForeignKey('Student', on_delete=models.CASCADE, verbose_name='Окуучу')
    phone = models.CharField(max_length=20, verbose_name='Телефон номери')
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='Telegram Chat ID')

    def __str__(self):
        return f'{self.parent_name} ({self.student})'

    class Meta:
        verbose_name = 'Ата-эне кабинети'
        verbose_name_plural = 'Ата-энелер кабинети'


class Accounting(models.Model):
    employee = models.CharField(max_length=100, verbose_name='Кызматкер / Мугалим')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Айлык акы / Сумма')
    month = models.CharField(max_length=50, verbose_name='Ай (Мезгил)')
    status = models.CharField(max_length=50, default='Төлөндү', verbose_name='Статусу')

    def __str__(self):
        return f'{self.employee} - {self.amount} сом'

    class Meta:
        verbose_name = 'Бухгалтерия'
        verbose_name_plural = 'Бухгалтерия ва айлык акы'


class Schedule(models.Model):
    subject = models.CharField(max_length=100, verbose_name='Предмет')
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, verbose_name='Мугалим')
    day_of_week = models.CharField(max_length=50, verbose_name='Апта күнү')
    time = models.TimeField(verbose_name='Убакыты')

    def __str__(self):
        return f'{self.subject} ({self.day_of_week} - {self.time})'

    class Meta:
        verbose_name = 'Сабак расписаниеси'
        verbose_name_plural = 'Сабактар жана расписание'


class DisciplineRecord(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, verbose_name='Окуучу')
    incident_type = models.CharField(max_length=100, verbose_name='Тартип бузуу же эскертүү')
    date = models.DateField(auto_now_add=True, verbose_name='Күнү')
    action_type = models.CharField(max_length=255, verbose_name='Көрүлгөн чара', blank=True)

    def __str__(self):
        return f'{self.student} - {self.incident_type}'

    class Meta:
        verbose_name = 'Тартип жазуусу'
        verbose_name_plural = 'Тартип жана балдар'


class DutyLog(models.Model):
    SHIFT_CHOICES = (
        ('day', 'Кундузги смена (08:00 - 17:00)'),
        ('night', 'Кечки смена (17:00 - 08:00)'),
    )
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, verbose_name="Дежур мугалим")
    date = models.DateField(auto_now_add=True, verbose_name="Күнү")
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES, default='day', verbose_name="Сменасы")
    teachers_attendance = models.TextField(blank=True, null=True, verbose_name="Устозрлордун келгени / келбегени")
    students_attendance = models.TextField(blank=True, null=True, verbose_name="Окуучулардын келгени жана себептери")
    note = models.TextField(blank=True, null=True, verbose_name="Кошумча эскертүү")

    class Meta:
        verbose_name = "Дежур назорат журналы"
        verbose_name_plural = "Дежур мугалимдер журналы (Архив)"
        ordering = ['-date']

    def __str__(self):
        return f"{self.teacher.name} - {self.date} ({self.get_shift_display()})"


class Attendance(models.Model):
    """Окуучулардын сабакка катышуусу (Давомат) ва Telegram хабарномаси"""
    STATUS_CHOICES = (
        ('present', 'Катышты (Келди)'),
        ('absent', 'Катышкан жок (Келген жок)'),
        ('late', 'Кечикти (Кечиккени)'),
        ('excused', 'Себептүү (Сабабли)'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances', verbose_name="Окуучу")
    date = models.DateField(verbose_name="Датасы")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present', verbose_name="Статусу")
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name="Эскертүү")

    class Meta:
        verbose_name = "Катышуу"
        verbose_name_plural = "Катышуу журналы"
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.date} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            old_status = Attendance.objects.filter(pk=self.pk).values_list('status', flat=True).first()

        super().save(*args, **kwargs)

        if self.status == 'absent' and (is_new or old_status != 'absent'):
            try:
                parent = ParentPortal.objects.filter(student=self.student).first()
                if parent and parent.telegram_chat_id:
                    token = "8723045070:AAGCb6vWDINDNTbKSLYDLthP9_ufxYJq2II"
                    msg = (
                        f"📌 *Имам Аль-Бухорий медресеси*\n\n"
                        f"Ҳурматли ота-эна *{parent.parent_name}*!\n"
                        f"Сизнинг фарзандингиз *{self.student.name}* ({self.student.group}) "
                        f"бугунги сабаққа келген жок.\n"
                        f"📅 Сана: {self.date}"
                    )
                    requests.post(
                        f"https://api.telegram.org/bot{token}/sendMessage",
                        json={"chat_id": parent.telegram_chat_id, "text": msg, "parse_mode": "Markdown"},
                        timeout=5
                    )
            except Exception as e:
                print(f"Telegram alert error: {e}")


class Payment(models.Model):
    """Окуучунун контракты жана төлөмдөрү"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments', verbose_name="Окуучу")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Суммасы")
    date = models.DateField(auto_now_add=True, verbose_name="Төлөнгөн күнү")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Мақсаты/Түшүндүрмө")

    class Meta:
        verbose_name = "Төлөм"
        verbose_name_plural = "Бухгалтерия ва төлөмдөр"

    def __str__(self):
        return f"{self.student.name} - {self.amount} сом ({self.date})"


class Quiz(models.Model):
    title = models.CharField(max_length=200, verbose_name="Тест номи")
    subject = models.CharField(max_length=100, verbose_name="Фан")
    group_name = models.CharField(max_length=50, verbose_name="Тайпа (Гуруҳ)")
    time_limit_minutes = models.IntegerField(default=30, verbose_name="Вақт чеклови (минут)")
    is_active = models.BooleanField(default=True, verbose_name="Фаол")

    class Meta:
        verbose_name = "Онлайн тест"
        verbose_name_plural = "Онлайн тестлар"

    def __str__(self):
        return f"{self.title} ({self.subject})"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name="Тест")
    text = models.TextField(verbose_name="Савол матни")

    class Meta:
        verbose_name = "Савол"
        verbose_name_plural = "Саволлар"

    def __str__(self):
        return self.text[:50]


class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name="Савол")
    text = models.CharField(max_length=255, verbose_name="Вариант матни")
    is_correct = models.BooleanField(default=False, verbose_name="Тўғри жавобми?")

    class Meta:
        verbose_name = "Жавоб варианти"
        verbose_name_plural = "Жавоб вариантлари"

    def __str__(self):
        return f"{self.text} ({'Тўғри' if self.is_correct else 'Нотўғри'})"


class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, verbose_name="Тест")
    student_name = models.CharField(max_length=100, verbose_name="Ўқувчи исми")
    score = models.IntegerField(verbose_name="Тўпланган балл")
    total_questions = models.IntegerField(verbose_name="Умумий саволлар")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Топширилган вақти")

    class Meta:
        verbose_name = "Тест натижаси"
        verbose_name_plural = "Тест натижалари"

    def __str__(self):
        return f"{self.student_name} — {self.quiz.title}: {self.score}/{self.total_questions}"