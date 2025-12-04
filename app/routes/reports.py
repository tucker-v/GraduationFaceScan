from app.db import get_db_connection
import psycopg2
from fastapi import APIRouter, HTTPException
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from fastapi.responses import StreamingResponse
from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

router = APIRouter(prefix="/api/reports", tags=["queue"])


@router.get("/charts")
def get_reports():
    try:
        charts = get_report_images(include_prefix=True)
        return charts
    except psycopg2.Error as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/download")
def download_report():
    images = get_report_images(include_prefix=False)
    pdf_buffer = create_pdf_from_base64(images)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="charts_report.pdf"'
        },
    )


# ---------- Data fetch functions ----------


def get_students_per_degree():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT degree_name, COUNT(*) AS num_students
        FROM STUDENT
        GROUP BY degree_name
        ORDER BY num_students DESC;
    """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    labels, values, cleaned_rows = [], [], []
    for degree_name, count in rows:
        label = degree_name if degree_name is not None else "Unknown"
        labels.append(label)
        values.append(count)
        cleaned_rows.append([label, count])
    return labels, values, cleaned_rows


def get_queued_status_breakdown():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT status, COUNT(*) AS num_entries
        FROM QUEUED
        GROUP BY status
        ORDER BY num_entries DESC;
    """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    labels, values, cleaned_rows = [], [], []
    for status, count in rows:
        label = status if status is not None else "Unknown"
        labels.append(label)
        values.append(count)
        cleaned_rows.append([label, count])
    return labels, values, cleaned_rows


def get_students_per_degree_type():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT degree_type, COUNT(*) AS num_students
        FROM STUDENT
        GROUP BY degree_type
        ORDER BY num_students DESC;
    """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    labels, values, cleaned_rows = [], [], []
    for degree_type, count in rows:
        label = degree_type if degree_type is not None else "Unknown"
        labels.append(label)
        values.append(count)
        cleaned_rows.append([label, count])
    return labels, values, cleaned_rows


def get_biometric_opt_in_breakdown():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT opt_in_biometric, COUNT(*) AS num_students
        FROM STUDENT
        GROUP BY opt_in_biometric
        ORDER BY num_students DESC;
    """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    labels, values, cleaned_rows = [], [], []
    for opt_in, count in rows:
        if opt_in is True:
            label = "Opt-in"
        elif opt_in is False:
            label = "Not Opt-in"
        else:
            label = "Unknown"
        labels.append(label)
        values.append(count)
        cleaned_rows.append([label, count])
    return labels, values, cleaned_rows


