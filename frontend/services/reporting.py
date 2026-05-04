from fpdf import FPDF


def build_match_report(
    candidate_name: str,
    experience_level: str,
    matched_skills: list[str],
    missing_skills: list[str],
    recommendations: list[str],
) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, "Resume Match Report", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Candidate: {candidate_name}", ln=True)
    pdf.cell(0, 8, f"Experience Level: {experience_level}", ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, "Matched Skills:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 6, ", ".join(matched_skills) or "None")
    pdf.ln(2)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, "Missing Skills:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 6, ", ".join(missing_skills) or "None")
    pdf.ln(2)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, "Recommendations:", ln=True)
    pdf.set_font("Arial", size=11)
    for rec in recommendations:
        pdf.multi_cell(0, 6, f"- {rec}")

    return bytes(pdf.output(dest="S"))
