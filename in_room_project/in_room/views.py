from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from .models import Employee, Department
import json


class InputPageView(TemplateView):
    template_name = 'in_room/input_page.html'


class StatusPageView(TemplateView):
    template_name = 'in_room/status_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 部署ごとに従業員をグループ化
        departments = Department.objects.all().order_by('name')
        departments_with_employees = []

        for department in departments:
            employees = Employee.objects.filter(department=department).order_by('name')
            in_room_employees = employees.filter(in_room_time__isnull=False)
            out_room_employees = employees.filter(in_room_time__isnull=True)

            departments_with_employees.append({
                'department': department,
                'in_room_employees': in_room_employees,
                'out_room_employees': out_room_employees,
                'in_room_count': in_room_employees.count(),
                'total_count': employees.count()
            })

        context['departments_with_employees'] = departments_with_employees
        context['total_in_room'] = Employee.objects.filter(in_room_time__isnull=False).count()
        context['total_employees'] = Employee.objects.count()

        return context


@method_decorator(csrf_exempt, name='dispatch')
class RecordEntryView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            employee_id = data.get('employee_id')

            # 社員番号の検証
            if not employee_id:
                return JsonResponse({
                    'status': 'error',
                    'message': '社員番号が入力されていません'
                }, status=400)

            # 社員を検索
            try:
                employee = Employee.objects.get(employee_number=employee_id)
            except Employee.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': f'社員番号 {employee_id} の社員が見つかりません'
                }, status=404)

            current_time = timezone.now()

            if action == 'enter':
                return self._handle_enter(employee, current_time)
            elif action == 'exit':
                return self._handle_exit(employee)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': '無効なアクションです'
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '無効なJSONデータです'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def _handle_enter(self, employee, current_time):
        """入室処理"""
        if employee.is_in_room:
            return JsonResponse({
                'status': 'error',
                'message': f'{employee.name}さんは既に入室済みです'
            }, status=400)

        employee.in_room_time = current_time
        employee.save()

        return JsonResponse({
            'status': 'success',
            'message': f'{employee.name}さんの入室を記録しました'
        })

    def _handle_exit(self, employee):
        """退室処理"""
        if not employee.is_in_room:
            return JsonResponse({
                'status': 'error',
                'message': f'{employee.name}さんは入室していません'
            }, status=400)

        employee.in_room_time = None
        employee.save()

        return JsonResponse({
            'status': 'success',
            'message': f'{employee.name}さんの退室を記録しました'
        })
