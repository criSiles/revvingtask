import json
import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import RawData
from datetime import datetime
from django.apps import apps
from decimal import Decimal


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

    # if value is not a number, cast it to float
    if dataFrame["value"].dtype != "float64":
        dataFrame["value"] = dataFrame["value"].astype(float)

    # Check if the dataFrame has any negative values
    if (dataFrame["value"] < 0).any():
        return False, "Negative values found in 'value' column"

    # Check if the dataFrame has any invalid date values
    try:
        pd.to_datetime(dataFrame["date"])
    except ValueError:
        return False, "Invalid date values found"

    # Check if the dataFrame is not a number, cast it to float
    if dataFrame["haircut percent"].dtype != "float64":
        dataFrame["haircut percent"] = dataFrame["haircut percent"].astype(float)

    # Check if the dataFrame has any invalid haircut percent values
    if (dataFrame["haircut percent"] < 0).any():
        return False, "Negative values found in 'haircut percent' column"

    # Check if the dataFrame is not a number, cast it to float
    if dataFrame["Daily fee percent"].dtype != "float64":
        dataFrame["Daily fee percent"] = dataFrame["Daily fee percent"].astype(float)

    # Check if the dataFrame has any invalid daily fee percent values
    if (dataFrame["Daily fee percent"] < 0).any():
        return False, "Negative values found in 'Daily fee percent' column"

    # Check if the dataFrame has any invalid currency values
    valid_currencies = ["USD", "EUR", "GBP", "JPY", "CNY"]
    if not all(currency in valid_currencies for currency in dataFrame["currency"]):
        return False, "Invalid currency values found"

    # Check if the expected payment duration is a number
    if dataFrame["Expected payment duration"].dtype != "int64":
        dataFrame["Expected payment duration"] = dataFrame[
            "Expected payment duration"
        ].astype(int)

    # Trim lead and trailing whitespaces from Revenue source and customer columns
    dataFrame["Revenue source"] = dataFrame["Revenue source"].str.strip()
    dataFrame["customer"] = dataFrame["customer"].str.strip()

    return True, ""


exchange_rate_dict = {
    ("USD", "EUR"): 0.85,
    ("EUR", "USD"): 1.18,
    ("USD", "GBP"): 0.73,
    ("GBP", "USD"): 1.37,
    # Add more exchange rates as needed
}


@csrf_exempt
def convert_and_sum_values(dataFrame, target_currency, exchange_rate_dict):
    advance_value = 0
    total_fees = 0
    # Convert values to target currency
    for index, row in dataFrame.iterrows():
        source_currency = row["currency"]
        if source_currency != target_currency:
            exchange_rate = exchange_rate_dict.get((source_currency, target_currency))
            if exchange_rate:
                dataFrame.at[index, "value"] = row["value"] * Decimal(
                    str(exchange_rate)
                )
        advance_value += (
            dataFrame.at[index, "value"] * dataFrame.at[index, "haircut_percent"] / 100
        )
        total_fees += (
            dataFrame.at[index, "value"]
            * dataFrame.at[index, "daily_fee_percent"]
            * dataFrame.at[index, "expected_payment_duration"]
            / 100
        )

    # Sum values
    total_value = dataFrame["value"].sum()

    # Round the values to 2 decimal places
    total_value = round(total_value, 2)
    advance_value = round(advance_value, 2)
    total_fees = round(total_fees, 2)

    return total_value, advance_value, total_fees


@csrf_exempt
def calculateRevenues(request):
    if request.method == "POST":
        #  Get parameters from the JSON request
        data = json.loads(request.body)
        revenue_source = data["revenue_source"]
        start_date = data["start_date"]
        end_date = data["end_date"]
        target_currency = data["target_currency"]

        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Filter data
        data = RawData.objects.filter(
            revenue_source=revenue_source,
            date__range=(start_date, end_date),
        ).values(
            "value",
            "haircut_percent",
            "daily_fee_percent",
            "currency",
            "expected_payment_duration",
        )

        dataFrame = pd.DataFrame.from_records(data)

        # Check if the dataFrame is empty
        if dataFrame.empty:
            return JsonResponse(
                {"error": "No data found for the given parameters"}, status=400
            )

        total_value, advance_value, total_fees = convert_and_sum_values(
            dataFrame, target_currency, exchange_rate_dict
        )

        return JsonResponse(
            {
                "total_value": total_value,
                "advance_value": advance_value,
                "total_fees": total_fees,
            }
        )


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
