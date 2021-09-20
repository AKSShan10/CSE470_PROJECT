from django.contrib.auth import models
from django.test import TestCase
from django.contrib.auth.models import User
from customer_portal.models import Customer, Orders
from car_dealer_portal.models import Area, CarDealer, Vehicles


class CarDealerTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='admin', password='1')
        user.first_name = 'Test'
        user.last_name = 'Test'
        user.save()

        area = Area(city='Dhaka', pincode = '1234')
        area.save()

        customer = Customer(user = user, mobile = '+8801*******', area = area)
        customer.save()
        self.user = user
        self.area = area
        self.customer = customer

    def login(self):
        self.client.login(username='admin', password='1')

    def test_index_without_login(self):
        response = self.client.get('/car_dealer_portal/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'car_dealer/login.html')
        self.assertContains(response, 'Welcome to online car rental system')

        self.login()
        response = self.client.get('/car_dealer_portal/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'car_dealer/home_page.html')
        self.assertContains(response, 'Admin: ' + self.user.username)

    def test_login_page(self):
        response = self.client.get('/car_dealer_portal/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'car_dealer/login.html')
        self.assertContains(response, 'Welcome to online car rental system')

    # Test for login post request
    def test_auth_view(self):
        self.client.logout()
        response = self.client.post('/car_dealer_portal/auth/', {'username': 'admin', 'password': '1'})   
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/car_dealer_portal/auth/')

    def test_logout_view(self):
        self.client.logout()
        response = self.client.get('/car_dealer_portal/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'car_dealer/login.html')
        self.assertContains(response, 'Welcome to online car rental system')

    def test_register_page(self):
        response = self.client.get('/car_dealer_portal/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'car_dealer/register.html')
        self.assertContains(response, 'Registration Form')

    def test_registration_view(self):
        response = self.client.post('/car_dealer_portal/registration/', data={
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

        # User count will be 2 cause 1 is created by setUp and other is created by test_registration_view
        users = User.objects.count()
        self.assertEqual(users, 2)

    def test_add_vehicle(self):
        self.login()
        cd = CarDealer.objects.create(car_dealer=self.user, mobile="017********", area=self.area)
        response = self.client.post('/car_dealer_portal/add_vehicle/', data={
            'car_name': 'Bugatti Centodieci',
            'color': 'Black',
            'cd': cd,
            'city':'France',
            'pincode': '12345',
            'description': 'A awesome car',
            'capacity': 4
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vehicle added successfully !')

        vehicle_count = Vehicles.objects.count()
        self.assertEqual(vehicle_count, 1)

        # Test vehicle manage
        response = self.client.get('/car_dealer_portal/manage_vehicles/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'car_dealer/manage.html')
        self.assertContains(response, 'Your Vehicles')
        self.assertEqual(len(response.context['vehicle_list']), 1)

    def test_order_list(self):
        self.login()
        cd = CarDealer.objects.create(car_dealer=self.user, mobile="017********", area=self.area)
        vehicle = Vehicles.objects.create(
            car_name='Bugatti Centodieci',
            color='Black',
            dealer=cd,
            area=self.area,
            capacity=6,
            description='Awesome car',
            is_available=False
        )
        days = '10' 
        customer = User.objects.create_user(
            username="orderuser",
            password='1',
            email='orderuser@ocrs.com',
            first_name='OrderUser',
            last_name='Last Name'
        )
        order = Orders.objects.create(
            user=customer,
            car_dealer=cd,
            rent=(int(vehicle.capacity))*400*(int(days)),
            vehicle=vehicle,
            days=days
        )

        response = self.client.get('/car_dealer_portal/order_list/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'car_dealer/order_list.html')
        self.assertContains(response, 'Order List')
        self.assertEqual(len(response.context['order_list']), 1)
        self.assertFalse(vehicle.is_available)
        self.assertFalse(order.is_complete)
        
        # Test Complete
        response = self.client.post('/car_dealer_portal/complete/', data={'id': order.id})
        self.assertEqual(response.status_code, 302)
        order = Orders.objects.get(id=order.id)
        vehicle = Vehicles.objects.get(id=vehicle.id)
        self.assertTrue(order.is_complete)
        self.assertTrue(vehicle.is_available)

        # Test history
        response = self.client.get('/car_dealer_portal/history/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['order_list']), 1)
        cd = CarDealer.objects.get(id=cd.id)
        self.assertEqual(response.context['wallet'], cd.wallet)

        # Test vehicle delete
        response = self.client.post('/car_dealer_portal/delete/', data={'id': vehicle.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vehicles.objects.count(), 0)