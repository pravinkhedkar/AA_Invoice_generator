import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import os

def read_student_data(excel_file, detailed_report=False):
    """Read student data from all sheets in Excel file"""
    students_fees = {}
    
    # Read all sheets from Excel file
    excel = pd.ExcelFile(excel_file)
    
    for sheet_name in excel.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # Forward fill student names (fills NaN with previous valid student name)
        df['Student'] = df['Student'].fillna(method='ffill')
        
        # Remove rows where all required columns are empty
        df = df.dropna(subset=['Student', 'Date', 'Paid'], how='all')
        
        # Process each student in the sheet
        for student_name in df['Student'].unique():
            student_data = df[df['Student'] == student_name].copy()
            student_name = str(student_name).strip()
            
            # Get the first row for total fees (initial fee amount)
            first_row = student_data.iloc[0]
            total_fees = float(first_row['Fee']) if pd.notna(first_row['Fee']) else 0.0
            
            # Get the last row for current remaining amount
            # latest_row = student_data.iloc[-1]
            remaining_fees = float(first_row['Remaining']) if pd.notna(first_row['Remaining']) else total_fees
            
            # Calculate total fees paid
            paid_fees = total_fees - remaining_fees
            
            # Create payment history if detailed report is requested
            payment_history = []
            if detailed_report:
                # Get rows where Paid column has values
                paid_rows = student_data[pd.notna(student_data['Paid'])]
                for _, row in paid_rows.iterrows():
                    if pd.notna(row['Paid']) and float(row['Paid']) > 0:
                        payment_history.append({
                            'date': row['Date'].strftime('%d-%m-%Y') if isinstance(row['Date'], pd._libs.tslibs.timestamps.Timestamp) else row['Date'],
                            'amount': float(row['Paid']),
                            'remaining': float(row['Remaining']) if pd.notna(row['Remaining']) else 0.0
                        })
            
            students_fees[student_name] = {
                'class_name': sheet_name,
                'total_fees': total_fees,
                'paid_fees': paid_fees,
                'remaining_fees': remaining_fees,
                'payment_history': payment_history if detailed_report else None
            }
    
    return students_fees

def generate_invoice(student_name, fees_data):
    # Create output directory if it doesn't exist
    output_dir = "invoices"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create PDF document
    invoice_file = os.path.join(output_dir, f"Adhyay_Academy_{student_name.replace(' ', '_')}_Invoice.pdf")
    doc = SimpleDocTemplate(invoice_file, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title Style
    title_style = ParagraphStyle(
        name="TitleStyle",
        fontSize=16,
        alignment=1,
        spaceAfter=20,
        textColor=colors.HexColor("#2E4053"),
    )

    # Header
    elements.append(Paragraph("<b>Adhyay Academy</b>", title_style))
    elements.append(Paragraph("<b>Student Fee Invoice</b>", title_style))
    elements.append(Spacer(1, 20))

    # Invoice Info
    date_today = datetime.today().strftime("%d-%m-%Y")
    info_style = styles["Normal"]
    elements.append(Paragraph(f"<b>Student Name:</b> {student_name}", info_style))
    elements.append(Paragraph(f"<b>Class:</b> {fees_data['class_name']}", info_style))
    elements.append(Paragraph(f"<b>Invoice Date:</b> {date_today}", info_style))
    elements.append(Spacer(1, 20))

    # Fee Details Table
    data = [
        ["Description", "Amount (Rs.)"],
        ["Total Fees", f"{fees_data['total_fees']:,.2f}"],
        ["Paid Fees", f"{fees_data['paid_fees']:,.2f}"],
        ["Remaining Fees", f"{fees_data['remaining_fees']:,.2f}"]
    ]

    table = Table(data, colWidths=[300, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#34495E")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#EAECEE"))
    ]))
    elements.append(table)

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        "<b>Note:</b> This is a system-generated invoice from Adhyay Academy.",
        styles["Italic"]
    ))

    # Build PDF
    doc.build(elements)
    print(f"Generated invoice for {student_name} ({fees_data['class_name']}): {invoice_file}")

