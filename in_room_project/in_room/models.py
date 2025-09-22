from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='部署名')

    class Meta:
        verbose_name = '部署'
        verbose_name_plural = '部署'

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=100, verbose_name='名前')
    employee_number = models.CharField(max_length=100, unique=True, verbose_name='社員番号')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='部署')
    email = models.EmailField(max_length=100, verbose_name='メールアドレス')
    phone = models.CharField(max_length=100, verbose_name='内線番号')
    in_room_time = models.DateTimeField(null=True, blank=True, verbose_name='入室時間')
    schedule = models.CharField(null=True, blank=True, verbose_name='予定', max_length=100)

    class Meta:
        verbose_name = '従業員'
        verbose_name_plural = '従業員'

    def __str__(self):
        return f"{self.name} ({self.employee_number})"

    @property
    def is_in_room(self):
        """入室中かどうかを判定"""
        return self.in_room_time is not None