from itertools import chain
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404, JsonResponse
from django.contrib.auth import get_user_model
from django.contrib import messages
from apps.forms.models import *
from apps.internalRequests.models import Traceability
import utils.utils as utils
from apps.teams.models import Team
from datetime import datetime
from django.db import transaction
import math
import ast
import json

statusMap = {
    "PENDIENTE": "secondary",
    "EN REVISIÓN": "info",
    "POR APROBAR": "primary",
    "DEVUELTO": "warning",
    "RECHAZADO": "danger",
    "RESUELTO": "success",
}

User = get_user_model()


# This function is used to get the request by its id
def get_request_by_id(id):
    models = [
        TravelAdvanceRequest,
        AdvanceLegalization,
        BillingAccount,
        Requisition,
        TravelExpenseLegalization,
    ]
    for model in models:
        try:
            return model.objects.get(id=id)
        except model.DoesNotExist:
            continue
    raise Http404(f"Request with id {id} not found in any of the tables")


@login_required
@csrf_exempt
def show_requests(request):
    """
    Show requests
    """
    message = None
    if 'changeStatusDenied' in request.GET:
        messages.add_message(request, messages.ERROR, 'No puedes cambiar el estado de una solicitud sin revisar.')
    elif 'changeStatusDone' in request.GET:
        messages.add_message(request, messages.SUCCESS, 'El estado de la solicitud ha sido actualizado correctamente.')
    elif 'changeStatusFailed' in request.GET:
        messages.add_message(request, messages.ERROR, 'No se pudo realizar la operación.')
    elif 'fixRequestDone' in request.GET:
        messages.add_message(request, messages.SUCCESS, 'El formulario ha sido enviado para revisión.')
    if request.user.is_superuser or request.user.is_leader:
        if (
            request.user.is_superuser
            or request.user.is_leader
            and Team.objects.filter(leader_id=request.user.id).exists()
        ):
            advance_legalization = [
                obj.__dict__.update(
                    {
                        "document": "Legalización de Anticipos",
                        "initial_date": obj.request_date,
                        "fullname": obj.traveler_name,
                        "final_date": (
                            obj.final_date if obj.final_date else "Por definir"
                        ),
                        "manager": (
                            obj.member_name if obj.member_name else "Por definir"
                        ),
                    }
                )
                or obj
                for obj in AdvanceLegalization.objects.all()
            ]
            billing_account = [
                obj.__dict__.update(
                    {
                        "document": "Cuenta de Cobro",
                        "initial_date": obj.request_date,
                        "fullname": obj.full_name,
                        "final_date": (
                            obj.final_date if obj.final_date else "Por definir"
                        ),
                        "manager": (
                            obj.member_name if obj.member_name else "Por definir"
                        ),
                    }
                )
                or obj
                for obj in BillingAccount.objects.all()
            ]
            requisition = [
                obj.__dict__.update(
                    {
                        "document": "Requisición",
                        "initial_date": obj.request_date,
                        "fullname": obj.requester_name,
                        "final_date": (
                            obj.final_date if obj.final_date else "Por definir"
                        ),
                        "manager": (
                            obj.member_name if obj.member_name else "Por definir"
                        ),
                    }
                )
                or obj
                for obj in Requisition.objects.all()
            ]
            travel_advance_request = [
                obj.__dict__.update(
                    {
                        "document": "Solicitud de Viaje",
                        "initial_date": obj.request_date,
                        "fullname": obj.traveler_name,
                        "final_date": (
                            obj.final_date if obj.final_date else "Por definir"
                        ),
                        "manager": (
                            obj.member_name if obj.member_name else "Por definir"
                        ),
                    }
                )
                or obj
                for obj in TravelAdvanceRequest.objects.all()
            ]
            travel_expense_request = [
                obj.__dict__.update(
                    {
                        "document": "Legalización de Gastos de Viaje",
                        "initial_date": obj.request_date,
                        "fullname": obj.traveler_name,
                        "final_date": (
                            obj.final_date if obj.final_date else "Por definir"
                        ),
                        "manager": (
                            obj.member_name if obj.member_name else "Por definir"
                        ),
                    }
                )
                or obj
                for obj in TravelExpenseLegalization.objects.all()
            ]
        else:
            return render(
                request, "show-internal-requests.html", {"no_permission": True}
            )
    else:
        advance_legalization = [
            obj.__dict__.update(
                {
                    "document": "Legalización de Anticipos",
                    "initial_date": obj.request_date,
                    "fullname": obj.traveler_name,
                    "final_date": obj.final_date if obj.final_date else "Por definir",
                    "manager": obj.member_name if obj.member_name else "Por definir",
                }
            )
            or obj
            for obj in AdvanceLegalization.objects.filter(id_person=request.user.id)
        ]
        billing_account = [
            obj.__dict__.update(
                {
                    "document": "Cuenta de Cobro",
                    "initial_date": obj.request_date,
                    "fullname": obj.full_name,
                    "final_date": obj.final_date if obj.final_date else "Por definir",
                    "manager": obj.member_name if obj.member_name else "Por definir",
                }
            )
            or obj
            for obj in BillingAccount.objects.filter(id_person=request.user.id)
        ]
        requisition = [
            obj.__dict__.update(
                {
                    "document": "Requisición",
                    "initial_date": obj.request_date,
                    "fullname": obj.requester_name,
                    "final_date": obj.final_date if obj.final_date else "Por definir",
                    "manager": obj.member_name if obj.member_name else "Por definir",
                }
            )
            or obj
            for obj in Requisition.objects.filter(id_person=request.user.id)
        ]
        travel_advance_request = [
            obj.__dict__.update(
                {
                    "document": "Solicitud de Viaje",
                    "initial_date": obj.request_date,
                    "fullname": obj.traveler_name,
                    "final_date": obj.final_date if obj.final_date else "Por definir",
                    "manager": obj.member_name if obj.member_name else "Por definir",
                }
            )
            or obj
            for obj in TravelAdvanceRequest.objects.filter(id_person=request.user.id)
        ]
        travel_expense_request = [
            obj.__dict__.update(
                {
                    "document": "Legalización de Gastos de Viaje",
                    "initial_date": obj.request_date,
                    "fullname": obj.traveler_name,
                    "final_date": obj.final_date if obj.final_date else "Por definir",
                    "manager": obj.member_name if obj.member_name else "Por definir",
                }
            )
            or obj
            for obj in TravelExpenseLegalization.objects.filter(
                id_person=request.user.id
            )
        ]

    requests_data = list(
        chain(
            advance_legalization,
            billing_account,
            requisition,
            travel_advance_request,
            travel_expense_request,
        )
    )

    for r in requests_data:
        r.status_color = statusMap[r.status]

    return render(request, "show-internal-requests.html", {"requests": requests_data})
        


