from django.test import TestCase
from customer_portal.models import *
from car_dealer_portal.models import *



class CustomerPortalTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='customer', password='1')
        user.first_name = 'Test'
        user.last_name = 'User'
        user.save()

        area = Area(city='Dhaka', pincode = '1234')
        area.save()

        customer = Customer(user = user, mobile = '+8801*******', area = area)
        customer.save()
        self.user = user
        self.area = area
        self.customer = customer

    def login(self):
        self.client.login(username='customer', password='1')

    def test_index(self):
        self.login()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/index.html')
        self.assertContains(response, 'Welcome to online car rental system')