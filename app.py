from flask import Flask, render_template, request, send_file, redirect, url_for
import pymssql
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI 없는 백엔드 사용
import matplotlib.pyplot as plt
import os, uuid, io
import base64
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from db_config import get_connection_string

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 한글 폰트 설정 (크로스 플랫폼 지원)
def setup_korean_font():
    """한글 폰트를 등록합니다 (Windows/Linux 모두 지원)"""
    font_paths = [
        os.path.join('fonts', 'malgun.ttf'),  # 프로젝트 내 폰트
        os.path.join('fonts', 'NanumGothic.ttf'),
        'C:/Windows/Fonts/malgun.ttf',  # Windows
        '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',  # Linux
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('KoreanFont', font_path))
            return 'KoreanFont'
    
    # 폰트를 찾지 못한 경우 기본 폰트 사용 (한글 깨질 수 있음)
    print("경고: 한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
    return 'Helvetica'

KOREAN_FONT = setup_korean_font()
logger.info(f"한글 폰트 설정: {KOREAN_FONT}")

# MSSQL 연결 (db_config.py에서 관리)
# 연결 문자열은 요청 시마다 가져옵니다 (앱 시작 시 DB 연결 방지)
try:
    test_conn_str = get_connection_string()
    logger.info("DB 연결 설정 완료")
except Exception as e:
    logger.error(f"DB 연결 설정 오류: {e}")
    test_conn_str = None

# 공차 (추후 Spec별로 바꾸는 것도 가능)
USL = 10.5
LSL = 9.5

CODES = ["C-MOP10", "C-MHG50", "C-MHG60" ,"C-DTB20","C-DTB40","C-DTD10", "C-DTD20", "C-DTW20" ,"C-DWE21","C-DWL40","C-EDE10","C-EDE15","C-EDE25","C-EDG10","C-EDG20"]

HIST_DIR = os.path.join("static", "hist")
os.makedirs(HIST_DIR, exist_ok=True)

def parse_value(val):
    try:
        return float(str(val).replace(",", "."))
    except:
        return None

def fetch_df(code, start, end):
    """데이터베이스에서 데이터 조회"""
    query = """
        SELECT L.BaseNo, L.SData, L.EntryDate, B.Spec
        FROM dbo.GaGongSelfL AS L
        JOIN dbo.GaGongSelfBase AS B ON L.BaseNo = B.BaseNo
        WHERE L.CodeNo = %s
          AND L.EntryDate BETWEEN %s AND %s
    """
    try:
        conn_params = get_connection_string()
        logger.info(f"DB 조회: code={code}, start={start}, end={end}")
        with pymssql.connect(**conn_params) as conn:
            df = pd.read_sql(query, conn, params=[code, start, end])
        
        df["SData_clean"] = df["SData"].apply(parse_value)
        df = df.dropna(subset=["SData_clean"])
        logger.info(f"조회 결과: {len(df)}개 레코드")
        return df
    except Exception as e:
        logger.error(f"DB 조회 오류: {e}")
        raise

def analyze(df):
    results = []
    grouped = df.groupby("Spec")

    for spec, group in grouped:
        values = group["SData_clean"]
        if len(values) < 2:
            continue

        mean_val = float(values.mean())
        std_val = float(values.std())

        if std_val == 0:
            cp = float("inf")
            cpk = float("inf")
        else:
            cp = (USL - LSL) / (6 * std_val)
            cpk = min((USL - mean_val) / (3 * std_val),
                      (mean_val - LSL) / (3 * std_val))

        # 히스토그램 이미지 생성 (메모리에만 저장)
        fig, ax = plt.subplots(figsize=(3.0, 1.2))
        ax.hist(values, bins=10, edgecolor="black")
        ax.axvline(mean_val, linestyle="dashed", color='red')
        ax.set_title(str(spec), fontsize=9)
        fig.tight_layout()
        
        # BytesIO로 이미지를 메모리에 저장
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=150)
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
        plt.close(fig)

        results.append({
            "spec": spec,
            "mean": mean_val,
            "std": std_val,
            "cp": cp,
            "cpk": cpk,
            "hist_img": img_base64  # base64 인코딩된 이미지
        })

    return results