def generate_detailed_invoice(student_name, fees_data):
    """Generate detailed invoice with payment history for a student"""
    output_dir = "invoices/detailed"
    os.makedirs(output_dir, exist_ok=True)
    
    invoice_file = os.path.join(output_dir, f"Adhyay_Academy_{student_name.replace(' ', '_')}_Detailed_Invoice.pdf")
    doc = SimpleDocTemplate(invoice_file, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title Style
    title_style = ParagraphStyle(
        name="TitleStyle",
        fontSize=16,
        alignment=1,
        spaceAfter=20,
        textColor=colors.HexColor("#2E4053"),
    )

    # Header
    elements.append(Paragraph("<b>Adhyay Academy</b>", title_style))
    elements.append(Paragraph("<b>Student Fee Detailed Report</b>", title_style))
    elements.append(Spacer(1, 20))

    # Student Info
    info_style = styles["Normal"]
    elements.append(Paragraph(f"<b>Student Name:</b> {student_name}", info_style))
    elements.append(Paragraph(f"<b>Class:</b> {fees_data['class_name']}", info_style))
    elements.append(Paragraph(f"<b>Report Date:</b> {datetime.today().strftime('%d-%m-%Y')}", info_style))
    elements.append(Spacer(1, 20))

    # Current Status Table
    # Current Status Table
    elements.append(Paragraph("<b>Current Status:</b>", info_style))
    elements.append(Spacer(1, 10))
    
    current_data = [
        ["Description", "Amount (Rs.)"],
        ["Total Fees", f"{fees_data['total_fees']:,.2f}"],
        ["Total Fees Paid", f"{fees_data['paid_fees']:,.2f}"],
        ["Balance Remaining", f"{fees_data['remaining_fees']:,.2f}"]
    ]

    current_table = Table(current_data, colWidths=[300, 200])
    current_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#34495E")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(current_table)
    elements.append(Spacer(1, 20))

    # Payment History Table
    if fees_data['payment_history']:
        elements.append(Paragraph("<b>Payment History:</b>", info_style))
        elements.append(Spacer(1, 10))
        
        history_data = [["Date", "Amount Paid (Rs.)"]]
        for payment in fees_data['payment_history']:
            history_data.append([
                payment['date'],
                f"{payment['amount']:,.2f}"
            ])

        history_table = Table(history_data, colWidths=[200, 300])
        history_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#34495E")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(history_table)

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        "<b>Note:</b> This is a detailed fee report generated by Adhyay Academy.",
        styles["Italic"]
    ))

    # Build PDF
    doc.build(elements)
    print(f"Generated detailed invoice for {student_name}: {invoice_file}")

def generate_combined_invoice(students_fees):
    """Generate a single combined invoice for all students"""
    output_dir = "invoices"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create PDF document
    invoice_file = os.path.join(output_dir, f"Adhyay_Academy_Combined_Invoice_{datetime.today().strftime('%Y%m%d')}.pdf")
    doc = SimpleDocTemplate(invoice_file, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title Style
    title_style = ParagraphStyle(
        name="TitleStyle",
        fontSize=16,
        alignment=1,
        spaceAfter=20,
        textColor=colors.HexColor("#2E4053"),
    )

    # Header
    elements.append(Paragraph("<b>Adhyay Academy</b>", title_style))
    elements.append(Paragraph("<b>Combined Fee Status Report</b>", title_style))
    elements.append(Spacer(1, 20))

    # Date
    date_today = datetime.today().strftime("%d-%m-%Y")
    elements.append(Paragraph(f"<b>Date:</b> {date_today}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Create table data
    data = [["Student Name", "Class", "Total Fees (Rs.)", "Paid Fees (Rs.)", "Remaining (Rs.)"]]
    
    # Group students by class and sort within each class
    class_groups = {}
    for student_name, info in students_fees.items():
        class_name = info['class_name']
        if class_name not in class_groups:
            class_groups[class_name] = []
        class_groups[class_name].append((student_name, info))
    
    # Add student rows - sorted by class, then by student name
    total_fees = paid_fees = remaining_fees = 0
    for class_name in sorted(class_groups.keys()):
        # Sort students within each class
        students = sorted(class_groups[class_name])
        for student_name, info in students:
            data.append([
                student_name,
                info['class_name'],
                f"{info['total_fees']:,.2f}",
                f"{info['paid_fees']:,.2f}",
                f"{info['remaining_fees']:,.2f}"
            ])
            total_fees += info['total_fees']
            paid_fees += info['paid_fees']
            remaining_fees += info['remaining_fees']
    
    # Add summary row
    data.append([
        "TOTAL (Rs.)",
        "",
        f"{total_fees:,.2f}",
        f"{paid_fees:,.2f}",
        f"{remaining_fees:,.2f}"
    ])

    # Create and style table
    table = Table(data, colWidths=[120, 80, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#34495E")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#EAECEE")),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(table)

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        "<b>Note:</b> This is a system-generated report for administrative purposes.",
        styles["Italic"]
    ))

    # Build PDF
    doc.build(elements)
    print(f"Generated combined invoice: {invoice_file}")
    return invoice_file

if __name__ == "__main__":
    # Configuration
    excel_file = "C:\\Users\\DELL\\Downloads\\AA Fee.xlsx"
    generate_individual = False  # Set to False for combined invoice only
    generate_combined = False    # Set to False for individual invoices only
    generate_detailed = True  # New flag for detailed reports
    try:
        # Read student data from Excel
        students_fees = read_student_data(excel_file, True)
        
        if generate_detailed:
            for student_name, fees_data in students_fees.items():
                generate_detailed_invoice(student_name, fees_data)
            print(f"\n✅ Successfully generated {len(students_fees)} detailed reports!")
        # Generate invoices based on flags
        if generate_individual:
            for student_name, fees_data in students_fees.items():
                generate_invoice(student_name, fees_data)
            print(f"\n✅ Successfully generated {len(students_fees)} individual invoices!")
        
        if generate_combined:
            combined_file = generate_combined_invoice(students_fees)
            print(f"\n✅ Successfully generated combined invoice!")
        
    except FileNotFoundError:
        print(f"Error: Excel file '{excel_file}' not found!")
    except Exception as e:
        print(f"Error: {str(e)}")