from django.contrib.auth import models
from django.test import TestCase
from django.contrib.auth.models import User
from customer_portal.models import Customer, Orders
from car_dealer_portal.models import Area, CarDealer, Vehicles


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

    def test_index_without_login(self):
        response = self.client.get('/customer_portal/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer/login.html')
        self.assertContains(response, 'Welcome to online car rental system')

    def test_index_with_login(self):
        self.login()
        response = self.client.get('/customer_portal/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer/home_page.html')
        self.assertContains(response, 'Welcome Traveller ! You shall drive the car of your dreams.')
    
    def test_login_page(self):
        response = self.client.get('/customer_portal/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer/login.html')
        self.assertContains(response, 'Welcome to online car rental system')

    # Test for login post request
    def test_auth_view(self):
        self.client.logout()
        response = self.client.post('/customer_portal/auth/', {'username': 'customer', 'password': '1'})   
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/customer_portal/auth/')

    def test_logout_view(self):
        self.client.logout()
        response = self.client.get('/customer_portal/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer/login.html')
        self.assertContains(response, 'Welcome to online car rental system')

    def test_register_page(self):
        response = self.client.get('/customer_portal/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer/register.html')
        self.assertContains(response, 'Registration Form')

    def test_registration_view(self):
        response = self.client.post('/customer_portal/registration/', data={
                    'username': 'testusername',
                    'password': '1',
                    'mobile': '017********',
                    'firstname': 'Test',
                    'lastname': 'Test',
                    'email': 'test@ocrs.com',
                    'city': 'Dhaka',
                    'pincode': '1234'
                })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registered successfully !')

    def test_search_page(self):
        self.login()
        response = self.client.get('/customer_portal/search/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer/search.html')
        self.assertContains(response, 'search')

    def test_registration_view(self):
        self.login()
        response = self.client.post('/customer_portal/search_results/', data={
                    'city': 'Dhaka',
                })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search Results')

    def make_vehicle(self):
        u = User.objects.create_user(username='car_dealer', password='1')
        cd = CarDealer.objects.create(car_dealer=u, mobile='017********', area=self.area)
        car = Vehicles.objects.create(car_name='BMW', color='Black', dealer=cd, area = self.area, description="Awesome Car", capacity=8)
        return car

    def test_renting_views(self):
        self.login()
        car = self.make_vehicle()
        response = self.client.post('/customer_portal/rent/', data={
                    'id': car.id,
                })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name : ' + car.car_name)

        # Test for order
        response = self.client.post('/customer_portal/confirmed/', data={
                    'days': 10,
                    'id': car.id,
                })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your vehicle order was successful !')
        self.assertContains(response, 'vehicle : ' + car.car_name)
        self.assertContains(response, 'duration : 10 days')

        # Test for order history
        response = self.client.get('/customer_portal/manage/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer/manage.html')
        l = response.context['od']
        self.assertEqual(len(l), 1)
        