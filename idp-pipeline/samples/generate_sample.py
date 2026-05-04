# generate_test_invoice.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_invoice():
    c = canvas.Canvas("samples/test_invoice_pass.pdf", pagesize=A4)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "INVOICE")
    
    c.setFont("Helvetica", 11)
    c.drawString(50, 770, "Invoice No: INV-2026-001")
    c.drawString(50, 750, "Issue Date: 2026-05-01")
    c.drawString(50, 730, "Due Date: 2026-06-01")
    
    c.drawString(50, 700, "FROM:")
    c.drawString(50, 680, "Acme Consulting Inc.")
    c.drawString(50, 660, "100 King Street West, Toronto ON M5X 1A9")
    c.drawString(50, 640, "billing@acmeconsulting.ca")
    
    c.drawString(300, 700, "BILL TO:")
    c.drawString(300, 680, "TD Bank Group")
    c.drawString(300, 660, "66 Wellington Street West, Toronto ON M5K 1A2")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 610, "Description")
    c.drawString(300, 610, "Qty")
    c.drawString(370, 610, "Unit Price")
    c.drawString(460, 610, "Amount")
    
    c.setFont("Helvetica", 11)
    c.drawString(50, 590, "Software Development Services")
    c.drawString(300, 590, "5")
    c.drawString(370, 590, "$200.00")
    c.drawString(460, 590, "$1000.00")
    
    c.drawString(50, 570, "Technical Documentation")
    c.drawString(300, 570, "3")
    c.drawString(370, 570, "$150.00")
    c.drawString(460, 570, "$450.00")
    
    c.drawString(50, 550, "Code Review Sessions")
    c.drawString(300, 550, "2")
    c.drawString(370, 550, "$175.00")
    c.drawString(460, 550, "$350.00")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(370, 520, "Subtotal:")
    c.drawString(460, 520, "$1800.00")
    c.drawString(370, 500, "Tax (13% HST):")
    c.drawString(460, 500, "$234.00")
    c.drawString(370, 480, "Total:")
    c.drawString(460, 480, "$2034.00")
    
    c.save()
    print("Generated: samples/test_invoice_pass.pdf")

generate_invoice()