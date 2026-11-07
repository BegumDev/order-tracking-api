import azure.functions as func
import pymssql
import os
import json
import logging

app = func.FunctionApp()

@app.function_name(name="OrderTracking")
@app.route(route="orderstatus", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def order_status(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for order status.')
    
    order_id = req.params.get("orderId")
    
    if not order_id:
        return func.HttpResponse(
            json.dumps({"error": "Please supply an orderId parameter."}),
            mimetype="application/json",
            status_code=400
        )
    
    try:
        # Connect to Azure SQL Database using environment variables
        conn = pymssql.connect(
            server=os.environ.get("DB_SERVER", "rb-sql-server.database.windows.net"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME", "cloudcart-db")
        )
        
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT order_id, status, total_amount, shipping_address, created_at FROM Orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()
        conn.close()
        
        if not order:
            return func.HttpResponse(
                json.dumps({"error": f"Order #{order_id} not found."}),
                mimetype="application/json",
                status_code=404
            )
            
        return func.HttpResponse(
            json.dumps(order, default=str),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error connecting to database."}),
            mimetype="application/json",
            status_code=500
        )