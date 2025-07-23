from django.shortcuts import render, redirect
from django.forms import formset_factory
import csv
import os
from datetime import datetime
from .forms import VisitorForm
from django.conf import settings


CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visitor_list.csv')

MAILING_LIST_FILE = os.path.join(settings.BASE_DIR, 'mailing_list.csv')
HOLIDAYS_FILE = os.path.join(settings.BASE_DIR, 'holidays.csv')

def index(request):
    visitors = []
    today = datetime.today().date()

    try:
        with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                visit_date = datetime.strptime(row['visit_date'], "%Y-%m-%d").date()
                if visit_date >= today:
                    row['cancelled_flag'] = row.get('cancelled', '').lower() in ['true', 'on', '1']
                    row['time_undecided_flag'] = row.get('time_undecided', '').lower() in ['true', 'on', '1']
                    visitors.append(row)

    except FileNotFoundError:
        pass

    return render(request, 'visitors/index.html', {'visitors': visitors})

def add_visitor(request):
    VisitorFormSet = formset_factory(VisitorForm, extra=3)
    formset = VisitorFormSet(request.POST or None)
    time_choices = formset.empty_form.fields['visit_time'].widget.choices  # ← ここを追加

    if request.method == 'POST':
        has_error = False
        valid_forms = []

        for form in formset:
            all_empty = all(
                not form.data.get(f'{form.prefix}-{field}')
                for field in form.fields
            )
            if all_empty:
                continue

            if form.is_valid():
                valid_forms.append(form)
            else:
                has_error = True

        if not has_error and valid_forms:
            current_id = 1
            try:
                with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    ids = [int(row['id']) for row in reader if row['id'].isdigit()]
                    current_id = max(ids) + 1 if ids else 1
            except FileNotFoundError:
                pass

            fieldnames = [
                'id', 'visit_date', 'visit_time', 'time_undecided', 'company_name',
                'last_name', 'first_name', 'title', 'purpose',
                'location', 'host_staff', 'notes', 'cancelled'
            ]
            write_header = not os.path.exists(CSV_FILE_PATH)

            with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()

                for form in valid_forms:
                    data = form.cleaned_data
                    data['cancelled'] = 'false'
                    data['id'] = str(current_id)
                    current_id += 1
                    filtered_data = {k: data.get(k, '') for k in fieldnames}
                    writer.writerow(filtered_data)

            return redirect('index')

    return render(request, 'visitors/add.html', {
        'formset': formset,
        'time_choices': [choice for choice in formset.empty_form.fields['visit_time'].widget.choices],
    })


def cancel_visitor(request, id):
    if request.method == 'POST':
        updated_rows = []
        try:
            with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                for row in reader:
                    if row.get('id') == str(id):
                        row['cancelled'] = 'true'
                    updated_rows.append(row)

            with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_rows)

        except FileNotFoundError:
            pass

    return redirect('index')

def edit_visitor(request, id):
    # CSVファイル読み込み
    rows = []
    target_row = None

    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['id'] == str(id):
                target_row = row
            rows.append(row)

    if not target_row:
        return redirect('index')

    # 初期データをフォームに渡す
    if request.method == 'POST':
        form = VisitorForm(request.POST)
        if form.is_valid():
            updated_row = form.cleaned_data
            updated_row['id'] = str(id)
            updated_row['cancelled'] = target_row.get('cancelled', 'false')

            # CSVを更新
            with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=target_row.keys())
                writer.writeheader()
                for row in rows:
                    if row['id'] == str(id):
                        writer.writerow(updated_row)
                    else:
                        writer.writerow(row)

            return redirect('index')
    else:
        form = VisitorForm(initial=target_row)

    return render(request, 'visitors/edit.html', {'form': form, 'visitor_id': id})

def settings_view(request):
    if request.method == 'POST':
        # メーリングリスト保存処理
        emails = request.POST.getlist('emails')
        with open(MAILING_LIST_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for email in emails:
                if email.strip():
                    writer.writerow([email.strip()])

        # 休日保存処理
        dates = request.POST.getlist('holidays')
        with open(HOLIDAYS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for date in dates:
                if date.strip():
                    writer.writerow([date.strip()])

        return redirect('settings')

    # 表示用データ読み込み
    with open(MAILING_LIST_FILE, 'r', encoding='utf-8') as f:
        mailing_list = [row[0] for row in csv.reader(f) if row]

    with open(HOLIDAYS_FILE, 'r', encoding='utf-8') as f:
        holidays = [row[0] for row in csv.reader(f) if row]

    return render(request, 'visitors/settings.html', {
        'mailing_list': mailing_list,
        'holidays': holidays,
    })
