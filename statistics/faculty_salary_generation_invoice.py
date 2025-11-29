import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import os

def generate_faculty_invoice(faculty_data, faculty_name, current_month, current_year):
    """Generate invoice for a specific faculty member"""
    
    # Create output directory
    output_dir = f"faculty_invoices\\{current_year}\\{current_month}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create PDF document
    invoice_file = os.path.join(output_dir, f"Adhyay_Academy_{faculty_name.replace(' ', '_')}_Salary_{datetime.today().strftime('%Y%m%d')}.pdf")
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
        leading=20,
    )

    # Header
    elements.append(Paragraph("<b>Adhyay Academy</b>", title_style))
    elements.append(Paragraph("<b>Faculty Salary Invoice</b>", title_style))
    
    elements.append(Spacer(1, 20))

    # Faculty Info
    date_today = datetime.today().strftime("%d-%m-%Y")
    info_style = styles["Normal"]
    elements.append(Paragraph(f"<b>Faculty Name:</b> {faculty_name}", info_style))
    elements.append(Paragraph(f"<b>Month:</b> {current_month} {current_year}", info_style))
    
    elements.append(Paragraph(f"<b>Invoice Date:</b> {date_today}", info_style))
    
    elements.append(Spacer(1, 15))

    # Create table data
    data = [["Class", "Hours", "Amount (Rs.)"]]
    total_hours = 0
    total_amount = 0
    
    # Group by class and sum hours and total
    class_summary = faculty_data.groupby('Class').agg({
        'Hours': 'sum',
        'Total': 'sum'
    }).reset_index()
    
    for _, row in class_summary.iterrows():
        data.append([
            row['Class'],
            f"{int(row['Hours'])}",
            f"{row['Total']:,.2f}"
        ])
        total_hours += row['Hours']
        total_amount += row['Total']

    # Add total row
    data.append(["Grand Total", f"{total_hours}", f"{total_amount:,.2f}"])

    # Create and style table
    table = Table(data, colWidths=[200, 100, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -2), colors.HexColor("#F8F9F9")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EAECEE")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(table)

    # Footer
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "<b>Note:</b> This is a system-generated salary invoice from Adhyay Academy.",
        styles["Italic"]
    ))

    # Build PDF
    doc.build(elements)
    print(f"Generated invoice for {faculty_name}: {invoice_file}")
    return invoice_file

def generate_combined_invoice(df, current_month, current_year):
    """Generate a combined invoice for all faculty members"""
    
    # Create output directory
    output_dir = f"faculty_invoices\\{current_year}\\{current_month}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create PDF document
    invoice_file = os.path.join(output_dir, f"Adhyay_Academy_Combined_Salary_{datetime.today().strftime('%Y%m%d')}.pdf")
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
        leading=20,
    )

    # Header
    elements.append(Paragraph("<b>Adhyay Academy</b>", title_style))
    elements.append(Paragraph("<b>Combined Faculty Salary Report</b>", title_style))
    elements.append(Spacer(1, 20))

    # Report Info
    date_today = datetime.today().strftime("%d-%m-%Y")
    info_style = styles["Normal"]
    elements.append(Paragraph(f"<b>Month:</b> {current_month} {current_year}", info_style))
    elements.append(Paragraph(f"<b>Date:</b> {date_today}", info_style))
    elements.append(Spacer(1, 15))

    # Create table data
    data = [["Faculty Name", "Class", "Hours", "Amount (Rs.)"]]
    grand_total_hours = 0
    grand_total_amount = 0

    # Process each faculty's data
    for faculty in sorted(df['Faculty'].unique()):
        faculty_data = df[df['Faculty'] == faculty]
        
        # Group by class and sum hours and total
        class_summary = faculty_data.groupby('Class').agg({
            'Hours': 'sum',
            'Total': 'sum'
        }).reset_index()
        
        faculty_total_hours = 0
        faculty_total_amount = 0
        
        # Add faculty's class-wise details
        for _, row in class_summary.iterrows():
            data.append([
                faculty if faculty_total_hours == 0 else "",  # Show faculty name only once
                row['Class'],
                f"{int(row['Hours'])}",
                f"{row['Total']:,.2f}"
            ])
            faculty_total_hours += row['Hours']
            faculty_total_amount += row['Total']
            
        # Add faculty subtotal
        data.append([
            "Subtotal",
            "",
            f"{faculty_total_hours}",
            f"{faculty_total_amount:,.2f}"
        ])
        data.append(["", "", "", ""])  # Empty row for spacing
        
        grand_total_hours += faculty_total_hours
        grand_total_amount += faculty_total_amount

    # Add grand total row
    data.append([
        "Grand Total",
        "",
        f"{grand_total_hours}",
        f"{grand_total_amount:,.2f}"
    ])

    # Create and style table
    table = Table(data, colWidths=[150, 150, 100, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),  # Center align numbers
        ("ALIGN", (0, 0), (1, -1), "LEFT"),     # Left align text
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EAECEE")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(table)

    # Footer
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "<b>Note:</b> This is a system-generated combined salary report from Adhyay Academy.",
        styles["Italic"]
    ))

    # Build PDF
    doc.build(elements)
    print(f"Generated combined invoice: {invoice_file}")
    return invoice_file

def main():
    # Configuration
    GENERATE_INDIVIDUAL = True  # Set to False to skip individual invoices
    GENERATE_COMBINED = True    # Set to False to skip combined invoice
    
    try:
        csv_file = "C:\\Users\\DELL\\Downloads\\AA Attendance - November.csv"
        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date'], format="%d-%m-%Y")
        
        first_date = df['Date'].iloc[0]
        current_month = first_date.strftime("%B")
        current_year = first_date.year
        
        if GENERATE_INDIVIDUAL:
            for faculty in df['Faculty'].unique():
                faculty_data = df[df['Faculty'] == faculty]
                generate_faculty_invoice(faculty_data, faculty, current_month, current_year)
            print("\n✅ Individual invoices generated successfully!")
            
        if GENERATE_COMBINED:
            generate_combined_invoice(df, current_month, current_year)
            print("\n✅ Combined invoice generated successfully!")
        
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found!")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()