def has_access(user_role, target):
    access_control = {
        'admin': ['all'],
        'doctor': ['doctor_dashboard', 'add_record'],
        'nurse': ['nurse_dashboard'],
        'patient': ['patient_dashboard']
    }
    return 'all' in access_control[user_role] or target in access_control[user_role]