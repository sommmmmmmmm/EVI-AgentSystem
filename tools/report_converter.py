# -*- coding: utf-8 -*-
"""
보고서 변환 도구 - Markdown을 HTML 및 PDF로 변환
"""

import markdown
from datetime import datetime
from pathlib import Path


class ReportConverter:
    """
    Markdown 보고서를 HTML 및 PDF로 변환
    """

    def __init__(self):
        self.html_template = self._create_html_template()

    def _create_html_template(self) -> str:
        """
        보고서용 HTML 템플릿 생성
        """
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Noto Sans KR', 'Segoe UI', sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f5f7fa;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 15px;
        }}

        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
            font-weight: 300;
        }}

        .header .date {{
            margin-top: 20px;
            font-size: 0.9em;
            opacity: 0.8;
        }}

        .content {{
            padding: 40px;
        }}

        .section {{
            margin-bottom: 50px;
            page-break-inside: avoid;
        }}

        .section:last-child {{
            margin-bottom: 0;
        }}

        h1 {{
            color: #667eea;
            font-size: 2em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 25px;
            margin-top: 40px;
        }}

        h1:first-child {{
            margin-top: 0;
        }}

        h2 {{
            color: #764ba2;
            font-size: 1.6em;
            margin-top: 30px;
            margin-bottom: 20px;
            padding-left: 15px;
            border-left: 4px solid #764ba2;
        }}

        h3 {{
            color: #555;
            font-size: 1.3em;
            margin-top: 25px;
            margin-bottom: 15px;
        }}

        h4 {{
            color: #666;
            font-size: 1.1em;
            margin-top: 20px;
            margin-bottom: 10px;
            font-weight: 500;
        }}

        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}

        ul, ol {{
            margin-left: 30px;
            margin-bottom: 15px;
        }}

        li {{
            margin-bottom: 8px;
        }}

        .highlight {{
            background: #fff3cd;
            padding: 20px;
            border-left: 5px solid #ffc107;
            margin: 20px 0;
            border-radius: 5px;
        }}

        .warning {{
            background: #f8d7da;
            padding: 20px;
            border-left: 5px solid #dc3545;
            margin: 20px 0;
            border-radius: 5px;
        }}

        .success {{
            background: #d4edda;
            padding: 20px;
            border-left: 5px solid #28a745;
            margin: 20px 0;
            border-radius: 5px;
        }}

        .info {{
            background: #d1ecf1;
            padding: 20px;
            border-left: 5px solid #17a2b8;
            margin: 20px 0;
            border-radius: 5px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}

        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 500;
        }}

        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #e83e8c;
        }}

        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 20px 0;
        }}

        pre code {{
            background: none;
            color: inherit;
            padding: 0;
        }}

        .divider {{
            height: 2px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            margin: 50px 0;
            opacity: 0.3;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 30px 40px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #ddd;
        }}

        .footer p {{
            margin: 5px 0;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
            }}

            .header {{
                page-break-after: always;
            }}

            .section {{
                page-break-inside: avoid;
            }}
        }}

        @media (max-width: 768px) {{
            .header {{
                padding: 40px 20px;
            }}

            .header h1 {{
                font-size: 1.8em;
            }}

            .content {{
                padding: 20px;
            }}

            h1 {{
                font-size: 1.5em;
            }}

            h2 {{
                font-size: 1.3em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>EV Investment Analysis Report</h1>
            <div class="subtitle">전기차 산업 투자 분석 보고서</div>
            <div class="date">{date}</div>
        </div>

        <div class="content">
            {content}
        </div>

        <div class="footer">
            <p><strong>생성 일시:</strong> {generated_time}</p>
            <p>이 보고서는 참고용으로만 사용되어야 합니다. 투자 결정은 투자자 자신의 판단과 책임 하에 이루어져야 합니다.</p>
            <p style="margin-top: 15px; opacity: 0.7;">Generated by EVI Agent System</p>
        </div>
    </div>
</body>
</html>"""

    def markdown_to_html(self, md_content: str, title: str = "Investment Report",
                         date: str = None) -> str:
        """
        Markdown을 HTML로 변환

        Args:
            md_content: Markdown 콘텐츠
            title: 보고서 제목
            date: 보고서 날짜

        Returns:
            HTML 문자열
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Markdown을 HTML로 변환
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'codehilite', 'toc', 'tables', 'fenced_code']
        )

        # 스타일 클래스 적용
        html_content = html_content.replace('<p>[WARNING]', '<div class="warning"><p><strong>[WARNING]</strong>')
        html_content = html_content.replace('<p>✅', '<div class="success"><p>✅')
        html_content = html_content.replace('<p>⚠️', '<div class="warning"><p>⚠️')
        html_content = html_content.replace('<p>[OK]', '<div class="success"><p><strong>[OK]</strong>')

        # 섹션 분리
        sections = html_content.split('<hr>')
        formatted_sections = []
        for section in sections:
            if section.strip():
                formatted_sections.append(f'<div class="section">{section}</div>')

        html_content = '<div class="divider"></div>'.join(formatted_sections)

        # 템플릿에 삽입
        html_output = self.html_template.format(
            title=title,
            date=date,
            content=html_content,
            generated_time=generated_time
        )

        return html_output

    def save_html(self, md_content: str, output_path: str,
                  title: str = "Investment Report", date: str = None):
        """
        Markdown을 HTML 파일로 저장

        Args:
            md_content: Markdown 콘텐츠
            output_path: 출력 파일 경로
            title: 보고서 제목
            date: 보고서 날짜
        """
        html_content = self.markdown_to_html(md_content, title, date)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"   [OK] HTML 저장 완료: {output_path}")

    def html_to_pdf(self, html_path: str, pdf_path: str):
        """
        HTML을 PDF로 변환

        Args:
            html_path: HTML 파일 경로
            pdf_path: PDF 출력 경로
        """
        try:
            import pdfkit

            options = {
                'page-size': 'A4',
                'margin-top': '20mm',
                'margin-right': '20mm',
                'margin-bottom': '20mm',
                'margin-left': '20mm',
                'encoding': 'UTF-8',
                'no-outline': None,
                'enable-local-file-access': None
            }

            pdfkit.from_file(html_path, pdf_path, options=options)
            print(f"   [OK] PDF 변환 완료: {pdf_path}")

        except ImportError:
            print("   [WARNING] pdfkit이 설치되지 않았습니다. PDF 변환을 건너뜁니다.")
            print("   설치 방법: pip install pdfkit")
            print("   wkhtmltopdf도 설치 필요: https://wkhtmltopdf.org/downloads.html")
        except Exception as e:
            print(f"   [WARNING] PDF 변환 실패: {e}")

    def convert_markdown_file(self, md_path: str, generate_pdf: bool = True):
        """
        Markdown 파일을 HTML과 PDF로 변환

        Args:
            md_path: Markdown 파일 경로
            generate_pdf: PDF 생성 여부
        """
        md_path = Path(md_path)

        # Markdown 읽기
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # HTML 저장
        html_path = md_path.with_suffix('.html')
        self.save_html(md_content, str(html_path),
                      title="EV Investment Analysis Report",
                      date=datetime.now().strftime("%Y년 %m월"))

        # PDF 생성 (옵션)
        if generate_pdf:
            pdf_path = md_path.with_suffix('.pdf')
            self.html_to_pdf(str(html_path), str(pdf_path))