def make_pdf(code, start, end, results):
    pdf_bytes = io.BytesIO()
    c = pdf_canvas.Canvas(pdf_bytes, pagesize=A4)
    width, height = A4
    y = height - 20 * mm

    c.setFont(KOREAN_FONT, 14)
    c.drawString(20 * mm, y, "공정능력 분석 리포트")
    y -= 10 * mm
    c.setFont(KOREAN_FONT, 12)
    c.drawString(20 * mm, y, f"제품코드: {code}")
    y -= 7 * mm
    c.drawString(20 * mm, y, f"기간: {start} ~ {end}")
    y -= 12 * mm

    c.setFont(KOREAN_FONT, 10)
    c.drawString(20 * mm, y, "Spec          평균          표준편차           Cp            Cpk")
    y -= 8 * mm

    for r in results:
        if y < 40 * mm:
            c.showPage()
            y = height - 20 * mm
            c.setFont(KOREAN_FONT, 10)

        c.drawString(20 * mm, y,
                     f"{str(r['spec']):<12} {r['mean']:>7.3f}         {r['std']:>7.3f}          {r['cp']:>6.3f}        {r['cpk']:>6.3f}")

        # 히스토그램은 서버 파일 경로로 넣어야 함
        img_path = os.path.join(".", r["hist_url"].lstrip("/"))
        if os.path.exists(img_path):
            c.drawImage(img_path, 150 * mm, y - 4 * mm, width=35 * mm, height=18 * mm)

        y -= 20 * mm

    c.save()
    pdf_bytes.seek(0)
    return pdf_bytes

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        code = request.form.get("code")
        start = request.form.get("start")
        end = request.form.get("end")

        if code and start and end:
            try:
                df = fetch_df(code, start, end)
                if df.empty:
                    return render_template("index.html", codes=CODES, code=code, start=start, end=end, results=[], msg="실측값이 포함된 데이터가 없습니다.")
                
                results = analyze(df)
                return render_template("index.html", codes=CODES, code=code, start=start, end=end, results=results, msg=None)
            except Exception as e:
                logger.error(f"데이터 처리 오류: {e}")
                return render_template("index.html", codes=CODES, code=code, start=start, end=end, results=[], msg=f"오류 발생: {str(e)}")
    
    return render_template("index.html", codes=CODES, results=None)

@app.route("/report", methods=["POST"])
def report():
    code = request.form.get("code")
    start = request.form.get("start")
    end = request.form.get("end")

    if not code or not start or not end:
        return redirect(url_for("index"))

    try:
        df = fetch_df(code, start, end)
        if df.empty:
            return render_template("report.html", code=code, start=start, end=end, results=[], msg="실측값이 포함된 데이터가 없습니다.")

        results = analyze(df)
        return render_template("report.html", code=code, start=start, end=end, results=results, msg=None)
    except Exception as e:
        logger.error(f"리포트 생성 오류: {e}")
        return render_template("report.html", code=code, start=start, end=end, results=[], msg=f"오류 발생: {str(e)}")

@app.route("/pdf", methods=["POST"])
def pdf():
    code = request.form.get("code")
    start = request.form.get("start")
    end = request.form.get("end")

    try:
        df = fetch_df(code, start, end)
        results = analyze(df)

        pdf_io = make_pdf(code, start, end, results)
        filename = f"quality_{code}_{start}_{end}.pdf"

        return send_file(pdf_io, mimetype="application/pdf", as_attachment=True, download_name=filename)
    except Exception as e:
        logger.error(f"PDF 생성 오류: {e}")
        return f"PDF 생성 오류: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
