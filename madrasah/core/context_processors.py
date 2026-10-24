# Ролго жараша меню. Жаңы бөлүмдөр кийинки этаптарда ушул тизмеге кошулат.
MENU = {
    "admin": [("dashboard", "Башкы панель"), ("user_list", "Колдонуучулар"),
              ("audit_list", "Аракеттер тарыхы")],
    "academic": [("dashboard", "Башкы панель")],
    "accountant": [("dashboard", "Башкы панель")],
    "hr": [("dashboard", "Башкы панель")],
    "duty": [("dashboard", "Башкы панель")],
    "teacher": [("dashboard", "Башкы панель")],
    "student": [("dashboard", "Башкы панель")],
    "parent": [("dashboard", "Башкы панель")],
}


def menu(request):
    if request.user.is_authenticated:
        return {"menu_items": MENU.get(request.user.role, [])}
    return {"menu_items": []}