def get_students_per_ceremony():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            C.name AS ceremony_name,
            COUNT(S.PID) AS num_students
        FROM CEREMONY C
        LEFT JOIN DEGREE D ON D.ceremony_id = C.ceremony_id
        LEFT JOIN STUDENT S ON S.degree_name = D.degree_name
        GROUP BY C.name
        ORDER BY num_students DESC;
    """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    labels, values, cleaned_rows = [], [], []
    for ceremony_name, count in rows:
        label = ceremony_name if ceremony_name is not None else "Unknown"
        labels.append(label)
        values.append(count)
        cleaned_rows.append([label, count])
    return labels, values, cleaned_rows


# ---------- Ceremony type mapping ----------


def map_ceremony_to_type(ceremony_name: str) -> str:
    if not ceremony_name:
        return "OTHER"

    name_lower = ceremony_name.lower()
    if "business" in name_lower:
        return "BUS"
    if "engineer" in name_lower:
        return "ENG"
    if "science" in name_lower:
        return "SCI"
    if "art" in name_lower:
        return "ART"
    return "OTHER"


# ---------- Managerial aggregates (DB only) ----------


def get_managerial_aggregates():
    """
    Compute managerial aggregates (min/avg/max etc.) for bar charts.
    Mirrors the logic of build_managerial_reports but returns values in memory.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # 1) Overall student counts and biometric opt-in
    cur.execute(
        """
        SELECT
            COUNT(*) AS total_students,
            SUM(CASE WHEN opt_in_biometric = TRUE THEN 1 ELSE 0 END) AS total_opt_in,
            SUM(CASE WHEN opt_in_biometric = FALSE THEN 1 ELSE 0 END) AS total_not_opt_in
        FROM STUDENT;
    """
    )
    total_students, total_opt_in, total_not_opt_in = cur.fetchone()

    # 2) Min/avg/max number of students per degree
    cur.execute(
        """
        SELECT
            MIN(num_students),
            MAX(num_students),
            AVG(num_students)
        FROM (
            SELECT degree_name, COUNT(*) AS num_students
            FROM STUDENT
            GROUP BY degree_name
        ) t;
    """
    )
    min_deg, max_deg, avg_deg = cur.fetchone()

    # 3) Min/avg/max number of students per ceremony
    cur.execute(
        """
        SELECT
            MIN(num_students),
            MAX(num_students),
            AVG(num_students)
        FROM (
            SELECT
                C.ceremony_id,
                COUNT(S.PID) AS num_students
            FROM CEREMONY C
            LEFT JOIN DEGREE D ON D.ceremony_id = C.ceremony_id
            LEFT JOIN STUDENT S ON S.degree_name = D.degree_name
            GROUP BY C.ceremony_id
        ) t;
    """
    )
    min_cer, max_cer, avg_cer = cur.fetchone()

    # 4) Min/avg/max number of students per degree type
    cur.execute(
        """
        SELECT
            MIN(num_students),
            MAX(num_students),
            AVG(num_students)
        FROM (
            SELECT degree_type, COUNT(*) AS num_students
            FROM STUDENT
            GROUP BY degree_type
        ) t;
    """
    )
    min_dtype, max_dtype, avg_dtype = cur.fetchone()

    # 5) Min/avg/max queued entries per ceremony
    cur.execute(
        """
        SELECT
            MIN(num_entries),
            MAX(num_entries),
            AVG(num_entries)
        FROM (
            SELECT ceremony_id, COUNT(*) AS num_entries
            FROM QUEUED
            GROUP BY ceremony_id
        ) t;
    """
    )
    min_q, max_q, avg_q = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "overall": (total_students, total_opt_in or 0, total_not_opt_in or 0),
        "students_per_degree": (min_deg or 0, float(avg_deg or 0), max_deg or 0),
        "students_per_ceremony": (min_cer or 0, float(avg_cer or 0), max_cer or 0),
        "students_per_degree_type": (min_dtype or 0, float(avg_dtype or 0), max_dtype or 0),
        "queued_per_ceremony": (min_q or 0, float(avg_q or 0), max_q or 0),
    }


# ---------- Chart helpers (pie + bar) ----------


def make_pie_chart(labels, values, title, legend_title, include_prefix=True):
    if not labels or not values:
        print(f"No data found for chart: {title}")
        return

    slice_labels = [str(lbl)[:3].upper() for lbl in labels]

    fig, ax = plt.subplots(figsize=(10, 5))

    wedges, text_labels, autotexts = ax.pie(
        values,
        labels=slice_labels,
        startangle=90,
        autopct="%1.1f%%",
        rotatelabels=True,
        labeldistance=1.05,
    )

    plt.subplots_adjust(left=0.05, right=0.7)

    ax.legend(
        wedges,
        labels,
        title=legend_title,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        borderaxespad=0.0,
    )

    ax.set_title(title)
    ax.axis("equal")

    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    data_url = f"data:image/png;base64,{img_base64}" if include_prefix else img_base64
    plt.close(fig)
    return data_url


def make_bar_chart(categories, values, title, ylabel, include_prefix=True):
    if not categories or not values:
        print(f"No data found for chart: {title}")
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(categories, values)
    ax.set_title(title)
    ax.set_ylabel(ylabel)

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.1f}",
            ha="center",
            va="bottom",
        )

    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    data_url = f"data:image/png;base64,{img_base64}" if include_prefix else img_base64
    plt.close(fig)
    return data_url