@csrf_exempt
@login_required
def change_status(request, id):
    """
    Allows users to change the status of a request.

    HTTP Methods:
    - GET: Renders a form to change the status of the request.
    - POST: Handles form submission, updates the status of the request, and records traceability.

    Dependencies:
    - Models: For accessing request data in the database.
    - Traceability: Model for recording changes in request status.
    - utils.utils.send_verification_email: Utility function to send notification emails.

    Parameters:
    - request: Django request object.
    - id: ID of the request to be updated.

    Returns:
    - JsonResponse: JSON response indicating the result of the operation.
    """
    if request.method == "GET":
        curr_request = get_request_by_id(id)
        if curr_request.status == "PENDIENTE":
            status_options = ["EN REVISIÓN"]
            return render(
                request,
                "change-status.html",
                {"request": curr_request, "status_options": status_options},
            )
        elif curr_request.status == "EN REVISIÓN" and curr_request.is_reviewed:
            review_data = ast.literal_eval(curr_request.review_data)
            resultReviewShow = False
            comments = None
            reason_data = ''
            for item in review_data:
                if item['id'] == 'reasonData':
                    reason_data = item['value']
                    break

            if reason_data == '':
                status_options = ["POR APROBAR"]
                comments_str = None
            else:
                status_options = ["DEVUELTO", "RECHAZADO"]
                resultReviewShow = True
                comments = ["Celdas afectadas:\n"]
                for item in review_data:
                    if item['id'] != 'reasonData':
                        if item['value'] == 'off':
                            comments.append("- " + item['message'])
                            if item['id'] in ['tableCheck', 'signCheck']:
                                status_options = ["RECHAZADO"]
                    else:
                        reason_data = item['value']

                comments.append('\n' + "Motivos: " + reason_data)
                comments_str = '\n'.join(comments)
            return render(
                request,
                "change-status.html",
                {"request": curr_request, "status_options": status_options, "resultReviewShow": resultReviewShow, "comments": comments_str},
            )
        elif curr_request.status == "POR APROBAR":
            status_options = ["RESUELTO", "DEVUELTO", "RECHAZADO"]
            return render(
                request,
                "change-status.html",
                {"request": curr_request, "status_options": status_options},
            )

    elif request.method == "POST":
        try:
            curr_request = get_request_by_id(id)
            new_status = request.POST.get("newStatus")
            new_reason = request.POST.get("reason")
            prev_status = curr_request.status
            curr_request.status = new_status
            team_id = curr_request.team_id

            Traceability.objects.create(
                modified_by=request.user,
                prev_state=prev_status,
                new_state=new_status,
                reason=new_reason,
                date=datetime.now(),
                request=id,
            )

            if not math.isnan(team_id):
                team = Team.objects.filter(id=team_id)
                if team.exists():
                    if request.user.is_superuser:
                        utils.send_verification_email(
                            request,
                            f"Actualización del estado de la solicitud {curr_request.id}",
                            "Notificación Vía Sistema de Contabilidad | Universidad Icesi <contabilidad@icesi.edu.co>",
                            team[0].leader.email,
                            f"Hola, el Administrador del Sistema ha cambiado el estado de la solicitud {curr_request.id}\nEstado Anterior:{prev_status}\nNuevo Estado: {new_status}\nMotivo: {new_reason}",
                        )
                    else:
                        utils.send_verification_email(
                            request,
                            f"Actualización del estado de la solicitud {curr_request.id}",
                            "Notificación Vía Sistema de Contabilidad | Universidad Icesi <contabilidad@icesi.edu.co>",
                            team[0].leader.email,
                            f"Hola, el usuario identificado como {request.user} del equipo {team[0]} ha cambiado el estado de la solicitud {curr_request.id}\nEstado Anterior:{prev_status}\nNuevo Estado: {new_status}\nMotivo: {new_reason}",
                        )
            curr_request.save()
            return redirect("/requests/?changeStatusDone")
            return JsonResponse(
                {
                    "message": f"El estado de la solicitud {id} ha sido actualizado correctamente."
                }
            )

        except Exception as e:
            return redirect("/requests/?changeStatusFailed")
            return JsonResponse(
                {"error": f"No se pudo realizar la operación: {str(e)}"}, status=500
            )


@never_cache
@csrf_exempt
@login_required
def detail_request(request, id):
    """
    Renders a page displaying details of a specific request.

    HTTP Method:
    - GET

    Dependencies:
    - requests.models: For accessing request data in the database.

    Parameters:
    - request: Django request object.
    - id: ID of the request to be displayed.

    Returns:
    - render: Renders the HTML template with request details.
    """
    request_data = get_request_by_id(id)
    context = {"request": request_data}

    # Use the request type to determine which template to render
    if isinstance(request_data, AdvanceLegalization):
        expenses = AdvanceLegalization_Table.objects.filter(
            general_data_id=request_data.id
        )
        context["expenses"] = expenses
        template = "forms/advance_legalization.html"
    elif isinstance(request_data, BillingAccount):
        context["include_cex"] = True
        template = "forms/billing_account.html"
    elif isinstance(request_data, Requisition):
        template = "forms/requisition.html"
    elif isinstance(request_data, TravelAdvanceRequest):
        expenses = json.loads(request_data.expenses)
        context["expenses"] = expenses
        template = "forms/travel_advance_request.html"
    elif isinstance(request_data, TravelExpenseLegalization):
        expenses = TravelExpenseLegalization_Table.objects.filter(
            travel_info_id=request_data.id
        )
        context["expenses"] = expenses
        template = "forms/travel_expense_legalization.html"
    else:
        template = "forms/default_form.html"

    if request_data.status == "DEVUELTO" and request.user.is_applicant:
        context["editable"] = True

    return render(request, template, context)


@csrf_exempt
@login_required
def show_traceability(request, request_id):
    """
    Renders a page displaying the traceability of a specific request.

    HTTP Method:
    - GET

    Dependencies:
    - Traceability: Model for accessing traceability information.

    Parameters:
    - request: Django request object.
    - request_id: ID of the request for which traceability is to be displayed.

    Returns:
    - render: Renders the HTML template with traceability information.
    """
    traceability = Traceability.objects.filter(request=request_id)
    for t in traceability:
        t.prev_color = statusMap[t.prev_state]
        t.new_color = statusMap[t.new_state]
    traceability = traceability[::-1]
    return render(request, "show-traceability.html", {"traceability": traceability})


@csrf_exempt
@login_required
def assign_request(request, request_id):
    """
    Allows users to assign a request to another user.

    HTTP Methods:
    - GET: Renders a form to select a user for assignment.
    - POST: Handles form submission, updates the request with the assigned user, and sends a notification email.

    Dependencies:
    - Team: Model for accessing team information.
    - utils.utils.send_verification_email: Utility function to send notification emails.

    Parameters:
    - request: Django request object.
    - request_id: ID of the request to be assigned.

    Returns:
    - redirect: Redirects to the requests page after assignment.
    """
    curr_request = get_request_by_id(request_id)
    if isinstance(curr_request, AdvanceLegalization):
        form_type = "Legalización de Anticipos"
    elif isinstance(curr_request, BillingAccount):
        form_type = "Cuenta de Cobro"
    elif isinstance(curr_request, Requisition):
        form_type = "Requisición"
    elif isinstance(curr_request, TravelAdvanceRequest):
        form_type = "Solicitud de Viaje"
    elif isinstance(curr_request, TravelExpenseLegalization):
        form_type = "Legalización de Gastos de Viaje"
    else:
        form_type = None

    if request.method == "GET":
        if form_type is not None:
            teams = Team.objects.filter(typeForm=form_type)
            if len(teams):
                users = teams[0].members.all()
            else:
                users = []
        else:
            users = []

        return render(
            request, "assign-request.html", {"users": users, "request": curr_request}
        )
    elif request.method == "POST":
        try:
            user_id = request.POST["user_id"]
            manager = get_object_or_404(User, pk=user_id)
            curr_request.member_name = manager.first_name + " " + manager.last_name
            curr_request.save()
            teams = Team.objects.filter(typeForm=form_type)
            try:
                utils.send_verification_email(
                    request,
                    "Solicitud Asignada",
                    "Notificación Vía Sistema de Contabilidad | Universidad Icesi <contabilidad@icesi.edu.co>",
                    manager.email,
                    f"Hola, como miembro del equipo {teams[0].name}, el líder {manager.first_name} {manager.last_name} le ha asignado una nueva solicitud en el Sistema de Contabilidad",
                )
            except:
                print("El destino no se encontró")
        except Exception as e:
            print(e)

@csrf_exempt
@login_required
def travel_advance_request(request):
    """
    Review the travel advance request form.

    HTTP Method:
    - POST

    Returns:
    - render: Changes status of the request to reviewed.
    """
    request_id = request.POST.get('id')
    review_data = request.POST.dict()
    request = TravelAdvanceRequest.objects.get(id=request_id)

    # Mapping of field names to data-message
    field_to_message = {
        'dateCheck': 'Fecha', 'nameCheck': 'Nombre', 'idCheck': 'ID', 'dependenceCheck': 'Dependencia',
        'costsCheck': 'Costos', 'destinationCheck': 'Destino', 'startTravelCheck': 'Inicio del viaje',
        'endTravelCheck': 'Fin del viaje', 'travelReasonCheck': 'Razón del viaje', 'tableCheck': 'Tabla',
        'signCheck': 'Firma', 'bankCheck': 'Banco', 'typeAccountCheck': 'Tipo de cuenta',
        'idBankCheck': 'ID del banco', 'observationsCheck': 'Observaciones', 'reasonData': 'Razón'
    }

    # Initialize review_data_list with all checkboxes with a value of 'off'
    review_data_list = [{'id': key, 'message': field_to_message.get(key, ''), 'value': 'off'} for key in field_to_message.keys()]

    # Update the values of the checkboxes that are checked
    for item in review_data_list:
        if item['id'] in review_data:
            item['value'] = review_data[item['id']]

    request.review_data = review_data_list
    request.is_reviewed = True
    request.save()
    return redirect("/requests/")


@csrf_exempt
@login_required
def travel_expense_legalization(request):
    """
    Review the travel expense legalization form.

    HTTP Method:
    - POST

    Returns:
    - render: Changes status of the request to reviewed.
    """
    request_id = request.POST.get('id')
    review_data = request.POST.dict()
    request = TravelExpenseLegalization.objects.get(id=request_id)

    # Mapping of field names to data-message
    field_to_message = {
        'dateCheck': 'Fecha', 'nameCheck': 'Nombre', 'idCheck': 'ID', 'dependenceCheck': 'Dependencia',
        'costsCheck': 'Costos', 'destinationCheck': 'Destino', 'startTravelCheck': 'Inicio de viaje',
        'endTravelCheck': 'Fin de viaje', 'travelReasonCheck': 'Razón de viaje', 'tableCheck': 'Tabla',
        'signCheck': 'Firma', 'bankCheck': 'Banco', 'typeAccountCheck': 'Tipo de cuenta',
        'idBankCheck': 'ID del banco', 'observationsCheck': 'Observaciones', 'reasonData': 'Razón'
    }

    # Initialize review_data_list with all checkboxes with a value of 'off'
    review_data_list = [{'id': key, 'message': field_to_message.get(key, ''), 'value': 'off'} for key in field_to_message.keys()]

    # Update the values of the checkboxes that are checked
    for item in review_data_list:
        if item['id'] in review_data:
            item['value'] = review_data[item['id']]

    request.review_data = review_data_list
    request.is_reviewed = True
    request.save()
    return redirect("/requests/")


@csrf_exempt
@login_required
def advance_legalization(request):
    """
    Review the advance legalization form.

    HTTP Method:
    - POST

    Returns:
    - render: Changes status of the request to reviewed.
    """
    request_id = request.POST.get('id')
    review_data = request.POST.dict()
    request = AdvanceLegalization.objects.get(id=request_id)

    # Mapping of field names to data-message
    field_to_message = {
        'dateCheck': 'Fecha', 'nameCheck': 'Nombre', 'idCheck': 'ID', 'dependenceCheck': 'Dependencia',
        'costsCheck': 'Costos', 'purchaseReasonCheck': 'Razón de compra', 'tableCheck': 'Tabla',
        'signCheck': 'Firma', 'bankCheck': 'Banco', 'typeAccountCheck': 'Tipo de cuenta',
        'idBankCheck': 'ID del banco', 'observationsCheck': 'Observaciones', 'reasonData': 'Razón'
    }

    # Inicializar review_data_list con todos los checkboxes con un valor de 'off'
    review_data_list = [{'id': key, 'message': field_to_message.get(key, ''), 'value': 'off'} for key in field_to_message.keys()]

    # Actualizar los valores de los checkboxes que están marcados
    for item in review_data_list:
        if item['id'] in review_data:
            item['value'] = review_data[item['id']]

    request.review_data = review_data_list
    request.is_reviewed = True
    request.save()
    return redirect("/requests/")

@csrf_exempt
@login_required
def billing_account(request):
    """
    Review the billing account form.

    HTTP Method:
    - POST

    Returns:
    - render: Changes status of the request to reviewed.
    """
    request_id = request.POST.get('id')
    review_data = request.POST.dict()
    request = BillingAccount.objects.get(id=request_id)

    # Mapping of field names to data-message
    field_to_message = {
        'dateCheck': 'Fecha', 'nameCheck': 'Nombre', 'idCheck': 'ID', 'valueCheck': 'Valor',
        'conceptCheck': 'Concepto', 'retentionCheck': 'Retención', 'taxCheck': 'Impuesto',
        'residentCheck': 'Residente', 'cityCheck': 'Ciudad', 'addressCheck': 'Dirección',
        'cellphoneCheck': 'Celular', 'signCheck': 'Firma', 'bankCheck': 'Banco',
        'typeAccountCheck': 'Tipo de cuenta', 'idBankCheck': 'ID del banco', 'cexCheck': 'CEX',
        'reasonData': 'Razón'
    }

    # Initialize review_data_list with all checkboxes with a value of 'off'
    review_data_list = [{'id': key, 'message': field_to_message.get(key, ''), 'value': 'off'} for key in field_to_message.keys()]

    # Update the values of the checkboxes that are checked
    for item in review_data_list:
        if item['id'] in review_data:
            item['value'] = review_data[item['id']]

    request.review_data = review_data_list
    request.is_reviewed = True
    request.save()
    return redirect("/requests/")

@csrf_exempt
@login_required
def requisition(request):
    """
    Review the requisition form.

    HTTP Method:
    - POST

    Returns:
    - render: Changes status of the request to reviewed.
    """
    request_id = request.POST.get('id')
    review_data = request.POST.dict()
    request = Requisition.objects.get(id=request_id)

    # Mapeo de los nombres de los campos a los data-message
    field_to_message = {
        'dateCheck': 'Fecha', 'nameCheck': 'Nombre', 'idCheck': 'ID', 'workCheck': 'Trabajo',
        'dependenceCheck': 'Dependencia', 'cencoCheck': 'Cenco', 'valueCheck': 'Valor',
        'conceptCheck': 'Concepto', 'descriptionCheck': 'Descripción', 'signCheck': 'Firma',
        'bankCheck': 'Banco', 'typeAccountCheck': 'Tipo de cuenta', 'idBankCheck': 'ID del banco',
        'observationsCheck': 'Observaciones', 'reasonData': 'Razón'
    }

    # Inicializar review_data_list con todos los checkboxes con un valor de 'off'
    review_data_list = [{'id': key, 'message': field_to_message.get(key, ''), 'value': 'off'} for key in field_to_message.keys()]

    # Actualizar los valores de los checkboxes que están marcados
    for item in review_data_list:
        if item['id'] in review_data:
            item['value'] = review_data[item['id']]

    request.review_data = review_data_list
    request.is_reviewed = True
    request.save()
    return redirect("/requests/")


@csrf_exempt
@login_required
def update_request(request, request_id):
    # Get the request object
    curr_request = get_request_by_id(request_id)

    # Check the type of the request
    if isinstance(curr_request, AdvanceLegalization):
        form_type = "Legalización de Anticipos"
    elif isinstance(curr_request, BillingAccount):
        form_type = "Cuenta de Cobro"
    elif isinstance(curr_request, Requisition):
        form_type = "Requisición"
    elif isinstance(curr_request, TravelAdvanceRequest):
        form_type = "Solicitud de Viaje"
    elif isinstance(curr_request, TravelExpenseLegalization):
        form_type = "Legalización de Gastos de Viaje"
    else:
        form_type = None

    # Update the status and is_reviewed fields
    with transaction.atomic():
        curr_request.status = "EN REVISIÓN"
        curr_request.is_reviewed = False

        # Update the request with the data from the method's request
        for key, value in request.POST.items():
            if hasattr(curr_request, key):
                setattr(curr_request, key, value)

        curr_request.save()

    Traceability.objects.create(
        modified_by=request.user,
        prev_state="DEVUELTO",
        new_state="EN REVISIÓN",
        reason="Corrección de formulario.",
        date=datetime.now(),
        request=request_id,
    )
    
    return redirect("/requests/?fixRequestDone")
