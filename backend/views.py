import json
import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import RawData
from django.db.models import Sum
from datetime import datetime
from django.apps import apps


@csrf_exempt
def rawdata(request):
    if request.method == "POST":
        data = json.loads(request.body)
        df = pd.DataFrame(data)

        # Validate and format the data
        is_valid, error_message = formatAndValidateData(df)
        if not is_valid:
            return JsonResponse({"error": error_message}, status=400)

        for _, row in df.iterrows():
            # Check if the record already exists
            if not RawData.objects.filter(
                invoice_number=row["invoice number"], customer=row["customer"]
            ).exists():
                RawData.objects.create(
                    date=row["date"],
                    invoice_number=row["invoice number"],
                    value=row["value"],
                    haircut_percent=row["haircut percent"],
                    daily_fee_percent=row["Daily fee percent"],
                    currency=row["currency"],
                    revenue_source=row["Revenue source"],
                    customer=row["customer"],
                    expected_payment_duration=row["Expected payment duration"],
                )

    # Get unique Revenue source types
    revenue_sources = RawData.objects.values_list(
        "revenue_source", flat=True
    ).distinct()

    # Return the list of unique Revenue source types
    return JsonResponse(list(revenue_sources), safe=False)


def formatAndValidateData(dataFrame):
    # Check if the dataFrame has the required columns
    required_columns = [
        "date",
        "invoice number",
        "value",
        "haircut percent",
        "Daily fee percent",
        "currency",
        "Revenue source",
        "customer",
        "Expected payment duration",
    ]
    if not all(col in dataFrame.columns for col in required_columns):
        return False, "Missing required columns"

    # Check if the dataFrame has any negative values
    if (dataFrame["value"] < 0).any():
        return False, "Negative values found in 'value' column"

    # Check if the dataFrame has any invalid date values
    try:
        pd.to_datetime(dataFrame["date"])
    except ValueError:
        return False, "Invalid date values found"

    # Check if the dataFrame has any invalid haircut percent values
    if (dataFrame["haircut percent"] < 0).any():
        return False, "Negative values found in 'haircut percent' column"

    # Check if the dataFrame has any invalid daily fee percent values
    if (dataFrame["Daily fee percent"] < 0).any():
        return False, "Negative values found in 'Daily fee percent' column"

    # Check if the dataFrame has any invalid currency values
    valid_currencies = ["USD", "EUR", "GBP", "JPY", "CNY"]
    if not all(currency in valid_currencies for currency in dataFrame["currency"]):
        return False, "Invalid currency values found"

    # Trim lead and trailing whitespaces from Revenue source and customer columns
    dataFrame["Revenue source"] = dataFrame["Revenue source"].str.strip()
    dataFrame["customer"] = dataFrame["customer"].str.strip()

    return True, ""


def totalValues(request):
    if request.method == "GET":
        client = request.GET.get("client")
        startdate = request.GET.get("startdate")
        enddate = request.GET.get("enddate")

        startdate = datetime.strptime(startdate, "%Y-%m-%d").date()
        enddate = datetime.strptime(enddate, "%Y-%m-%d").date()

        # Filter data
        total_value = RawData.objects.filter(
            customer=client, date__range=(startdate, enddate)
        ).aggregate(Sum("value"))["value__sum"]

        return JsonResponse({"total_value": total_value})


@csrf_exempt
def reset_database(request):
    if request.method == "POST":
        # Get all models
        models = apps.get_models()

        # Delete all records from all models
        for model in models:
            model.objects.all().delete()

        return HttpResponse("Database reset successfully.")


def get_database(request):
    if request.method == "GET":
        # Get all records from RawData model
        data = RawData.objects.all().values()

        return JsonResponse(list(data), safe=False)