# ---------- Aggregate to images ----------


def get_report_images(include_prefix: bool):
    # Pie charts
    spd_labels, spd_values, _ = get_students_per_degree()
    spd_pie_chart_image = make_pie_chart(
        labels=spd_labels,
        values=spd_values,
        title="Students Per Degree",
        legend_title="Degree",
        include_prefix=include_prefix,
    )

    q_labels, q_values, _ = get_queued_status_breakdown()
    q_pie_chart_image = make_pie_chart(
        labels=q_labels,
        values=q_values,
        title="Queued Status Breakdown",
        legend_title="Status",
        include_prefix=include_prefix,
    )

    spt_labels, spt_values, _ = get_students_per_degree_type()
    spt_pie_chart_image = make_pie_chart(
        labels=spt_labels,
        values=spt_values,
        title="Students Per Degree Type",
        legend_title="Degree Type",
        include_prefix=include_prefix,
    )

    o_labels, o_values, _ = get_biometric_opt_in_breakdown()
    o_pie_chart_image = make_pie_chart(
        labels=o_labels,
        values=o_values,
        title="Biometric Opt-in Status",
        legend_title="Opt in Status",
        include_prefix=include_prefix,
    )

    c_labels, c_values, _ = get_students_per_ceremony()
    c_pie_chart_image = make_pie_chart(
        labels=c_labels,
        values=c_values,
        title="Students Per Ceremony",
        legend_title="Ceremony",
        include_prefix=include_prefix,
    )

    # Managerial bar charts
    mgr = get_managerial_aggregates()

    overall_bar = make_bar_chart(
        categories=["Total Students", "Opt-in", "Not Opt-in"],
        values=list(mgr["overall"]),
        title="Overall Students and Biometric Opt-in",
        ylabel="Count",
        include_prefix=include_prefix,
    )

    deg_bar = make_bar_chart(
        categories=["Min per Degree", "Avg per Degree", "Max per Degree"],
        values=list(mgr["students_per_degree"]),
        title="Students per Degree (Min/Avg/Max)",
        ylabel="Students",
        include_prefix=include_prefix,
    )

    cer_bar = make_bar_chart(
        categories=["Min per Ceremony", "Avg per Ceremony", "Max per Ceremony"],
        values=list(mgr["students_per_ceremony"]),
        title="Students per Ceremony (Min/Avg/Max)",
        ylabel="Students",
        include_prefix=include_prefix,
    )

    dtype_bar = make_bar_chart(
        categories=["Min per Degree Type", "Avg per Degree Type", "Max per Degree Type"],
        values=list(mgr["students_per_degree_type"]),
        title="Students per Degree Type (Min/Avg/Max)",
        ylabel="Students",
        include_prefix=include_prefix,
    )

    queued_bar = make_bar_chart(
        categories=["Min Queued/Ceremony", "Avg Queued/Ceremony", "Max Queued/Ceremony"],
        values=list(mgr["queued_per_ceremony"]),
        title="Queued Entries per Ceremony (Min/Avg/Max)",
        ylabel="Queued Entries",
        include_prefix=include_prefix,
    )

    return [
        spd_pie_chart_image,
        q_pie_chart_image,
        spt_pie_chart_image,
        o_pie_chart_image,
        c_pie_chart_image,
        overall_bar,
        deg_bar,
        cer_bar,
        dtype_bar,
        queued_bar,
    ]


# ---------- PDF helper ----------


def create_pdf_from_base64(images, title="Graduation Reports") -> BytesIO:
    """
    Takes a list of base64 images (no data: prefix) and returns an in-memory PDF buffer.
    """
    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Title"]

    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.3 * inch))

    for b64str in images:
        if not b64str:
            continue
        img_bytes = base64.b64decode(b64str)
        img_buffer = BytesIO(img_bytes)

        chart = Image(img_buffer)
        chart._restrictSize(7 * inch, 9 * inch)
        elements.append(chart)
        elements.append(Spacer(1, 0.5 * inch))

    pdf.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer
