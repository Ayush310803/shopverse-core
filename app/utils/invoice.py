import os
import pdfkit
from app.schemas.orderschema import OrderResponse
from jinja2 import Template
from fastapi import BackgroundTasks
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from twilio.rest import Client
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from email.mime.application import MIMEApplication
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.colors import orange, white 
import os
from datetime import datetime
from app.config import settings

def send_sms_notification(phone_number, message_body):
    account_sid= settings.ACCOUNT_SID
    auth_token= settings.AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message_body,
        from_= settings.PHONE_NO,
        to=phone_number
    )
    return message.sid

templates = Jinja2Templates(directory="app/templates")


def add_header_footer(canvas, doc):
    width, height = letter

    canvas.setFillColor(orange)
    canvas.rect(0, height - 50, width, 50, stroke=0, fill=1)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.setFillColor(white)
    canvas.drawString(30, height - 35, "Invoice - Ecommerce")  

    canvas.setFillColor(orange)
    canvas.rect(0, 0, width, 50, stroke=0, fill=1)
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(white)
    canvas.drawString(30, 20, "Thank you for your business!")  
    canvas.drawRightString(width - 30, 20, f"Page {doc.page}")  

def generate_invoice_pdf(order_data, output_dir="static/invoices"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    pdf_filename = f"invoice_{order_data.order_id}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='InvoiceHeading', fontSize=24, alignment=1, leading=30, spaceAfter=20))
    styles.add(ParagraphStyle(name='TableHeading', fontSize=16, leading=22))

    story.append(Paragraph("INVOICE", styles['InvoiceHeading']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Invoice Number: {invoice_number}", styles['Normal']))
    story.append(Paragraph(f"Order ID: {order_data.order_id}", styles['Normal']))
    story.append(Paragraph(f"Buyer: {order_data.buyer_name}", styles['Normal']))
    story.append(Paragraph(f"Order Date: {order_data.order_date}", styles['Normal']))
    story.append(Spacer(1, 24))

    story.append(Paragraph("Items", styles['TableHeading']))
    table_data = [["Index", "Product Name", "Quantity", "Price", "Total_Price"]] + [
        [index + 1, item.product_name, item.quantity, f"Rs{item.price}", f"Rs{item.price * item.quantity}"]
        for index, item in enumerate(order_data.items)
    ]
    items_table = Table(table_data, colWidths=[50, 100, 100, 100, 100])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Total Price: Rs{order_data.total_price}", styles['Normal']))
    if order_data.coupon_code:
        story.append(Paragraph(f"Coupon Code: {order_data.coupon_code}", styles['Normal']))
        discount_amount = f"{order_data.total_price - order_data.final_price:.2f}"
        final_price = f"{order_data.final_price:.2f}"
    
        story.append(Paragraph(f"Discount Amount: - Rs{discount_amount}", styles['Normal']))
        story.append(Paragraph(f"Final Price: Rs{final_price}", styles['Normal']))
    story.append(Spacer(1, 24))

    story.append(Paragraph("Vendor Details", styles['TableHeading']))
    vendor_data = {}
    for index, item in enumerate(order_data.items):
        vendor_name = item.seller.seller_name
        contact = item.seller.seller_contact or 'N/A'
        store = item.seller.store_name or 'N/A'
        location = item.seller.store_location or 'N/A'
        if vendor_name not in vendor_data:
            vendor_data[vendor_name] = {
                "contact": contact,
                "store": store,
                "location": location,
                "products": []
            }
        vendor_data[vendor_name]["products"].append(item.product_name)

    vendor_table_data = [["Index", "Vendor Name", "Contact", "Store", "Location", "Products"]] + [
        [
            index + 1,
            vendor_name,
            details["contact"],
            details["store"],
            details["location"],
            ', '.join(details["products"])
        ]
        for index, (vendor_name, details) in enumerate(vendor_data.items())
    ]
    vendor_table = Table(vendor_table_data, colWidths=[35, 90, 90, 80, 80, 75])
    vendor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ]))
    story.append(vendor_table)
    story.append(Spacer(1, 12))

    address_table_data = [
        [
            Paragraph("Delivery Address", styles['TableHeading']),
            ""
        ],
        [
            Paragraph("<br />".join([
                order_data.delivery_address.address_line1,
                f"{order_data.delivery_address.city}, {order_data.delivery_address.state}",
                f"{order_data.delivery_address.country} - {order_data.delivery_address.postal_code}"
            ]), styles['Normal']),
            Image("./static/logo/paidlogo.jpg", width=100, height=80) if order_data.payment_method == 'online' else Image(
                "./static/logo/unpaidlogo.jpg", width=100, height=80)
        ]
    ]
    address_table = Table(address_table_data, colWidths=[400, 100])
    address_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(address_table)
    story.append(Spacer(1, 24))

    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    return pdf_path

def send_email_with_invoice(to_email, subject, order_data: OrderResponse, attachment_path: str):
    sender_email = settings.SENDER_EMAIL
    password = settings.EMAIL_PASSWORD

    with open('app/templates/invoice_temp.html', 'r') as file:
        template = Template(file.read())
    
    html_content = template.render(
        order_id=order_data.order_id,
        buyer_name=order_data.buyer_name,
        order_date=order_data.order_date,
        items=order_data.items,
        total_price=order_data.total_price,
        delivery_address=order_data.delivery_address,
        coupon_code=order_data.coupon_code if hasattr(order_data, 'coupon_code') else None,
        discount_price=order_data.discount_price if hasattr(order_data, 'discount_price') else 0,
        final_price=order_data.final_price if hasattr(order_data, 'final_price') else order_data.total_price
    )

    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html'))

    with open(attachment_path, 'rb') as attachment:
        part = MIMEApplication(attachment.read(), _subtype="pdf")
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
        msg.attach(part)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)

def send_low_stock_email(seller_email: str, product_name: str):
    sender_email = settings.SENDER_EMAIL
    password = settings.EMAIL_PASSWORD

    subject = f"Low Stock Alert: {product_name}"
    body = f"The stock of your product '{product_name}' is below 10. Please replenish your stock."

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = seller_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  
            server.login(sender_email, password)
            server.sendmail(sender_email, seller_email, message.as_string())
        print(f"Low stock email sent to {seller_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")