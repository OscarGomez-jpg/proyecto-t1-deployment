from django.db import models
import json

class TravelRequest(models.Model):
    request_date = models.DateField()
    traveler_name = models.CharField(max_length=200)
    id_number = models.CharField(max_length=200)
    dependence = models.CharField(max_length=200)
    cost_center = models.CharField(max_length=200)
    destination_city = models.CharField(max_length=200)
    departure_date = models.DateField()
    return_date = models.DateField()
    travel_reason = models.CharField(max_length=200)
    currency = models.CharField(max_length=200)
    expenses = models.TextField()
    signature_status = models.CharField(max_length=200)
    bank = models.CharField(max_length=200)
    account_type = models.CharField(max_length=200)
    account_number = models.CharField(max_length=200)
    observations = models.TextField()

    def set_expenses(self, expenses_dict):
        self.expenses = json.dumps(expenses_dict)

    def get_expenses(self):
        return json.loads(self.expenses)

class TravelInfo(models.Model):
    request_date = models.DateField()
    traveler_name = models.CharField(max_length=200)
    id_number = models.CharField(max_length=200)
    dependence = models.CharField(max_length=200)
    cost_center = models.CharField(max_length=200)
    destination_city = models.CharField(max_length=200)
    departure_date = models.DateField()
    return_date = models.DateField()
    travel_reason = models.TextField()
    total1 = models.DecimalField(max_digits=10, decimal_places=2)
    total2 = models.DecimalField(max_digits=10, decimal_places=2)
    total3 = models.DecimalField(max_digits=10, decimal_places=2)
    advance_total1 = models.DecimalField(max_digits=10, decimal_places=2)
    advance_total2 = models.DecimalField(max_digits=10, decimal_places=2)
    advance_total3 = models.DecimalField(max_digits=10, decimal_places=2)
    employee_balance1 = models.DecimalField(max_digits=10, decimal_places=2)
    employee_balance2 = models.DecimalField(max_digits=10, decimal_places=2)
    employee_balance3 = models.DecimalField(max_digits=10, decimal_places=2)
    icesi_balance1 = models.DecimalField(max_digits=10, decimal_places=2)
    icesi_balance2 = models.DecimalField(max_digits=10, decimal_places=2)
    icesi_balance3 = models.DecimalField(max_digits=10, decimal_places=2)
    signature_status = models.BooleanField()
    bank = models.CharField(max_length=200)
    account_type = models.CharField(max_length=200)
    account_number = models.CharField(max_length=200)
    observations = models.TextField()

class ExpenseDetail(models.Model):
    travel_info = models.ForeignKey(TravelInfo, on_delete=models.CASCADE)
    category = models.CharField(max_length=200)
    provider = models.CharField(max_length=200)
    nit = models.CharField(max_length=200)
    concept = models.CharField(max_length=200)
    pesos = models.DecimalField(max_digits=10, decimal_places=2)
    dollars = models.DecimalField(max_digits=10, decimal_places=2)
    euros = models.DecimalField(max_digits=10, decimal_places=2)

    def serialize(self):
        return json.dumps({
            'category': self.category,
            'provider': self.provider,
            'nit': self.nit,
            'concept': self.concept,
            'pesos': str(self.pesos),
            'dollars': str(self.dollars),
            'euros': str(self.euros),
        })