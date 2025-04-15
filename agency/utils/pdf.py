from reportlab.pdfgen import canvas
from io import BytesIO

def generate_coordinator_pdf(coordinators):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    y = 800

    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "State/County Entities")
    y -= 30

    p.setFont("Helvetica", 10)
    for coordinator in coordinators:
        for county in coordinator.counties.all():
            lines = [
                f"{county.name}: {coordinator.contact_first_name} {coordinator.contact_last_name} ({coordinator.entity_type.upper() if coordinator.entity_type else ''})",
                f"{coordinator.job_title}, {coordinator.contact_phone_number}, {coordinator.contact_email}",
                ""
            ]
            for line in lines:
                p.drawString(40, y, line)
                y -= 15
                if y < 50:
                    p.showPage()
                    y = 800

    p.save()
    buffer.seek(0)
    return buffer
