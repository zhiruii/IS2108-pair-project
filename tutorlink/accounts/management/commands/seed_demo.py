from django.core.management.base import BaseCommand

from accounts.models import Child, TutorProfile, User

PASSWORD = 'demo1234'

STAFF = {'email': 'staff@demo.com', 'first_name': 'Sam', 'last_name': 'Staff'}

TUTORS = [
    {
        'email': 'tutor1@demo.com', 'first_name': 'Amy', 'last_name': 'Tan',
        'bio': 'NIE-trained maths tutor focused on exam technique.',
        'qualification': 'NIE', 'years_experience': 8, 'teaching_mode': 'HYBRID',
    },
    {
        'email': 'tutor2@demo.com', 'first_name': 'Daniel', 'last_name': 'Ong',
        'bio': 'Degree holder teaching science online.',
        'qualification': 'DEGREE', 'years_experience': 3, 'teaching_mode': 'ONLINE',
    },
    {
        'email': 'tutor3@demo.com', 'first_name': 'Priya', 'last_name': 'Nair',
        'bio': 'University student tutoring English in person.',
        'qualification': 'STUDENT', 'years_experience': 1, 'teaching_mode': 'IN_PERSON',
    },
]

PARENT = {'email': 'parent1@demo.com', 'first_name': 'Bob', 'last_name': 'Lim'}

CHILDREN = [
    {'first_name': 'Ben', 'last_name': 'Lim', 'level': 'P4'},
    {'first_name': 'Beth', 'last_name': 'Lim', 'level': 'S2'},
]


class Command(BaseCommand):
    help = 'Create demo users, tutor profiles and children'

    def make_user(self, data, role):
        user = User.objects.filter(email=data['email']).first()
        if user:
            self.stdout.write(f'skipped {data["email"]} (already exists)')
            return user
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role,
            is_staff=(role == 'STAFF'),
        )
        self.stdout.write(f'created {data["email"]}')
        return user

    def handle(self, *args, **options):
        self.make_user(STAFF, 'STAFF')

        for data in TUTORS:
            tutor = self.make_user(data, 'TUTOR')
            TutorProfile.objects.get_or_create(
                user=tutor,
                defaults={
                    'bio': data['bio'],
                    'qualification': data['qualification'],
                    'years_experience': data['years_experience'],
                    'teaching_mode': data['teaching_mode'],
                },
            )

        parent = self.make_user(PARENT, 'PARENT')
        for data in CHILDREN:
            Child.objects.get_or_create(
                parent=parent,
                first_name=data['first_name'],
                last_name=data['last_name'],
                defaults={'level': data['level']},
            )

        self.stdout.write(self.style.SUCCESS(f'Demo data ready. Password for all: {PASSWORD}'))
