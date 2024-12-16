from django.db import models
from django.contrib.auth.models import User

class District(models.Model):
    STATUS_CHOICES = [
        ('active', 'Действует'),
        ('deleted', 'Удален'),
    ]
    district_name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(max_length=5000, verbose_name="Описание")
    flight_time = models.IntegerField(verbose_name="Время пролета района (в минутах)")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    image_url = models.URLField(verbose_name="Ссылка на изображение", max_length=1000, blank=True)

    class Meta:
        verbose_name = "Район"
        verbose_name_plural = "Районы"

    def __str__(self):
        return self.district_name

    def formatted_flight_time(self):
        hours = self.flight_time // 60
        minutes = self.flight_time % 60
        return f"{hours} ч. {minutes} мин." if hours else f"{minutes} мин."
    formatted_flight_time.short_description = "Время пролета"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Zone(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('submitted', 'Сформирован'),
        ('completed', 'Завершен'),
        ('rejected', 'Отклонен'),
        ('deleted', 'Удален'),
    ]

    zone_name = models.CharField(max_length=255, null=True, verbose_name="Название")
    zone_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата формирования")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    creator = models.ForeignKey(
        User,
        related_name="zone_creator",
        on_delete=models.PROTECT,  # Запрещено удаление пользователя, если он является создателем
        verbose_name="Создатель"
    )
    moderator = models.ForeignKey(
        User,
        related_name="zone_moderator",
        on_delete=models.SET_NULL,  # Если модератор удален, поле становится NULL
        null=True,
        blank=True,
        verbose_name="Модератор"
    )
    description = models.TextField(max_length=500, null=True, blank=True, verbose_name="Комментарий к пролету")

    class Meta:
        verbose_name = "Пролет"
        verbose_name_plural = "Пролеты"

    def __str__(self):
        return f"Цель пролета: {self.zone_name}, статус: {self.get_zone_status_display()}"


class ZoneDistrict(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'Высокий'),
        ('medium', 'Средний'),
        ('low', 'Низкий'),
    ]

    zone = models.ForeignKey(
        Zone,
        related_name="districts",
        on_delete=models.PROTECT,  # Запрещено удаление пролета, если есть привязанные районы
        verbose_name="Пролет"
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,  # Запрещено удаление района, если он привязан к пролету
        verbose_name="Район"
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name="Приоритет")
    is_main = models.BooleanField(default=False, verbose_name="Ключевой район")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["zone", "district"], name="unique_zone_district"),
        ]
        verbose_name = "Район пролета"
        verbose_name_plural = "Районы пролетов"

    def total_flight_time(self):
        return sum([zd.district.flight_time for zd in self.zone.districts.all()])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Пролет {self.zone.zone_name} над районом {self.district.district_name}"
